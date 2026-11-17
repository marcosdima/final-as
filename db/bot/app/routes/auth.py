from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    ROLE_FROM_DB,
    AuthenticatedUser,
    create_access_token,
    get_current_user,
    resolve_academic_profile,
    verify_password,
)
from app.models.institute import InstituteUser
from app.schemas.auth import LoginRequest, TokenResponse, UserProfileResponse

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])


async def _authenticate_and_issue_token(
    email: str,
    password: str,
    db: AsyncSession,
) -> TokenResponse:
    email_norm = email.strip().lower()
    stmt = select(InstituteUser).where(InstituteUser.email == email_norm)
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Institutional account is disabled.",
        )

    api_role = ROLE_FROM_DB.get(user.role, user.role)
    student_id, teacher_id, file_number = await resolve_academic_profile(db, user)

    token = create_access_token(user_id=user.id, email=user.email, role=api_role)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
        user=UserProfileResponse(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            role=api_role,
            student_id=student_id,
            teacher_id=teacher_id,
            file_number=file_number,
        ),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Institutional JSON login returning JWT",
)
async def login(
    request: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Authenticate credentials against `instituto.usuario` (bcrypt) and issue an RBAC JWT."""
    return await _authenticate_and_issue_token(request.email, request.password, db)


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="OAuth2 form login for Swagger UI Authorize button",
)
async def login_oauth2_form(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """OAuth2PasswordBearer-compatible endpoint used directly by Swagger UI (/docs)."""
    return await _authenticate_and_issue_token(form_data.username, form_data.password, db)


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Get authenticated user profile",
)
async def get_me(
    current_user: Annotated[AuthenticatedUser, Depends(get_current_user)],
):
    return UserProfileResponse(
        id=current_user.user_id,
        full_name=current_user.full_name,
        email=current_user.email,
        role=current_user.role,
        student_id=current_user.student_id,
        teacher_id=current_user.teacher_id,
        file_number=current_user.file_number,
    )
