-- ============================================================================
-- ISFT 189 — Sistema Integral de Gestión Académica
-- Archivo 02: DML (Datos de Prueba Oficiales y Consultas de Validación)
-- Motor: PostgreSQL 16+
-- Esquema: instituto
-- Carreras cargadas según Diseños Curriculares oficiales (docs/planes/):
--   1. Tecnicatura Superior en Análisis, Desarrollo y Programación de Aplicaciones (Res. 6175/03)
--   2. Tecnicatura Superior en Desarrollo de Software (IF-2019-35276485-GDEBA-CPEYTDGCYE)
-- Contraseña de prueba para todos los usuarios (bcrypt): isft189.2026
-- ============================================================================

SET search_path TO instituto, public;

BEGIN;

-- ============================================================================
-- 1. PK-SEC: USUARIOS Y AVISOS INSTITUCIONALES
-- ============================================================================

INSERT INTO instituto.usuario (id, nombre, email, password_hash, rol, fecha_alta, activo) VALUES
(1, 'Nora Gómez',        'admin@isft189.edu.ar',                 '$2b$12$Crih1RMeyVqzTvOsKv1kA.20PMBYlF/40a/HuPwJ0EmFkmJJjQxta', 'ADMINISTRADOR', '2024-02-01 08:00:00-03', TRUE),
(2, 'Roberto Paz',       'rpaz@isft189.edu.ar',                  '$2b$12$Crih1RMeyVqzTvOsKv1kA.20PMBYlF/40a/HuPwJ0EmFkmJJjQxta', 'PRECEPTOR',     '2024-02-01 08:30:00-03', TRUE),
(3, 'Laura Morales',     'lmorales@isft189.edu.ar',              '$2b$12$Crih1RMeyVqzTvOsKv1kA.20PMBYlF/40a/HuPwJ0EmFkmJJjQxta', 'PRECEPTOR',     '2024-02-01 09:00:00-03', TRUE),
(4, 'Leonel Luengo',     'lluengo@isft189.edu.ar',               '$2b$12$Crih1RMeyVqzTvOsKv1kA.20PMBYlF/40a/HuPwJ0EmFkmJJjQxta', 'DOCENTE',       '2024-02-10 10:00:00-03', TRUE),
(5, 'Juan Carlos Romero','jcromero@isft189.edu.ar',              '$2b$12$Crih1RMeyVqzTvOsKv1kA.20PMBYlF/40a/HuPwJ0EmFkmJJjQxta', 'DOCENTE',       '2024-02-10 10:30:00-03', TRUE),
(6, 'Esteban Vega',      'evega@isft189.edu.ar',                 '$2b$12$Crih1RMeyVqzTvOsKv1kA.20PMBYlF/40a/HuPwJ0EmFkmJJjQxta', 'DOCENTE',       '2024-02-10 11:00:00-03', TRUE),
(7, 'Silvina Romero',    'sromero@isft189.edu.ar',               '$2b$12$Crih1RMeyVqzTvOsKv1kA.20PMBYlF/40a/HuPwJ0EmFkmJJjQxta', 'DOCENTE',       '2024-02-10 11:30:00-03', TRUE),
(8, 'Marcos Di Matteo',  'mdimatteo@alumno.isft189.edu.ar',      '$2b$12$Crih1RMeyVqzTvOsKv1kA.20PMBYlF/40a/HuPwJ0EmFkmJJjQxta', 'ALUMNO',        '2024-02-15 14:00:00-03', TRUE),
(9, 'Nahuel Quiñonez',   'nquinonez@alumno.isft189.edu.ar',      '$2b$12$Crih1RMeyVqzTvOsKv1kA.20PMBYlF/40a/HuPwJ0EmFkmJJjQxta', 'ALUMNO',        '2024-02-15 14:30:00-03', TRUE),
(10, 'Matías Gómez',     'mgomez@alumno.isft189.edu.ar',         '$2b$12$Crih1RMeyVqzTvOsKv1kA.20PMBYlF/40a/HuPwJ0EmFkmJJjQxta', 'ALUMNO',        '2024-02-15 15:00:00-03', TRUE),
(11, 'Sofía Álvarez',    'salvarez@alumno.isft189.edu.ar',       '$2b$12$Crih1RMeyVqzTvOsKv1kA.20PMBYlF/40a/HuPwJ0EmFkmJJjQxta', 'ALUMNO',        '2025-02-20 10:00:00-03', TRUE),
(12, 'Mateo Castro',     'mcastro@alumno.isft189.edu.ar',        '$2b$12$Crih1RMeyVqzTvOsKv1kA.20PMBYlF/40a/HuPwJ0EmFkmJJjQxta', 'ALUMNO',        '2025-02-20 10:30:00-03', TRUE),
(13, 'Camila Duarte',    'cduarte@alumno.isft189.edu.ar',        '$2b$12$Crih1RMeyVqzTvOsKv1kA.20PMBYlF/40a/HuPwJ0EmFkmJJjQxta', 'ALUMNO',        '2026-02-10 09:00:00-03', TRUE);

