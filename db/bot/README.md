# TPI Base de Datos — ISFT 189

**Proyecto:** Asistente Virtual Inteligente (RAG) para el ISFT 189  
**Iteración 1:** modelo relacional (documentos, historial de consultas y vinculación a usuarios institucionales)  
**Arquitectura Modular:** Este módulo se integra con el subsistema institucional ([`db/instituto`](file:///home/marcosdima/Desktop/Institut/Segundo%20año/Analisis%20de%20sitemas/integrador/análisis-2/db/instituto)), delegando la gestión de usuarios a la tabla `instituto.usuario` sin duplicar entidades.

> **Alcance:** esta iteración cubre el modelo E-R, el modelo físico (DBML) y los
> scripts DDL/DML con datos de prueba. La **vectorización** (pgvector, embeddings,
> índice HNSW, consultas de similitud) queda **prevista para la próxima
> iteración** — ver [Próxima iteración](#próxima-iteración-vectorización-pendiente).

---

## Archivos

| Archivo | Contenido |
|---|---|
| `er.drawio` | Diagrama **E-R** con simbología Chen: rectángulos (entidades), rombos (relaciones), elipses (atributos), cardinalidades y leyenda. Se abre en VS Code con la extensión Draw.io Integration. |
| `modelo.dbml` | Modelo en **DBML**: entidades, tipos enum, PK/FK e índices. Fuente de referencia de `01_ddl.sql`. |
| `01_ddl.sql` | DDL: esquema, tipos enum, tablas, restricciones e índices. |
| `02_dml.sql` | DML: datos de prueba (7 usuarios, 7 documentos, 12 consultas) + 8 consultas de validación. |
| `Consigna TPI - Base de Datos - ISFT 189.pdf` | Consigna del trabajo. |

---

## Modelo Entidad-Relación

Diagrama en **`er.drawio`** (notación Chen):

| Símbolo | Significado |
|---|---|
| Rectángulo | Entidad — nombres en singular: Usuario, Consulta, Documento, Fragmento |
| Rombo | Relación — Realiza, Se divide en |
| Elipse | Atributo — la clave primaria se muestra subrayada |
| Línea con `1` / `N` | Cardinalidad de la relación |
| Rectángulo punteado | Entidad prevista para la próxima iteración |

Cardinalidades:

- **Usuario 1 → N Consulta** (relación *Realiza*): cada consulta pertenece a un
  usuario.
- **Documento 1 → N Fragmento** (relación *Se divide en*): un documento origina
  muchos fragmentos; la entidad *Fragmento* queda prevista para la próxima
  iteración (vectorización).

### Cómo abrir y exportar

1. Abrir `er.drawio` en VS Code con la extensión **Draw.io Integration**, o en
   <https://app.diagrams.net>.
2. Exportar para el informe: **File → Export as → PNG / PDF**.

---

## Decisiones de diseño

| Decisión | Motivo |
|---|---|
| Esquema propio `isft189` | Aísla el proyecto del `public`; facilita un `DROP SCHEMA CASCADE` para re-ejecutar los scripts. |
| Integración con `instituto.usuario` | Desacopla la gestión de usuarios evitando redundancia de datos. `historial_consultas.usuario_id` es FK a `instituto.usuario(id)`. |
| `tipo_documento` como **ENUM** | Dominios cerrados y estables; el tipo documenta los valores posibles y los rechaza si no están en la lista. |
| `fecha_subida` / `fecha_consulta` como `TIMESTAMPTZ` | El instituto opera con horario local (Argentina); con zona horaria explícita no hay ambigüedad al migrar o consultar desde otra zona. |
| FK `historial_consultas → instituto.usuario` con `ON DELETE RESTRICT` | El historial es auditoría: no debe perderse por un borrado de usuario. `ON UPDATE CASCADE` para renumeraciones de PK. |
| `carrera` nullable en `documentos_metadata` | Reglamentos y resoluciones son institucionales (no pertenecen a una carrera); `NULL` lo expresa sin inventar un valor mágico. |
| Índices: `rol`, `tipo_documento`, `carrera`, `usuario_id`, `fecha_consulta DESC` | Cubren los filtros de las consultas de validación (Q2–Q8) y el orden del historial. |
| CHECK `length(btrim(...)) > 0` en `pregunta`/`respuesta`/`titulo` | Impide strings vacío o solo espacios, que romperían la búsqueda RAG posterior. |
| IDs explícitos en el DML + `setval(...)` | Hace deterministas los datos de prueba (las FK del historial referencian usuarios conocidos) y sincroniza las secuencias para que los INSERT futuros sin `id` no choquen. |

---

## Cómo ejecutar

Requisitos: Docker y `psql` (o usar `docker exec`).

```bash
# 1. Levantar PostgreSQL 16 con pgvector (imagen oficial de la consigna)
docker run -d --name tpi-isft189 \
  -e POSTGRES_USER=tpi \
  -e POSTGRES_PASSWORD=tpi123 \
  -e POSTGRES_DB=isft189 \
  -p 55432:5432 \
  pgvector/pgvector:pg16

# 2. Esperar a que esté listo
docker exec tpi-isft189 pg_isready -U tpi -d isft189

# 3. Crear el esquema y las tablas (primero instituto, luego bot)
psql -h localhost -p 55432 -U tpi -d isft189 -v ON_ERROR_STOP=1 -f ../instituto/01_ddl.sql
psql -h localhost -p 55432 -U tpi -d isft189 -v ON_ERROR_STOP=1 -f ../instituto/02_dml.sql
psql -h localhost -p 55432 -U tpi -d isft189 -v ON_ERROR_STOP=1 -f 01_ddl.sql

# 4. Cargar datos de prueba del bot y correr las consultas de validación
psql -h localhost -p 55432 -U tpi -d isft189 -v ON_ERROR_STOP=1 -f 02_dml.sql
```

Ambos scripts son **re-ejecutables**: el DDL hace `DROP SCHEMA IF EXISTS ... CASCADE`
al inicio y el DML corre dentro de una transacción.

> `pgvector` se usa como base de la consigna, pero **esta iteración no habilita
> la extensión** (se hará en la próxima).

---

## Consultas de validación (`02_dml.sql`)

| # | Técnica | Qué comprueba |
|---|---|---|
| Q1 | `INNER JOIN` | Consultas con los datos del usuario que las hizo |
| Q2 | `LEFT JOIN` + `IS NULL` | Usuarios sin consultas (antimerga) |
| Q3 | Filtros + `IN` + `ORDER BY` | Documentos vigentes por carrera y tipo |
| Q4 | `GROUP BY` + `COUNT`/`MAX` | Agregado por rol |
| Q5 | `DISTINCT ON` | Última consulta de cada usuario |
| Q6 | Subconsulta en `HAVING` | Usuarios sobre el promedio de consultas |
| Q7 | Filtro `IS NULL` + `GROUP BY` | Documentos institucionales por tipo |
| Q8 | Filtro por email único + rango de fechas | Búsqueda puntual en el historial |

---

## Próxima iteración: vectorización (pendiente)

Queda previsto (no implementado en esta iteración):

1. **Extensión:**
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
2. **Tabla vectorial** (ya modelada en `modelo.dbml` y en el diagrama `er.drawio`):
   ```sql
   CREATE TABLE isft189.documentos_vectoriales (
       id          BIGSERIAL PRIMARY KEY,
       documento_id BIGINT NOT NULL
                    REFERENCES isft189.documentos_metadata (id) ON DELETE CASCADE,
       contenido   TEXT NOT NULL,
       metadata    JSONB,
       embedding   VECTOR(n)          -- n a definir: 384 (modelos locales) o 1536 (API)
   );
   ```
3. **Índice HNSW** (justificación para el informe: HNSW ofrece mejor precisión
   que IVFFlat con pocos datos y sin re-entrenamiento; `vector_cosine_ops`
   porque la similitud de coseno es la métrica estándar en RAG):
   ```sql
   CREATE INDEX idx_vectoriales_embedding
       ON isft189.documentos_vectoriales
       USING hnsw (embedding vector_cosine_ops);
   ```
4. **Consulta híbrida** (relacional + JSONB + similitud de coseno con `<=>`):
   ```sql
   SELECT v.id,
          v.contenido,
          m.titulo,
          v.metadata ->> 'pagina'          AS pagina,
          (v.embedding <=> $1::vector)     AS distancia
   FROM   isft189.documentos_vectoriales v
          JOIN isft189.documentos_metadata m ON m.id = v.documento_id
   WHERE  m.tipo_documento = 'plan_estudio'
          AND m.carrera = 'Analista Programador Universitario'
          AND v.metadata ->> 'seccion' = 'correlatividades'
   ORDER  BY v.embedding <=> $1::vector
   LIMIT  5;
   ```

El informe técnico deberá agregar el **análisis de tiempos de respuesta**
(`EXPLAIN ANALYZE`) del índice HNSW, que es un entregable de la consigna.

---

## Validación realizada

- `01_ddl.sql` y `02_dml.sql` ejecutados sin errores sobre `pgvector/pgvector:pg16`
  con `ON_ERROR_STOP=1`.
- Restricciones probadas con casos negativos: email inválido → `CHECK`; email
  duplicado → `UNIQUE`; borrado de usuario con consultas → `FK RESTRICT`;
  pregunta vacía → `CHECK`.
- Secuencias sincronizadas: un INSERT sin `id` posterior a la carga inserta
  correctamente.
- `modelo.dbml` compilado con `npx -p @dbml/cli dbml2sql --postgres` y también con
  `@dbml/core@10.3.1` (la versión que bundlea la extensión de VS Code);
  el SQL generado corrió limpio en una base nueva.
- `er.drawio` validado como XML con todas las celdas y aristas referenciadas
  correctamente (se abre con la extensión Draw.io Integration de VS Code).
