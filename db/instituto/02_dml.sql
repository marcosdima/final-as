-- ============================================================================
-- ISFT 189 — Sistema Integral de Gestión Académica Global
-- Archivo 02: DML (Datos de Prueba y Consultas de Validación)
-- Motor: PostgreSQL 16+
-- Esquema: instituto
-- Convención: Todas las tablas en SINGULAR
-- ============================================================================

SET search_path TO instituto, public;

BEGIN;

-- ============================================================================
-- 1. PK-SEC: USUARIOS Y AVISOS INSTITUCIONALES
-- ============================================================================

INSERT INTO instituto.usuario (id, nombre, email, password_hash, rol, fecha_alta, activo) VALUES
(1, 'Nora Gómez',        'admin@isft189.edu.ar',     '$2b$12$eK8K5O0QY4UaXbV9Kj8yReP5G9F2r4Xj.NoraGomezHash',      'ADMINISTRADOR', '2024-02-01 08:00:00-03', TRUE),
(2, 'Roberto Paz',       'rpaz@isft189.edu.ar',      '$2b$12$eK8K5O0QY4UaXbV9Kj8yReP5G9F2r4Xj.RobertoPazHash',     'PRECEPTOR',     '2024-02-01 08:30:00-03', TRUE),
(3, 'Laura Morales',     'lmorales@isft189.edu.ar',  '$2b$12$eK8K5O0QY4UaXbV9Kj8yReP5G9F2r4Xj.LauraMoralesHash',   'PRECEPTOR',     '2024-02-01 09:00:00-03', TRUE),
(4, 'Carlos Benítez',    'cbenitez@isft189.edu.ar',  '$2b$12$eK8K5O0QY4UaXbV9Kj8yReP5G9F2r4Xj.CarlosBenitezHash',   'DOCENTE',       '2024-02-10 10:00:00-03', TRUE),
(5, 'Mariana Díaz',      'mdiaz@isft189.edu.ar',     '$2b$12$eK8K5O0QY4UaXbV9Kj8yReP5G9F2r4Xj.MarianaDiazHash',     'DOCENTE',       '2024-02-10 10:30:00-03', TRUE),
(6, 'Esteban Vega',      'evega@isft189.edu.ar',     '$2b$12$eK8K5O0QY4UaXbV9Kj8yReP5G9F2r4Xj.EstebanVegaHash',     'DOCENTE',       '2024-02-10 11:00:00-03', TRUE),
(7, 'Silvina Romero',    'sromero@isft189.edu.ar',   '$2b$12$eK8K5O0QY4UaXbV9Kj8yReP5G9F2r4Xj.SilvinaRomeroHash',   'DOCENTE',       '2024-02-10 11:30:00-03', TRUE),
(8, 'Lucas Fernández',   'lfernandez@alumno.isft189.edu.ar', '$2b$12$eK8K5O0QY4UaXbV9Kj8yReP5G9F2r4Xj.LucasFHash', 'ALUMNO',      '2024-02-15 14:00:00-03', TRUE),
(9, 'Valentina Rossi',   'vrossi@alumno.isft189.edu.ar',     '$2b$12$eK8K5O0QY4UaXbV9Kj8yReP5G9F2r4Xj.ValenRHash', 'ALUMNO',      '2024-02-15 14:30:00-03', TRUE),
(10, 'Matías Gómez',     'mgomez@alumno.isft189.edu.ar',     '$2b$12$eK8K5O0QY4UaXbV9Kj8yReP5G9F2r4Xj.MatiasGHash', 'ALUMNO',      '2024-02-15 15:00:00-03', TRUE),
(11, 'Sofía Álvarez',    'salvarez@alumno.isft189.edu.ar',   '$2b$12$eK8K5O0QY4UaXbV9Kj8yReP5G9F2r4Xj.SofiaAHash',  'ALUMNO',      '2025-02-20 10:00:00-03', TRUE),
(12, 'Mateo Castro',     'mcastro@alumno.isft189.edu.ar',    '$2b$12$eK8K5O0QY4UaXbV9Kj8yReP5G9F2r4Xj.MateoCHash',  'ALUMNO',      '2025-02-20 10:30:00-03', TRUE),
(13, 'Camila Duarte',    'cduarte@alumno.isft189.edu.ar',    '$2b$12$eK8K5O0QY4UaXbV9Kj8yReP5G9F2r4Xj.CamilaDHash', 'ALUMNO',      '2026-02-10 09:00:00-03', TRUE);

