from datetime import UTC, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base

DocumentTypePgEnum = PgEnum(
    "plan_estudio",
    "reglamento",
    "correlatividades",
    "resolucion",
    "otro",
    name="tipo_documento",
    schema="isft189",
    create_type=False,
)


def _utc_now() -> datetime:
    return datetime.now(UTC)


class BotUser(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "isft189"}

    id = Column(BigInteger, primary_key=True, index=True)
    full_name = Column("nombre", String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    role = Column("rol", String(20), nullable=False, default="ALUMNO")
    registered_at = Column("fecha_registro", DateTime(timezone=True), default=_utc_now, nullable=False)

    queries = relationship("ChatHistory", back_populates="user")


class DocumentMetadata(Base):
    __tablename__ = "documentos_metadata"
    __table_args__ = {"schema": "isft189"}

    id = Column(BigInteger, primary_key=True, index=True)
    title = Column("titulo", String(200), nullable=False)
    document_type = Column("tipo_documento", DocumentTypePgEnum, nullable=False, index=True)
    uploaded_at = Column("fecha_subida", DateTime(timezone=True), default=_utc_now, nullable=False)
    career_id = Column(
        "carrera_id",
        BigInteger,
        ForeignKey("instituto.carrera.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )
    active = Column("activo", Boolean, nullable=False, default=True)

    chunks = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )


class DocumentChunk(Base):
    __tablename__ = "documentos_vectoriales"
    __table_args__ = {"schema": "isft189"}

    id = Column(BigInteger, primary_key=True, index=True)
    document_id = Column(
        "documento_id",
        BigInteger,
        ForeignKey("isft189.documentos_metadata.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content = Column("contenido", Text, nullable=False)
    meta = Column("metadata", JSONB, nullable=False, default=dict)
    embedding = Column(Vector(384), nullable=False)
    created_at = Column("fecha_creacion", DateTime(timezone=True), default=_utc_now, nullable=False)

    document = relationship("DocumentMetadata", back_populates="chunks")


class ChatHistory(Base):
    __tablename__ = "historial_consultas"
    __table_args__ = {"schema": "isft189"}

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(
        "usuario_id",
        BigInteger,
        ForeignKey("isft189.usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    question = Column("pregunta", Text, nullable=False)
    answer = Column("respuesta", Text, nullable=False)
    created_at = Column("fecha_consulta", DateTime(timezone=True), default=_utc_now, nullable=False)

    user = relationship("BotUser", back_populates="queries")