SELECT setval('instituto.usuario_id_seq', 13);

INSERT INTO instituto.aviso (id, publicado_por_id, titulo, cuerpo, fecha_publicacion, dirigido_a) VALUES
(1, 1, 'Inicio del Ciclo Lectivo 2026', 'Se informa a toda la comunidad educativa que el inicio de clases será el 16 de marzo en el horario habitual.', '2026-02-15 09:00:00-03', NULL),
(2, 1, 'Inscripción a Exámenes Finales Turno Julio', 'Recordar a los alumnos que el período ordinario de inscripción a mesas finales es del 1 al 15 de julio.', '2026-06-10 10:00:00-03', 'ALUMNO'),
(3, 1, 'Cierre de Cursadas y Entrega de Planillas', 'Estimados docentes: la fecha límite para asentar regularidades y notas parciales es el 25 de noviembre.', '2026-11-01 12:00:00-03', 'DOCENTE');

SELECT setval('instituto.aviso_id_seq', 3);

-- ============================================================================
-- 2. PK-CUR: ESTRUCTURA CURRICULAR (SEGÚN PLANES OFICIALES), CICLO Y PERIODOS
-- ============================================================================

INSERT INTO instituto.carrera (id, nombre, titulo_otorgado, activa) VALUES
(1, 'Tecnicatura Superior en Análisis, Desarrollo y Programación de Aplicaciones', 'Analista Programador en Desarrollo de Aplicaciones', TRUE),
(2, 'Tecnicatura Superior en Desarrollo de Software', 'Desarrollador de Software', TRUE);

SELECT setval('instituto.carrera_id_seq', 2);

INSERT INTO instituto.plan_estudio (id, carrera_id, anio, resolucion, vigente) VALUES
(1, 1, 2003, 'Res. 6175/03', TRUE),
(2, 2, 2019, 'IF-2019-35276485-GDEBA-CPEYTDGCYE', TRUE);

SELECT setval('instituto.plan_estudio_id_seq', 2);

-- Materias Carrera 1: Análisis, Desarrollo y Programación de Aplicaciones (Res. 6175/03 - 1824 hs)
INSERT INTO instituto.materia (id, plan_estudio_id, nombre, anio_en_plan, carga_horaria) VALUES
-- 1er Año (640 hs)
(1,  1, 'Álgebra',                                 1, 64),
(2,  1, 'Análisis Matemático I',                   1, 64),
(3,  1, 'Inglés Técnico I',                        1, 64),
(4,  1, 'Administración de las Organizaciones',    1, 64),
(5,  1, 'Metodología de la Investigación',         1, 64),
(6,  1, 'Programación I',                          1, 128),
(7,  1, 'Sistemas de Computación',                 1, 128),
(8,  1, 'Espacio de Definición Institucional I',   1, 64),
-- 2do Año (640 hs)
(9,  1, 'Probabilidad y Estadística',              2, 64),
(10, 1, 'Análisis Matemático II',                  2, 64),
(11, 1, 'Inglés Técnico II',                       2, 64),
(12, 1, 'Análisis de Sistemas',                    2, 96),
(13, 1, 'Programación Orientada a Objetos',        2, 128),
(14, 1, 'Seminario de Programación',               2, 64),
(15, 1, 'Sistemas Operativos',                     2, 64),
(16, 1, 'Base de Datos',                           2, 64),
(17, 1, 'Espacio de Definición Institucional II',  2, 32),
-- 3er Año (544 hs)
(18, 1, 'Investigación Operativa',                 3, 96),
(19, 1, 'Economía Empresarial',                    3, 64),
(20, 1, 'Teleinformática',                         3, 64),
(21, 1, 'Práctica Profesional',                    3, 128),
(22, 1, 'Diseño e Implementación de Sistemas',     3, 64),
(23, 1, 'Gestión de Base de Datos',                3, 64),
(24, 1, 'Espacio de Definición Institucional III', 3, 64),

