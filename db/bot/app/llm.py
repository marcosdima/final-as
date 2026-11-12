import logging
from typing import List, Optional
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_ISFT189 = """Sos el asistente virtual académico del Instituto Superior de Formación Técnica N° 189 (ISFT 189).
Tu propósito es responder consultas de estudiantes, docentes y postulantes sobre planes de estudio, correlatividades, reglamentos institucionales, régimen de asistencia y resoluciones oficiales.

Instrucciones:
1. Respondé fundamentándote EXCLUSIVAMENTE en el contexto proporcionado más abajo.
2. Sé claro, conciso, empático y formalmente correcto.
3. Si la respuesta no surge del contexto recuperado, aclará explícitamente que no disponés de esa información en los documentos institucionales oficiales cargados actualmente y recomendá consultar en Secretaría del Instituto.
4. Mencioná el documento de referencia (resolución, reglamento o plan de carrera) cuando corresponda.
"""


class LLMService:
    def __init__(self):
        self.base_url, self.api_key, self.model = settings.get_llm_credentials()
        self._client: Optional[AsyncOpenAI] = None

    def _get_client(self) -> Optional[AsyncOpenAI]:
        if not self.api_key or self.api_key.startswith("gsk_tu_clave") or self.api_key.startswith("sk-or-v1-tu_clave"):
            return None
        if self._client is None:
            self._client = AsyncOpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=30.0
            )
        return self._client

    async def generate_response(
        self,
        query: str,
        context_fragments: List[str],
        temperature: float = 0.2
    ) -> str:
        """
        Genera una respuesta contextualizada usando Groq u OpenRouter.
        """
        client = self._get_client()

        # Construir contexto unificado para el prompt
        if context_fragments:
            context_block = "\n\n--- FRAGMENTO INSTITUCIONAL ---\n".join(context_fragments)
            augmented_prompt = (
                f"CONTEXTO DOCUMENTAL INSTITUCIONAL:\n{context_block}\n\n"
                f"PREGUNTA DEL USUARIO:\n{query}"
            )
        else:
            augmented_prompt = (
                "CONTEXTO DOCUMENTAL INSTITUCIONAL: (No se hallaron fragmentos relevantes en la base vectorial)\n\n"
                f"PREGUNTA DEL USUARIO:\n{query}"
            )

        if not client:
            # Fallback informativo cuando no se ha configurado API Key externa
            logger.warning("No hay LLM API key configurada (%s). Devolviendo respuesta basada en contexto directo.", settings.LLM_PROVIDER)
            if not context_fragments:
                return (
                    "No se hallaron documentos relacionados con su consulta en la base vectorial del ISFT 189. "
                    "(Nota: Configure GROQ_API_KEY u OPENROUTER_API_KEY en .env para respuestas generativas)."
                )
            return (
                f"Información institucional recuperada del ISFT 189:\n\n{context_fragments[0]}\n\n"
                f"(Respuesta sintetizada automáticamente sin LLM activo. Para habilitar Groq u OpenRouter, defina la clave en .env)."
            )

        try:
            response = await client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_ISFT189},
                    {"role": "user", "content": augmented_prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error("Error al invocar API de %s (%s): %s", settings.LLM_PROVIDER, self.model, e)
            return (
                f"Ocurrió un error al consultar el servicio de lenguaje {settings.LLM_PROVIDER}: {e}. "
                "Por favor verifique la conectividad y su clave de API."
            )


llm_service = LLMService()
