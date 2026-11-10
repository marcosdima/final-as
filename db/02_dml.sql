-- ISFT 189 — TPI Base de Datos · Archivo 02: DML (datos de prueba + consultas de validación)
-- Ejecutar después de 01_ddl.sql: psql -U <usuario> -d <base> -f 02_dml.sql
-- Las fechas son fijas para que los resultados sean reproducibles.

SET search_path TO isft189, public;

START TRANSACTION;

-- usuarios
INSERT INTO isft189.usuarios (id, nombre, email, rol, fecha_alta, activo) VALUES
    (1, 'Leonel Luengo',   'leonel.luengo@isft189.edu.ar',  'admin',   '2024-03-01 08:00:00-03', TRUE),
    (2, 'Maria Fernandez', 'maria.fernandez@isft189.edu.ar', 'docente', '2024-03-05 09:15:00-03', TRUE),
    (3, 'Carlos Gomez',    'carlos.gomez@isft189.edu.ar',    'docente', '2024-03-10 10:30:00-03', TRUE),
    (4, 'Ana Torres',      'ana.torres@isft189.edu.ar',      'alumno',  '2024-08-01 14:00:00-03', TRUE),
    (5, 'Diego Ramirez',   'diego.ramirez@isft189.edu.ar',   'alumno',  '2024-08-02 14:20:00-03', TRUE),
    (6, 'Sofia Beltran',   'sofia.beltran@isft189.edu.ar',   'alumno',  '2024-08-03 15:45:00-03', TRUE),
    (7, 'Lucas Pereira',   'lucas.pereira@isft189.edu.ar',   'alumno',  '2024-08-05 16:00:00-03', FALSE);

-- Sincroniza la secuencia tras la carga con IDs explícitos
SELECT setval(pg_get_serial_sequence('isft189.usuarios', 'id'),
              (SELECT MAX(id) FROM isft189.usuarios));

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

-- historial_consultas
INSERT INTO isft189.historial_consultas
    (id, usuario_id, pregunta, respuesta, fecha_consulta) VALUES
    (1, 4, '¿Cual es la correlatividad de la materia Bases de Datos?',
        'Para cursar Bases de Datos se requiere haber aprobado Algoritmos y Estructuras de Datos.',
        '2024-08-10 10:15:00-03'),
    (2, 4, '¿Cuantas materias tiene el plan de Analista Programador?',
        'El plan vigente tiene 24 materias distribuidas en cuatro cuatrimestres.',
        '2024-08-12 11:05:00-03'),
    (3, 5, '¿Que dice el reglamento sobre la asistencia obligatoria?',
        'El regimen de asistencia exige un minimo del 75% de las clases dictadas para rendir.',
        '2024-08-13 09:40:00-03'),
    (4, 5, '¿Cuando se rinde el final de Bases de Datos?',
        'Segun el reglamento de examenes finales, la instancia final se agenda dentro de los 60 dias de cerrada la catedra.',
        '2024-08-15 16:20:00-03'),
    (5, 6, '¿Que materias se cursan en el primer cuatrimestre?',
        'En el primer cuatrimestre se cursan Introduccion a la Programacion, Matematica y Sistemas de Computacion.',
        '2024-08-18 12:30:00-03'),
    (6, 6, '¿El plan de Desarrollo de Software incluye taller?',
        'Si, el plan incluye Taller de Proyectos Integradores en los ultimos dos cuatrimestres.',
        '2024-08-20 13:10:00-03'),
    (7, 2, '¿Cual es la carga horaria de la materia Bases de Datos?',
        'Bases de Datos tiene 6 horas semanales de teoria y practica.',
        '2024-09-02 08:50:00-03'),
    (8, 2, '¿Como se aprueba el taller?',
        'El taller se aprueba con entrega de proyecto final y defensa oral.',
        '2024-09-02 09:05:00-03'),
    (9, 3, '¿Que dice la resolucion 123/2024?',
        'La resolucion 123/2024 establece el regimen de asistencia para todas las carreras del instituto.',
        '2024-09-10 15:25:00-03'),
    (10, 4, '¿Puedo cursar Analisis Matematico sin aprobar Matematica?',
        'No, Analisis Matematico tiene como correlatividad aprobada Matematica.',
        '2024-09-15 17:45:00-03'),
    (11, 5, '¿Los examenes finales se rinden por escrito?',
        'Si, el reglamento de examenes finales establece instancia escrita y oral segun la catedra.',
        '2024-09-20 10:00:00-03'),
    (12, 6, '¿Cual es la nota minima para aprobar?',
        'Se requiere nota minima de 6 sobre 10 en cualquier materia.',
        '2024-09-25 11:35:00-03');

SELECT setval(pg_get_serial_sequence('isft189.historial_consultas', 'id'),
              (SELECT MAX(id) FROM isft189.historial_consultas));

COMMIT;

-- Consultas de validación

-- Q1: consultas con los datos del usuario que las hizo (JOIN)
SELECT h.id                                            AS consulta_id,
       u.nombre                                        AS usuario,
       u.rol                                           AS rol,
       h.pregunta,
       h.fecha_consulta
FROM   isft189.historial_consultas h
       INNER JOIN isft189.usuarios u ON u.id = h.usuario_id
ORDER  BY h.fecha_consulta;

-- Q2: usuarios sin consultas (LEFT JOIN + IS NULL)
SELECT u.nombre,
       u.email,
       u.rol
FROM   isft189.usuarios u
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
FROM   isft189.usuarios u
       LEFT JOIN isft189.historial_consultas h ON h.usuario_id = u.id
GROUP  BY u.rol
ORDER  BY total_consultas DESC;

-- Q5: última consulta de cada usuario (DISTINCT ON)
SELECT DISTINCT ON (h.usuario_id)
       u.nombre,
       h.pregunta,
       h.fecha_consulta
FROM   isft189.historial_consultas h
       INNER JOIN isft189.usuarios u ON u.id = h.usuario_id
ORDER  BY h.usuario_id, h.fecha_consulta DESC;

-- Q6: usuarios con más consultas que el promedio (subconsulta en HAVING)
SELECT u.nombre,
       u.rol,
       COUNT(*) AS total_consultas
FROM   isft189.historial_consultas h
       INNER JOIN isft189.usuarios u ON u.id = h.usuario_id
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
       INNER JOIN isft189.usuarios u ON u.id = h.usuario_id
WHERE  u.email = 'diego.ramirez@isft189.edu.ar'
       AND h.fecha_consulta BETWEEN '2024-08-01' AND '2024-09-30'
ORDER  BY h.fecha_consulta;
