from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text
)
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from app.database import Base

TipoDocumentoEnum = PgEnum(
    "plan_estudio",
    "reglamento",
    "correlatividades",
    "resolucion",
    "otro",
    name="tipo_documento",
    schema="isft189",
    create_type=False
)


class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "isft189"}

    id = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    rol = Column(String(20), nullable=False, default="ALUMNO")
    fecha_registro = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    consultas = relationship("HistorialConsulta", back_populates="usuario")


class DocumentoMetadata(Base):
    __tablename__ = "documentos_metadata"
    __table_args__ = {"schema": "isft189"}

    id = Column(BigInteger, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    tipo_documento = Column(TipoDocumentoEnum, nullable=False, index=True)
    fecha_subida = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    carrera = Column(String(100), nullable=True, index=True)
    activo = Column(Boolean, nullable=False, default=True)

    fragmentos = relationship(
        "DocumentoVectorial",
        back_populates="documento",
        cascade="all, delete-orphan"
    )


class DocumentoVectorial(Base):
    __tablename__ = "documentos_vectoriales"
    __table_args__ = {"schema": "isft189"}

    id = Column(BigInteger, primary_key=True, index=True)
    documento_id = Column(
        BigInteger,
        ForeignKey("isft189.documentos_metadata.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    contenido = Column(Text, nullable=False)
    # Mapeo a la columna SQL "metadata" sin colisionar con Base.metadata
    meta = Column("metadata", JSONB, nullable=False, default=dict)
    embedding = Column(Vector(384), nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    documento = relationship("DocumentoMetadata", back_populates="fragmentos")


class HistorialConsulta(Base):
    __tablename__ = "historial_consultas"
    __table_args__ = {"schema": "isft189"}

    id = Column(BigInteger, primary_key=True, index=True)
    usuario_id = Column(
        BigInteger,
        ForeignKey("isft189.usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    pregunta = Column(Text, nullable=False)
    respuesta = Column(Text, nullable=False)
    fecha_consulta = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    usuario = relationship("Usuario", back_populates="consultas")
