-- ============================================================================
-- ISFT 189 — Sistema Integral de Gestión Académica Global
-- Archivo 01: DDL (Definición de Datos)
-- Motor: PostgreSQL 16+
-- Esquema: instituto
-- Convención: Todas las tablas en SINGULAR
-- Nota: La auditoría del Asistente Virtual reside en db/bot y referencia a instituto.usuario
-- ============================================================================

DROP SCHEMA IF EXISTS instituto CASCADE;
CREATE SCHEMA instituto;
SET search_path TO instituto, public;

-- ============================================================================
-- 1. TIPOS ENUMERADOS (Dominios cerrados del sistema)
-- ============================================================================

CREATE TYPE instituto.rol_usuario AS ENUM (
    'ALUMNO',
    'DOCENTE',
    'PRECEPTOR',
    'ADMINISTRADOR'
);

CREATE TYPE instituto.tipo_correlatividad AS ENUM (
    'PARA_CURSAR',
    'PARA_RENDIR'
);

CREATE TYPE instituto.estado_ciclo AS ENUM (
    'ABIERTO',
    'CERRADO'
);

CREATE TYPE instituto.tipo_periodo AS ENUM (
    'CURSADA',
    'EXAMEN'
);

CREATE TYPE instituto.estado_alumno AS ENUM (
    'ACTIVO',
    'BAJA'
);

CREATE TYPE instituto.estado_inscripcion_carrera AS ENUM (
    'ACTIVA',
    'BAJA'
);

CREATE TYPE instituto.cargo_docente AS ENUM (
    'TITULAR',
    'OBSERVADOR'
);

CREATE TYPE instituto.condicion_cursada AS ENUM (
    'CURSANDO',
    'REGULAR',
    'PROMOCIONADO',
    'LIBRE'
);

CREATE TYPE instituto.instancia_evaluacion AS ENUM (
    'PARCIAL',
    'TRABAJO_PRACTICO'
);

CREATE TYPE instituto.estado_acta AS ENUM (
    'ABIERTA',
    'CERRADA'
);

CREATE TYPE instituto.estado_inscripcion_examen AS ENUM (
    'INSCRIPTO',
    'ANULADO'
);

-- ============================================================================
-- 2. PK-SEC: SEGURIDAD, ACCESO Y AVISOS INSTITUCIONALES
-- ============================================================================

