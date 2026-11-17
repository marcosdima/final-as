from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.documents import DocumentChunkResponse, DocumentType


class ChatQueryRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Natural-language question from the authenticated user")
    career_id_filter: int | None = Field(
        None,
        ge=1,
        description="Optional career ID filter for vector search",
    )
    document_type_filter: DocumentType | None = Field(None, description="Optional document category filter")
    metadata_filter: dict[str, Any] | None = Field(
        None,
        description="Optional JSONB containment filter (@>) over chunk metadata",
    )
    top_k: int | None = Field(None, ge=1, le=10, description="Number of vector chunks to retrieve")
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
        },
    )


class ChatQueryResponse(BaseModel):
    question: str
    answer: str
    llm_provider: str
    model: str
    user_role: str
    retrieved_chunks: list[DocumentChunkResponse]
    academic_sources: list[str] = Field(default_factory=list)
    created_at: datetime


class ChatHistoryItemResponse(BaseModel):
    id: int
    user_id: int | None
    question: str
    answer: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