SELECT setval('instituto.usuario_id_seq', 13);

INSERT INTO instituto.aviso (id, publicado_por_id, titulo, cuerpo, fecha_publicacion, dirigido_a) VALUES
(1, 1, 'Inicio del Ciclo Lectivo 2026', 'Se informa a toda la comunidad educativa que el inicio de clases será el 16 de marzo.', '2026-02-15 09:00:00-03', NULL),
(2, 1, 'Inscripción a Exámenes Finales Turno Julio', 'Recordar a los alumnos que el período de inscripción finaliza el 30 de junio.', '2026-06-10 10:00:00-03', 'ALUMNO'),
(3, 1, 'Cierre de Cursadas y Entrega de Planillas', 'Estimados docentes: la fecha límite para asentar regularidades y notas es el 25 de noviembre.', '2026-11-01 12:00:00-03', 'DOCENTE');

SELECT setval('instituto.aviso_id_seq', 3);

-- ============================================================================
-- 2. PK-CUR: ESTRUCTURA CURRICULAR, CICLO LECTIVO Y PERIODOS
-- ============================================================================

INSERT INTO instituto.carrera (id, nombre, titulo_otorgado, activa) VALUES
(1, 'Tecnicatura Superior en Análisis de Sistemas', 'Técnico Superior en Análisis de Sistemas', TRUE),
(2, 'Tecnicatura Superior en Desarrollo de Software', 'Técnico Superior en Desarrollo de Software', TRUE);

SELECT setval('instituto.carrera_id_seq', 2);

INSERT INTO instituto.plan_estudio (id, carrera_id, anio, resolucion, vigente) VALUES
(1, 1, 2023, 'Res. 5847/19', TRUE),
(2, 2, 2024, 'Res. 6112/23', TRUE);

SELECT setval('instituto.plan_estudio_id_seq', 2);

-- Materias para TSAS (Plan 2023)
INSERT INTO instituto.materia (id, plan_estudio_id, nombre, anio_en_plan, carga_horaria) VALUES
-- 1er Año
(1, 1, 'Programación I',               1, 128),
(2, 1, 'Sistemas y Organizaciones',     1, 64),
(3, 1, 'Arquitectura de Computadores', 1, 64),
(4, 1, 'Matemática Discreta',          1, 64),
-- 2do Año
(5, 1, 'Programación II',              2, 128),
(6, 1, 'Bases de Datos',               2, 96),
(7, 1, 'Análisis de Sistemas',         2, 96),
(8, 1, 'Redes y Comunicaciones',       2, 64),
-- 3er Año
(9, 1, 'Práctica Profesionalizante II', 3, 160),
(10, 1, 'Ingeniería de Software',       3, 96);

SELECT setval('instituto.materia_id_seq', 10);

-- Régimen de Correlatividades (RF-009, RF-021, RF-026)
INSERT INTO instituto.correlatividad (id, materia_id, materia_correlativa_id, tipo) VALUES
-- Para cursar Programación II se requiere cursada de Programación I
(1, 5, 1, 'PARA_CURSAR'),
-- Para rendir Programación II se requiere final de Programación I
(2, 5, 1, 'PARA_RENDIR'),
-- Para cursar Análisis de Sistemas se requiere cursada de Sistemas y Organizaciones
(3, 7, 2, 'PARA_CURSAR'),
-- Para rendir Análisis de Sistemas se requiere final de Sistemas y Organizaciones
(4, 7, 2, 'PARA_RENDIR'),
-- Para cursar Bases de Datos se requiere cursada de Programación I y Sistemas y Organizaciones
(5, 6, 1, 'PARA_CURSAR'),
(6, 6, 2, 'PARA_CURSAR'),
-- Para rendir Bases de Datos se requiere final de Programación I y Sistemas y Organizaciones
(7, 6, 1, 'PARA_RENDIR'),
(8, 6, 2, 'PARA_RENDIR'),
-- Para cursar Práctica Profesionalizante II se requiere cursada de Programación II y Bases de Datos
(9, 9, 5, 'PARA_CURSAR'),
(10, 9, 6, 'PARA_CURSAR');

