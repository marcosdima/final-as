import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import BotUser, ChatHistory
from app.schemas import ChatHistoryItemResponse, ChatQueryRequest, ChatQueryResponse
from app.security import AuthenticatedUser, get_current_user
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
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Process a natural-language query for the JWT-authenticated user, combining
    hybrid pgvector search with RBAC-scoped queries over the `instituto` schema.
    """
    try:
        return await answer_chat_query(db, request, current_user)
    except Exception:
        await db.rollback()
        logger.exception("Error processing RAG chat query")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while processing assistant query.",
        )


@router.get(
    "/history",
    response_model=List[ChatHistoryItemResponse],
    summary="Audit log: chat query history (RBAC-isolated)",
)
async def get_chat_history(
    user_id: Optional[int] = Query(
        None,
        description="Filter by `isft189.usuarios.id` (Preceptor / Admin only)",
    ),
    limit: int = Query(20, ge=1, le=100),
    current_user: AuthenticatedUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Return audited interactions from `isft189.historial_consultas`:
    - STUDENT / TEACHER: strictly limited to their own history.
    - PRECEPTOR / ADMIN: institution-wide audit log with optional `user_id` filter.
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
            stmt = stmt.where(ChatHistory.user_id == user_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role not authorized to inspect chat history.",
        )

    result = await db.execute(stmt)
    return list(result.scalars().all())