-- Materias Carrera 2: Tecnicatura Superior en Desarrollo de Software (2019 - 1824 hs)
-- 1er Año (576 hs)
(25, 2, 'Análisis Matemático',                     1, 64),
(26, 2, 'Administración y gestión de base de datos', 1, 96),
(27, 2, 'Introducción a la programación',          1, 96),
(28, 2, 'Introducción a las redes de datos',       1, 64),
(29, 2, 'Sistemas Digitales',                      1, 64),
(30, 2, 'Sistemas operativos',                     1, 64),
(31, 2, 'Laboratorio de Hardware',                 1, 64),
(32, 2, 'Prácticas Profesionalizantes I',          1, 64),
-- 2do Año (672 hs)
(33, 2, 'Inglés I',                                2, 64),
(34, 2, 'Desarrollo de aplicativos móviles',       2, 96),
(35, 2, 'Álgebra y lógica',                        2, 64),
(36, 2, 'Programación',                            2, 96),
(37, 2, 'Diseño Web',                              2, 64),
(38, 2, 'Estadística y Probabilidades',            2, 64),
(39, 2, 'Desarrollo de sistemas Orientado a Objetos', 2, 128),
(40, 2, 'Prácticas Profesionalizantes II',         2, 96),
-- 3er Año (576 hs)
(41, 2, 'Inglés II',                               3, 64),
(42, 2, 'Gestión de Proyectos',                    3, 64),
(43, 2, 'Desarrollo de sistemas Web',              3, 128),
(44, 2, 'Ingeniería de software',                  3, 128),
(45, 2, 'Metodología de pruebas de sistemas',      3, 64),
(46, 2, 'Prácticas Profesionalizantes III',        3, 128);

SELECT setval('instituto.materia_id_seq', 46);

-- Régimen Oficial de Correlatividades (RF-009, RF-021, RF-026)
INSERT INTO instituto.correlatividad (materia_id, materia_correlativa_id, tipo) VALUES
-- Carrera 1: Análisis, Desarrollo y Programación de Aplicaciones (Res. 6175/03)
(9,  1, 'PARA_CURSAR'), (9,  1, 'PARA_RENDIR'),
(9,  2, 'PARA_CURSAR'), (9,  2, 'PARA_RENDIR'),
(10, 2, 'PARA_CURSAR'), (10, 2, 'PARA_RENDIR'),
(11, 3, 'PARA_CURSAR'), (11, 3, 'PARA_RENDIR'),
(12, 4, 'PARA_CURSAR'), (12, 4, 'PARA_RENDIR'),
(13, 6, 'PARA_CURSAR'), (13, 6, 'PARA_RENDIR'),
(15, 7, 'PARA_CURSAR'), (15, 7, 'PARA_RENDIR'),
(16, 6, 'PARA_CURSAR'), (16, 6, 'PARA_RENDIR'),
(14, 6, 'PARA_CURSAR'), (14, 6, 'PARA_RENDIR'),
(18, 9, 'PARA_CURSAR'), (18, 9, 'PARA_RENDIR'),
(18, 10, 'PARA_CURSAR'), (18, 10, 'PARA_RENDIR'),
(18, 13, 'PARA_CURSAR'), (18, 13, 'PARA_RENDIR'),
(19, 12, 'PARA_CURSAR'), (19, 12, 'PARA_RENDIR'),
(20, 15, 'PARA_CURSAR'), (20, 15, 'PARA_RENDIR'),
(22, 12, 'PARA_CURSAR'), (22, 12, 'PARA_RENDIR'),
(23, 16, 'PARA_CURSAR'), (23, 16, 'PARA_RENDIR'),
(21, 5, 'PARA_CURSAR'), (21, 5, 'PARA_RENDIR'),
(21, 13, 'PARA_CURSAR'), (21, 13, 'PARA_RENDIR'),
(21, 16, 'PARA_CURSAR'), (21, 16, 'PARA_RENDIR'),
(21, 12, 'PARA_CURSAR'), (21, 12, 'PARA_RENDIR'),

