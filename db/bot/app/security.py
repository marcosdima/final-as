from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.institute_models import InstituteUser, Student, Teacher

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)

ROLE_FROM_DB = {
    "ALUMNO": "STUDENT",
    "DOCENTE": "TEACHER",
    "PRECEPTOR": "PRECEPTOR",
    "ADMINISTRADOR": "ADMIN",
}
ROLE_TO_DB = {v: k for k, v in ROLE_FROM_DB.items()}


@dataclass
class AuthenticatedUser:
    """Authenticated institutional user and resolved RBAC context."""

    user_id: int
    full_name: str
    email: str
    role: str      # STUDENT | TEACHER | PRECEPTOR | ADMIN
    db_role: str   # ALUMNO | DOCENTE | PRECEPTOR | ADMINISTRADOR
    student_id: Optional[int] = None
    teacher_id: Optional[int] = None
    file_number: Optional[int] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(
    user_id: int,
    email: str,
    role: str,
    expires_minutes: Optional[int] = None,
) -> str:
    expire_delta = timedelta(minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES)
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + expire_delta).timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def resolve_academic_profile(
    db: AsyncSession,
    user: InstituteUser,
) -> tuple[Optional[int], Optional[int], Optional[int]]:
    """Resolve (student_id, teacher_id, file_number) for an InstituteUser."""
    if user.role == "ALUMNO":
        student = (
            await db.execute(select(Student).where(Student.user_id == user.id))
        ).scalar_one_or_none()
        if student:
            return student.id, None, student.file_number
    elif user.role == "DOCENTE":
        teacher = (
            await db.execute(select(Teacher).where(Teacher.user_id == user.id))
        ).scalar_one_or_none()
        if teacher:
            return None, teacher.id, teacher.file_number
    return None, None, None


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> AuthenticatedUser:
    """Validate Bearer JWT and resolve the active user and academic profile."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer JWT authentication is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(token)
    sub = payload.get("sub")
    if not sub or not str(sub).isdigit():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token does not contain a valid user identifier.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(sub)
    stmt = select(InstituteUser).where(InstituteUser.id == user_id)
    user = (await db.execute(stmt)).scalar_one_or_none()

    if not user or not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_role = ROLE_FROM_DB.get(user.role, user.role)
    student_id, teacher_id, file_number = await resolve_academic_profile(db, user)

    return AuthenticatedUser(
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        role=api_role,
        db_role=user.role,
        student_id=student_id,
        teacher_id=teacher_id,
        file_number=file_number,
    )


def require_roles(*allowed_roles: str) -> Callable:
    """RBAC guard restricting endpoint access to the specified roles."""
    async def role_checker(
        current_user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access denied for role '{current_user.role}'. "
                    f"Required role: {', '.join(allowed_roles)}."
                ),
            )
        return current_user

    return role_checker
