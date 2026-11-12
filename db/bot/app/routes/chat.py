from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import HistorialConsulta
from app.schemas import ChatQueryRequest, ChatQueryResponse
from app.services.rag import answer_chat_query

router = APIRouter(prefix="/chat", tags=["Consultas y RAG"])


@router.post(
    "/",
    response_model=ChatQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar asistente virtual académico (RAG)"
)
async def chat_endpoint(
    request: ChatQueryRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Recibe una consulta de un estudiante o docente, recupera los fragmentos
    institucionales más relevantes utilizando búsqueda híbrida en pgvector,
    genera la respuesta mediante Groq u OpenRouter y registra la interacción en el historial.
    """
    try:
        response = await answer_chat_query(db, request)
        return response
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar consulta RAG: {str(e)}"
        )


@router.get(
    "/history",
    summary="Auditoría: Historial de consultas"
)
async def get_chat_history(
    usuario_id: Optional[int] = Query(None, description="Filtrar por ID de usuario"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Devuelve las consultas y respuestas auditadas en isft189.historial_consultas.
    """
    stmt = (
        select(HistorialConsulta)
        .order_by(HistorialConsulta.fecha_consulta.desc())
        .limit(limit)
    )
    if usuario_id is not None:
        stmt = stmt.where(HistorialConsulta.usuario_id == usuario_id)

    result = await db.execute(stmt)
    records = result.scalars().all()

    return [
        {
            "id": r.id,
            "usuario_id": r.usuario_id,
            "pregunta": r.pregunta,
            "respuesta": r.respuesta,
            "fecha_consulta": r.fecha_consulta
        }
        for r in records
    ]
