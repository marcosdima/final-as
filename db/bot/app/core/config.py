import os
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # PostgreSQL database hosting both `instituto` and `isft189` schemas
    DATABASE_URL: str = "postgresql+asyncpg://tpi:tpi123@localhost:55432/isft189"

    # JWT authentication & RBAC
    JWT_SECRET_KEY: str = "isft189-dev-secret-change-in-production-32bytes"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 120

    # Allowed CORS origins (comma-separated)
    CORS_ORIGINS: str = (
        "http://localhost:3000,http://localhost:5173,http://localhost:8000,http://127.0.0.1:8000"
    )

    # LLM provider
    LLM_PROVIDER: Literal["groq", "openrouter"] = "groq"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_BASE_URL: str = ""

    # Multilingual 384-d embeddings matching VECTOR(384)
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIM: int = 384

    # RAG retrieval parameters
    TOP_K: int = 4
    MAX_COSINE_DISTANCE: float = 0.85

    def get_cors_origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    def get_llm_credentials(self) -> tuple[str, str, str]:
        """Return (base_url, api_key, model) for the configured LLM provider."""
        if self.LLM_PROVIDER == "groq":
            base_url = self.LLM_BASE_URL or "https://api.groq.com/openai/v1"
            api_key = self.GROQ_API_KEY
            model = self.LLM_MODEL or "llama-3.3-70b-versatile"
        elif self.LLM_PROVIDER == "openrouter":
            base_url = self.LLM_BASE_URL or "https://openrouter.ai/api/v1"
            api_key = self.OPENROUTER_API_KEY
            model = self.LLM_MODEL or "meta-llama/llama-3.3-70b-instruct"
        else:
            raise ValueError(f"Unsupported LLM provider: {self.LLM_PROVIDER}")

        return base_url, api_key, model


settings = Settings()
