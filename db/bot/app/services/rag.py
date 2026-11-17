import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.embeddings import embed_query_async
from app.institute_models import Career
from app.llm import llm_service
from app.models import BotUser, ChatHistory, DocumentChunk, DocumentMetadata
from app.schemas import ChatQueryRequest, ChatQueryResponse, DocumentChunkResponse
from app.security import AuthenticatedUser
from app.services import academic
from app.services.ingestion import DOC_TYPE_FROM_DB, DOC_TYPE_TO_DB


async def retrieve_relevant_fragments(
    db: AsyncSession,
    query: str,
    career_id_filter: Optional[int] = None,
    document_type_filter: Optional[str] = None,
    metadata_filter: Optional[Dict[str, Any]] = None,
    top_k: int = 4,
) -> List[Tuple[DocumentChunk, DocumentMetadata, Optional[str], float]]:
    """
    Hybrid pgvector search combining cosine distance (<=>) with relational filters
    (`active`, `career_id`, `document_type`) and JSONB containment (`@>`).
    """
    query_vec = await embed_query_async(query)
    distance_col = DocumentChunk.embedding.cosine_distance(query_vec).label("distance")

    stmt = (
        select(DocumentChunk, DocumentMetadata, Career.name.label("career_name"), distance_col)
        .join(DocumentMetadata, DocumentChunk.document_id == DocumentMetadata.id)
        .outerjoin(Career, DocumentMetadata.career_id == Career.id)
        .where(DocumentMetadata.active == True)
    )

    if career_id_filter is not None:
        stmt = stmt.where(
            or_(
                DocumentMetadata.career_id == career_id_filter,
                DocumentMetadata.career_id.is_(None),
            )
        )

    if document_type_filter:
        db_doc_type = DOC_TYPE_TO_DB.get(document_type_filter, document_type_filter)
        stmt = stmt.where(DocumentMetadata.document_type == db_doc_type)

    if metadata_filter:
        stmt = stmt.where(DocumentChunk.meta.contains(metadata_filter))

    stmt = stmt.order_by(distance_col.asc()).limit(top_k)

    records = (await db.execute(stmt)).all()
    return [
        (chunk_row, doc_row, career_name, float(dist))
        for chunk_row, doc_row, career_name, dist in records
        if dist <= settings.MAX_COSINE_DISTANCE
    ]


def _format_fragment_for_llm(
    chunk_row: DocumentChunk,
    doc_row: DocumentMetadata,
    career_name: Optional[str],
) -> str:
    career_label = career_name or "Institution-wide"
    doc_type_label = DOC_TYPE_FROM_DB.get(doc_row.document_type, doc_row.document_type)
    return (
        f"[Fuente: {doc_row.title} | Tipo: {doc_type_label} | Carrera: {career_label}]\n"
        f"{chunk_row.content}"
    )


