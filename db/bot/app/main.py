import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.routes.chat import router as chat_router
from app.routes.documents import router as documents_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("isft189.rag")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verificación de conexión a PostgreSQL y extensión vector
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT extversion FROM pg_extension WHERE extname = 'vector'"))
            row = result.first()
            if row:
                logger.info("Conexión exitosa a PostgreSQL. pgvector versión: %s", row[0])
            else:
                logger.warning("Conectado a PostgreSQL pero la extensión 'vector' no figura instalada.")
    except Exception as e:
        logger.error("No se pudo conectar a PostgreSQL al iniciar: %s", e)

    yield

    # Cleanup al apagar
    await engine.dispose()
    logger.info("Motor de base de datos liberado.")


app = FastAPI(
    title="ISFT 189 - Asistente Virtual Inteligente (API RAG)",
    description=(
        "Servicio backend RAG para consultas académicas institucionales. "
        "Desarrollado con FastAPI, PostgreSQL 16 + pgvector (384 dimensiones, índice HNSW) "
        "e integración con proveedores LLM en la nube (Groq y OpenRouter)."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers bajo el prefijo /api/v1
app.include_router(documents_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")


@app.get("/", tags=["Estado"])
async def root():
    base_url, _, model_name = settings.get_llm_credentials()
    return {
        "sistema": "ISFT 189 - Asistente Virtual Inteligente",
        "version": "1.0.0",
        "docs": "/docs",
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": model_name,
        "embedding_model": settings.EMBEDDING_MODEL,
        "embedding_dim": settings.EMBEDDING_DIM
    }


@app.get("/health", tags=["Estado"])
async def health_check():
    db_status = "ok"
    pgvector_status = "desconocido"
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT extversion FROM pg_extension WHERE extname = 'vector'"))
            row = result.first()
            if row:
                pgvector_status = f"activo (v{row[0]})"
            else:
                pgvector_status = "no instalado"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "database": db_status,
        "pgvector": pgvector_status
    }
