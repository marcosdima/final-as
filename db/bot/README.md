# TPI Base de Datos — ISFT 189: Asistente Virtual Académico (RAG)

Servicio backend de Asistente Virtual Inteligente basado en **Generación Aumentada por Recuperación (RAG)** para el Instituto Superior de Formación Técnica N° 189.

Desarrollado con **FastAPI**, **PostgreSQL 16 + pgvector** (embeddings de 384 dimensiones e índice **HNSW**) y compatibilidad nativa con proveedores LLM en la nube (**Groq** y **OpenRouter**).

---

## 1. Arquitectura del Módulo

El sistema resuelve la ingesta documental, segmentación de texto (chunking), representación semántica vectorial y generación de respuestas contextualizadas a partir de documentos oficiales institucionales (planes de estudio, correlatividades, régimen de asistencia y reglamentos).

```
[Documento PDF / Texto]
         │
         ▼
[ Ingesta y Chunking ] ──> [ Embeddings 384-d ] ──> [ PostgreSQL + pgvector ]
                                                      (isft189.documentos_vectoriales)
                                                      (Índice HNSW: vector_cosine_ops)
                                                                     │
[ Estudiante / Docente ]                                             │
         │                                                           ▼
         ▼                                                  [ Búsqueda Híbrida ]
[ Consulta /chat ] ──────> [ Embedding Consulta ] ────────> (Filtros + Operador <=>)
                                                                     │
                                                                     ▼
[ Respuesta Final ] <───── [ LLM: Groq / OpenRouter ] <──── [ Top-k Fragmentos ]
```

---

## 2. Estructura de Base de Datos (`isft189`)

El esquema `isft189` implementa las especificaciones solicitadas en la consigna de cátedra:

1. **`isft189.usuarios`**:
   - `id`, `nombre`, `email` (UNIQUE), `rol` ('ALUMNO', 'DOCENTE', 'ADMIN', etc.), `fecha_registro`.
2. **`isft189.documentos_metadata`**:
   - `id`, `titulo`, `tipo_documento` (ENUM: `plan_estudio`, `reglamento`, `correlatividades`, `resolucion`, `otro`), `fecha_subida`, `carrera` (NULL para documentos institucionales comunes), `activo`.
3. **`isft189.documentos_vectoriales`**:
   - `id`, `documento_id` (FK ON DELETE CASCADE), `contenido` (TEXT), `metadata` (JSONB con índice GIN), `embedding` (`VECTOR(384)` con índice **HNSW**).
4. **`isft189.historial_consultas`**:
   - `id`, `usuario_id` (FK ON DELETE SET NULL), `pregunta`, `respuesta`, `fecha_consulta`.

### Índice HNSW y Búsqueda de Coseno

Se utiliza el operador de distancia de coseno (`<=>`) y un índice HNSW para garantizar recuperación con complejidad $O(\log N)$ en lugar de escaneos secuenciales:

```sql
CREATE INDEX idx_vectoriales_hnsw
    ON isft189.documentos_vectoriales
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

---

## 3. Estructura del Proyecto

```
db/bot/
├── 01_ddl.sql              # Definición de esquema, pgvector, tablas, tipos e índices
├── 02_dml.sql              # Carga inicial, vectores normalizados y consultas híbridas
├── modelo.dbml             # Modelo físico en formato DBML
├── README.md               # Esta documentación
├── requirements.txt        # Dependencias Python
├── .env.example            # Plantilla de variables de entorno
└── app/
    ├── __init__.py
    ├── config.py           # Configuración con Pydantic Settings
    ├── database.py         # Motor asíncrono SQLAlchemy + asyncpg
    ├── models.py           # Modelos ORM (pgvector Vector(384), JSONB)
    ├── schemas.py          # Esquemas de validación Pydantic v2
    ├── embeddings.py       # Generador de embeddings (FastEmbed 384-d / fallback)
    ├── llm.py              # Cliente OpenAI compatible para Groq y OpenRouter
    ├── services/
    │   ├── ingestion.py    # Chunking de documentos y almacenamiento
    │   └── rag.py          # Búsqueda híbrida con <=> y armado de prompt
    ├── routes/
    │   ├── documents.py    # Endpoints de ingesta y gestión documental
    │   └── chat.py         # Endpoints de consulta RAG y auditoría
    └── main.py             # Aplicación FastAPI, lifespan y healthcheck
