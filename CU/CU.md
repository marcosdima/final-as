# Casos de Uso del Sistema - ISFT 189

En este documento se detallan los Casos de Uso del Sistema de Gestión Académica para el ISFT 189, organizados por paquetes funcionales, con su identificador, nombre, actor primario y la referencia a los Requisitos Funcionales (RF) que amparan.

---

## 1. Seguridad y Acceso (PK-SEC)

| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ID&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Nombre del Caso de Uso | Actor Primario | RF Referencia |
|---|---|---|---|
| CU-01 | Iniciar sesión | Usuario | RF-041 |
| CU-02 | Recuperar contraseña | Usuario | RF-042 |
| CU-03 | Asignar roles a usuarios/as | Administrador/a | RF-043 |
| CU-04 | Publicar avisos institucionales | Administrador/a | RF-044 |

---

## 2. Estructura Curricular y Ciclo Lectivo (PK-CUR)

| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ID&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Nombre del Caso de Uso | Actor Primario | RF Referencia |
|---|---|---|---|
| CU-05 | Registrar carrera | Administrador/a | RF-005 |
| CU-06 | Modificar carrera | Administrador/a | RF-006 |
| CU-07 | Registrar plan de estudios | Administrador/a | RF-007 |
| CU-08 | Registrar materia | Administrador/a | RF-008 |
| CU-09 | Configurar régimen de correlatividades | Administrador/a | RF-009 |
| CU-10 | Configurar ciclo lectivo y períodos de inscripción | Administrador/a | RF-010 |

---

## 3. Gestión de Alumnos y Legajos (PK-ALU)

| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ID&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Nombre del Caso de Uso | Actor Primario | RF Referencia |
|---|---|---|---|
| CU-11 | Registrar alumno/a | Preceptor/a | RF-001 |
| CU-12 | Modificar datos de alumno/a | Preceptor/a | RF-002 |
| CU-13 | Consultar datos de alumno/a | Preceptor/a | RF-003 |
| CU-14 | Dar de baja alumno/a | Preceptor/a | RF-004 |
| CU-15 | Inscribir alumno/a a carrera | Preceptor/a | RF-018 |
| CU-16 | Consultar historia académica | Alumno/a | RF-038 |

---

## 4. Gestión de Planta Docente (PK-DOC)

| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ID&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Nombre del Caso de Uso | Actor Primario | RF Referencia |
|---|---|---|---|
| CU-17 | Registrar docente | Administrador/a | RF-011 |
| CU-18 | Modificar datos de docente | Administrador/a | RF-012 |
| CU-19 | Asignar docente a materia | Preceptor/a | RF-013 |
| CU-20 | Consultar materias asignadas | Docente | RF-014 |
| CU-21 | Consultar nómina de alumnos/as por materia | Docente | RF-015 |
| CU-22 | Consultar nómina general de alumnos/as inscriptos/as | Preceptor/a | RF-016 |
| CU-23 | Consultar mesas de examen asignadas | Docente | RF-017 |

---

## 5. Cursadas, Asistencias y Calificaciones Parciales (PK-CURS)

| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ID&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Nombre del Caso de Uso | Actor Primario | RF Referencia |
|---|---|---|---|
| CU-24 | Inscribirse a cursada de materia | Alumno/a | RF-019, RF-021 |
| CU-25 | Inscribir alumno/a a cursada fuera de término | Preceptor/a | RF-020, RF-021 |
| CU-26 | Validar correlatividades de cursada | Inclusión (CU-24, CU-25) | RF-021 |
| CU-27 | Anular inscripción a cursada | Alumno/a | RF-022 |
| CU-28 | Registrar asistencia de alumnos/as | Docente | RF-028 |
| CU-29 | Consultar porcentaje de asistencia | Alumno/a, Docente, Preceptor/a | RF-029 |
| CU-30 | Registrar calificaciones parciales | Docente | RF-030 |
| CU-31 | Modificar calificaciones parciales | Docente | RF-031 |
| CU-32 | Registrar condición final de cursada | Docente | RF-032 |
| CU-33 | Consultar y exportar planillas de cursada consolidadas | Preceptor/a | RF-033 |
| CU-34 | Generar nómina de inscriptos y planilla de asistencia | Preceptor/a | RF-037 |

---

## 6. Exámenes Finales y Actas Oficiales (PK-EXAM)

| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ID&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Nombre del Caso de Uso | Actor Primario | RF Referencia |
|---|---|---|---|
| CU-35 | Programar mesa de examen final | Preceptor/a | RF-023 |
| CU-36 | Inscribirse a examen final | Alumno/a | RF-024, RF-026 |
| CU-37 | Inscribir alumno/a a examen final fuera de término | Preceptor/a | RF-025, RF-026 |
| CU-38 | Validar condiciones para examen final | Inclusión (CU-36, CU-37) | RF-026 |
| CU-39 | Anular inscripción a examen final | Alumno/a | RF-027 |
| CU-40 | Generar acta de examen | Preceptor/a | RF-034 |
| CU-41 | Cargar calificaciones en acta de examen | Docente | RF-035 |
| CU-42 | Cerrar acta de examen | Preceptor/a | RF-036 |

---

## 7. Gestión Documental Institucional (PK-DOCUM)

| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ID&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Nombre del Caso de Uso | Actor Primario | RF Referencia |
|---|---|---|---|
| CU-43 | Cargar plantilla de documento oficial | Preceptor/a | RF-039 |
| CU-44 | Consultar plantillas de documentos oficiales | Usuario | RF-040 |

---

## 8. Asistente Virtual / Chatbot (PK-CHAT)

| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ID&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Nombre del Caso de Uso | Actor Primario | RF Referencia |
|---|---|---|---|
| CU-45 | Realizar consulta al asistente virtual | Usuario | RF-045 |
| CU-46 | Validar rol y permisos de consulta | Inclusión (CU-45) | RF-046 |
| CU-47 | Consultar información en la base de datos | Inclusión (CU-45) | RF-047 |
| CU-48 | Consultar correlatividades de una materia (ejemplo) | Alumno/a | RF-047, RF-009, RF-021 |
| CU-49 | Registrar la conversación | Inclusión (CU-45) | RF-048 |
