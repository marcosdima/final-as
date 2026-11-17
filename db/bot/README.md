# TPI Base de Datos & Análisis de Sistemas — ISFT 189: Sistema Integrado y Asistente Virtual (RAG)

Servicio backend unificado para el **Sistema Integral de Gestión Académica** (esquema `instituto`) y el **Asistente Virtual Inteligente basado en RAG + Tool Calling** (esquema `isft189`) del Instituto Superior de Formación Técnica N° 189.

Desarrollado con **FastAPI**, **PostgreSQL 16 + pgvector** (embeddings multilingües de 384 dimensiones e índice **HNSW**), **JWT + RBAC** (`ControladorAcceso`) y compatibilidad nativa con proveedores LLM en la nube (**Groq** y **OpenRouter**).

---

## 1. Arquitectura Unificada

Los entregables SQL de ambas materias se mantienen **separados académicamente** (`db/instituto/` y `db/bot/`), pero conviven en la misma base PostgreSQL y son consumidos de forma integrada por la API:

```
                   ┌──────────────────────────────────────────┐
                   │   Cliente Web / Swagger / App Móvil      │
                   └────────────────────┬─────────────────────┘
                                        │ Bearer JWT (RBAC)
                                        ▼
                   ┌──────────────────────────────────────────┐
                   │      FastAPI Backend (db/bot/app/)       │
                   │  • Auth & RBAC (ControladorAcceso)       │
                   │  • Orquestador RAG + Tool Calling        │
                   └──────┬───────────────────────────┬───────┘
                          │                           │
       ┌──────────────────▼──────────┐     ┌──────────▼──────────────────────┐
       │   Esquema: isft189 (RAG)    │     │ Esquema: instituto (Académico)  │
       │  • documentos_metadata      │     │  • usuario, alumno, docente     │
       │  • documentos_vectoriales   │     │  • carrera, plan_estudio        │
       │    (VECTOR(384), HNSW, GIN) │     │  • materia, correlatividad      │
       │  • historial_consultas      │     │  • cursadas, asistencias, actas │
       └─────────────────────────────┘     └─────────────────────────────────┘
```

---

## 2. Estructura del Proyecto

```
db/
├── instituto/                # Esquema relacional académico global (19 tablas)
│   ├── 01_ddl.sql
│   └── 02_dml.sql            # Planes oficiales (Res. 6175/03 y Desarrollo de Software 2019)
└── bot/
    ├── 01_ddl.sql            # Esquema isft189, pgvector, tablas e índices HNSW/GIN
    ├── 02_dml.sql            # Datos iniciales y embeddings multilingües (384-d)
    ├── er.drawio             # Diagrama Entidad-Relación conceptual
    ├── modelo.dbml           # Modelo físico en formato DBML
    ├── requirements.txt      # Dependencias Python
    ├── .env.example          # Plantilla de variables de entorno
    ├── tests/
    │   └── test_app.py       # Pruebas unitarias e integración (JWT, RBAC, PDF, RAG)
    └── app/
        ├── .venv/            # Entorno virtual Python
        ├── config.py         # Configuración (DB, JWT, CORS, LLM, Embeddings)
        ├── database.py       # Motor asíncrono SQLAlchemy + asyncpg
        ├── models.py         # Modelos ORM esquema isft189
        ├── institute_models.py # Modelos ORM esquema instituto
        ├── security.py       # Bcrypt, JWT y ControladorAcceso (RBAC)
        ├── schemas.py        # Esquemas Pydantic v2 con validaciones
        ├── embeddings.py     # FastEmbed multilingüe 384-d + wrappers async
        ├── llm.py            # Cliente Groq / OpenRouter con Tool Calling
        ├── services/
        │   ├── academic.py   # Consultas parametrizadas RBAC sobre instituto
        │   ├── ingestion.py  # Chunking seguro, extracción PDF y vectorización
        │   └── rag.py        # Búsqueda híbrida HNSW + herramientas académicas
        ├── routes/
        │   ├── auth.py       # /api/v1/auth/login, /token y /me
        │   ├── academic.py   # /api/v1/academic/*
        │   ├── documents.py  # /api/v1/documents/* (JSON y PDF)
        │   └── chat.py       # /api/v1/chat/ y /history (aislado por rol)
        └── main.py           # Aplicación FastAPI, lifespan y /health
```

---

## 3. Puesta en Marcha

### Paso 1: Levantar PostgreSQL con pgvector

```bash
docker run -d --name tpi-isft189 \
  -e POSTGRES_USER=tpi \
  -e POSTGRES_PASSWORD=tpi123 \
  -e POSTGRES_DB=isft189 \
  -p 55432:5432 \
  pgvector/pgvector:pg16
```

### Paso 2: Cargar ambos esquemas (`instituto` + `isft189`)

> **Importante:** `isft189.documentos_metadata.carrera_id` tiene una clave foránea hacia `instituto.carrera(id)`, por lo que se debe ejecutar `db/instituto/01_ddl.sql` y `02_dml.sql` **antes** que los scripts de `db/bot/`.

