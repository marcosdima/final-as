import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import AuthenticatedUser, get_current_user
from app.models.bot import BotUser, ChatHistory
from app.models.institute import InstituteUser
from app.schemas.chat import ChatHistoryItemResponse, ChatQueryRequest, ChatQueryResponse
from app.services.rag import answer_chat_query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Virtual Assistant (RAG)"])


@router.post(
    "/",
    response_model=ChatQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Query the academic virtual assistant (RAG + Institute DB with RBAC)",
)
async def chat_endpoint(
    request: ChatQueryRequest,
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Process a natural-language query for the JWT-authenticated user, combining
    hybrid pgvector search with RBAC-scoped queries over the `instituto` schema.
    """
    try:
        return await answer_chat_query(db, request, current_user)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        await db.rollback()
        logger.exception("Error processing RAG chat query")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while processing assistant query.",
        ) from exc


@router.get(
    "/history",
    response_model=list[ChatHistoryItemResponse],
    summary="Audit log: chat query history (RBAC-isolated)",
)
async def get_chat_history(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[
        int | None,
        Query(ge=1, description="Filter by `instituto.usuario.id` (Preceptor / Admin only)"),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """
    Return audited interactions from `isft189.historial_consultas`:
    - STUDENT / TEACHER: strictly limited to their own history.
    - PRECEPTOR / ADMIN: institution-wide audit log with optional `user_id` (`instituto.usuario.id`) filter.
    """
    stmt = (
        select(ChatHistory)
        .order_by(ChatHistory.created_at.desc())
        .limit(limit)
    )

    if current_user.role in ("STUDENT", "TEACHER"):
        if user_id is not None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view another user's chat history.",
            )
        bot_user = (
            await db.execute(select(BotUser).where(BotUser.email == current_user.email))
        ).scalar_one_or_none()
        if not bot_user:
            return []
        stmt = stmt.where(ChatHistory.user_id == bot_user.id)
    elif current_user.role in ("PRECEPTOR", "ADMIN"):
        if user_id is not None:
            inst_user = (
                await db.execute(select(InstituteUser).where(InstituteUser.id == user_id))
            ).scalar_one_or_none()
            if not inst_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Institutional user with id={user_id} not found.",
                )
            bot_user = (
                await db.execute(select(BotUser).where(BotUser.email == inst_user.email))
            ).scalar_one_or_none()
            if not bot_user:
                return []
            stmt = stmt.where(ChatHistory.user_id == bot_user.id)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role not authorized to inspect chat history.",
        )

    result = await db.execute(stmt)
    return list(result.scalars().all())