CREATE TABLE instituto.usuario (
    id            BIGSERIAL             PRIMARY KEY,
    nombre        VARCHAR(100)          NOT NULL,
    email         VARCHAR(150)          NOT NULL,
    password_hash VARCHAR(255)          NOT NULL,
    rol           instituto.rol_usuario NOT NULL,
    fecha_alta    TIMESTAMPTZ           NOT NULL DEFAULT now(),
    activo        BOOLEAN               NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_usuario_email UNIQUE (email),
    CONSTRAINT ck_usuario_nombre_no_vacio CHECK (length(btrim(nombre)) > 0),
    CONSTRAINT ck_usuario_email_formato CHECK (email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$')
);

CREATE INDEX idx_usuario_rol ON instituto.usuario (rol);
CREATE INDEX idx_usuario_activo ON instituto.usuario (activo);

CREATE TABLE instituto.aviso (
    id                 BIGSERIAL             PRIMARY KEY,
    publicado_por_id   BIGINT                NOT NULL,
    titulo             VARCHAR(200)          NOT NULL,
    cuerpo             TEXT                  NOT NULL,
    fecha_publicacion  TIMESTAMPTZ           NOT NULL DEFAULT now(),
    dirigido_a         instituto.rol_usuario NULL, -- NULL = para toda la comunidad

    CONSTRAINT fk_aviso_usuario
        FOREIGN KEY (publicado_por_id)
        REFERENCES instituto.usuario (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT ck_aviso_titulo_no_vacio CHECK (length(btrim(titulo)) > 0),
    CONSTRAINT ck_aviso_cuerpo_no_vacio CHECK (length(btrim(cuerpo)) > 0)
);

CREATE INDEX idx_aviso_fecha ON instituto.aviso (fecha_publicacion DESC);
CREATE INDEX idx_aviso_dirigido ON instituto.aviso (dirigido_a);

-- ============================================================================
-- 3. PK-CUR: ESTRUCTURA CURRICULAR Y CICLO LECTIVO
-- ============================================================================

CREATE TABLE instituto.carrera (
    id              BIGSERIAL        PRIMARY KEY,
    nombre          VARCHAR(150)     NOT NULL,
    titulo_otorgado VARCHAR(200)     NOT NULL,
    activa          BOOLEAN          NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_carrera_nombre UNIQUE (nombre),
    CONSTRAINT ck_carrera_nombre_no_vacio CHECK (length(btrim(nombre)) > 0),
    CONSTRAINT ck_carrera_titulo_no_vacio CHECK (length(btrim(titulo_otorgado)) > 0)
);

CREATE TABLE instituto.plan_estudio (
    id          BIGSERIAL    PRIMARY KEY,
    carrera_id  BIGINT       NOT NULL,
    anio        INT          NOT NULL,
    resolucion  VARCHAR(100),
    vigente     BOOLEAN      NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_plan_estudio_carrera
        FOREIGN KEY (carrera_id)
        REFERENCES instituto.carrera (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT uq_plan_estudio_carrera_anio UNIQUE (carrera_id, anio),
    CONSTRAINT ck_plan_estudio_anio_valido CHECK (anio BETWEEN 1990 AND 2100)
);

CREATE INDEX idx_plan_estudio_carrera ON instituto.plan_estudio (carrera_id);

CREATE TABLE instituto.materia (
    id              BIGSERIAL    PRIMARY KEY,
    plan_estudio_id BIGINT       NOT NULL,
    nombre          VARCHAR(150) NOT NULL,
    anio_en_plan    INT          NOT NULL,
    carga_horaria   INT          NOT NULL,

    CONSTRAINT fk_materia_plan
        FOREIGN KEY (plan_estudio_id)
        REFERENCES instituto.plan_estudio (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT uq_materia_plan_nombre UNIQUE (plan_estudio_id, nombre),
    CONSTRAINT ck_materia_nombre_no_vacio CHECK (length(btrim(nombre)) > 0),
    CONSTRAINT ck_materia_anio_en_plan CHECK (anio_en_plan BETWEEN 1 AND 5),
    CONSTRAINT ck_materia_carga_horaria CHECK (carga_horaria > 0)
);

CREATE INDEX idx_materia_plan ON instituto.materia (plan_estudio_id);
CREATE INDEX idx_materia_anio ON instituto.materia (anio_en_plan);

CREATE TABLE instituto.correlatividad (
    id                     BIGSERIAL    PRIMARY KEY,
    materia_id             BIGINT       NOT NULL,
    materia_correlativa_id BIGINT       NOT NULL,
    tipo                   instituto.tipo_correlatividad NOT NULL,

    CONSTRAINT fk_correlatividad_materia
        FOREIGN KEY (materia_id)
        REFERENCES instituto.materia (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_correlatividad_requisito
        FOREIGN KEY (materia_correlativa_id)
        REFERENCES instituto.materia (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT uq_correlatividad_tipo UNIQUE (materia_id, materia_correlativa_id, tipo),
    CONSTRAINT ck_correlatividad_no_reflexiva CHECK (materia_id <> materia_correlativa_id)
);

CREATE INDEX idx_correlatividad_materia ON instituto.correlatividad (materia_id);
CREATE INDEX idx_correlatividad_requisito ON instituto.correlatividad (materia_correlativa_id);

CREATE TABLE instituto.ciclo_lectivo (
    id     BIGSERIAL             PRIMARY KEY,
    anio   INT                   NOT NULL UNIQUE,
    estado instituto.estado_ciclo NOT NULL DEFAULT 'ABIERTO',

    CONSTRAINT ck_ciclo_lectivo_anio_valido CHECK (anio BETWEEN 2000 AND 2100)
);

CREATE TABLE instituto.periodo_inscripcion (
    id               BIGSERIAL               PRIMARY KEY,
    ciclo_lectivo_id BIGINT                  NOT NULL,
    tipo             instituto.tipo_periodo  NOT NULL,
    fecha_inicio     DATE                    NOT NULL,
    fecha_fin        DATE                    NOT NULL,

    CONSTRAINT fk_periodo_inscripcion_ciclo
        FOREIGN KEY (ciclo_lectivo_id)
        REFERENCES instituto.ciclo_lectivo (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT ck_periodo_inscripcion_rango_fechas CHECK (fecha_fin >= fecha_inicio)
);

CREATE INDEX idx_periodo_inscripcion_ciclo ON instituto.periodo_inscripcion (ciclo_lectivo_id);

-- ============================================================================
-- 4. PK-ALU: GESTIÓN DE ALUMNOS Y LEGAJOS
-- ============================================================================

CREATE TABLE instituto.alumno (
    id               BIGSERIAL               PRIMARY KEY,
    usuario_id       BIGINT                  NOT NULL UNIQUE,
    legajo           INT                     NOT NULL UNIQUE,
    nombre           VARCHAR(100)            NOT NULL,
    apellido         VARCHAR(100)            NOT NULL,
    dni              VARCHAR(20)             NOT NULL UNIQUE,
    fecha_nacimiento DATE                    NOT NULL,
    email            VARCHAR(150)            NOT NULL,
    telefono         VARCHAR(50),
    estado           instituto.estado_alumno NOT NULL DEFAULT 'ACTIVO',

    CONSTRAINT fk_alumno_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES instituto.usuario (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT ck_alumno_nombre_no_vacio CHECK (length(btrim(nombre)) > 0),
    CONSTRAINT ck_alumno_apellido_no_vacio CHECK (length(btrim(apellido)) > 0),
    CONSTRAINT ck_alumno_dni_no_vacio CHECK (length(btrim(dni)) > 0),
    CONSTRAINT ck_alumno_email_formato CHECK (email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$')
);

CREATE INDEX idx_alumno_apellido_nombre ON instituto.alumno (apellido, nombre);
CREATE INDEX idx_alumno_estado ON instituto.alumno (estado);

CREATE TABLE instituto.inscripcion_carrera (
    id                BIGSERIAL                            PRIMARY KEY,
    alumno_id         BIGINT                               NOT NULL,
    carrera_id        BIGINT                               NOT NULL,
    fecha_inscripcion DATE                                 NOT NULL DEFAULT CURRENT_DATE,
    estado            instituto.estado_inscripcion_carrera NOT NULL DEFAULT 'ACTIVA',

    CONSTRAINT fk_inscripcion_carrera_alumno
        FOREIGN KEY (alumno_id)
        REFERENCES instituto.alumno (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_inscripcion_carrera_carrera
        FOREIGN KEY (carrera_id)
        REFERENCES instituto.carrera (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT uq_inscripcion_carrera_alumno_carrera UNIQUE (alumno_id, carrera_id)
);

CREATE INDEX idx_inscripcion_carrera_alumno ON instituto.inscripcion_carrera (alumno_id);
CREATE INDEX idx_inscripcion_carrera_carrera ON instituto.inscripcion_carrera (carrera_id);

-- ============================================================================
-- 5. PK-DOC: PLANTA DOCENTE Y ASIGNACIONES
-- ============================================================================

CREATE TABLE instituto.docente (
    id         BIGSERIAL    PRIMARY KEY,
    usuario_id BIGINT       NOT NULL UNIQUE,
    legajo     INT          NOT NULL UNIQUE,
    nombre     VARCHAR(150) NOT NULL,
    cuil       VARCHAR(20)  NOT NULL UNIQUE,
    email      VARCHAR(150) NOT NULL,
    activo     BOOLEAN      NOT NULL DEFAULT TRUE,

    CONSTRAINT fk_docente_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES instituto.usuario (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT ck_docente_nombre_no_vacio CHECK (length(btrim(nombre)) > 0),
    CONSTRAINT ck_docente_cuil_no_vacio CHECK (length(btrim(cuil)) > 0),
    CONSTRAINT ck_docente_email_formato CHECK (email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$')
);

CREATE INDEX idx_docente_nombre ON instituto.docente (nombre);

CREATE TABLE instituto.asignacion_materia (
    id               BIGSERIAL                PRIMARY KEY,
    docente_id       BIGINT                   NOT NULL,
    materia_id       BIGINT                   NOT NULL,
    ciclo_lectivo_id BIGINT                   NOT NULL,
    cargo            instituto.cargo_docente  NOT NULL DEFAULT 'TITULAR',

    CONSTRAINT fk_asignacion_materia_docente
        FOREIGN KEY (docente_id)
        REFERENCES instituto.docente (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_asignacion_materia_materia
        FOREIGN KEY (materia_id)
        REFERENCES instituto.materia (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_asignacion_materia_ciclo
        FOREIGN KEY (ciclo_lectivo_id)
        REFERENCES instituto.ciclo_lectivo (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT uq_asignacion_materia_docente_materia_ciclo_cargo
        UNIQUE (docente_id, materia_id, ciclo_lectivo_id, cargo)
);

CREATE INDEX idx_asignacion_materia_docente ON instituto.asignacion_materia (docente_id);
CREATE INDEX idx_asignacion_materia_materia_ciclo ON instituto.asignacion_materia (materia_id, ciclo_lectivo_id);

-- ============================================================================
-- 6. PK-CURS: CURSADAS, ASISTENCIAS Y CALIFICACIONES PARCIALES
-- ============================================================================

CREATE TABLE instituto.inscripcion_cursada (
    id               BIGSERIAL                    PRIMARY KEY,
    materia_id       BIGINT                       NOT NULL,
    alumno_id        BIGINT                       NOT NULL,
    ciclo_lectivo_id BIGINT                       NOT NULL,
    fecha            DATE                         NOT NULL DEFAULT CURRENT_DATE,
    condicion        instituto.condicion_cursada  NOT NULL DEFAULT 'CURSANDO',
    fuera_de_termino BOOLEAN                      NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_inscripcion_cursada_materia
        FOREIGN KEY (materia_id)
        REFERENCES instituto.materia (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_inscripcion_cursada_alumno
        FOREIGN KEY (alumno_id)
        REFERENCES instituto.alumno (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_inscripcion_cursada_ciclo
        FOREIGN KEY (ciclo_lectivo_id)
        REFERENCES instituto.ciclo_lectivo (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT uq_inscripcion_cursada_alumno_materia_ciclo
        UNIQUE (alumno_id, materia_id, ciclo_lectivo_id)
);

CREATE INDEX idx_inscripcion_cursada_alumno ON instituto.inscripcion_cursada (alumno_id);
CREATE INDEX idx_inscripcion_cursada_materia_ciclo ON instituto.inscripcion_cursada (materia_id, ciclo_lectivo_id);
CREATE INDEX idx_inscripcion_cursada_condicion ON instituto.inscripcion_cursada (condicion);

CREATE TABLE instituto.asistencia (
    id                     BIGSERIAL PRIMARY KEY,
    inscripcion_cursada_id BIGINT    NOT NULL,
    fecha_clase            DATE      NOT NULL,
    presente               BOOLEAN   NOT NULL,

    CONSTRAINT fk_asistencia_cursada
        FOREIGN KEY (inscripcion_cursada_id)
        REFERENCES instituto.inscripcion_cursada (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT uq_asistencia_cursada_fecha
        UNIQUE (inscripcion_cursada_id, fecha_clase)
);

CREATE INDEX idx_asistencia_cursada ON instituto.asistencia (inscripcion_cursada_id);

CREATE TABLE instituto.calificacion_parcial (
    id                     BIGSERIAL                      PRIMARY KEY,
    inscripcion_cursada_id BIGINT                         NOT NULL,
    instancia              instituto.instancia_evaluacion NOT NULL,
    numero_instancia       INT                            NOT NULL DEFAULT 1,
    nota                   NUMERIC(4,2)                   NOT NULL,
    fecha_carga            DATE                           NOT NULL DEFAULT CURRENT_DATE,

    CONSTRAINT fk_calificacion_parcial_cursada
        FOREIGN KEY (inscripcion_cursada_id)
        REFERENCES instituto.inscripcion_cursada (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT uq_calificacion_parcial_instancia
        UNIQUE (inscripcion_cursada_id, instancia, numero_instancia),
    CONSTRAINT ck_calificacion_parcial_nota_rango
        CHECK (nota >= 1.00 AND nota <= 10.00),
    CONSTRAINT ck_calificacion_parcial_numero_positivo
        CHECK (numero_instancia >= 1)
);

CREATE INDEX idx_calificacion_parcial_cursada ON instituto.calificacion_parcial (inscripcion_cursada_id);

-- ============================================================================
-- 7. PK-EXAM: MESAS DE EXAMEN FINAL Y ACTAS OFICIALES
-- ============================================================================

CREATE TABLE instituto.mesa_examen (
    id                    BIGSERIAL    PRIMARY KEY,
    materia_id            BIGINT       NOT NULL,
    ciclo_lectivo_id      BIGINT       NOT NULL,
    fecha                 DATE         NOT NULL,
    hora                  TIME         NOT NULL,
    docente_titular_id    BIGINT       NOT NULL,
    docente_observador_id BIGINT,

    CONSTRAINT fk_mesa_examen_materia
        FOREIGN KEY (materia_id)
        REFERENCES instituto.materia (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_mesa_examen_ciclo
        FOREIGN KEY (ciclo_lectivo_id)
        REFERENCES instituto.ciclo_lectivo (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_mesa_examen_docente_titular
        FOREIGN KEY (docente_titular_id)
        REFERENCES instituto.docente (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_mesa_examen_docente_observador
        FOREIGN KEY (docente_observador_id)
        REFERENCES instituto.docente (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT ck_mesa_examen_docentes_distintos
        CHECK (docente_observador_id IS NULL OR docente_titular_id <> docente_observador_id)
);

CREATE INDEX idx_mesa_examen_materia ON instituto.mesa_examen (materia_id);
CREATE INDEX idx_mesa_examen_fecha ON instituto.mesa_examen (fecha);
CREATE INDEX idx_mesa_examen_titular ON instituto.mesa_examen (docente_titular_id);
CREATE INDEX idx_mesa_examen_observador ON instituto.mesa_examen (docente_observador_id);

CREATE TABLE instituto.acta_examen (
    id             BIGSERIAL             PRIMARY KEY,
    mesa_examen_id BIGINT                NOT NULL UNIQUE,
    numero         INT                   NOT NULL UNIQUE,
    estado         instituto.estado_acta NOT NULL DEFAULT 'ABIERTA',
    fecha_cierre   TIMESTAMPTZ,

    CONSTRAINT fk_acta_examen_mesa
        FOREIGN KEY (mesa_examen_id)
        REFERENCES instituto.mesa_examen (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT ck_acta_examen_cierre_coherente
        CHECK ((estado = 'ABIERTA' AND fecha_cierre IS NULL) OR (estado = 'CERRADA' AND fecha_cierre IS NOT NULL))
);

CREATE TABLE instituto.inscripcion_examen (
    id               BIGSERIAL                           PRIMARY KEY,
    mesa_examen_id   BIGINT                              NOT NULL,
    alumno_id        BIGINT                              NOT NULL,
    acta_examen_id   BIGINT,
    fecha            DATE                                NOT NULL DEFAULT CURRENT_DATE,
    fuera_de_termino BOOLEAN                             NOT NULL DEFAULT FALSE,
    nota_final       NUMERIC(4,2),
    estado           instituto.estado_inscripcion_examen NOT NULL DEFAULT 'INSCRIPTO',

    CONSTRAINT fk_inscripcion_examen_mesa
        FOREIGN KEY (mesa_examen_id)
        REFERENCES instituto.mesa_examen (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_inscripcion_examen_alumno
        FOREIGN KEY (alumno_id)
        REFERENCES instituto.alumno (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT fk_inscripcion_examen_acta
        FOREIGN KEY (acta_examen_id)
        REFERENCES instituto.acta_examen (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT uq_inscripcion_examen_alumno_mesa
        UNIQUE (alumno_id, mesa_examen_id),
    CONSTRAINT ck_inscripcion_examen_nota_rango
        CHECK (nota_final IS NULL OR (nota_final >= 1.00 AND nota_final <= 10.00))
);

CREATE INDEX idx_inscripcion_examen_alumno ON instituto.inscripcion_examen (alumno_id);
CREATE INDEX idx_inscripcion_examen_mesa ON instituto.inscripcion_examen (mesa_examen_id);
CREATE INDEX idx_inscripcion_examen_acta ON instituto.inscripcion_examen (acta_examen_id);

-- ============================================================================
-- 8. PK-DOCUM: GESTIÓN DOCUMENTAL INSTITUCIONAL
-- ============================================================================

CREATE TABLE instituto.plantilla_documento (
    id                     BIGSERIAL    PRIMARY KEY,
    cargada_por_usuario_id BIGINT       NOT NULL,
    nombre                 VARCHAR(150) NOT NULL,
    tipo_acta              VARCHAR(100) NOT NULL,
    archivo                VARCHAR(255) NOT NULL,
    version                INT          NOT NULL DEFAULT 1,
    fecha_carga            TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT fk_plantilla_documento_usuario
        FOREIGN KEY (cargada_por_usuario_id)
        REFERENCES instituto.usuario (id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    CONSTRAINT ck_plantilla_documento_nombre_no_vacio CHECK (length(btrim(nombre)) > 0),
    CONSTRAINT ck_plantilla_documento_archivo_no_vacio CHECK (length(btrim(archivo)) > 0),
    CONSTRAINT ck_plantilla_documento_version_positiva CHECK (version >= 1)
);

CREATE INDEX idx_plantilla_documento_tipo ON instituto.plantilla_documento (tipo_acta);

-- ============================================================================
-- 9. COMENTARIOS EXPLICATIVOS DEL ESQUEMA
-- ============================================================================

COMMENT ON SCHEMA instituto IS
  'ISFT 189 - Base de Datos Global del Sistema de Gestión Académica';

COMMENT ON TABLE instituto.usuario IS
  'Cuentas de usuario institucionales para autenticación y control de accesos RBAC (RF-041 a RF-043)';
COMMENT ON TABLE instituto.aviso IS
  'Avisos institucionales publicados por el Administrador para toda la comunidad o roles específicos (RF-044)';
COMMENT ON TABLE instituto.carrera IS
  'Carreras dictadas en el instituto (RF-005, RF-006)';
COMMENT ON TABLE instituto.plan_estudio IS
  'Planes de estudio y estructuras curriculares oficiales (RF-007)';
COMMENT ON TABLE instituto.materia IS
  'Unidades curriculares de cada plan de estudio (RF-008)';
COMMENT ON TABLE instituto.correlatividad IS
  'Régimen de correlatividades para cursar y rendir (RF-009, RF-021, RF-026)';
COMMENT ON TABLE instituto.ciclo_lectivo IS
  'Ciclos lectivos anuales (RF-010)';
COMMENT ON TABLE instituto.periodo_inscripcion IS
  'Ventanas ordinarias de inscripción a cursadas y exámenes finales (RF-010)';
COMMENT ON TABLE instituto.alumno IS
  'Legajos de alumnos y datos de contacto (RF-001 a RF-004)';
COMMENT ON TABLE instituto.inscripcion_carrera IS
  'Formalización de matriculación a carrera (RF-018)';
COMMENT ON TABLE instituto.docente IS
  'Registro y legajos de la planta docente (RF-011, RF-012)';
COMMENT ON TABLE instituto.asignacion_materia IS
  'Asignación docente a cátedras por ciclo lectivo (RF-013 a RF-016)';
COMMENT ON TABLE instituto.inscripcion_cursada IS
  'Inscripciones a materias en aula, cursado regular y condición final (RF-019, RF-020, RF-032)';
COMMENT ON TABLE instituto.asistencia IS
  'Registro de presentismo de clases (RF-028, RF-029)';
COMMENT ON TABLE instituto.calificacion_parcial IS
  'Calificaciones de parciales y TPs (RF-030, RF-031)';
COMMENT ON TABLE instituto.mesa_examen IS
  'Mesas de exámenes finales estructuradas con tribunal docente (RF-017, RF-023)';
COMMENT ON TABLE instituto.acta_examen IS
  'Actas oficiales de examen final con numeración única y cierre formal (RF-034 a RF-036)';
COMMENT ON TABLE instituto.inscripcion_examen IS
  'Inscripciones a mesas finales y notas definitivas asentadas (RF-024 a RF-027, RF-035)';
COMMENT ON TABLE instituto.plantilla_documento IS
  'Repositorio de documentos y constancias oficiales en blanco (RF-039, RF-040)';
