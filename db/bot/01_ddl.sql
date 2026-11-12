-- ISFT 189 — TPI Base de Datos · Archivo 01: DDL
-- Requiere PostgreSQL 16+ con extensión pgvector.
-- Módulo: Asistente Virtual Inteligente (RAG)
-- Ejecutar: psql -U <usuario> -d <base> -f 01_ddl.sql

-- Habilitar extensión pgvector para almacenamiento y búsqueda de embeddings
CREATE EXTENSION IF NOT EXISTS vector;

DROP SCHEMA IF EXISTS isft189 CASCADE;

CREATE SCHEMA IF NOT EXISTS isft189;

SET search_path TO isft189, public;

-- Dominios de tipos de documento
CREATE TYPE isft189.tipo_documento AS ENUM (
    'plan_estudio',
    'reglamento',
    'correlatividades',
    'resolucion',
    'otro'
);

-- Tabla 1: usuarios (acceso e identificación)
CREATE TABLE isft189.usuarios (
    id             BIGSERIAL        PRIMARY KEY,
    nombre         VARCHAR(100)     NOT NULL,
    email          VARCHAR(100)     NOT NULL UNIQUE,
    rol            VARCHAR(20)      NOT NULL DEFAULT 'ALUMNO',
    fecha_registro TIMESTAMPTZ      NOT NULL DEFAULT now(),

    CONSTRAINT ck_usuarios_nombre_no_vacio
        CHECK (length(btrim(nombre)) > 0),
    CONSTRAINT ck_usuarios_email_valido
        CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_usuarios_email
    ON isft189.usuarios (email);

-- Tabla 2: documentos_metadata (registro estructurado de documentos institucionales)
CREATE TABLE isft189.documentos_metadata (
    id             BIGSERIAL        PRIMARY KEY,
    titulo         VARCHAR(200)     NOT NULL,
    tipo_documento isft189.tipo_documento NOT NULL,
    fecha_subida   TIMESTAMPTZ      NOT NULL DEFAULT now(),
    carrera        VARCHAR(100),
    activo         BOOLEAN          NOT NULL DEFAULT TRUE,

    CONSTRAINT ck_documentos_titulo_no_vacio
        CHECK (length(btrim(titulo)) > 0),
    CONSTRAINT ck_documentos_carrera_no_vacia
        CHECK (carrera IS NULL OR length(btrim(carrera)) > 0)
);

CREATE INDEX idx_documentos_tipo
    ON isft189.documentos_metadata (tipo_documento);

CREATE INDEX idx_documentos_carrera
    ON isft189.documentos_metadata (carrera);

-- Tabla 3: documentos_vectoriales (fragmentos de texto y embeddings vectoriales)
CREATE TABLE isft189.documentos_vectoriales (
    id             BIGSERIAL        PRIMARY KEY,
    documento_id   BIGINT           NOT NULL,
    contenido      TEXT             NOT NULL,
    metadata       JSONB            NOT NULL DEFAULT '{}'::jsonb,
    embedding      VECTOR(384)      NOT NULL,
    fecha_creacion TIMESTAMPTZ      NOT NULL DEFAULT now(),

    CONSTRAINT fk_vectoriales_documento
        FOREIGN KEY (documento_id)
        REFERENCES isft189.documentos_metadata (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT ck_vectoriales_contenido_no_vacio
        CHECK (length(btrim(contenido)) > 0)
);

-- Índice HNSW optimizado para búsquedas por similitud de coseno (<=>)
CREATE INDEX idx_vectoriales_hnsw
    ON isft189.documentos_vectoriales
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Índice GIN para acelerar filtros relacionales sobre metadatos JSONB
CREATE INDEX idx_vectoriales_metadata_gin
    ON isft189.documentos_vectoriales
    USING gin (metadata);

CREATE INDEX idx_vectoriales_documento_id
    ON isft189.documentos_vectoriales (documento_id);

-- Tabla 4: historial_consultas (auditoría e historial de interacciones con el bot)
CREATE TABLE isft189.historial_consultas (
    id             BIGSERIAL    PRIMARY KEY,
    usuario_id     BIGINT       NULL,
    pregunta       TEXT         NOT NULL,
    respuesta      TEXT         NOT NULL,
    fecha_consulta TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT fk_historial_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES isft189.usuarios (id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,

    CONSTRAINT ck_historial_pregunta_no_vacia
        CHECK (length(btrim(pregunta)) > 0),
    CONSTRAINT ck_historial_respuesta_no_vacia
        CHECK (length(btrim(respuesta)) > 0)
);

CREATE INDEX idx_historial_usuario
    ON isft189.historial_consultas (usuario_id);

CREATE INDEX idx_historial_fecha_consulta
    ON isft189.historial_consultas (fecha_consulta DESC);

COMMENT ON SCHEMA isft189 IS
  'TPI Base de Datos ISFT 189 - Asistente Virtual Inteligente (RAG)';
COMMENT ON TABLE isft189.usuarios IS
  'Usuarios del sistema de consultas y administración';
COMMENT ON TABLE isft189.documentos_metadata IS
  'Documentos oficiales del instituto indexados para RAG (planes, reglamentos, correlatividades)';
COMMENT ON TABLE isft189.documentos_vectoriales IS
  'Fragmentos chunked con representacion semantica vectorial y metadatos JSONB';
COMMENT ON TABLE isft189.historial_consultas IS
  'Auditoria e historial de preguntas y respuestas generadas por el asistente RAG';
COMMENT ON INDEX isft189.idx_vectoriales_hnsw IS
  'Indice HNSW con distancia de coseno para recuperacion top-k eficiente';