```bash
# 1. Esquema académico del instituto
PGPASSWORD=tpi123 psql -h localhost -p 55432 -U tpi -d isft189 -v ON_ERROR_STOP=1 -f db/instituto/01_ddl.sql
PGPASSWORD=tpi123 psql -h localhost -p 55432 -U tpi -d isft189 -v ON_ERROR_STOP=1 -f db/instituto/02_dml.sql

# 2. Esquema vectorial del bot RAG
PGPASSWORD=tpi123 psql -h localhost -p 55432 -U tpi -d isft189 -v ON_ERROR_STOP=1 -f db/bot/01_ddl.sql
PGPASSWORD=tpi123 psql -h localhost -p 55432 -U tpi -d isft189 -v ON_ERROR_STOP=1 -f db/bot/02_dml.sql
```

### Paso 3: Entorno Python y Variables de Entorno

```bash
cd db/bot
python3 -m venv app/.venv
source app/.venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Configurar en `.env` tu clave de **Groq** o **OpenRouter** y un `JWT_SECRET_KEY` seguro.

### Paso 4: Iniciar Servidor y Ejecutar Tests

```bash
# Desde db/bot (o desde db/bot/app usando uvicorn main:app)
app/.venv/bin/uvicorn app.main:app --reload --port 8000

# Ejecutar suite de pruebas
app/.venv/bin/pytest -v tests/test_app.py
```

Documentación interactiva (Swagger UI con botón **Authorize** integrado): `http://localhost:8000/docs`

---

## 4. Credenciales de Prueba (`db/instituto/02_dml.sql`)

Contraseña para todos los usuarios de prueba: **`isft189.2026`**

| Rol | Email | Perfil / Legajo |
|---|---|---|
| `ADMIN` | `admin@isft189.edu.ar` | Nora Gómez |
| `PRECEPTOR` | `rpaz@isft189.edu.ar` | Roberto Paz |
| `TEACHER` | `lluengo@isft189.edu.ar` | Leonel Luengo (Legajo 201) |
| `TEACHER` | `jcromero@isft189.edu.ar` | Juan Carlos Romero (Legajo 202) |
| `STUDENT` | `mdimatteo@alumno.isft189.edu.ar` | Marcos Di Matteo (Legajo 1001 - Análisis y Desarrollo) |
| `STUDENT` | `nquinonez@alumno.isft189.edu.ar` | Nahuel Quiñonez (Legajo 1002 - Análisis y Desarrollo) |
| `STUDENT` | `salvarez@alumno.isft189.edu.ar` | Sofía Álvarez (Legajo 1004 - Desarrollo de Software) |

---

## 5. Endpoints Principales (`/api/v1`)

| Método | Endpoint | Acceso RBAC | Descripción |
|---|---|---|---|
| `GET` | `/health` | Público | Estado de PostgreSQL, `pgvector` y esquemas `instituto`/`isft189` |
| `POST` | `/api/v1/auth/login` | Público | Autenticación bcrypt (JSON) y emisión de JWT |
| `POST` | `/api/v1/auth/token` | Público | Login OAuth2 para botón **Authorize** en Swagger `/docs` |
| `GET` | `/api/v1/auth/me` | Autenticado | Perfil y legajo del usuario del token |
| `GET` | `/api/v1/academic/careers` | Autenticado | Carreras vigentes con sus materias anidadas (`subjects`) |
| `GET` | `/api/v1/academic/notices` | Autenticado | Avisos filtrados por rol |
| `GET` | `/api/v1/academic/enrollment-periods` | Autenticado | Ventanas de inscripción (`COURSE` o `EXAM`) |
| `GET` | `/api/v1/academic/exam-boards` | Autenticado | Mesas de examen y períodos exclusivamente de tipo `EXAM` |
| `GET` | `/api/v1/academic/students/me/history` | `STUDENT` | Historia académica y promedio propio |
| `GET` | `/api/v1/academic/students/me/attendance` | `STUDENT` | Porcentaje de asistencia por materia |
| `GET` | `/api/v1/academic/students/me/prerequisites` | `STUDENT` | Validación de correlativas `TO_ENROLL` y `TO_TAKE_EXAM` |
| `GET` | `/api/v1/academic/teachers/me/rosters` | `TEACHER` | Cátedras asignadas y nómina de alumnos |
| `GET` | `/api/v1/academic/teachers/me/exam-boards` | `TEACHER` | Mesas donde integra tribunal |
| `GET` | `/api/v1/academic/admin/students` | `PRECEPTOR`, `ADMIN` | Consulta de legajo por `file_number` o `dni` |
| `POST` | `/api/v1/documents/ingest` | `PRECEPTOR`, `ADMIN` | Ingesta de texto, chunking y vectorización |
| `POST` | `/api/v1/documents/ingest-pdf` | `PRECEPTOR`, `ADMIN` | Subida e indexación directa de PDFs |
| `GET` | `/api/v1/documents/` | Autenticado | Listado de documentos y conteo de chunks |
| `DELETE` | `/api/v1/documents/{document_id}` | `PRECEPTOR`, `ADMIN` | Eliminación en cascada |
| `POST` | `/api/v1/chat/` | Autenticado | Asistente híbrido (RAG vectorial + tools sobre `instituto`) |
| `GET` | `/api/v1/chat/history` | Autenticado (aislado) | Historial propio (`STUDENT`/`TEACHER`) o auditoría (`PRECEPTOR`/`ADMIN`) |