def _build_tools_for_user(user: AuthenticatedUser) -> List[Dict[str, Any]]:
    """Build the OpenAI tool catalog scoped strictly by the user's RBAC role."""
    tools: List[Dict[str, Any]] = [
        {
            "type": "function",
            "function": {
                "name": "search_institutional_docs",
                "description": (
                    "Search the vector database for official ISFT 189 regulations, resolutions, "
                    "study plans, and general prerequisite rules."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Semantic search text"},
                        "career_id_filter": {"type": ["integer", "null"], "description": "Optional career ID from instituto.carrera"},
                        "document_type_filter": {
                            "type": ["string", "null"],
                            "enum": ["study_plan", "regulation", "prerequisites", "resolution", "other", None],
                        },
                    },
                    "required": ["query"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_institutional_notices",
                "description": "Retrieve active institutional notices visible to the user's role.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_academic_offer",
                "description": "List active careers, study plans, and subjects with workload hours.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "career": {"type": ["string", "null"], "description": "Optional partial career name"},
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_exam_boards",
                "description": "Retrieve exam enrollment periods and scheduled final exam boards.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subject": {"type": ["string", "null"], "description": "Optional partial subject name"},
                    },
                },
            },
        },
    ]

    if user.role == "STUDENT" and user.student_id is not None:
        tools.extend([
            {
                "type": "function",
                "function": {
                    "name": "get_my_academic_history",
                    "description": "Retrieve careers, course enrollments, partial grades, final exams, and average for the authenticated student.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_my_attendance",
                    "description": "Calculate accumulated attendance percentage per subject for the authenticated student.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "check_my_prerequisites",
                    "description": "Check whether the authenticated student satisfies prerequisites to enroll or take the final exam for a subject.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "subject_name": {"type": "string", "description": "Target subject name"},
                        },
                        "required": ["subject_name"],
                    },
                },
            },
        ])

    if user.role == "TEACHER" and user.teacher_id is not None:
        tools.extend([
            {
                "type": "function",
                "function": {
                    "name": "get_my_course_rosters",
                    "description": "List subjects assigned to the authenticated teacher and enrolled student rosters.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "subject_name": {"type": ["string", "null"], "description": "Optional partial subject name"},
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_my_exam_boards",
                    "description": "List exam boards where the authenticated teacher acts as chair or observer.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
        ])

    if user.role in ("PRECEPTOR", "ADMIN"):
        tools.append({
            "type": "function",
            "function": {
                "name": "get_student_record_admin",
                "description": "Look up a student's academic history and attendance by file_number or dni (Preceptor/Admin only).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_number": {"type": ["integer", "null"], "description": "Student file number (legajo)"},
                        "dni": {"type": ["string", "null"], "description": "Student national ID (DNI)"},
                    },
                },
            },
        })

    return tools


async def _ensure_bot_user_id(db: AsyncSession, user: AuthenticatedUser) -> int:
    """Atomically upsert `isft189.usuarios` by email to bridge `instituto.usuario` safely."""
    stmt = (
        pg_insert(BotUser)
        .values(
            nombre=user.full_name,
            email=user.email,
            rol=user.db_role,
            fecha_registro=datetime.now(timezone.utc),
        )
        .on_conflict_do_update(
            index_elements=[BotUser.email],
            set_={"nombre": user.full_name, "rol": user.db_role},
        )
        .returning(BotUser.id)
    )
    bot_user_id = (await db.execute(stmt)).scalar_one()
    return int(bot_user_id)


async def _fallback_academic_lookup(
    db: AsyncSession,
    user: AuthenticatedUser,
    question: str,
    academic_sources: List[str],
) -> Optional[str]:
    """Deterministic academic lookup when no external LLM API key is configured."""
    q = question.lower()

    if "aviso" in q or "comunicado" in q or "novedad" in q:
        notices = await academic.get_active_notices(db, user.db_role)
        academic_sources.append("instituto.aviso")
        return "Avisos institucionales vigentes:\n" + json.dumps(notices, ensure_ascii=False, indent=2)

    if "mesa" in q or "examen" in q or "inscripcion" in q or "inscripción" in q or "periodo" in q or "período" in q:
        boards = await academic.get_exam_boards_overview(db)
        academic_sources.append("instituto.mesa_examen / instituto.periodo_inscripcion")
        return "Mesas de examen y períodos vigentes:\n" + json.dumps(boards, ensure_ascii=False, indent=2)

    if user.role == "STUDENT" and user.student_id is not None:
        if "asistencia" in q or "falta" in q or "presentismo" in q:
            attendance = await academic.get_student_attendance(db, user.student_id)
            academic_sources.append("instituto.asistencia")
            return "Tu registro de asistencias:\n" + json.dumps(attendance, ensure_ascii=False, indent=2)
        if "nota" in q or "historia" in q or "promedio" in q or "cursada" in q:
            history = await academic.get_student_history(db, user.student_id)
            academic_sources.append("instituto.inscripcion_cursada / instituto.inscripcion_examen")
            return "Tu historia académica:\n" + json.dumps(history, ensure_ascii=False, indent=2)
        if "correlativ" in q or "puedo cursar" in q or "puedo rendir" in q:
            # Extract probable subject keywords after stripping common filler words
            subject_hint = q.replace("correlatividades", "").replace("correlativa", "").strip()
            if subject_hint:
                academic_sources.append("instituto.correlatividad")
                prereqs = await academic.check_student_prerequisites(db, user.student_id, subject_hint)
                if prereqs.get("matches"):
                    return "Validación de correlatividades:\n" + json.dumps(prereqs, ensure_ascii=False, indent=2)

    if user.role == "TEACHER" and user.teacher_id is not None:
        if "nomina" in q or "nómina" in q or "alumno" in q or "materia" in q:
            rosters = await academic.get_teacher_course_rosters(db, user.teacher_id)
            academic_sources.append("instituto.asignacion_materia / instituto.inscripcion_cursada")
            return "Tus materias y nóminas:\n" + json.dumps(rosters, ensure_ascii=False, indent=2)

    return None