-- Carrera 2: Tecnicatura Superior en Desarrollo de Software (2019)
(39, 27, 'PARA_CURSAR'), (39, 27, 'PARA_RENDIR'),
(39, 30, 'PARA_CURSAR'), (39, 30, 'PARA_RENDIR'),
(34, 27, 'PARA_CURSAR'), (34, 27, 'PARA_RENDIR'),
(35, 25, 'PARA_CURSAR'), (35, 25, 'PARA_RENDIR'),
(36, 27, 'PARA_CURSAR'), (36, 27, 'PARA_RENDIR'),
(38, 27, 'PARA_CURSAR'), (38, 27, 'PARA_RENDIR'),
(38, 25, 'PARA_CURSAR'), (38, 25, 'PARA_RENDIR'),
(40, 32, 'PARA_CURSAR'), (40, 32, 'PARA_RENDIR'),
(40, 31, 'PARA_CURSAR'), (40, 31, 'PARA_RENDIR'),
(40, 26, 'PARA_CURSAR'), (40, 26, 'PARA_RENDIR'),
(44, 27, 'PARA_CURSAR'), (44, 27, 'PARA_RENDIR'),
(44, 36, 'PARA_CURSAR'), (44, 36, 'PARA_RENDIR'),
(44, 38, 'PARA_CURSAR'), (44, 38, 'PARA_RENDIR'),
(45, 39, 'PARA_CURSAR'), (45, 39, 'PARA_RENDIR'),
(45, 36, 'PARA_CURSAR'), (45, 36, 'PARA_RENDIR'),
(45, 37, 'PARA_CURSAR'), (45, 37, 'PARA_RENDIR'),
(41, 33, 'PARA_CURSAR'), (41, 33, 'PARA_RENDIR'),
(43, 27, 'PARA_CURSAR'), (43, 27, 'PARA_RENDIR'),
(43, 26, 'PARA_CURSAR'), (43, 26, 'PARA_RENDIR'),
(43, 37, 'PARA_CURSAR'), (43, 37, 'PARA_RENDIR'),
(46, 40, 'PARA_CURSAR'), (46, 40, 'PARA_RENDIR'),
(46, 36, 'PARA_CURSAR'), (46, 36, 'PARA_RENDIR'),
(46, 39, 'PARA_CURSAR'), (46, 39, 'PARA_RENDIR'),
(46, 37, 'PARA_CURSAR'), (46, 37, 'PARA_RENDIR'),
(46, 34, 'PARA_CURSAR'), (46, 34, 'PARA_RENDIR');

INSERT INTO instituto.ciclo_lectivo (id, anio, estado) VALUES
(1, 2025, 'CERRADO'),
(2, 2026, 'ABIERTO');

SELECT setval('instituto.ciclo_lectivo_id_seq', 2);

INSERT INTO instituto.periodo_inscripcion (id, ciclo_lectivo_id, tipo, fecha_inicio, fecha_fin) VALUES
(1, 1, 'CURSADA', '2025-02-15', '2025-03-20'),
(2, 1, 'EXAMEN',  '2025-07-01', '2025-07-15'),
(3, 1, 'EXAMEN',  '2025-11-20', '2025-12-05'),
(4, 2, 'CURSADA', '2026-02-15', '2026-03-20'),
(5, 2, 'EXAMEN',  '2026-07-01', '2026-07-15'),
(6, 2, 'EXAMEN',  '2026-11-20', '2026-12-05');

SELECT setval('instituto.periodo_inscripcion_id_seq', 6);

-- ============================================================================
-- 3. PK-ALU: ALUMNOS Y MATRICULACIONES A CARRERA
-- ============================================================================

INSERT INTO instituto.alumno (id, usuario_id, legajo, nombre, apellido, dni, fecha_nacimiento, email, telefono, estado) VALUES
(1, 8,  1001, 'Marcos', 'Di Matteo', '41234567', '2000-05-14', 'mdimatteo@alumno.isft189.edu.ar', '11-4567-8901', 'ACTIVO'),
(2, 9,  1002, 'Nahuel', 'Quiñonez',  '42345678', '2001-08-22', 'nquinonez@alumno.isft189.edu.ar', '11-5678-9012', 'ACTIVO'),
(3, 10, 1003, 'Matías', 'Gómez',     '40987654', '1999-11-30', 'mgomez@alumno.isft189.edu.ar',    '11-6789-0123', 'ACTIVO'),
(4, 11, 1004, 'Sofía',  'Álvarez',   '43567890', '2002-03-10', 'salvarez@alumno.isft189.edu.ar',  '11-7890-1234', 'ACTIVO'),
(5, 12, 1005, 'Mateo',  'Castro',    '44123890', '2003-01-25', 'mcastro@alumno.isft189.edu.ar',   '11-8901-2345', 'ACTIVO'),
(6, 13, 1006, 'Camila', 'Duarte',    '45012345', '2004-09-18', 'cduarte@alumno.isft189.edu.ar',   '11-9012-3456', 'ACTIVO');

SELECT setval('instituto.alumno_id_seq', 6);

INSERT INTO instituto.inscripcion_carrera (id, alumno_id, carrera_id, fecha_inscripcion, estado) VALUES
(1, 1, 1, '2024-02-20', 'ACTIVA'),
(2, 2, 1, '2024-02-20', 'ACTIVA'),
(3, 3, 1, '2024-02-21', 'ACTIVA'),
(4, 4, 2, '2025-02-22', 'ACTIVA'),
(5, 5, 2, '2025-02-22', 'ACTIVA'),
(6, 6, 1, '2026-02-12', 'ACTIVA');

SELECT setval('instituto.inscripcion_carrera_id_seq', 6);

-- ============================================================================
-- 4. PK-DOC: PLANTA DOCENTE Y ASIGNACIONES
-- ============================================================================

