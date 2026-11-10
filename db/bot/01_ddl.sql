-- ISFT 189 — TPI Base de Datos · Archivo 01: DDL
-- Requiere PostgreSQL 16+. Ejecutar: psql -U <usuario> -d <base> -f 01_ddl.sql
-- La extensión vector y la tabla documentos_vectoriales quedan para la próxima iteración (ver README.md).

DROP SCHEMA IF EXISTS isft189 CASCADE;

CREATE SCHEMA IF NOT EXISTS isft189;

SET search_path TO isft189, public;

-- Dominios cerrados
CREATE TYPE isft189.rol_usuario AS ENUM (
    'admin',
    'docente',
    'preceptor',
    'alumno'
);

CREATE TYPE isft189.tipo_documento AS ENUM (
    'plan_estudio',
    'reglamento',
    'correlatividades',
    'resolucion',
    'otro'
);

-- Tabla: carreras (RF-005). La carrera deja de ser un varchar libre:
-- ahora es una entidad propia a la que los documentos referencian
CREATE TABLE isft189.carreras (
    id              BIGSERIAL        PRIMARY KEY,
    nombre          VARCHAR(100)     NOT NULL,
    titulo_otorgado VARCHAR(200)     NOT NULL,
    activo          BOOLEAN          NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_carreras_nombre UNIQUE (nombre),
    CONSTRAINT ck_carreras_nombre_no_vacio
        CHECK (length(btrim(nombre)) > 0),
    CONSTRAINT ck_carreras_titulo_no_vacio
        CHECK (length(btrim(titulo_otorgado)) > 0)
);

-- Tabla: usuarios
CREATE TABLE isft189.usuarios (
    id         BIGSERIAL        PRIMARY KEY,
    nombre     VARCHAR(100)     NOT NULL,
    email      VARCHAR(150)     NOT NULL,
    rol        isft189.rol_usuario NOT NULL DEFAULT 'alumno',
    fecha_alta TIMESTAMPTZ      NOT NULL DEFAULT now(),
    activo     BOOLEAN          NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_usuarios_email UNIQUE (email),
    CONSTRAINT ck_usuarios_email_formato
        CHECK (email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$')
);

CREATE INDEX idx_usuarios_rol
    ON isft189.usuarios (rol);

-- Tabla: documentos_metadata (carrera_id NULL = documento institucional)
CREATE TABLE isft189.documentos_metadata (
    id             BIGSERIAL        PRIMARY KEY,
    titulo         VARCHAR(200)     NOT NULL,
    tipo_documento isft189.tipo_documento NOT NULL,
    fecha_subida   TIMESTAMPTZ      NOT NULL DEFAULT now(),
    carrera_id     BIGINT,
    activo         BOOLEAN          NOT NULL DEFAULT TRUE,

    CONSTRAINT ck_documentos_titulo_no_vacio
        CHECK (length(btrim(titulo)) > 0),
    CONSTRAINT fk_documentos_carrera
        FOREIGN KEY (carrera_id)
        REFERENCES isft189.carreras (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

CREATE INDEX idx_documentos_tipo
    ON isft189.documentos_metadata (tipo_documento);

CREATE INDEX idx_documentos_carrera
    ON isft189.documentos_metadata (carrera_id);

-- Tabla: historial_consultas (auditoría: no se borran usuarios con consultas)
CREATE TABLE isft189.historial_consultas (
    id             BIGSERIAL    PRIMARY KEY,
    usuario_id     BIGINT       NOT NULL,
    pregunta       TEXT         NOT NULL,
    respuesta      TEXT         NOT NULL,
    fecha_consulta TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT fk_historial_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES isft189.usuarios (id)
        ON DELETE RESTRICT
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
  'Informacion de acceso e identificacion de los usuarios';
COMMENT ON TABLE isft189.documentos_metadata IS
  'Documentos oficiales del instituto (planes, reglamentos, correlatividades)';
COMMENT ON TABLE isft189.historial_consultas IS
  'Auditoria de interacciones con la IA';
COMMENT ON COLUMN isft189.historial_consultas.usuario_id IS
  'FK -> usuarios.id, ON DELETE RESTRICT';
COMMENT ON TABLE isft189.carreras IS
  'Carreras de la institucion (RF-005: registra, RF-007 la referencia el plan)';
COMMENT ON COLUMN isft189.documentos_metadata.carrera_id IS
  'FK -> carreras.id, ON DELETE RESTRICT. NULL si el documento es institucional';