```

---

## 4. Puesta en Marcha

### Requisitos
- Docker (o PostgreSQL 16 con `pgvector` instalado)
- Python 3.10 o superior

### Paso 1: Levantar PostgreSQL con pgvector

```bash
docker run -d --name tpi-isft189 \
  -e POSTGRES_USER=tpi \
  -e POSTGRES_PASSWORD=tpi123 \
  -e POSTGRES_DB=isft189 \
  -p 55432:5432 \
  pgvector/pgvector:pg16
```

### Paso 2: Ejecutar DDL y DML

```bash
# Crear tablas e índices HNSW
PGPASSWORD=tpi123 psql -h localhost -p 55432 -U tpi -d isft189 -f db/bot/01_ddl.sql

# Cargar datos de prueba y ejecutar validaciones híbridas
PGPASSWORD=tpi123 psql -h localhost -p 55432 -U tpi -d isft189 -f db/bot/02_dml.sql
```

### Paso 3: Configurar el Entorno Python

```bash
cd db/bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copia la plantilla `.env.example` a `.env` y configura tu API Key de **Groq** o **OpenRouter**:

```bash
cp .env.example .env
```

Ejemplo para **Groq**:
```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_tu_clave_real_de_groq
LLM_MODEL=llama-3.3-70b-versatile
DATABASE_URL=postgresql+asyncpg://tpi:tpi123@localhost:55432/isft189
```

Ejemplo para **OpenRouter**:
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-tu_clave_de_openrouter
LLM_MODEL=meta-llama/llama-3.3-70b-instruct
DATABASE_URL=postgresql+asyncpg://tpi:tpi123@localhost:55432/isft189
```

### Paso 4: Iniciar el Servidor FastAPI

```bash
uvicorn app.main:app --reload --port 8000
```

Documentación interactiva disponible en:
- Swagger UI: `http://localhost:8000/docs`
- Redoc: `http://localhost:8000/redoc`

---

## 5. Endpoints de la API

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/health` | Chequeo de estado de PostgreSQL y extensión `pgvector` |
| `POST` | `/api/v1/documents/ingest` | Ingesta, chunking y vectorización de un documento |
| `GET` | `/api/v1/documents/` | Listado de documentos y conteo de fragmentos |
| `GET` | `/api/v1/documents/{id}` | Detalle de un documento específico |
| `DELETE` | `/api/v1/documents/{id}` | Eliminación en cascada de documento y sus vectores |
| `POST` | `/api/v1/chat/` | Consulta al asistente académico (RAG con Groq/OpenRouter) |
| `GET` | `/api/v1/chat/history` | Historial de preguntas y respuestas auditadas |

---

## 6. Ejemplos de Uso con cURL

### Ingestar un documento
```bash
curl -X POST http://localhost:8000/api/v1/documents/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Régimen de Correlatividades de Sistemas 2024",
    "tipo_documento": "correlatividades",
    "carrera": "Tecnicatura Superior en Desarrollo de Software",
    "contenido_completo": "Para cursar Arquitectura Web se debe tener aprobada Programación II. Para rendir el examen final de Base de Datos II es requisito haber aprobado el final de Base de Datos I.",
    "chunk_size": 300,
    "chunk_overlap": 30
  }'
```

### Realizar una consulta académica (RAG)
```bash
curl -X POST http://localhost:8000/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Qué correlatividad necesito para rendir Base de Datos II?",
    "filtro_carrera": "Tecnicatura Superior en Desarrollo de Software",
    "top_k": 3
  }'
```

### Ver historial de consultas auditadas
```bash
curl -X GET "http://localhost:8000/api/v1/chat/history?limit=5"
```