async def answer_chat_query(
    db: AsyncSession,
    request: ChatQueryRequest,
    user: AuthenticatedUser,
) -> ChatQueryResponse:
    """Orchestrate hybrid vector search, RBAC academic tools, LLM synthesis, and audit logging."""
    if request.career_id_filter is not None:
        career_exists = (
            await db.execute(select(Career.id).where(Career.id == request.career_id_filter))
        ).scalar_one_or_none()
        if career_exists is None:
            raise LookupError(f"Career with id={request.career_id_filter} not found.")

    top_k = request.top_k or settings.TOP_K

    initial_results = await retrieve_relevant_fragments(
        db=db,
        query=request.question,
        career_id_filter=request.career_id_filter,
        document_type_filter=request.document_type_filter,
        metadata_filter=request.metadata_filter,
        top_k=top_k,
    )

    collected_chunks: Dict[int, DocumentChunkResponse] = {}
    llm_context_fragments: List[str] = []
    for chunk_row, doc_row, career_name, dist in initial_results:
        collected_chunks[chunk_row.id] = DocumentChunkResponse(
            id=chunk_row.id,
            document_id=chunk_row.document_id,
            content=chunk_row.content,
            metadata=chunk_row.meta,
            cosine_distance=round(dist, 4),
        )
        llm_context_fragments.append(_format_fragment_for_llm(chunk_row, doc_row, career_name))

    academic_sources: List[str] = []

    async def execute_tool(tool_name: str, args: Dict[str, Any]) -> str:
        if tool_name == "search_institutional_docs":
            results = await retrieve_relevant_fragments(
                db=db,
                query=args.get("query", request.question),
                career_id_filter=args.get("career_id_filter") or request.career_id_filter,
                document_type_filter=args.get("document_type_filter") or request.document_type_filter,
                top_k=top_k,
            )
            if not results:
                return "No relevant document fragments were found for that search."
            blocks = []
            for c_row, d_row, c_name, dist in results:
                collected_chunks[c_row.id] = DocumentChunkResponse(
                    id=c_row.id,
                    document_id=c_row.document_id,
                    content=c_row.content,
                    metadata=c_row.meta,
                    cosine_distance=round(dist, 4),
                )
                blocks.append(_format_fragment_for_llm(c_row, d_row, c_name))
            return "\n\n".join(blocks)

        if tool_name == "get_institutional_notices":
            academic_sources.append("instituto.aviso")
            data = await academic.get_active_notices(db, user.db_role)
            return json.dumps(data, ensure_ascii=False)

        if tool_name == "get_academic_offer":
            academic_sources.append("instituto.carrera / plan_estudio / materia")
            data = await academic.get_careers_with_subjects(db, args.get("career"))
            return json.dumps(data, ensure_ascii=False)

        if tool_name == "get_exam_boards":
            academic_sources.append("instituto.mesa_examen / periodo_inscripcion")
            data = await academic.get_exam_boards_overview(db, args.get("subject"))
            return json.dumps(data, ensure_ascii=False)

        if tool_name == "get_my_academic_history" and user.role == "STUDENT" and user.student_id:
            academic_sources.append("instituto.inscripcion_cursada / calificacion_parcial / inscripcion_examen")
            data = await academic.get_student_history(db, user.student_id)
            return json.dumps(data, ensure_ascii=False)

        if tool_name == "get_my_attendance" and user.role == "STUDENT" and user.student_id:
            academic_sources.append("instituto.asistencia")
            data = await academic.get_student_attendance(db, user.student_id)
            return json.dumps(data, ensure_ascii=False)

        if tool_name == "check_my_prerequisites" and user.role == "STUDENT" and user.student_id:
            academic_sources.append("instituto.correlatividad")
            data = await academic.check_student_prerequisites(
                db, user.student_id, args.get("subject_name", "")
            )
            return json.dumps(data, ensure_ascii=False)

        if tool_name == "get_my_course_rosters" and user.role == "TEACHER" and user.teacher_id:
            academic_sources.append("instituto.asignacion_materia / inscripcion_cursada")
            data = await academic.get_teacher_course_rosters(
                db, user.teacher_id, args.get("subject_name")
            )
            return json.dumps(data, ensure_ascii=False)

        if tool_name == "get_my_exam_boards" and user.role == "TEACHER" and user.teacher_id:
            academic_sources.append("instituto.mesa_examen")
            data = await academic.get_teacher_exam_boards(db, user.teacher_id)
            return json.dumps(data, ensure_ascii=False)

        if tool_name == "get_student_record_admin" and user.role in ("PRECEPTOR", "ADMIN"):
            academic_sources.append("instituto.alumno (administrative query)")
            data = await academic.get_student_admin_detail(
                db, file_number=args.get("file_number"), dni=args.get("dni")
            )
            return json.dumps(data, ensure_ascii=False)

        return json.dumps({"error": "Tool not authorized for the current user role."})

    user_context = (
        f"Name: {user.full_name} | Email: {user.email} | Role: {user.role} | "
        f"File number: {user.file_number or 'N/A'}"
    )
    tools = _build_tools_for_user(user)

    generated_answer = await llm_service.generate_with_tools(
        query=request.question,
        user_context=user_context,
        context_fragments=llm_context_fragments,
        tools=tools,
        tool_executor=execute_tool,
        temperature=request.temperature,
    )

    if generated_answer is None:
        acad_fallback = await _fallback_academic_lookup(db, user, request.question, academic_sources)
        if acad_fallback:
            generated_answer = (
                f"{acad_fallback}\n\n"
                "(Respuesta directa de base académica sin LLM activo. Configure GROQ_API_KEY u OPENROUTER_API_KEY para síntesis conversacional)."
            )
        elif llm_context_fragments:
            generated_answer = (
                f"Información institucional recuperada del ISFT 189:\n\n{llm_context_fragments[0]}\n\n"
                "(Respuesta sintetizada automáticamente sin LLM activo. Configure la clave en .env)."
            )
        else:
            generated_answer = (
                "No se hallaron documentos ni registros académicos relacionados con su consulta. "
                "Recomendamos consultar en Secretaría del Instituto."
            )

    bot_user_id = await _ensure_bot_user_id(db, user)
    history_entry = ChatHistory(
        user_id=bot_user_id,
        question=request.question,
        answer=generated_answer,
        created_at=datetime.now(timezone.utc),
    )
    db.add(history_entry)
    await db.commit()

    _, _, model_name = settings.get_llm_credentials()
    unique_sources = list(dict.fromkeys(academic_sources))

    return ChatQueryResponse(
        question=request.question,
        answer=generated_answer,
        llm_provider=settings.LLM_PROVIDER,
        model=model_name,
        user_role=user.role,
        retrieved_chunks=list(collected_chunks.values()),
        academic_sources=unique_sources,
        created_at=history_entry.created_at,
    )
