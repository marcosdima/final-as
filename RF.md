# Requisitos Funcionales y No Funcionales - Sistema de Gestión Académica (ISFT 189)

## Requisitos Funcionales (RF)

| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ID&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Nombre | Descripción |
|---|---|---|
| RF-001 | Registrar alumno/a | El sistema deberá permitir al/a la preceptor/a registrar un/a nuevo/a alumno/a en la institución. |
| RF-002 | Modificar datos de alumno/a | El sistema deberá permitir al/a la preceptor/a actualizar los datos personales y de contacto de un/a alumno/a. |
| RF-003 | Consultar datos de alumno/a | El sistema deberá permitir al/a la preceptor/a buscar y visualizar el legajo y la información académica de un/a alumno/a. |
| RF-004 | Dar de baja alumno/a | El sistema deberá permitir al/a la preceptor/a registrar la baja de un/a alumno/a en la institución. |
| RF-005 | Registrar carrera | El sistema deberá permitir al/a la administrador/a registrar una nueva carrera. |
| RF-006 | Modificar carrera | El sistema deberá permitir al/a la administrador/a editar los datos de una carrera. |
| RF-007 | Registrar plan de estudios | El sistema deberá permitir al/a la administrador/a asociar un plan de estudios a una carrera. |
| RF-008 | Registrar materia | El sistema deberá permitir al/a la administrador/a registrar una materia en un plan de estudios. |
| RF-009 | Configurar régimen de correlatividades | El sistema deberá permitir al/a la administrador/a definir los requisitos de correlatividad para cursar y para rendir examen final de cada materia. |
| RF-010 | Configurar ciclo lectivo y períodos de inscripción | El sistema deberá permitir al/a la administrador/a aperturar el ciclo lectivo y establecer las fechas de inicio y fin para los períodos ordinarios de inscripción a cursadas y exámenes. |
| RF-011 | Registrar docente | El sistema deberá permitir al/a la administrador/a registrar los datos personales y legajo de un/a docente. |
| RF-012 | Modificar datos de docente | El sistema deberá permitir al/a la administrador/a actualizar la información de un/a docente. |
| RF-013 | Asignar docente a materia | El sistema deberá permitir al/a la preceptor/a asignar un/a docente titular a la materia correspondiente al ciclo lectivo. |
| RF-014 | Consultar materias asignadas | El sistema deberá permitir al/a la docente visualizar las materias que le fueron asignadas en el ciclo lectivo vigente. |
| RF-015 | Consultar nómina de alumnos/as por materia | El sistema deberá permitir al/a la docente visualizar la lista de alumnos/as inscriptos/as en sus materias asignadas. |
| RF-016 | Consultar nómina general de alumnos/as inscriptos/as | El sistema deberá permitir al/a la preceptor/a consultar la lista general de alumnos/as inscriptos/as a cursadas y mesas de examen por materia y carrera. |
| RF-017 | Consultar mesas de examen asignadas | El sistema deberá permitir al/a la docente consultar el cronograma de mesas de examen donde participa como evaluador/a o como docente observador/a. |
| RF-018 | Inscribir alumno/a a carrera | El sistema deberá permitir al/a la preceptor/a formalizar la inscripción de un/a alumno/a a una carrera. |
| RF-019 | Inscribir alumno/a a cursada | El sistema deberá permitir al/a la alumno/a inscribirse a la cursada de una materia dentro de los plazos habilitados. |
| RF-020 | Inscribir alumno/a a cursada fuera de término | El sistema deberá permitir al/a la preceptor/a registrar la inscripción de un/a alumno/a a la cursada de una materia de forma excepcional fuera del período habilitado. |
| RF-021 | Validar correlatividades para cursada | El sistema deberá verificar automáticamente que el/la alumno/a cumpla con las materias correlativas requeridas antes de confirmar su inscripción a la cursada. |
| RF-022 | Anular inscripción a cursada | El sistema deberá permitir al/a la alumno/a anular su inscripción a la cursada de una materia dentro de los plazos habilitados. |
| RF-023 | Registrar mesa de examen | El sistema deberá permitir al/a la preceptor/a programar una mesa de examen final, indicando fecha, horario, materia, docente a cargo y docente observador/a. |
| RF-024 | Inscribir alumno/a a examen final | El sistema deberá permitir al/a la alumno/a inscribirse a una mesa de examen final dentro del período ordinario habilitado. |
| RF-025 | Inscribir alumno/a a examen final fuera de término | El sistema deberá permitir al/a la preceptor/a registrar la inscripción excepcional de un/a alumno/a a una mesa de examen fuera del plazo ordinario. |
| RF-026 | Validar condiciones para examen final | El sistema deberá verificar automáticamente que el/la alumno/a tenga la condición de regular y cumpla con las correlativas de aprobación antes de confirmar la inscripción al examen final. |
| RF-027 | Anular inscripción a examen final | El sistema deberá permitir al/a la alumno/a anular su inscripción a una mesa de examen final dentro del plazo habilitado. |
| RF-028 | Registrar asistencia de alumnos/as | El sistema deberá permitir al/a la docente registrar el presentismo de los/as alumnos/as en cada clase de su materia. |
| RF-029 | Consultar porcentaje de asistencia | El sistema deberá permitir al/a la alumno/a, al/a la docente y al/a la preceptor/a consultar el porcentaje de asistencia acumulado en cada materia. |
| RF-030 | Registrar calificaciones parciales | El sistema deberá permitir al/a la docente registrar las notas de evaluaciones parciales y trabajos prácticos de los/as alumnos/as en su materia. |
| RF-031 | Modificar calificaciones parciales | El sistema deberá permitir al/a la docente rectificar una calificación parcial previamente registrada. |
| RF-032 | Registrar condición final de cursada | El sistema deberá permitir al/a la docente asentar la condición final de cursada del/de la alumno/a (regular, promocionado o libre) al término del período lectivo. |
| RF-033 | Consultar y exportar planillas de cursada consolidadas | El sistema deberá permitir al/a la preceptor/a consultar y exportar las planillas de calificaciones y asistencias registradas por los docentes para su transcripción a los registros físicos. |
| RF-034 | Generar acta de examen | El sistema deberá permitir al/a la preceptor/a generar e imprimir el acta de examen para la mesa evaluadora física, incluyendo a los/as alumnos/as inscriptos/as y a quienes hayan obtenido la condición de promocionado/a. |
| RF-035 | Cargar calificaciones en acta de examen | El sistema deberá permitir al/a la docente a cargo de la mesa asentar las calificaciones finales obtenidas por los/as alumnos/as en el acta de examen digital. |
| RF-036 | Cerrar acta de examen | El sistema deberá permitir al/a la preceptor/a cerrar de forma definitiva el acta de examen en el sistema para bloquear modificaciones y proceder a su archivo formal. |
| RF-037 | Generar listado de inscriptos y planilla de asistencia | El sistema deberá permitir al/a la preceptor/a exportar e imprimir la lista de alumnos/as inscriptos/as y las planillas de asistencia en blanco por materia. |
| RF-038 | Consultar historia académica | El sistema deberá permitir al/a la alumno/a consultar su registro de materias cursadas, calificaciones obtenidas y promedio general. |
| RF-039 | Cargar plantilla de documento oficial | El sistema deberá permitir al/a la preceptor/a cargar archivos con plantillas en blanco de documentos y constancias institucionales. |
| RF-040 | Consultar plantillas de documentos oficiales | El sistema deberá permitir al/a la usuario/a consultar las plantillas en blanco de documentos oficiales para su posterior impresión y completado manual. |
| RF-041 | Iniciar sesión en el sistema | El sistema deberá permitir a los/as usuarios/as autenticarse mediante sus credenciales de acceso. |
| RF-042 | Recuperar contraseña | El sistema deberá permitir a los/as usuarios/as solicitar el restablecimiento de su contraseña de acceso. |
| RF-043 | Asignar roles a usuarios/as | El sistema deberá permitir al/a la administrador/a asignar roles a las cuentas de usuario (Alumno/a, Docente, Preceptor/a, Administrador/a). |
| RF-044 | Publicar avisos institucionales | El sistema deberá permitir al/a la administrador/a emitir y publicar comunicados dirigidos a los miembros de la institución. |

