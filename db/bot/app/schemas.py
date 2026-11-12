from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


# Tipos de documento permitidos según el esquema institucional
TipoDocumento = Literal[
    "plan_estudio",
    "reglamento",
    "correlatividades",
    "resolucion",
    "otro"
]


# Esquemas para Documentos
class DocumentoIngestRequest(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=200, description="Título del documento oficial")
    tipo_documento: TipoDocumento = Field(..., description="Tipo de documento institucional")
    carrera: Optional[str] = Field(None, description="Carrera a la que aplica o NULL si es general")
    contenido_completo: Optional[str] = Field(None, description="Texto completo para fragmentar automáticamente")
    fragmentos: Optional[List[str]] = Field(None, description="Lista opcional de fragmentos ya pre-divididos")
    metadata_adicional: Optional[Dict[str, Any]] = Field(default_factory=dict)
    chunk_size: int = Field(500, ge=100, le=2000, description="Tamaño objetivo de cada fragmento")
    chunk_overlap: int = Field(50, ge=0, le=200, description="Solapamiento entre fragmentos")


class FragmentoResponse(BaseModel):
    id: int
    documento_id: int
    contenido: str
    metadata: Dict[str, Any]
    distancia_coseno: Optional[float] = None

    class Config:
        from_attributes = True


class DocumentoMetadataResponse(BaseModel):
    id: int
    titulo: str
    tipo_documento: str
    fecha_subida: datetime
    carrera: Optional[str]
    activo: bool
    total_fragmentos: int = 0

    class Config:
        from_attributes = True


class DocumentoIngestResponse(BaseModel):
    documento_id: int
    titulo: str
    tipo_documento: str
    carrera: Optional[str]
    fragmentos_creados: int
    mensaje: str


# Esquemas para Consultas RAG
class ChatQueryRequest(BaseModel):
    pregunta: str = Field(..., min_length=3, description="Pregunta del usuario")
    usuario_id: Optional[int] = Field(None, description="ID del usuario (opcional para auditoría)")
    filtro_carrera: Optional[str] = Field(None, description="Filtrar contexto por carrera específica")
    filtro_tipo_documento: Optional[TipoDocumento] = Field(None, description="Filtrar por tipo de documento")
    top_k: Optional[int] = Field(None, ge=1, le=10, description="Cantidad de fragmentos a recuperar")
    temperatura: float = Field(0.2, ge=0.0, le=1.0, description="Creatividad del modelo LLM")


class ChatQueryResponse(BaseModel):
    pregunta: str
    respuesta: str
    proveedor_llm: str
    modelo: str
    fragmentos_recuperados: List[FragmentoResponse]
    fecha_consulta: datetime