INSERT INTO instituto.docente (id, usuario_id, legajo, nombre, cuil, email, activo) VALUES
(1, 4, 201, 'Leonel Luengo',      '20-28123456-7', 'lluengo@isft189.edu.ar',  TRUE),
(2, 5, 202, 'Juan Carlos Romero', '20-30987654-3', 'jcromero@isft189.edu.ar', TRUE),
(3, 6, 203, 'Esteban Vega',       '20-29567890-5', 'evega@isft189.edu.ar',    TRUE),
(4, 7, 204, 'Silvina Romero',     '27-31456789-2', 'sromero@isft189.edu.ar',  TRUE);

SELECT setval('instituto.docente_id_seq', 4);

INSERT INTO instituto.asignacion_materia (id, docente_id, materia_id, ciclo_lectivo_id, cargo) VALUES
-- Ciclo 2025
(1, 1, 6,  1, 'TITULAR'),     -- Programación I (Carrera 1)
(2, 2, 4,  1, 'TITULAR'),     -- Administración de las Organizaciones (Carrera 1)
(3, 4, 7,  1, 'TITULAR'),     -- Sistemas de Computación (Carrera 1)
(4, 1, 27, 1, 'TITULAR'),     -- Introducción a la programación (Carrera 2)
-- Ciclo 2026
(5, 1, 13, 2, 'TITULAR'),     -- Programación Orientada a Objetos (Carrera 1)
(6, 2, 12, 2, 'TITULAR'),     -- Análisis de Sistemas (Carrera 1)
(7, 3, 16, 2, 'TITULAR'),     -- Base de Datos (Carrera 1)
(8, 4, 16, 2, 'OBSERVADOR'),  -- Base de Datos (Carrera 1)
(9, 1, 36, 2, 'TITULAR');     -- Programación (Carrera 2)

SELECT setval('instituto.asignacion_materia_id_seq', 9);

-- ============================================================================
-- 5. PK-CURS: INSCRIPCIONES A CURSADAS, ASISTENCIAS Y PARCIALES
-- ============================================================================

-- Cursadas 2025
INSERT INTO instituto.inscripcion_cursada (id, materia_id, alumno_id, ciclo_lectivo_id, fecha, condicion, fuera_de_termino) VALUES
(1,  6,  1, 1, '2025-03-01', 'REGULAR',      FALSE), -- Marcos: Programación I
(2,  4,  1, 1, '2025-03-01', 'REGULAR',      FALSE), -- Marcos: Administración de las Organizaciones
(3,  6,  2, 1, '2025-03-01', 'PROMOCIONADO', FALSE), -- Nahuel: Programación I
(4,  4,  2, 1, '2025-03-01', 'PROMOCIONADO', FALSE), -- Nahuel: Administración de las Organizaciones
(5,  6,  3, 1, '2025-03-05', 'LIBRE',        FALSE), -- Matías: Programación I
(6,  4,  3, 1, '2025-03-05', 'REGULAR',      FALSE), -- Matías: Administración de las Organizaciones
(7,  27, 4, 1, '2025-03-01', 'REGULAR',      FALSE), -- Sofía (Software): Introducción a la programación
(8,  26, 4, 1, '2025-03-01', 'REGULAR',      FALSE); -- Sofía (Software): Admin. y gestión de BD

-- Cursadas 2026 (en curso)
INSERT INTO instituto.inscripcion_cursada (id, materia_id, alumno_id, ciclo_lectivo_id, fecha, condicion, fuera_de_termino) VALUES
(9,  13, 1, 2, '2026-03-01', 'CURSANDO', FALSE), -- Marcos: POO
(10, 16, 1, 2, '2026-03-01', 'CURSANDO', FALSE), -- Marcos: Base de Datos
(11, 12, 1, 2, '2026-03-01', 'CURSANDO', FALSE), -- Marcos: Análisis de Sistemas
(12, 13, 2, 2, '2026-03-01', 'CURSANDO', FALSE), -- Nahuel: POO
(13, 16, 2, 2, '2026-03-01', 'CURSANDO', FALSE), -- Nahuel: Base de Datos
(14, 36, 4, 2, '2026-03-01', 'CURSANDO', FALSE), -- Sofía: Programación (Software)
(15, 37, 4, 2, '2026-03-01', 'CURSANDO', FALSE), -- Sofía: Diseño Web (Software)
(16, 27, 5, 2, '2026-03-25', 'CURSANDO', TRUE),  -- Mateo: Introducción a la programación (fuera de término)
(17, 6,  6, 2, '2026-03-01', 'CURSANDO', FALSE); -- Camila: Programación I

SELECT setval('instituto.inscripcion_cursada_id_seq', 17);

