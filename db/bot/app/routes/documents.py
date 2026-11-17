import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pypdf.errors import PdfReadError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import AuthenticatedUser, get_current_user, require_roles
from app.models.bot import DocumentChunk, DocumentMetadata
from app.models.institute import Career
from app.schemas.documents import (
    DocumentIngestRequest,
    DocumentIngestResponse,
    DocumentMetadataResponse,
    DocumentType,
)
from app.services.ingestion import (
    DOC_TYPE_FROM_DB,
    DOC_TYPE_TO_DB,
    extract_text_from_pdf_bytes,
    ingest_document,
)

logger = logging.getLogger(__name__)
MAX_PDF_BYTES = 15 * 1024 * 1024  # 15 MB upload guard

router = APIRouter(prefix="/documents", tags=["Documents (RAG)"])


@router.post(
    "/ingest",
    response_model=DocumentIngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest and vectorize a plain-text document (Admin / Preceptor)",
)
async def ingest_document_endpoint(
    request: DocumentIngestRequest,
    current_user: Annotated[AuthenticatedUser, Depends(require_roles("ADMIN", "PRECEPTOR"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Split an institutional document into chunks, generate 384-d embeddings, and index in pgvector."""
    try:
        return await ingest_document(db, request)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        await db.rollback()
        logger.exception("Document ingestion failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error during document ingestion.",
        ) from exc


@router.post(
    "/ingest-pdf",
    response_model=DocumentIngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and vectorize an official PDF document (Admin / Preceptor)",
)
async def ingest_pdf_endpoint(
    file: Annotated[UploadFile, File(description="Official PDF file")],
    title: Annotated[str, Form(min_length=3, max_length=200)],
    document_type: Annotated[DocumentType, Form()],
    current_user: Annotated[AuthenticatedUser, Depends(require_roles("ADMIN", "PRECEPTOR"))],
    db: Annotated[AsyncSession, Depends(get_db)],
    career_id: Annotated[int | None, Form(ge=1, description="Career ID from instituto.carrera")] = None,
    chunk_size: Annotated[int, Form(ge=100, le=2000)] = 500,
    chunk_overlap: Annotated[int, Form(ge=0, le=200)] = 50,
):
    filename = (file.filename or "").lower()
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Uploaded file must have a .pdf extension.")

    pdf_bytes = await file.read(MAX_PDF_BYTES + 1)
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded PDF file is empty.")
    if len(pdf_bytes) > MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="Uploaded PDF exceeds the 15 MB size limit.")
    if not pdf_bytes.lstrip().startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid PDF document.")

    clean_title = title.strip()
    if len(clean_title) < 3:
        raise HTTPException(status_code=400, detail="Title must have at least 3 non-whitespace characters.")

    try:
        extracted_text = await asyncio.to_thread(extract_text_from_pdf_bytes, pdf_bytes)
        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the PDF (it may be a scanned document without OCR).",
            )

        ingest_req = DocumentIngestRequest(
            title=clean_title,
            document_type=document_type,
            career_id=career_id,
            full_content=extracted_text,
            additional_metadata={"source_filename": file.filename or "document.pdf"},
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return await ingest_document(db, ingest_req)
    except HTTPException:
        raise
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (PdfReadError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid PDF or parameters: {exc}") from exc
    except Exception as exc:
        await db.rollback()
        logger.exception("PDF ingestion failed")
        raise HTTPException(status_code=500, detail="Internal error while processing the PDF file.") from exc


@router.get(
    "/",
    response_model=list[DocumentMetadataResponse],
    summary="List indexed institutional documents",
)
async def list_documents(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    document_type: Annotated[DocumentType | None, Query(description="Filter by document type")] = None,
    career_id: Annotated[int | None, Query(ge=1, description="Filter by career ID")] = None,
    active_only: Annotated[bool, Query(description="Show active documents only")] = True,
):
    """Return registered documents along with their career name and indexed chunk count."""
    stmt = (
        select(
            DocumentMetadata,
            Career.name.label("career_name"),
            func.count(DocumentChunk.id).label("total_chunks"),
        )
        .outerjoin(Career, DocumentMetadata.career_id == Career.id)
        .outerjoin(DocumentChunk, DocumentMetadata.id == DocumentChunk.document_id)
        .group_by(DocumentMetadata.id, Career.name)
        .order_by(DocumentMetadata.id.desc())
    )

    if active_only:
        stmt = stmt.where(DocumentMetadata.active.is_(True))
    if document_type:
        stmt = stmt.where(DocumentMetadata.document_type == DOC_TYPE_TO_DB[document_type])
    if career_id is not None:
        stmt = stmt.where(DocumentMetadata.career_id == career_id)

    rows = (await db.execute(stmt)).all()

    return [
        DocumentMetadataResponse(
            id=doc.id,
            title=doc.title,
            document_type=DOC_TYPE_FROM_DB.get(doc.document_type, doc.document_type),
            uploaded_at=doc.uploaded_at,
            career_id=doc.career_id,
            career_name=career_name,
            active=doc.active,
            total_chunks=count,
        )
        for doc, career_name, count in rows
    ]


@router.get(
    "/{document_id}",
    response_model=DocumentMetadataResponse,
    summary="Get document details",
)
async def get_document(
    document_id: int,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = (
        select(
            DocumentMetadata,
            Career.name.label("career_name"),
            func.count(DocumentChunk.id).label("total_chunks"),
        )
        .outerjoin(Career, DocumentMetadata.career_id == Career.id)
        .outerjoin(DocumentChunk, DocumentMetadata.id == DocumentChunk.document_id)
        .where(DocumentMetadata.id == document_id)
        .group_by(DocumentMetadata.id, Career.name)
    )
    row = (await db.execute(stmt)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found.")

    doc, career_name, count = row
    return DocumentMetadataResponse(
        id=doc.id,
        title=doc.title,
        document_type=DOC_TYPE_FROM_DB.get(doc.document_type, doc.document_type),
        uploaded_at=doc.uploaded_at,
        career_id=doc.career_id,
        career_name=career_name,
        active=doc.active,
        total_chunks=count,
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a document and its vector chunks (Admin / Preceptor)",
)
async def delete_document(
    document_id: int,
    current_user: Annotated[AuthenticatedUser, Depends(require_roles("ADMIN", "PRECEPTOR"))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    stmt = select(DocumentMetadata).where(DocumentMetadata.id == document_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    await db.delete(doc)
    await db.commit()
    return {"message": f"Document {document_id} and its vector chunks deleted successfully."}
