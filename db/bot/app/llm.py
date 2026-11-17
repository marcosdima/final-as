import json
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

# Note: ISFT 189 end users interact in Spanish, so the assistant replies in Spanish.
SYSTEM_PROMPT_ISFT189 = """Sos el asistente virtual académico del Instituto Superior de Formación Técnica N° 189 (ISFT 189).
Tu propósito es responder consultas de estudiantes, docentes, preceptores y administradores sobre planes de estudio, correlatividades, reglamentos institucionales, historia académica, asistencias, mesas de examen y avisos oficiales.

Instrucciones estrictas:
1. Respondé fundamentándote EXCLUSIVAMENTE en el contexto documental recuperado y en los datos obtenidos mediante las herramientas académicas de la base de datos.
2. Si el usuario consulta sobre sus notas, asistencias, correlatividades personales, nóminas o mesas, utilizá la herramienta académica correspondiente antes de responder.
3. Respetá estrictamente el alcance del rol del usuario autenticado.
4. Si la respuesta no surge de los documentos ni de los datos recuperados, aclará explícitamente que no disponés de esa información en los registros actuales y recomendá consultar en Secretaría del Instituto.
5. Mencioná el documento o fuente de referencia (título de resolución, reglamento, plan de carrera o registro académico) cuando corresponda.
6. Sé claro, conciso, formal y empático.
"""

ToolExecutor = Callable[[str, Dict[str, Any]], Awaitable[str]]


class LLMService:
    def __init__(self) -> None:
        self._client: Optional[AsyncOpenAI] = None

    def has_valid_api_key(self) -> bool:
        _, api_key, _ = settings.get_llm_credentials()
        if not api_key:
            return False
        if api_key.startswith("gsk_tu_clave") or api_key.startswith("sk-or-v1-tu_clave"):
            return False
        return True

    def _get_client(self) -> Optional[AsyncOpenAI]:
        if not self.has_valid_api_key():
            return None
        base_url, api_key, _ = settings.get_llm_credentials()
        if self._client is None:
            self._client = AsyncOpenAI(
                base_url=base_url,
                api_key=api_key,
                timeout=30.0,
            )
        return self._client

    async def generate_with_tools(
        self,
        query: str,
        user_context: str,
        context_fragments: List[str],
        tools: List[Dict[str, Any]],
        tool_executor: ToolExecutor,
        temperature: float = 0.2,
        max_rounds: int = 3,
    ) -> Optional[str]:
        """
        Execute RAG generation with OpenAI-compatible Tool Calling (Groq / OpenRouter).
        Returns None when no API key is configured so local fallback can run.
        """
        client = self._get_client()
        if not client:
            return None

        _, _, model_name = settings.get_llm_credentials()

        if context_fragments:
            context_block = "\n\n--- INSTITUTIONAL FRAGMENT ---\n".join(context_fragments)
        else:
            context_block = "(No relevant document fragments found in initial vector search)"

        user_prompt = (
            f"AUTHENTICATED USER:\n{user_context}\n\n"
            f"RETRIEVED DOCUMENT CONTEXT:\n{context_block}\n\n"
            f"USER QUESTION:\n{query}"
        )

        messages: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT_ISFT189},
            {"role": "user", "content": user_prompt},
        ]

        try:
            for _ in range(max_rounds):
                kwargs: Dict[str, Any] = {
                    "model": model_name,
                    "temperature": temperature,
                    "messages": messages,
                }
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = "auto"

                response = await client.chat.completions.create(**kwargs)
                msg = response.choices[0].message

                if not msg.tool_calls:
                    return (msg.content or "").strip() or (
                        "No pude generar una respuesta a partir de los datos recuperados."
                    )

                messages.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments or "{}",
                            },
                        }
                        for tc in msg.tool_calls
                    ],
                })

                for tc in msg.tool_calls:
                    try:
                        args = json.loads(tc.function.arguments or "{}")
                        if not isinstance(args, dict):
                            args = {}
                    except json.JSONDecodeError:
                        args = {}

                    tool_output = await tool_executor(tc.function.name, args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": tool_output,
                    })

            final_resp = await client.chat.completions.create(
                model=model_name,
                temperature=temperature,
                messages=messages,
            )
            return (final_resp.choices[0].message.content or "").strip() or (
                "No pude generar una respuesta a partir de los datos recuperados."
            )

        except Exception as exc:
            logger.error("Error calling %s (%s): %s", settings.LLM_PROVIDER, model_name, exc)
            return (
                "Ocurrió un error temporal al consultar el servicio de lenguaje. "
                "Por favor intente nuevamente más tarde o consulte en Secretaría del Instituto."
            )


llm_service = LLMService()