-- Asistencias de prueba para cursada 10 (Marcos en Base de Datos - 80%)
INSERT INTO instituto.asistencia (id, inscripcion_cursada_id, fecha_clase, presente) VALUES
(1, 10, '2026-04-03', TRUE),
(2, 10, '2026-04-10', TRUE),
(3, 10, '2026-04-17', FALSE),
(4, 10, '2026-04-24', TRUE),
(5, 10, '2026-05-01', TRUE);

-- Asistencias de prueba para cursada 13 (Nahuel en Base de Datos - 100%)
INSERT INTO instituto.asistencia (id, inscripcion_cursada_id, fecha_clase, presente) VALUES
(6,  13, '2026-04-03', TRUE),
(7,  13, '2026-04-10', TRUE),
(8,  13, '2026-04-17', TRUE),
(9,  13, '2026-04-24', TRUE),
(10, 13, '2026-05-01', TRUE);

SELECT setval('instituto.asistencia_id_seq', 10);

-- Calificaciones parciales
INSERT INTO instituto.calificacion_parcial (id, inscripcion_cursada_id, instancia, numero_instancia, nota, fecha_carga) VALUES
(1, 10, 'PARCIAL', 1, 7.50, '2026-05-15'),
(2, 10, 'TRABAJO_PRACTICO', 1, 8.00, '2026-05-20'),
(3, 13, 'PARCIAL', 1, 9.50, '2026-05-15'),
(4, 13, 'TRABAJO_PRACTICO', 1, 10.00, '2026-05-20'),
(5, 14, 'PARCIAL', 1, 8.50, '2026-05-18');

SELECT setval('instituto.calificacion_parcial_id_seq', 5);

-- ============================================================================
-- 6. PK-EXAM: MESAS DE EXAMEN FINAL, ACTAS E INSCRIPCIONES
-- ============================================================================

INSERT INTO instituto.mesa_examen (id, materia_id, ciclo_lectivo_id, fecha, hora, docente_titular_id, docente_observador_id) VALUES
(1, 6,  1, '2025-12-10', '18:30:00', 1, 3), -- Programación I (Carrera 1)
(2, 4,  1, '2025-12-12', '18:30:00', 2, 4), -- Administración de las Organizaciones (Carrera 1)
(3, 27, 1, '2025-12-15', '18:30:00', 1, 3), -- Introducción a la programación (Carrera 2)
(4, 13, 2, '2026-07-08', '18:30:00', 1, 3); -- Programación Orientada a Objetos (Carrera 1)

SELECT setval('instituto.mesa_examen_id_seq', 4);

-- Actas oficiales
INSERT INTO instituto.acta_examen (id, mesa_examen_id, numero, estado, fecha_cierre) VALUES
(1, 1, 501, 'CERRADA', '2025-12-10 22:00:00-03'),
(2, 2, 502, 'CERRADA', '2025-12-12 21:45:00-03'),
(3, 3, 503, 'CERRADA', '2025-12-15 21:30:00-03'),
(4, 4, 504, 'ABIERTA', NULL);

SELECT setval('instituto.acta_examen_id_seq', 4);

-- Inscripciones a examen y notas finales
INSERT INTO instituto.inscripcion_examen (id, mesa_examen_id, alumno_id, acta_examen_id, fecha, fuera_de_termino, nota_final, estado) VALUES
(1, 1, 1, 1, '2025-11-25', FALSE, 8.00, 'INSCRIPTO'), -- Marcos aprobó Programación I con 8
(2, 1, 2, 1, '2025-11-25', FALSE, 9.00, 'INSCRIPTO'), -- Nahuel aprobó Programación I con 9
(3, 2, 1, 2, '2025-11-26', FALSE, 7.00, 'INSCRIPTO'), -- Marcos aprobó Admin. Organizaciones con 7
(4, 2, 2, 2, '2025-11-26', FALSE, 9.50, 'INSCRIPTO'), -- Nahuel aprobó Admin. Organizaciones con 9.5
(5, 3, 4, 3, '2025-11-27', FALSE, 8.50, 'INSCRIPTO'), -- Sofía aprobó Intro a la programación con 8.5
(6, 4, 1, 4, '2026-06-20', FALSE, NULL, 'INSCRIPTO'), -- Marcos inscripto a POO turno julio 2026
(7, 4, 2, 4, '2026-06-22', FALSE, NULL, 'INSCRIPTO'); -- Nahuel inscripto a POO turno julio 2026

SELECT setval('instituto.inscripcion_examen_id_seq', 7);

-- ============================================================================
-- 7. PK-DOCUM: PLANTILLAS DE DOCUMENTOS OFICIALES
-- ============================================================================

