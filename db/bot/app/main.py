import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import engine
from app.routes.academic import router as academic_router
from app.routes.auth import router as auth_router
from app.routes.chat import router as chat_router
from app.routes.documents import router as documents_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("isft189.rag")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.JWT_SECRET_KEY == "isft189-dev-secret-change-in-production-32bytes":
        logger.warning("Using default development JWT_SECRET_KEY. Set a strong secret in .env for production.")
    try:
        async with engine.connect() as conn:
            ext_res = await conn.execute(
                text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            )
            row = ext_res.first()
            if row:
                logger.info("Connected to PostgreSQL. pgvector version: %s", row[0])
            else:
                logger.warning("Connected to PostgreSQL, but 'vector' extension is not installed.")

            sch_res = await conn.execute(
                text(
                    "SELECT schema_name FROM information_schema.schemata "
                    "WHERE schema_name IN ('instituto', 'isft189')"
                )
            )
            schemas = sorted(r[0] for r in sch_res.all())
            logger.info("Available PostgreSQL schemas: %s", schemas)
    except Exception as exc:
        logger.error("Failed to connect to PostgreSQL on startup: %s", exc)

    yield

    await engine.dispose()
    logger.info("Database engine disposed.")


app = FastAPI(
    title="ISFT 189 - Unified Academic & Virtual Assistant API",
    description=(
        "Unified backend integrating the Academic Management System (`instituto` schema) "
        "and the RAG Virtual Assistant (`isft189` schema on PostgreSQL 16 + pgvector HNSW), "
        "protected with JWT authentication and role-based access control (RBAC).\n\n"
        "### Quick Swagger Usage\n"
        "1. Click **Authorize** (top-right).\n"
        "2. Enter an institutional email as `username` (e.g. `mdimatteo@alumno.isft189.edu.ar`) "
        "and `isft189.2026` as `password`.\n"
        "3. Test any endpoint directly using **Try it out**."
    ),
    version="2.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
        "docExpansion": "list",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(academic_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")


@app.get("/", tags=["Status"])
async def root():
    _, _, model_name = settings.get_llm_credentials()
    return {
        "system": "ISFT 189 - Unified Academic & Virtual Assistant API",
        "version": "2.0.0",
        "docs": "/docs",
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": model_name,
        "embedding_model": settings.EMBEDDING_MODEL,
        "embedding_dim": settings.EMBEDDING_DIM,
        "auth": "JWT Bearer (RBAC)",
    }


@app.get("/health", tags=["Status"])
async def health_check():
    db_status = "ok"
    pgvector_status = "unknown"
    schemas_status: list[str] = []
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
            )
            row = result.first()
            pgvector_status = f"active (v{row[0]})" if row else "not installed"

            sch_res = await conn.execute(
                text(
                    "SELECT schema_name FROM information_schema.schemata "
                    "WHERE schema_name IN ('instituto', 'isft189')"
                )
            )
            schemas_status = sorted(r[0] for r in sch_res.all())
    except Exception as exc:
        db_status = f"error: {str(exc)}"

    healthy = db_status == "ok" and "instituto" in schemas_status and "isft189" in schemas_status
    return {
        "status": "healthy" if healthy else "degraded",
        "database": db_status,
        "pgvector": pgvector_status,
        "schemas": schemas_status,
    }
