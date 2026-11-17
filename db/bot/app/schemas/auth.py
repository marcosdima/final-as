from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

UserRole = Literal[
    "STUDENT",
    "TEACHER",
    "PRECEPTOR",
    "ADMIN",
]


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=150, description="Institutional email")
    password: str = Field(..., min_length=4, max_length=128, description="Account password")

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "email": "mdimatteo@alumno.isft189.edu.ar",
                "password": "isft189.2026",
            }
        },
    )


class UserProfileResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: UserRole
    student_id: int | None = None
    teacher_id: int | None = None
    file_number: int | None = None

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfileResponse
