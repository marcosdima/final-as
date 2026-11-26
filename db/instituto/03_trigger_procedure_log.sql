-- ============================================================================
-- ISFT 189 — Sistema Integral de Gestión Académica
-- Archivo 03: Log de eventos + Trigger de auditoría + Procedure de cierre de acta
-- Motor: PostgreSQL 16+
-- Esquema: instituto
--
-- Ejecutar DESPUÉS de 01_ddl.sql y 02_dml.sql:
--   psql -U tpi -d isft189 -v ON_ERROR_STOP=1 -f db/instituto/03_trigger_procedure_log.sql
-- ============================================================================

SET search_path TO instituto, public;

-- ----------------------------------------------------------------------------
-- 1) LOG DE EVENTOS
--    Tabla append-only donde el trigger y el procedure dejan su rastro.
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS instituto.log_eventos (
    id          BIGSERIAL    PRIMARY KEY,
    fecha       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    nivel       VARCHAR(10)  NOT NULL DEFAULT 'INFO',
    origen      VARCHAR(60)  NOT NULL,
    mensaje     TEXT         NOT NULL,
    detalle     JSONB        NOT NULL DEFAULT '{}'::jsonb,
    usuario_bd  TEXT         NOT NULL DEFAULT current_user,

    CONSTRAINT ck_log_eventos_nivel
        CHECK (nivel IN ('INFO', 'WARN', 'ERROR')),
    CONSTRAINT ck_log_eventos_mensaje_no_vacio
        CHECK (length(btrim(mensaje)) > 0)
);

CREATE INDEX IF NOT EXISTS idx_log_eventos_fecha
    ON instituto.log_eventos (fecha DESC);

CREATE INDEX IF NOT EXISTS idx_log_eventos_origen
    ON instituto.log_eventos (origen);

COMMENT ON TABLE instituto.log_eventos IS
  'Registro cronológico de eventos del sistema (trigger de notas y procedure de cierre de acta)';

-- Función auxiliar: cualquier rutina escribe un evento con una sola llamada.
CREATE OR REPLACE FUNCTION instituto.fn_log(
    p_nivel   VARCHAR,
    p_origen  VARCHAR,
    p_mensaje TEXT,
    p_detalle JSONB DEFAULT '{}'::jsonb
) RETURNS BIGINT
LANGUAGE plpgsql AS $$
DECLARE
    v_id BIGINT;
BEGIN
    INSERT INTO instituto.log_eventos (nivel, origen, mensaje, detalle)
    VALUES (p_nivel, p_origen, p_mensaje, COALESCE(p_detalle, '{}'::jsonb))
    RETURNING id INTO v_id;

    RETURN v_id;
END;
$$;

COMMENT ON FUNCTION instituto.fn_log(VARCHAR, VARCHAR, TEXT, JSONB) IS
  'Inserta un evento en instituto.log_eventos y devuelve su id';

-- ----------------------------------------------------------------------------
-- 2) TRIGGER: audita cambios de la nota final en inscripcion_examen
--    AFTER UPDATE OF nota_final → solo actúa cuando se toca esa columna.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION instituto.fn_log_nota_final()
RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    -- Compara OLD vs NEW: si la nota no cambió, no ensucia el log.
    IF NEW.nota_final IS DISTINCT FROM OLD.nota_final THEN
        PERFORM instituto.fn_log(
            'INFO',
            'trg_nota_final',
            'Nota final modificada',
            jsonb_build_object(
                'inscripcion_examen_id', NEW.id,
                'alumno_id',             NEW.alumno_id,
                'mesa_examen_id',        NEW.mesa_examen_id,
                'nota_anterior',         OLD.nota_final,
                'nota_nueva',            NEW.nota_final
            )
        );
    END IF;

    RETURN NEW;
END;
$$;

COMMENT ON FUNCTION instituto.fn_log_nota_final() IS
  'Trigger: registra en log_eventos el valor anterior y nuevo de la nota final';

DROP TRIGGER IF EXISTS trg_log_nota_final ON instituto.inscripcion_examen;

CREATE TRIGGER trg_log_nota_final
AFTER UPDATE OF nota_final ON instituto.inscripcion_examen
FOR EACH ROW
EXECUTE FUNCTION instituto.fn_log_nota_final();

-- ----------------------------------------------------------------------------
-- 3) PROCEDURE: cierra un acta de examen con validaciones y registro en el log
-- ----------------------------------------------------------------------------
CREATE OR REPLACE PROCEDURE instituto.sp_cerrar_acta(p_acta_id BIGINT)
LANGUAGE plpgsql AS $$
DECLARE
    v_estado   instituto.estado_acta;
    v_numero   INT;
    v_total    INT;
    v_cargadas INT;
BEGIN
    -- Bloquea la fila para que dos cierres simultáneos no se pisen.
    SELECT estado, numero
      INTO v_estado, v_numero
      FROM instituto.acta_examen
     WHERE id = p_acta_id
       FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'El acta % no existe', p_acta_id;
    END IF;

    -- Cierre idempotente: si ya está cerrada, se advierte y no se toca nada.
    IF v_estado = 'CERRADA' THEN
        PERFORM instituto.fn_log(
            'WARN', 'sp_cerrar_acta', 'Intento de cerrar un acta ya cerrada',
            jsonb_build_object('acta_id', p_acta_id, 'numero', v_numero)
        );
        RAISE NOTICE 'El acta % (N° %) ya estaba cerrada; no se modificó.',
            p_acta_id, v_numero;
        RETURN;
    END IF;

    -- Métricas para el log: inscriptos y cuántos tienen nota cargada.
    SELECT count(*), count(nota_final)
      INTO v_total, v_cargadas
      FROM instituto.inscripcion_examen
     WHERE acta_examen_id = p_acta_id;

    UPDATE instituto.acta_examen
       SET estado = 'CERRADA',
           fecha_cierre = now()
     WHERE id = p_acta_id;

    PERFORM instituto.fn_log(
        'INFO', 'sp_cerrar_acta', 'Acta cerrada',
        jsonb_build_object(
            'acta_id',    p_acta_id,
            'numero',     v_numero,
            'inscriptos', v_total,
            'con_nota',   v_cargadas
        )
    );

    RAISE NOTICE 'Acta % (N° %) cerrada: % inscriptos, % con nota final.',
        p_acta_id, v_numero, v_total, v_cargadas;
END;
$$;

COMMENT ON PROCEDURE instituto.sp_cerrar_acta(BIGINT) IS
  'Cierra un acta ABIERTA, valida su estado y registra el evento en log_eventos';

-- ----------------------------------------------------------------------------
-- 4) EJEMPLOS DE USO (ejecutar manualmente)
-- ----------------------------------------------------------------------------
-- CALL instituto.sp_cerrar_acta(4);
--
-- UPDATE instituto.inscripcion_examen
--    SET nota_final = 9.25
--  WHERE id = 1;
--
-- SELECT id, fecha, nivel, origen, mensaje, detalle
--   FROM instituto.log_eventos
--  ORDER BY id DESC
--  LIMIT 10;