SELECT setval('instituto.correlatividad_id_seq', 10);

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
(1, 8,  1001, 'Lucas',     'Fernández', '41234567', '2000-05-14', 'lfernandez@alumno.isft189.edu.ar', '11-4567-8901', 'ACTIVO'),
(2, 9,  1002, 'Valentina', 'Rossi',     '42345678', '2001-08-22', 'vrossi@alumno.isft189.edu.ar',     '11-5678-9012', 'ACTIVO'),
(3, 10, 1003, 'Matías',    'Gómez',     '40987654', '1999-11-30', 'mgomez@alumno.isft189.edu.ar',     '11-6789-0123', 'ACTIVO'),
(4, 11, 1004, 'Sofía',     'Álvarez',   '43567890', '2002-03-10', 'salvarez@alumno.isft189.edu.ar',   '11-7890-1234', 'ACTIVO'),
(5, 12, 1005, 'Mateo',     'Castro',    '44123890', '2003-01-25', 'mcastro@alumno.isft189.edu.ar',    '11-8901-2345', 'ACTIVO'),
(6, 13, 1006, 'Camila',    'Duarte',    '45012345', '2004-09-18', 'cduarte@alumno.isft189.edu.ar',    '11-9012-3456', 'ACTIVO');

SELECT setval('instituto.alumno_id_seq', 6);

INSERT INTO instituto.inscripcion_carrera (id, alumno_id, carrera_id, fecha_inscripcion, estado) VALUES
(1, 1, 1, '2024-02-20', 'ACTIVA'),
(2, 2, 1, '2024-02-20', 'ACTIVA'),
(3, 3, 1, '2024-02-21', 'ACTIVA'),
(4, 4, 1, '2025-02-22', 'ACTIVA'),
(5, 5, 1, '2025-02-22', 'ACTIVA'),
(6, 6, 1, '2026-02-12', 'ACTIVA');

SELECT setval('instituto.inscripcion_carrera_id_seq', 6);

-- ============================================================================
-- 4. PK-DOC: PLANTA DOCENTE Y ASIGNACIONES
-- ============================================================================

INSERT INTO instituto.docente (id, usuario_id, legajo, nombre, cuil, email, activo) VALUES
(1, 4, 201, 'Carlos Benítez', '20-28123456-7', 'cbenitez@isft189.edu.ar', TRUE),
(2, 5, 202, 'Mariana Díaz',   '27-30987654-3', 'mdiaz@isft189.edu.ar',    TRUE),
(3, 6, 203, 'Esteban Vega',   '20-29567890-5', 'evega@isft189.edu.ar',    TRUE),
(4, 7, 204, 'Silvina Romero', '27-31456789-2', 'sromero@isft189.edu.ar',  TRUE);

SELECT setval('instituto.docente_id_seq', 4);

INSERT INTO instituto.asignacion_materia (id, docente_id, materia_id, ciclo_lectivo_id, cargo) VALUES
-- Ciclo 2025
(1, 1, 1, 1, 'TITULAR'),
(2, 2, 2, 1, 'TITULAR'),
(3, 4, 3, 1, 'TITULAR'),
-- Ciclo 2026
(4, 1, 1, 2, 'TITULAR'),
(5, 1, 5, 2, 'TITULAR'),
(6, 2, 7, 2, 'TITULAR'),
(7, 3, 6, 2, 'TITULAR'),
(8, 4, 6, 2, 'OBSERVADOR');

SELECT setval('instituto.asignacion_materia_id_seq', 8);

-- ============================================================================
-- 5. PK-CURS: INSCRIPCIONES A CURSADAS, ASISTENCIAS Y PARCIALES
-- ============================================================================

-- Cursadas 2025 (cerradas con regularidad/promoción/libre)
INSERT INTO instituto.inscripcion_cursada (id, materia_id, alumno_id, ciclo_lectivo_id, fecha, condicion, fuera_de_termino) VALUES
(1, 1, 1, 1, '2025-03-01', 'REGULAR',      FALSE), -- Lucas F: Regularizó Prog I
(2, 2, 1, 1, '2025-03-01', 'REGULAR',      FALSE), -- Lucas F: Regularizó SyO
(3, 1, 2, 1, '2025-03-01', 'PROMOCIONADO', FALSE), -- Valentina: Promocionó Prog I
(4, 2, 2, 1, '2025-03-01', 'PROMOCIONADO', FALSE), -- Valentina: Promocionó SyO
(5, 1, 3, 1, '2025-03-05', 'LIBRE',        FALSE), -- Matías: Quedó libre Prog I
(6, 2, 3, 1, '2025-03-05', 'REGULAR',      FALSE); -- Matías: Regularizó SyO

