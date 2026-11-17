from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

DocumentType = Literal[
    "study_plan",
    "regulation",
    "prerequisites",
    "resolution",
    "other",
]


class DocumentIngestRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, description="Official document title")
    document_type: DocumentType = Field(..., description="Institutional document category")
    career_id: int | None = Field(
        None,
        ge=1,
        description="Target career ID from `instituto.carrera`, or NULL if institution-wide",
    )
    full_content: str | None = Field(None, description="Full plain text to split automatically into chunks")
    chunks: list[str] | None = Field(None, description="Optional list of pre-split chunks")
    additional_metadata: dict[str, Any] | None = Field(default_factory=dict)
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
        },
    )


class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    content: str
    metadata: dict[str, Any]
    cosine_distance: float | None = None

    model_config = ConfigDict(from_attributes=True)


class DocumentMetadataResponse(BaseModel):
    id: int
    title: str
    document_type: str
    uploaded_at: datetime
    career_id: int | None = None
    career_name: str | None = None
    active: bool
    total_chunks: int = 0

    model_config = ConfigDict(from_attributes=True)


class DocumentIngestResponse(BaseModel):
    document_id: int
    title: str
    document_type: str
    career_id: int | None = None
    career_name: str | None = None
    chunks_created: int
    message: str
