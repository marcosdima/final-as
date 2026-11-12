-- ISFT 189 — TPI Base de Datos · Archivo 02: DML (datos de prueba + consultas de validación)
-- Ejecutar después de:
--   1. psql -U <usuario> -d <base> -f db/instituto/01_ddl.sql
--   2. psql -U <usuario> -d <base> -f db/instituto/02_dml.sql
--   3. psql -U <usuario> -d <base> -f db/bot/01_ddl.sql
--   4. psql -U <usuario> -d <base> -f db/bot/02_dml.sql

SET search_path TO isft189, instituto, public;

START TRANSACTION;

-- documentos_metadata
INSERT INTO isft189.documentos_metadata
    (id, titulo, tipo_documento, fecha_subida, carrera, activo) VALUES
    (1, 'Plan de Estudio 2024 - Analista Programador Universitario',
        'plan_estudio',     '2024-02-15 09:00:00-03',
        'Analista Programador Universitario', TRUE),
    (2, 'Plan de Estudio 2024 - Tecnico Superior en Desarrollo de Software',
        'plan_estudio',     '2024-02-15 09:30:00-03',
        'Tecnico Superior en Desarrollo de Software', TRUE),
    (3, 'Reglamento General del Estudiante',
        'reglamento',       '2024-02-20 11:00:00-03',
        NULL, TRUE),
    (4, 'Correlatividades - Analista Programador Universitario',
        'correlatividades', '2024-03-01 10:00:00-03',
        'Analista Programador Universitario', TRUE),
    (5, 'Correlatividades - Tecnico Superior en Desarrollo de Software',
        'correlatividades', '2024-03-01 10:20:00-03',
        'Tecnico Superior en Desarrollo de Software', TRUE),
    (6, 'Resolucion 123/2024 - Regimen de Asistencia',
        'resolucion',       '2024-04-10 08:45:00-03',
        NULL, TRUE),
    (7, 'Reglamento de Examenes Finales',
        'reglamento',       '2024-05-20 12:00:00-03',
        NULL, FALSE);

SELECT setval(pg_get_serial_sequence('isft189.documentos_metadata', 'id'),
              (SELECT MAX(id) FROM isft189.documentos_metadata));

-- historial_consultas (referencia a los usuarios existentes en instituto.usuario)
-- IDs utilizados de instituto.usuario:
--   8: Lucas Fernández (ALUMNO)
--   9: Valentina Rossi (ALUMNO)
--   10: Matías Gómez (ALUMNO)
--   4: Carlos Benítez (DOCENTE)
INSERT INTO isft189.historial_consultas
    (id, usuario_id, pregunta, respuesta, fecha_consulta) VALUES
    (1, 8, '¿Cual es la correlatividad de la materia Bases de Datos?',
        'Para cursar Bases de Datos se requiere haber aprobado Algoritmos y Estructuras de Datos.',
        '2024-08-10 10:15:00-03'),
    (2, 8, '¿Cuantas materias tiene el plan de Analista Programador?',
        'El plan vigente tiene 24 materias distribuidas en cuatro cuatrimestres.',
        '2024-08-12 11:05:00-03'),
    (3, 9, '¿Que dice el reglamento sobre la asistencia obligatoria?',
        'El regimen de asistencia exige un minimo del 75% de las clases dictadas para rendir.',
        '2024-08-13 09:40:00-03'),
    (4, 9, '¿Cuando se rinde el final de Bases de Datos?',
        'Segun el reglamento de examenes finales, la instancia final se agenda dentro de los 60 dias de cerrada la catedra.',
        '2024-08-15 16:20:00-03'),
    (5, 10, '¿Que materias se cursan en el primer cuatrimestre?',
        'En el primer cuatrimestre se cursan Introduccion a la Programacion, Matematica y Sistemas de Computacion.',
        '2024-08-18 12:30:00-03'),
    (6, 10, '¿El plan de Desarrollo de Software incluye taller?',
        'Si, el plan incluye Taller de Proyectos Integradores en los ultimos dos cuatrimestres.',
        '2024-08-19 14:10:00-03'),
    (7, 8, '¿Puedo cursar sin tener aprobada la correlativa?',
        'No, el regimen de correlatividades es estricto segun resolucion vigente.',
        '2024-08-20 17:00:00-03'),
    (8, 9, '¿Cual es el plazo para presentar equivalencias?',
        'Las equivalencias se solicitan durante las dos primeras semanas del ciclo lectivo.',
        '2024-08-22 10:00:00-03'),
    (9, 4, '¿Como se computan las inasistencias justificadas?',
        'Las inasistencias con certificado medico se descuentan del computo segun art. 14.',
        '2024-08-25 11:30:00-03'),
    (10, 8, '¿Donde encuentro el programa de Programacion II?',
        'El programa analitico esta disponible en la seccion de planes de estudio del portal.',
        '2024-08-28 09:15:00-03'),
    (11, 4, '¿Cual es el formato de entrega del proyecto final?',
        'El proyecto debe incluir codigo fuente en repositorio institucional y memoria tecnica en PDF.',
        '2024-08-30 15:00:00-03'),
    (12, 8, '¿Hay mesas extraordinarias en mayo?',
        'Las mesas extraordinarias solo se habilitan para alumnos que adeuden hasta dos materias para recibirse.',
        '2024-09-02 16:45:00-03');

