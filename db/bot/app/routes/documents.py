from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import DocumentoMetadata, DocumentoVectorial
from app.schemas import (
    DocumentoIngestRequest,
    DocumentoIngestResponse,
    DocumentoMetadataResponse
)
from app.services.ingestion import ingest_document

router = APIRouter(prefix="/documents", tags=["Documentos"])


@router.post(
    "/ingest",
    response_model=DocumentoIngestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingestar y vectorizar documento"
)
async def ingest_document_endpoint(
    request: DocumentoIngestRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Registra un documento institucional, lo divide en fragmentos semánticos,
    calcula sus embeddings con pgvector (384 dimensiones) y los indexa.
    """
    try:
        response = await ingest_document(db, request)
        return response
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante la ingesta: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[DocumentoMetadataResponse],
    summary="Listar documentos institucionales"
)
async def list_documents(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    carrera: Optional[str] = Query(None, description="Filtrar por carrera"),
    solo_activos: bool = Query(True, description="Mostrar solo documentos activos"),
    db: AsyncSession = Depends(get_db)
):
    """
    Devuelve la lista de documentos registrados junto con la cantidad de fragmentos indexados.
    """
    stmt = (
        select(
            DocumentoMetadata,
            func.count(DocumentoVectorial.id).label("total_fragmentos")
        )
        .outerjoin(
            DocumentoVectorial,
            DocumentoMetadata.id == DocumentoVectorial.documento_id
        )
        .group_by(DocumentoMetadata.id)
        .order_by(DocumentoMetadata.id.desc())
    )

    if solo_activos:
        stmt = stmt.where(DocumentoMetadata.activo == True)
    if tipo:
        stmt = stmt.where(DocumentoMetadata.tipo_documento == tipo)
    if carrera:
        stmt = stmt.where(DocumentoMetadata.carrera == carrera)

    result = await db.execute(stmt)
    rows = result.all()

    response = []
    for doc, count in rows:
        item = DocumentoMetadataResponse(
            id=doc.id,
            titulo=doc.titulo,
            tipo_documento=doc.tipo_documento,
            fecha_subida=doc.fecha_subida,
            carrera=doc.carrera,
            activo=doc.activo,
            total_fragmentos=count
        )
        response.append(item)

    return response


@router.get(
    "/{document_id}",
    response_model=DocumentoMetadataResponse,
    summary="Obtener detalle de documento"
)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(
            DocumentoMetadata,
            func.count(DocumentoVectorial.id).label("total_fragmentos")
        )
        .outerjoin(
            DocumentoVectorial,
            DocumentoMetadata.id == DocumentoVectorial.documento_id
        )
        .where(DocumentoMetadata.id == document_id)
        .group_by(DocumentoMetadata.id)
    )
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    doc, count = row
    return DocumentoMetadataResponse(
        id=doc.id,
        titulo=doc.titulo,
        tipo_documento=doc.tipo_documento,
        fecha_subida=doc.fecha_subida,
        carrera=doc.carrera,
        activo=doc.activo,
        total_fragmentos=count
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar documento e indexaciones asociadas"
)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(DocumentoMetadata).where(DocumentoMetadata.id == document_id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    await db.delete(doc)
    await db.commit()
    return {"mensaje": f"Documento {document_id} y sus vectores eliminados exitosamente."}