INSERT INTO instituto.plantilla_documento (id, cargada_por_usuario_id, nombre, tipo_acta, archivo, version, fecha_carga) VALUES
(1, 2, 'Constancia de Alumno Regular', 'CONSTANCIA', '/docs/plantillas/constancia_regular_v2.pdf', 2, '2026-02-15 11:00:00-03'),
(2, 2, 'Solicitud de Equivalencias de Materias', 'SOLICITUD', '/docs/plantillas/solicitud_equivalencias_v1.pdf', 1, '2026-02-15 11:30:00-03'),
(3, 3, 'Acta Volante de Mesa de Examen Final', 'ACTA_EXAMEN', '/docs/plantillas/acta_volante_v3.pdf', 3, '2026-02-16 09:15:00-03');

SELECT setval('instituto.plantilla_documento_id_seq', 3);

COMMIT;

-- ============================================================================
-- 8. CONSULTAS DE VALIDACIÓN DE CASOS DE USO (RF / CU)
-- ============================================================================

-- Q1: Consulta de estructura curricular completa (Carrera -> Plan -> Materias)
SELECT 
    c.nombre AS carrera,
    p.anio AS anio_plan,
    p.resolucion,
    m.anio_en_plan,
    m.nombre AS materia,
    m.carga_horaria
FROM instituto.carrera c
JOIN instituto.plan_estudio p ON p.carrera_id = c.id
JOIN instituto.materia m ON m.plan_estudio_id = p.id
WHERE p.vigente = TRUE
ORDER BY c.nombre, m.anio_en_plan, m.nombre;

-- Q2: Validación integral de correlatividades para cursar o rendir (CU-26 / RF-021 / RF-026)
-- Evalúa cursadas regulares/promocionadas Y exámenes finales aprobados (>= 4.00)
WITH estado_alumno AS (
    SELECT
        m.id AS materia_id,
        BOOL_OR(ic.condicion IN ('REGULAR', 'PROMOCIONADO')) AS tiene_regularidad,
        BOOL_OR(ic.condicion = 'PROMOCIONADO' OR (ie.estado = 'INSCRIPTO' AND ie.nota_final >= 4.00)) AS tiene_final_aprobado
    FROM instituto.materia m
    LEFT JOIN instituto.inscripcion_cursada ic
           ON ic.materia_id = m.id AND ic.alumno_id = 1
    LEFT JOIN instituto.mesa_examen me
           ON me.materia_id = m.id
    LEFT JOIN instituto.inscripcion_examen ie
           ON ie.mesa_examen_id = me.id AND ie.alumno_id = 1
    GROUP BY m.id
)
SELECT 
    m_dest.nombre AS materia_objetivo,
    m_req.nombre AS requisito_necesario,
    corr.tipo AS tipo_requisito,
    CASE 
        WHEN corr.tipo = 'PARA_CURSAR' AND COALESCE(ea.tiene_regularidad, FALSE) THEN 'CUMPLE'
        WHEN corr.tipo = 'PARA_RENDIR' AND COALESCE(ea.tiene_final_aprobado, FALSE) THEN 'CUMPLE'
        ELSE 'NO_CUMPLE'
    END AS resultado_validacion
FROM instituto.correlatividad corr
JOIN instituto.materia m_dest ON m_dest.id = corr.materia_id
JOIN instituto.materia m_req ON m_req.id = corr.materia_correlativa_id
LEFT JOIN estado_alumno ea ON ea.materia_id = m_req.id
WHERE corr.materia_id = 16;

-- Q3: Nómina de alumnos inscriptos por materia asignada al docente (CU-21 / RF-015)
SELECT 
    m.nombre AS materia,
    d.nombre AS docente_titular,
    a.legajo AS legajo_alumno,
    a.apellido || ', ' || a.nombre AS alumno,
    a.email,
    ic.fecha AS fecha_inscripcion,
    ic.fuera_de_termino,
    ic.condicion
FROM instituto.asignacion_materia am
JOIN instituto.docente d ON d.id = am.docente_id
JOIN instituto.materia m ON m.id = am.materia_id
JOIN instituto.inscripcion_cursada ic ON ic.materia_id = m.id AND ic.ciclo_lectivo_id = am.ciclo_lectivo_id
JOIN instituto.alumno a ON a.id = ic.alumno_id
WHERE d.legajo = 201 AND m.id = 13 AND am.ciclo_lectivo_id = 2
ORDER BY a.apellido, a.nombre;

