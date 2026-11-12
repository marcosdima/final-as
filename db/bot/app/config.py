import os
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Base de Datos
    DATABASE_URL: str = "postgresql+asyncpg://tpi:tpi123@localhost:55432/isft189"

    # Proveedor LLM
    LLM_PROVIDER: Literal["groq", "openrouter"] = "groq"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_BASE_URL: str = ""

    # Embeddings
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBEDDING_DIM: int = 384

    # RAG
    TOP_K: int = 4
    MAX_COSINE_DISTANCE: float = 0.85

    def get_llm_credentials(self) -> tuple[str, str, str]:
        """
        Retorna (base_url, api_key, model) según el proveedor configurado.
        """
        if self.LLM_PROVIDER == "groq":
            base_url = self.LLM_BASE_URL or "https://api.groq.com/openai/v1"
            api_key = self.GROQ_API_KEY
            model = self.LLM_MODEL or "llama-3.3-70b-versatile"
        elif self.LLM_PROVIDER == "openrouter":
            base_url = self.LLM_BASE_URL or "https://openrouter.ai/api/v1"
            api_key = self.OPENROUTER_API_KEY
            model = self.LLM_MODEL or "meta-llama/llama-3.3-70b-instruct"
        else:
            raise ValueError(f"Proveedor no soportado: {self.LLM_PROVIDER}")

        return base_url, api_key, model


settings = Settings()