-- Cursadas 2026 (en curso)
INSERT INTO instituto.inscripcion_cursada (id, materia_id, alumno_id, ciclo_lectivo_id, fecha, condicion, fuera_de_termino) VALUES
(7,  5, 1, 2, '2026-03-01', 'CURSANDO', FALSE), -- Lucas: Cursando Prog II (válido: tiene Prog I regular)
(8,  6, 1, 2, '2026-03-01', 'CURSANDO', FALSE), -- Lucas: Cursando BD (válido: tiene Prog I y SyO regular)
(9,  7, 1, 2, '2026-03-01', 'CURSANDO', FALSE), -- Lucas: Cursando Análisis (válido: tiene SyO regular)
(10, 5, 2, 2, '2026-03-01', 'CURSANDO', FALSE), -- Valentina: Cursando Prog II
(11, 6, 2, 2, '2026-03-01', 'CURSANDO', FALSE), -- Valentina: Cursando BD
(12, 1, 4, 2, '2026-03-01', 'CURSANDO', FALSE), -- Sofía: Cursando Prog I
(13, 1, 5, 2, '2026-03-25', 'CURSANDO', TRUE);  -- Mateo: Inscripción fuera de término Prog I (RF-020)

SELECT setval('instituto.inscripcion_cursada_id_seq', 13);

-- Asistencias de prueba para cursada 8 (Lucas en Bases de Datos 2026)
-- 5 clases registradas: 4 presentes, 1 ausente => 80% de asistencia
INSERT INTO instituto.asistencia (id, inscripcion_cursada_id, fecha_clase, presente) VALUES
(1, 8, '2026-04-03', TRUE),
(2, 8, '2026-04-10', TRUE),
(3, 8, '2026-04-17', FALSE),
(4, 8, '2026-04-24', TRUE),
(5, 8, '2026-05-01', TRUE);

-- Asistencias de prueba para cursada 11 (Valentina en Bases de Datos 2026)
-- 5 clases registradas: 5 presentes => 100% de asistencia
INSERT INTO instituto.asistencia (id, inscripcion_cursada_id, fecha_clase, presente) VALUES
(6,  11, '2026-04-03', TRUE),
(7,  11, '2026-04-10', TRUE),
(8,  11, '2026-04-17', TRUE),
(9,  11, '2026-04-24', TRUE),
(10, 11, '2026-05-01', TRUE);

SELECT setval('instituto.asistencia_id_seq', 10);

-- Calificaciones parciales
INSERT INTO instituto.calificacion_parcial (id, inscripcion_cursada_id, instancia, numero_instancia, nota, fecha_carga) VALUES
(1, 8, 'PARCIAL', 1, 7.50, '2026-05-15'),
(2, 8, 'TRABAJO_PRACTICO', 1, 8.00, '2026-05-20'),
(3, 11, 'PARCIAL', 1, 9.50, '2026-05-15'),
(4, 11, 'TRABAJO_PRACTICO', 1, 10.00, '2026-05-20');

SELECT setval('instituto.calificacion_parcial_id_seq', 4);

-- ============================================================================
-- 6. PK-EXAM: MESAS DE EXAMEN FINAL, ACTAS E INSCRIPCIONES
-- ============================================================================

-- Mesa Dic 2025 para Programación I
INSERT INTO instituto.mesa_examen (id, materia_id, ciclo_lectivo_id, fecha, hora, docente_titular_id, docente_observador_id) VALUES
(1, 1, 1, '2025-12-10', '18:30:00', 1, 3), -- Prog I: Benítez (titular), Vega (observador)
(2, 2, 1, '2025-12-12', '18:30:00', 2, 4), -- SyO: Díaz (titular), Romero (observador)
(3, 5, 2, '2026-07-08', '18:30:00', 1, 3); -- Prog II Turno Julio 2026

SELECT setval('instituto.mesa_examen_id_seq', 3);

-- Actas oficiales
INSERT INTO instituto.acta_examen (id, mesa_examen_id, numero, estado, fecha_cierre) VALUES
(1, 1, 501, 'CERRADA', '2025-12-10 22:00:00-03'),
(2, 2, 502, 'CERRADA', '2025-12-12 21:45:00-03'),
(3, 3, 503, 'ABIERTA', NULL);

