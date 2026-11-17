from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

DocumentType = Literal[
    "study_plan",
    "regulation",
    "prerequisites",
    "resolution",
    "other",
]

UserRole = Literal[
    "STUDENT",
    "TEACHER",
    "PRECEPTOR",
    "ADMIN",
]

PeriodType = Literal["COURSE", "EXAM"]


# ============================================================================
# Authentication & RBAC
# ============================================================================

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
    student_id: Optional[int] = None
    teacher_id: Optional[int] = None
    file_number: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserProfileResponse


# ============================================================================
# Academic Domain (`instituto`)
# ============================================================================

class SubjectItemResponse(BaseModel):
    id: int
    name: str
    year_in_plan: int
    workload_hours: int


class CareerResponse(BaseModel):
    id: int
    name: str
    awarded_title: str
    active: bool
    plan_year: Optional[int] = None
    resolution: Optional[str] = None
    subjects: List[SubjectItemResponse] = Field(default_factory=list)


class NoticeResponse(BaseModel):
    id: int
    title: str
    body: str
    published_at: str
    target_role: str


class EnrollmentPeriodResponse(BaseModel):
    id: int
    academic_year: int
    period_type: PeriodType
    start_date: str
    end_date: str


class ExamBoardItemResponse(BaseModel):
    id: int
    career: str
    subject: str
    academic_year: int
    exam_date: str
    exam_time: str
    chair_teacher: str
    observer_teacher: Optional[str] = None
    record_number: Optional[int] = None
    record_status: Optional[str] = None


class ExamBoardsOverviewResponse(BaseModel):
    exam_enrollment_periods: List[EnrollmentPeriodResponse]
    exam_boards: List[ExamBoardItemResponse]


class SubjectAttendanceResponse(BaseModel):
    subject: str
    academic_year: int
    condition: str
    total_classes: int
    attended_classes: int
    attendance_percentage: float


# ============================================================================
# Documents & Vectorization (`isft189`)
# ============================================================================

class DocumentIngestRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, description="Official document title")
    document_type: DocumentType = Field(..., description="Institutional document category")
    career_id: Optional[int] = Field(
        None,
        ge=1,
        description="Target career ID from `instituto.carrera`, or NULL if institution-wide",
    )
    full_content: Optional[str] = Field(None, description="Full plain text to split automatically into chunks")
    chunks: Optional[List[str]] = Field(None, description="Optional list of pre-split chunks")
    additional_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    chunk_size: int = Field(500, ge=100, le=2000, description="Target chunk size in characters")
    chunk_overlap: int = Field(50, ge=0, le=200, description="Overlap between adjacent chunks")

    @model_validator(mode="after")
    def validate_content_and_chunking(self) -> "DocumentIngestRequest":
        if len(self.title.strip()) < 3:
            raise ValueError("title must have at least 3 non-whitespace characters")

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")

        has_full_text = bool(self.full_content and self.full_content.strip())
        has_chunks = bool(self.chunks and any(c.strip() for c in self.chunks))
        if not has_full_text and not has_chunks:
            raise ValueError("Either 'full_content' or at least one non-empty item in 'chunks' must be provided")

        return self

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "title": "Régimen de Correlatividades - Desarrollo de Software",
                "document_type": "prerequisites",
                "career_id": 2,
                "full_content": "Para cursar y aprobar Desarrollo de sistemas Web se requiere Introducción a la programación, Administración y gestión de base de datos y Diseño Web.",
                "chunk_size": 500,
                "chunk_overlap": 50,
            }
        }
    )


class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    content: str
    metadata: Dict[str, Any]
    cosine_distance: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentMetadataResponse(BaseModel):
    id: int
    title: str
    document_type: str
    uploaded_at: datetime
    career_id: Optional[int] = None
    career_name: Optional[str] = None
    active: bool
    total_chunks: int = 0

    model_config = ConfigDict(from_attributes=True)


class DocumentIngestResponse(BaseModel):
    document_id: int
    title: str
    document_type: str
    career_id: Optional[int] = None
    career_name: Optional[str] = None
    chunks_created: int
    message: str


# ============================================================================
# Hybrid RAG Chat (`RF-045` to `RF-048`)
# ============================================================================

class ChatQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Natural-language question from the authenticated user")
    career_id_filter: Optional[int] = Field(
        None,
        ge=1,
        description="Optional career ID filter for vector search",
    )
    document_type_filter: Optional[DocumentType] = Field(None, description="Optional document category filter")
    metadata_filter: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional JSONB containment filter (@>) over chunk metadata",
    )
    top_k: Optional[int] = Field(None, ge=1, le=10, description="Number of vector chunks to retrieve")
    temperature: float = Field(0.2, ge=0.0, le=1.0, description="LLM sampling temperature")

    @model_validator(mode="after")
    def normalize_question(self) -> "ChatQueryRequest":
        if len(self.question.strip()) < 3:
            raise ValueError("question must have at least 3 non-whitespace characters")
        return self

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "question": "¿Cuál es mi porcentaje de asistencia en Base de Datos y qué mínimo exige el reglamento?",
                "top_k": 4,
                "temperature": 0.2,
            }
        }
    )


class ChatQueryResponse(BaseModel):
    question: str
    answer: str
    llm_provider: str
    model: str
    user_role: str
    retrieved_chunks: List[DocumentChunkResponse]
    academic_sources: List[str] = Field(default_factory=list)
    created_at: datetime


class ChatHistoryItemResponse(BaseModel):
    id: int
    user_id: Optional[int]
    question: str
    answer: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
