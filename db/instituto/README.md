# Propuesta de Base de Datos Institucional — ISFT 189

**Proyecto:** Sistema Integral de Gestión Académica  
**Institución:** Instituto Superior de Formación Técnica N° 189 (ISFT 189)  
**Alcance:** Estructura académica, administrativa y curricular global del instituto basada en la documentación formal de **Casos de Uso (CU-01 a CU-44)** y **Diagramas de Clases (PK-SEC, PK-CUR, PK-ALU, PK-DOC, PK-CURS, PK-EXAM, PK-DOCUM)**.

---

## Archivos de la Propuesta

| Archivo | Descripción |
|---|---|
| [`modelo.dbml`](file:///home/marcosdima/Desktop/Institut/Segundo%20año/Analisis%20de%20sitemas/integrador/análisis-2/db/instituto/modelo.dbml) | Especificación del modelo físico relacional en **DBML**: tipos enumerados, tablas, restricciones de clave primaria/foránea, índices de rendimiento y agrupación por módulos funcionales (`TableGroup`). Permite generar y visualizar el esquema en herramientas como [dbdocs.io](https://dbdocs.io) o [dbdiagram.io](https://dbdiagram.io). |
| [`01_ddl.sql`](file:///home/marcosdima/Desktop/Institut/Segundo%20año/Analisis%20de%20sitemas/integrador/análisis-2/db/instituto/01_ddl.sql) | Script **DDL** idempotente para PostgreSQL 16+: creación del esquema `instituto`, 11 tipos `ENUM`, 18 tablas con restricciones de integridad (`PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`, `CHECK`), índices B-Tree y comentarios explicativos (`COMMENT ON`). |
| [`02_dml.sql`](file:///home/marcosdima/Desktop/Institut/Segundo%20año/Analisis%20de%20sitemas/integrador/análisis-2/db/instituto/02_dml.sql) | Script **DML** transaccional con datos de prueba realistas para la *Tecnicatura Superior en Análisis de Sistemas* + **8 consultas SQL de validación** que comprueban la resolución de los Casos de Uso del sistema. |

---

## Cobertura de Requisitos Funcionales y Casos de Uso

```mermaid
flowchart TD
    subgraph SEC["PK-SEC & PK-DOCUM: Seguridad y Documentación"]
        U["usuario (RBAC)"] --> AV["aviso"]
        U --> PD["plantilla_documento"]
    end

    subgraph CUR["PK-CUR: Estructura Curricular"]
        CA["carrera"] --> P["plan_estudio"]
        P --> MAT["materia"]
        MAT -.->|recursiva| CORR["correlatividad<br>(cursar / rendir)"]
        CL["ciclo_lectivo"] --> PI["periodo_inscripcion"]
    end

    subgraph ALU["PK-ALU: Alumnos y Legajos"]
        U --- ALU_ENT["alumno"]
        ALU_ENT --> IC["inscripcion_carrera"]
        CA --> IC
    end

    subgraph DOC["PK-DOC: Planta Docente"]
        U --- DOC_ENT["docente"]
        DOC_ENT --> AM["asignacion_materia"]
        MAT --> AM
        CL --> AM
    end

    subgraph CURS["PK-CURS: Cursadas y Asistencias"]
        ALU_ENT --> CURS_ENT["inscripcion_cursada"]
        MAT --> CURS_ENT
        CL --> CURS_ENT
        CURS_ENT --> ASI["asistencia (presentismo)"]
        CURS_ENT --> CAL["calificacion_parcial"]
    end

    subgraph EXAM["PK-EXAM: Exámenes Finales y Actas"]
        MAT --> MESA["mesa_examen"]
        CL --> MESA
        DOC_ENT -->|titular / observador| MESA
        MESA --> ACTA["acta_examen (oficial)"]
        ALU_ENT --> IE["inscripcion_examen"]
        MESA --> IE
        ACTA --> IE
    end
```

| Módulo / Paquete | Casos de Uso Respaldados | Tablas Relacionales |
|---|---|---|
| **PK-SEC: Seguridad y Acceso** | CU-01 (*Iniciar sesión*), CU-02 (*Recuperar contraseña*), CU-03 (*Asignar roles*), CU-04 (*Publicar avisos*) | `usuario`, `aviso` |
| **PK-CUR: Estructura Curricular** | CU-05 (*Registrar carrera*), CU-06 (*Modificar carrera*), CU-07 (*Plan de estudios*), CU-08 (*Materia*), CU-09 (*Correlatividades*), CU-10 (*Ciclo lectivo y períodos*) | `carrera`, `plan_estudio`, `materia`, `correlatividad`, `ciclo_lectivo`, `periodo_inscripcion` |
| **PK-ALU: Alumnos y Legajos** | CU-11 a CU-14 (*Legajo de alumno*), CU-15 (*Inscribir a carrera*), CU-16 (*Historia académica*) | `alumno`, `inscripcion_carrera` |
| **PK-DOC: Planta Docente** | CU-17 y CU-18 (*Legajo docente*), CU-19 (*Asignar a materia*), CU-20 a CU-23 (*Nóminas y mesas asignadas*) | `docente`, `asignacion_materia` |
| **PK-CURS: Cursadas y Asistencias** | CU-24 y CU-25 (*Inscripción ordinaria y fuera de término*), CU-26 (*Validación correlatividades*), CU-27 (*Anulación*), CU-28 y CU-29 (*Asistencias*), CU-30 a CU-32 (*Notas parciales y condición final*), CU-33 y CU-34 (*Planillas consolidadas*) | `inscripcion_cursada`, `asistencia`, `calificacion_parcial` |
| **PK-EXAM: Exámenes y Actas** | CU-35 (*Programar mesa*), CU-36 a CU-39 (*Inscripción y validación*), CU-40 a CU-42 (*Generación, carga de notas y cierre de acta oficial*) | `mesa_examen`, `acta_examen`, `inscripcion_examen` |
| **PK-DOCUM: Gestión Documental** | CU-43 (*Cargar plantilla oficial*), CU-44 (*Consultar plantillas*) | `plantilla_documento` |

---

## Diccionario de Tablas

1. **`usuario`**: Cuentas institucionales con credenciales hash (bcrypt), estado y rol (`ALUMNO`, `DOCENTE`, `PRECEPTOR`, `ADMINISTRADOR`).
2. **`aviso`**: Comunicados institucionales emitidos por administración con alcance general o segmentado por rol.
3. **`carrera`**: Carreras terciarias técnicas del instituto.
4. **`plan_estudio`**: Estructuras curriculares oficiales asociadas a una carrera y año de resolución.
5. **`materia`**: Unidades curriculares con año (`1..5`) y carga horaria.
6. **`correlatividad`**: Requisitos entre materias (`PARA_CURSAR` o `PARA_RENDIR`).
7. **`ciclo_lectivo`**: Años académicos con estado (`ABIERTO`, `CERRADO`).
8. **`periodo_inscripcion`**: Ventanas temporales ordinarias para cursadas y exámenes finales.
9. **`alumno`**: Legajo único, DNI, datos de contacto y estado (`ACTIVO`, `BAJA`).
10. **`inscripcion_carrera`**: Matriculación formal del alumno a la tecnicatura.
11. **`docente`**: Legajo docente, CUIL y cuenta de usuario vinculada.
12. **`asignacion_materia`**: Cátedras designadas con cargo (`TITULAR`, `OBSERVADOR`) por ciclo lectivo.
13. **`inscripcion_cursada`**: Registro en aula con condición final (`CURSANDO`, `REGULAR`, `PROMOCIONADO`, `LIBRE`) y flag `fuera_de_termino`.
14. **`asistencia`**: Presentismo clase a clase para cómputo de porcentaje de asistencia.
15. **`calificacion_parcial`**: Notas de parciales y trabajos prácticos (escala 1 a 10).
16. **`mesa_examen`**: Turnos de examen final con tribunal asignado (docente titular y observador).
17. **`acta_examen`**: Acta oficial digital con folio único; inmutable al cerrarse con registro de fecha.
18. **`inscripcion_examen`**: Alumnos inscriptos, nota final y estado (`INSCRIPTO`, `ANULADO`).
19. **`plantilla_documento`**: Repositorio de modelos en blanco descargables (constancias, actas modelo).

---

## Decisiones de Diseño de Ingeniería de Datos

1. **Aislamiento en Esquema Propio (`instituto`)**:  
   Garantiza la modularidad frente a otros subsistemas y permite migraciones independientes.

2. **Tipos Enumerados (`ENUM`)**:  
   Garantizan dominio cerrado, integridad semántica a nivel de motor y evitan inconsistencias tipográficas en estados (`condicion_cursada`, `estado_acta`, `rol_usuario`, etc.).

3. **Restricciones de Integridad y Reglas de Negocio en Base de Datos**:  
   - `CHECK (email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$')`: validación de formato de correo electrónico.  
   - `CHECK (nota >= 1.00 AND nota <= 10.00)`: escala de calificación estándar.  
   - `CHECK (materia_id <> materia_correlativa_id)`: evita autoreferencias circulares en correlatividades.  
   - `CHECK (docente_titular_id <> docente_observador_id)`: garantiza diversidad en el tribunal evaluador.  
   - `CHECK ((estado = 'ABIERTA' AND fecha_cierre IS NULL) OR (estado = 'CERRADA' AND fecha_cierre IS NOT NULL))`: consistencia temporal del acta oficial.

4. **Acciones Referenciales (`ON DELETE`)**:  
   - Tablas maestras e históricas (`usuario`, `alumno`, `docente`, `materia`, `mesa_examen`, `acta_examen`) implementan **`ON DELETE RESTRICT`** para preservar la integridad de la historia académica.  
   - Entidades subordinadas dependientes del encabezado (`asistencia`, `calificacion_parcial`) implementan **`ON DELETE CASCADE`** respecto a su cursada.

---

## Instrucciones de Ejecución

### Opción A: PostgreSQL Local
```bash
# 1. Crear el esquema y las tablas
psql -d postgres -v ON_ERROR_STOP=1 -f db/instituto/01_ddl.sql

# 2. Cargar datos de prueba y ejecutar las 8 consultas de validación
psql -d postgres -v ON_ERROR_STOP=1 -f db/instituto/02_dml.sql
```

### Opción B: Mediante Docker
```bash
docker exec -i pg-isft189 psql -U postgres -v ON_ERROR_STOP=1 < db/instituto/01_ddl.sql
docker exec -i pg-isft189 psql -U postgres -v ON_ERROR_STOP=1 < db/instituto/02_dml.sql
```

---

## Consultas de Validación Incluidas en `02_dml.sql`

1. **Q1 — Estructura Curricular**: Jerarquía Carrera $\to$ Plan de Estudio $\to$ Materias por año con carga horaria.
2. **Q2 — Validación de Correlatividades (CU-26 / RF-021)**: Verifica cumplimiento de regularidades para cursar una materia.
3. **Q3 — Nómina de Cursada para Docente (CU-21 / RF-015)**: Lista alumnos inscriptos por materia asignada al docente titular en el ciclo lectivo.
4. **Q4 — Cálculo de Asistencia Acumulada (CU-29 / RF-029)**: Porcentaje de presentismo sobre clases registradas.
5. **Q5 — Planilla Consolidada de Cursada (CU-33 / RF-033)**: Agrupa notas parciales, trabajos prácticos y condición final alcanzada.
6. **Q6 — Cronograma de Mesas Asignadas (CU-23 / RF-017)**: Mesas de examen final con tribunal asignado e inscriptos.
7. **Q7 — Acta Oficial de Examen (CU-40 a CU-42 / RF-034 a RF-036)**: Detalle del acta cerrada con notas finales asentadas.
8. **Q8 — Historia Académica del Alumno (CU-16 / RF-038)**: Materias aprobadas y promedio general calculado mediante funciones de ventana.