-- Q4: Cálculo de porcentaje de asistencias acumuladas por alumno (CU-29 / RF-029)
SELECT 
    a.legajo,
    a.apellido || ', ' || a.nombre AS alumno,
    m.nombre AS materia,
    COUNT(asi.id) AS total_clases,
    SUM(CASE WHEN asi.presente THEN 1 ELSE 0 END) AS clases_presente,
    ROUND((SUM(CASE WHEN asi.presente THEN 1.0 ELSE 0.0 END) / COUNT(asi.id)) * 100, 2) AS porcentaje_asistencia
FROM instituto.inscripcion_cursada ic
JOIN instituto.alumno a ON a.id = ic.alumno_id
JOIN instituto.materia m ON m.id = ic.materia_id
JOIN instituto.asistencia asi ON asi.inscripcion_cursada_id = ic.id
GROUP BY a.legajo, a.apellido, a.nombre, m.nombre
ORDER BY a.legajo;

-- Q5: Planilla consolidada de cursada con notas parciales (CU-33 / RF-033)
SELECT 
    m.nombre AS materia,
    a.legajo,
    a.apellido || ', ' || a.nombre AS alumno,
    MAX(CASE WHEN cp.instancia = 'PARCIAL' AND cp.numero_instancia = 1 THEN cp.nota END) AS parcial_1,
    MAX(CASE WHEN cp.instancia = 'TRABAJO_PRACTICO' AND cp.numero_instancia = 1 THEN cp.nota END) AS tp_1,
    ic.condicion AS condicion_final
FROM instituto.inscripcion_cursada ic
JOIN instituto.materia m ON m.id = ic.materia_id
JOIN instituto.alumno a ON a.id = ic.alumno_id
LEFT JOIN instituto.calificacion_parcial cp ON cp.inscripcion_cursada_id = ic.id
WHERE m.id = 16 AND ic.ciclo_lectivo_id = 2
GROUP BY m.nombre, a.legajo, a.apellido, a.nombre, ic.condicion
ORDER BY a.apellido, a.nombre;

-- Q6: Cronograma de mesas de examen asignadas a docentes (CU-23 / RF-017)
SELECT 
    me.id AS mesa_id,
    m.nombre AS materia,
    me.fecha,
    me.hora,
    dt.nombre AS docente_titular,
    COALESCE(dob.nombre, 'Sin observador') AS docente_observador,
    act.numero AS numero_acta,
    act.estado AS estado_acta,
    COUNT(ie.id) AS total_inscriptos
FROM instituto.mesa_examen me
JOIN instituto.materia m ON m.id = me.materia_id
JOIN instituto.docente dt ON dt.id = me.docente_titular_id
LEFT JOIN instituto.docente dob ON dob.id = me.docente_observador_id
LEFT JOIN instituto.acta_examen act ON act.mesa_examen_id = me.id
LEFT JOIN instituto.inscripcion_examen ie ON ie.mesa_examen_id = me.id
GROUP BY me.id, m.nombre, me.fecha, me.hora, dt.nombre, dob.nombre, act.numero, act.estado
ORDER BY me.fecha DESC, me.hora;

-- Q7: Detalle del acta oficial cerrada con notas finales (CU-40, CU-41 / RF-034, RF-035)
SELECT 
    act.numero AS numero_acta,
    act.estado AS estado_acta,
    act.fecha_cierre,
    m.nombre AS materia,
    a.legajo,
    a.apellido || ', ' || a.nombre AS alumno,
    ie.nota_final,
    CASE 
        WHEN ie.nota_final >= 4.00 THEN 'APROBADO'
        WHEN ie.nota_final IS NOT NULL THEN 'DESAPROBADO'
        ELSE 'PENDIENTE'
    END AS resultado
FROM instituto.acta_examen act
JOIN instituto.mesa_examen me ON me.id = act.mesa_examen_id
JOIN instituto.materia m ON m.id = me.materia_id
JOIN instituto.inscripcion_examen ie ON ie.mesa_examen_id = me.id
JOIN instituto.alumno a ON a.id = ie.alumno_id
WHERE act.numero = 501
ORDER BY a.apellido, a.nombre;

-- Q8: Historia académica consolidada y promedio general del alumno (CU-16 / RF-038)
SELECT 
    a.legajo,
    a.apellido || ', ' || a.nombre AS alumno,
    m.nombre AS materia,
    m.anio_en_plan,
    ie.fecha AS fecha_aprobacion,
    ie.nota_final,
    ROUND(AVG(ie.nota_final) OVER (PARTITION BY a.id), 2) AS promedio_general
FROM instituto.alumno a
JOIN instituto.inscripcion_examen ie ON ie.alumno_id = a.id
JOIN instituto.mesa_examen me ON me.id = ie.mesa_examen_id
JOIN instituto.materia m ON m.id = me.materia_id
WHERE a.legajo = 1001 AND ie.nota_final >= 4.00
ORDER BY m.anio_en_plan, m.nombre;
