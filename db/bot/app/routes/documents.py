import asyncio
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from pypdf.errors import PdfReadError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import DocumentChunk, DocumentMetadata
from app.schemas import (
    DocumentIngestRequest,
    DocumentIngestResponse,
    DocumentMetadataResponse,
    DocumentType,
)
from app.security import AuthenticatedUser, get_current_user, require_roles
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
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN", "PRECEPTOR")),
    db: AsyncSession = Depends(get_db),
):
    """Split an institutional document into chunks, generate 384-d embeddings, and index in pgvector."""
    try:
        return await ingest_document(db, request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception:
        await db.rollback()
        logger.exception("Document ingestion failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error during document ingestion.",
        )


@router.post(
    "/ingest-pdf",
    response_model=DocumentIngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and vectorize an official PDF document (Admin / Preceptor)",
)
async def ingest_pdf_endpoint(
    file: UploadFile = File(..., description="Official PDF file"),
    title: str = Form(..., min_length=3, max_length=200),
    document_type: DocumentType = Form(...),
    career: Optional[str] = Form(None),
    chunk_size: int = Form(500, ge=100, le=2000),
    chunk_overlap: int = Form(50, ge=0, le=200),
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN", "PRECEPTOR")),
    db: AsyncSession = Depends(get_db),
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
    clean_career = career.strip() or None if career else None

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
            career=clean_career,
            full_content=extracted_text,
            additional_metadata={"source_filename": file.filename or "document.pdf"},
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        return await ingest_document(db, ingest_req)
    except HTTPException:
        raise
    except (PdfReadError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid PDF or parameters: {exc}")
    except Exception:
        await db.rollback()
        logger.exception("PDF ingestion failed")
        raise HTTPException(status_code=500, detail="Internal error while processing the PDF file.")


@router.get(
    "/",
    response_model=List[DocumentMetadataResponse],
    summary="List indexed institutional documents",
)
async def list_documents(
    document_type: Optional[DocumentType] = Query(None, description="Filter by document type"),
    career: Optional[str] = Query(None, description="Filter by career"),
    active_only: bool = Query(True, description="Show active documents only"),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return registered documents along with their indexed chunk count."""
    stmt = (
        select(
            DocumentMetadata,
            func.count(DocumentChunk.id).label("total_chunks"),
        )
        .outerjoin(
            DocumentChunk,
            DocumentMetadata.id == DocumentChunk.document_id,
        )
        .group_by(DocumentMetadata.id)
        .order_by(DocumentMetadata.id.desc())
    )

    if active_only:
        stmt = stmt.where(DocumentMetadata.active == True)
    if document_type:
        stmt = stmt.where(DocumentMetadata.document_type == DOC_TYPE_TO_DB[document_type])
    if career and career.strip():
        stmt = stmt.where(DocumentMetadata.career.ilike(f"%{career.strip()}%"))

    rows = (await db.execute(stmt)).all()

    return [
        DocumentMetadataResponse(
            id=doc.id,
            title=doc.title,
            document_type=DOC_TYPE_FROM_DB.get(doc.document_type, doc.document_type),
            uploaded_at=doc.uploaded_at,
            career=doc.career,
            active=doc.active,
            total_chunks=count,
        )
        for doc, count in rows
    ]


@router.get(
    "/{document_id}",
    response_model=DocumentMetadataResponse,
    summary="Get document details",
)
async def get_document(
    document_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(
            DocumentMetadata,
            func.count(DocumentChunk.id).label("total_chunks"),
        )
        .outerjoin(
            DocumentChunk,
            DocumentMetadata.id == DocumentChunk.document_id,
        )
        .where(DocumentMetadata.id == document_id)
        .group_by(DocumentMetadata.id)
    )
    row = (await db.execute(stmt)).first()
    if not row:
        raise HTTPException(status_code=404, detail="Document not found.")

    doc, count = row
    return DocumentMetadataResponse(
        id=doc.id,
        title=doc.title,
        document_type=DOC_TYPE_FROM_DB.get(doc.document_type, doc.document_type),
        uploaded_at=doc.uploaded_at,
        career=doc.career,
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
    current_user: AuthenticatedUser = Depends(require_roles("ADMIN", "PRECEPTOR")),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(DocumentMetadata).where(DocumentMetadata.id == document_id)
    doc = (await db.execute(stmt)).scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    await db.delete(doc)
    await db.commit()
    return {"message": f"Document {document_id} and its vector chunks deleted successfully."}