SELECT setval('instituto.acta_examen_id_seq', 3);

-- Inscripciones a examen y notas finales
INSERT INTO instituto.inscripcion_examen (id, mesa_examen_id, alumno_id, acta_examen_id, fecha, fuera_de_termino, nota_final, estado) VALUES
(1, 1, 1, 1, '2025-11-25', FALSE, 8.00, 'INSCRIPTO'), -- Lucas aprobó final Prog I con 8
(2, 1, 2, 1, '2025-11-25', FALSE, 9.00, 'INSCRIPTO'), -- Valentina ratificó promoción Prog I con 9
(3, 2, 1, 2, '2025-11-26', FALSE, 7.00, 'INSCRIPTO'), -- Lucas aprobó final SyO con 7
(4, 2, 2, 2, '2025-11-26', FALSE, 9.50, 'INSCRIPTO'), -- Valentina aprobó final SyO con 9.50
(5, 3, 1, 3, '2026-06-20', FALSE, NULL, 'INSCRIPTO'), -- Lucas inscripto a rendir Prog II (pendiente)
(6, 3, 2, 3, '2026-06-22', FALSE, NULL, 'INSCRIPTO'); -- Valentina inscripta a rendir Prog II (pendiente)

SELECT setval('instituto.inscripcion_examen_id_seq', 6);

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

-- ----------------------------------------------------------------------------
-- Q1: Consulta de estructura curricular completa (Carrera -> Plan -> Materias)
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- Q2: Validación de correlatividades para cursar una materia (CU-26 / RF-021)
-- Materia destino: Bases de Datos (id=6). Alumno: Lucas Fernández (id=1).
-- ----------------------------------------------------------------------------
SELECT 
    m_dest.nombre AS materia_a_cursar,
    m_req.nombre AS requisito_necesario,
    corr.tipo AS tipo_requisito,
    COALESCE(cur.condicion::TEXT, 'NO_CURSADA') AS estado_alumno_en_requisito,
    CASE 
        WHEN corr.tipo = 'PARA_CURSAR' AND cur.condicion IN ('REGULAR', 'PROMOCIONADO') THEN 'CUMPLE'
        WHEN corr.tipo = 'PARA_RENDIR' AND cur.condicion = 'PROMOCIONADO' THEN 'CUMPLE'
        ELSE 'NO_CUMPLE'
    END AS resultado_validacion
FROM instituto.correlatividad corr
JOIN instituto.materia m_dest ON m_dest.id = corr.materia_id
JOIN instituto.materia m_req ON m_req.id = corr.materia_correlativa_id
LEFT JOIN instituto.inscripcion_cursada cur 
       ON cur.materia_id = m_req.id AND cur.alumno_id = 1
WHERE corr.materia_id = 6 AND corr.tipo = 'PARA_CURSAR';

-- ----------------------------------------------------------------------------
-- Q3: Nómina de alumnos inscriptos por materia asignada al docente (CU-21 / RF-015)
-- Docente: Carlos Benítez (legajo=201), Materia: Programación II (id=5)
-- ----------------------------------------------------------------------------
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
WHERE d.legajo = 201 AND m.id = 5 AND am.ciclo_lectivo_id = 2
ORDER BY a.apellido, a.nombre;

-- ----------------------------------------------------------------------------
-- Q4: Cálculo de porcentaje de asistencias acumuladas por alumno (CU-29 / RF-029)
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- Q5: Planilla consolidada de cursada con notas parciales (CU-33 / RF-033)
-- ----------------------------------------------------------------------------
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
WHERE m.id = 6 AND ic.ciclo_lectivo_id = 2
GROUP BY m.nombre, a.legajo, a.apellido, a.nombre, ic.condicion
ORDER BY a.apellido, a.nombre;

-- ----------------------------------------------------------------------------
-- Q6: Cronograma de mesas de examen asignadas a docentes (CU-23 / RF-017)
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- Q7: Detalle del acta oficial cerrada con notas finales (CU-40, CU-41 / RF-034, RF-035)
-- ----------------------------------------------------------------------------
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

-- ----------------------------------------------------------------------------
-- Q8: Historia académica consolidada y promedio general del alumno (CU-16 / RF-038)
-- Alumno: Lucas Fernández (legajo=1001)
-- ----------------------------------------------------------------------------
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