---

## Requisitos No Funcionales (RNF)

| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;ID&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Nombre | Descripción |
|---|---|---|
| RNF-001 | Usabilidad | La interfaz gráfica de usuario deberá obtener una puntuación mínima de 75 puntos en la escala estandarizada de usabilidad SUS (System Usability Scale) durante las pruebas con usuarios/as finales. |
| RNF-002 | Diseño responsivo | La interfaz web deberá ser adaptable a pantallas móviles, tablets y de escritorio, soportando puntos de interrupción estándar (breakpoints desde 360px hasta 1920px). |
| RNF-003 | Tiempo de respuesta | Las consultas y operaciones habituales del sistema deberán procesarse y responder en un tiempo inferior a 3 segundos en el percentil 95 (P95) bajo condiciones normales de carga. |
| RNF-004 | Disponibilidad | El sistema deberá garantizar una disponibilidad operativa mínima del 99% mensual durante los períodos de inscripción a cursadas y mesas de examen. |
| RNF-005 | Concurrencia | El sistema deberá soportar al menos 200 usuarios/as concurrentes activos/as simultáneamente durante los picos de apertura de inscripciones sin interrupción ni caída del servicio. |
| RNF-006 | Seguridad en autenticación | Las contraseñas de acceso deberán ser almacenadas mediante funciones de hash criptográfico seguro y con salting (bcrypt o Argon2). |
| RNF-007 | Control de acceso por roles | El sistema deberá implementar un esquema de autorización basado en roles (RBAC) para restringir el acceso a funcionalidades e información sensible según el rol asignado (Alumno/a, Docente, Preceptor/a, Administrador/a). |
| RNF-008 | Integridad transaccional | La base de datos relacional deberá garantizar la integridad referencial y el cumplimiento de las propiedades ACID en las operaciones críticas de inscripción y carga de notas. |
| RNF-009 | Auditoría y trazabilidad | El sistema deberá almacenar registros inmutables de auditoría (logs) de operaciones sensibles (modificación de calificaciones, cierres de actas, altas/bajas de inscripciones) detallando usuario, fecha, hora y acción realizada. |
| RNF-010 | Compatibilidad web | La aplicación deberá ser compatible y totalmente operativa en las dos últimas versiones estables de los principales navegadores web (Google Chrome, Mozilla Firefox, Microsoft Edge y Safari). |
| RNF-011 | Mantenibilidad y calidad | El código del backend deberá estructurarse en una arquitectura modular por capas y contar con una cobertura mínima de pruebas automatizadas del 70% en la lógica de negocio (validaciones de correlatividades, inscripciones y cierres). |
| RNF-012 | Protección de datos personales | El sistema deberá implementar las medidas de confidencialidad y resguardo de la información académica y personal exigidas por la Ley de Protección de Datos Personales N° 25.326 de la República Argentina. |
