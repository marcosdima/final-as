from datetime import datetime
from typing import List, Tuple
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.embeddings import embed_query
from app.llm import llm_service
from app.models import DocumentoMetadata, DocumentoVectorial, HistorialConsulta
from app.schemas import ChatQueryRequest, ChatQueryResponse, FragmentoResponse


async def retrieve_relevant_fragments(
    db: AsyncSession,
    query: str,
    filtro_carrera: str | None = None,
    filtro_tipo_documento: str | None = None,
    top_k: int = 4
) -> List[Tuple[DocumentoVectorial, float]]:
    """
    Búsqueda híbrida con pgvector: combina distancia de coseno (<=>)
    con filtros relacionales y metadatos JSONB.
    """
    # 1. Generar vector para la consulta
    query_vec = embed_query(query)

    # 2. Construir distancia de coseno
    distance_col = DocumentoVectorial.embedding.cosine_distance(query_vec).label("distancia")

    stmt = (
        select(DocumentoVectorial, distance_col)
        .join(DocumentoMetadata, DocumentoVectorial.documento_id == DocumentoMetadata.id)
        .where(DocumentoMetadata.activo == True)
    )

    # Filtro relacional opcional por carrera (o documentos institucionales comunes con carrera IS NULL)
    if filtro_carrera:
        stmt = stmt.where(
            or_(
                DocumentoMetadata.carrera == filtro_carrera,
                DocumentoMetadata.carrera.is_(None)
            )
        )

    # Filtro relacional opcional por tipo de documento
    if filtro_tipo_documento:
        stmt = stmt.where(DocumentoMetadata.tipo_documento == filtro_tipo_documento)

    # Ordenar por proximidad angular en el espacio vectorial (operador <=> de HNSW)
    stmt = stmt.order_by(distance_col.asc()).limit(top_k)

    result = await db.execute(stmt)
    records = result.all()

    # Filtrar por distancia máxima admisible
    filtered = [
        (vec_row, float(dist))
        for vec_row, dist in records
        if dist <= settings.MAX_COSINE_DISTANCE
    ]

    return filtered


async def answer_chat_query(
    db: AsyncSession,
    request: ChatQueryRequest
) -> ChatQueryResponse:
    """
    Orquesta la recuperación de fragmentos, generación con LLM y registro de auditoría.
    """
    top_k = request.top_k or settings.TOP_K

    # 1. Recuperación vectorial híbrida
    results = await retrieve_relevant_fragments(
        db=db,
        query=request.pregunta,
        filtro_carrera=request.filtro_carrera,
        filtro_tipo_documento=request.filtro_tipo_documento,
        top_k=top_k
    )

    # 2. Formatear fragmentos para el LLM y la respuesta
    fragment_texts = [row.contenido for row, _ in results]
    fragment_responses = [
        FragmentoResponse(
            id=row.id,
            documento_id=row.documento_id,
            contenido=row.contenido,
            metadata=row.meta,
            distancia_coseno=round(dist, 4)
        )
        for row, dist in results
    ]

    # 3. Generar respuesta con el proveedor LLM configurado (Groq / OpenRouter)
    respuesta_generada = await llm_service.generate_response(
        query=request.pregunta,
        context_fragments=fragment_texts,
        temperature=request.temperatura
    )

    # 4. Auditoría: persistir en historial_consultas
    historial_entry = HistorialConsulta(
        usuario_id=request.usuario_id,
        pregunta=request.pregunta,
        respuesta=respuesta_generada,
        fecha_consulta=datetime.utcnow()
    )
    db.add(historial_entry)
    await db.commit()

    _, _, model_name = settings.get_llm_credentials()

    return ChatQueryResponse(
        pregunta=request.pregunta,
        respuesta=respuesta_generada,
        proveedor_llm=settings.LLM_PROVIDER,
        modelo=model_name,
        fragmentos_recuperados=fragment_responses,
        fecha_consulta=historial_entry.fecha_consulta
    )