SELECT setval(pg_get_serial_sequence('isft189.historial_consultas', 'id'),
              (SELECT MAX(id) FROM isft189.historial_consultas));

COMMIT;

-- Consultas de validación

-- Q1: historial completo con datos del usuario institucional (JOIN)
SELECT h.id                                            AS consulta_id,
       u.nombre                                        AS usuario,
       u.rol                                           AS rol,
       h.pregunta,
       h.fecha_consulta
FROM   isft189.historial_consultas h
       INNER JOIN instituto.usuario u ON u.id = h.usuario_id
ORDER  BY h.fecha_consulta;

-- Q2: usuarios institucionales sin consultas (LEFT JOIN + IS NULL)
SELECT u.nombre,
       u.email,
       u.rol
FROM   instituto.usuario u
       LEFT JOIN isft189.historial_consultas h ON h.usuario_id = u.id
WHERE  h.id IS NULL
ORDER  BY u.nombre;

-- Q3: documentos vigentes por carrera, filtrados por tipo
SELECT d.carrera,
       d.tipo_documento,
       d.titulo,
       d.fecha_subida
FROM   isft189.documentos_metadata d
WHERE  d.activo = TRUE
       AND d.tipo_documento IN ('plan_estudio', 'correlatividades')
ORDER  BY d.carrera, d.tipo_documento, d.titulo;

-- Q4: cantidad de consultas por rol (agrupación)
SELECT u.rol,
       COUNT(*)                          AS total_consultas,
       COUNT(DISTINCT h.usuario_id)      AS usuarios_con_consultas,
       MAX(h.fecha_consulta)             AS ultima_consulta
FROM   instituto.usuario u
       LEFT JOIN isft189.historial_consultas h ON h.usuario_id = u.id
GROUP  BY u.rol
ORDER  BY total_consultas DESC;

-- Q5: última consulta de cada usuario (DISTINCT ON)
SELECT DISTINCT ON (h.usuario_id)
       u.nombre,
       h.pregunta,
       h.fecha_consulta
FROM   isft189.historial_consultas h
       INNER JOIN instituto.usuario u ON u.id = h.usuario_id
ORDER  BY h.usuario_id, h.fecha_consulta DESC;

-- Q6: usuarios con más consultas que el promedio (subconsulta en HAVING)
SELECT u.nombre,
       u.rol,
       COUNT(*) AS total_consultas
FROM   isft189.historial_consultas h
       INNER JOIN instituto.usuario u ON u.id = h.usuario_id
GROUP  BY u.nombre, u.rol
HAVING COUNT(*) > (SELECT AVG(c)
                   FROM   (SELECT COUNT(*) AS c
                           FROM   isft189.historial_consultas
                           GROUP  BY usuario_id) t)
ORDER  BY total_consultas DESC;

-- Q7: documentos institucionales (sin carrera) agrupados por tipo
SELECT d.tipo_documento,
       COUNT(*) AS total_documentos
FROM   isft189.documentos_metadata d
WHERE  d.carrera IS NULL
GROUP  BY d.tipo_documento
ORDER  BY total_documentos DESC;

-- Q8: consultas de un usuario en un rango de fechas (email único + BETWEEN)
SELECT h.fecha_consulta,
       h.pregunta
FROM   isft189.historial_consultas h
       INNER JOIN instituto.usuario u ON u.id = h.usuario_id
WHERE  u.email = 'lfernandez@alumno.isft189.edu.ar'
       AND h.fecha_consulta BETWEEN '2024-08-01' AND '2024-09-30'
ORDER  BY h.fecha_consulta;
