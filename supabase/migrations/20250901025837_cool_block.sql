/*
  # Funciones de validación y reglas de negocio

  1. Validaciones de datos
    - Validar combinaciones torre-sector
    - Validar rangos de mediciones
    - Validar formatos de ubicación

  2. Triggers de validación
    - Validar datos antes de insertar/actualizar
    - Aplicar reglas de negocio específicas

  3. Funciones de utilidad
    - Generar identificadores únicos
    - Formatear datos
    - Calcular estadísticas
*/

-- Función para validar combinación torre-sector
CREATE OR REPLACE FUNCTION validar_torre_sector(torre_param text, sector_param text)
RETURNS boolean AS $$
BEGIN
  -- Torres C y H no tienen sector Norte
  IF torre_param IN ('C', 'H') AND sector_param = 'Norte' THEN
    RETURN false;
  END IF;
  
  -- Validar que el sector sea válido
  IF sector_param IS NOT NULL AND sector_param NOT IN ('Norte', 'Poniente', 'Oriente') THEN
    RETURN false;
  END IF;
  
  RETURN true;
END;
$$ LANGUAGE plpgsql;

-- Función para validar rangos de medición
CREATE OR REPLACE FUNCTION validar_rango_medicion(tipo_medicion_param text, valores_param jsonb)
RETURNS text AS $$
DECLARE
  valor_numerico numeric;
  estado_calculado text := 'OK';
BEGIN
  CASE tipo_medicion_param
    WHEN 'alambrico-t1' THEN
      valor_numerico := (valores_param->>'alambrico_t1')::numeric;
      IF valor_numerico < 45 OR valor_numerico > 75 THEN
        estado_calculado := 'FALLA';
      ELSIF valor_numerico < 50 OR valor_numerico > 70 THEN
        estado_calculado := 'ADVERTENCIA';
      END IF;
      
    WHEN 'alambrico-t2' THEN
      valor_numerico := (valores_param->>'alambrico_t2')::numeric;
      IF valor_numerico < 45 OR valor_numerico > 75 THEN
        estado_calculado := 'FALLA';
      ELSIF valor_numerico < 50 OR valor_numerico > 70 THEN
        estado_calculado := 'ADVERTENCIA';
      END IF;
      
    WHEN 'coaxial' THEN
      valor_numerico := (valores_param->>'coaxial')::numeric;
      IF valor_numerico < 45 OR valor_numerico > 75 THEN
        estado_calculado := 'FALLA';
      ELSIF valor_numerico < 50 OR valor_numerico > 70 THEN
        estado_calculado := 'ADVERTENCIA';
      END IF;
      
    WHEN 'fibra' THEN
      -- Verificar potencia TX
      IF valores_param ? 'potencia_tx' THEN
        valor_numerico := (valores_param->>'potencia_tx')::numeric;
        IF valor_numerico < -30 OR valor_numerico > -8 THEN
          estado_calculado := 'FALLA';
        ELSIF valor_numerico < -25 OR valor_numerico > -13 THEN
          estado_calculado := 'ADVERTENCIA';
        END IF;
      END IF;
      
      -- Verificar potencia RX
      IF valores_param ? 'potencia_rx' AND estado_calculado != 'FALLA' THEN
        valor_numerico := (valores_param->>'potencia_rx')::numeric;
        IF valor_numerico < -30 OR valor_numerico > -8 THEN
          estado_calculado := 'FALLA';
        ELSIF valor_numerico < -25 OR valor_numerico > -13 THEN
          estado_calculado := 'ADVERTENCIA';
        END IF;
      END IF;
      
    WHEN 'wifi' THEN
      valor_numerico := (valores_param->>'wifi')::numeric;
      IF valor_numerico < -80 OR valor_numerico > -30 THEN
        estado_calculado := 'FALLA';
      ELSIF valor_numerico < -75 OR valor_numerico > -35 THEN
        estado_calculado := 'ADVERTENCIA';
      END IF;
      
    WHEN 'certificacion' THEN
      CASE valores_param->>'certificacion'
        WHEN 'RECHAZADO' THEN estado_calculado := 'FALLA';
        WHEN 'APROBADO_CON_OBSERVACIONES' THEN estado_calculado := 'ADVERTENCIA';
        ELSE estado_calculado := 'OK';
      END CASE;
      
    ELSE
      estado_calculado := 'OK';
  END CASE;
  
  RETURN estado_calculado;
END;
$$ LANGUAGE plpgsql;

-- Trigger para validar avances antes de insertar/actualizar
CREATE OR REPLACE FUNCTION validar_avance_trigger()
RETURNS trigger AS $$
BEGIN
  -- Validar combinación torre-sector
  IF NOT validar_torre_sector(NEW.torre, NEW.sector) THEN
    RAISE EXCEPTION 'Combinación torre-sector inválida: Torre % no puede tener sector %', NEW.torre, NEW.sector;
  END IF;
  
  -- Validar que el porcentaje sea válido
  IF NEW.porcentaje < 0 OR NEW.porcentaje > 100 THEN
    RAISE EXCEPTION 'Porcentaje debe estar entre 0 y 100, recibido: %', NEW.porcentaje;
  END IF;
  
  -- Validar torre
  IF NEW.torre NOT IN ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN
    RAISE EXCEPTION 'Torre inválida: %', NEW.torre;
  END IF;
  
  -- Validar piso si se especifica
  IF NEW.piso IS NOT NULL AND NEW.piso NOT IN (1, 3) THEN
    RAISE EXCEPTION 'Piso inválido: %. Solo se permiten pisos 1 y 3', NEW.piso;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger de validación a avances
DROP TRIGGER IF EXISTS trigger_validar_avance ON avances;
CREATE TRIGGER trigger_validar_avance
  BEFORE INSERT OR UPDATE ON avances
  FOR EACH ROW EXECUTE FUNCTION validar_avance_trigger();

-- Trigger para calcular estado automático de mediciones
CREATE OR REPLACE FUNCTION calcular_estado_medicion_trigger()
RETURNS trigger AS $$
BEGIN
  -- Calcular estado automáticamente basado en valores
  NEW.estado := validar_rango_medicion(NEW.tipo_medicion, NEW.valores);
  
  -- Validar torre
  IF NEW.torre NOT IN ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J') THEN
    RAISE EXCEPTION 'Torre inválida: %', NEW.torre;
  END IF;
  
  -- Validar piso
  IF NEW.piso NOT IN (1, 3) THEN
    RAISE EXCEPTION 'Piso inválido: %. Solo se permiten pisos 1 y 3', NEW.piso;
  END IF;
  
  -- Validar tipo de medición
  IF NEW.tipo_medicion NOT IN ('alambrico-t1', 'alambrico-t2', 'coaxial', 'fibra', 'wifi', 'certificacion') THEN
    RAISE EXCEPTION 'Tipo de medición inválido: %', NEW.tipo_medicion;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar trigger de cálculo de estado a mediciones
DROP TRIGGER IF EXISTS trigger_calcular_estado_medicion ON mediciones;
CREATE TRIGGER trigger_calcular_estado_medicion
  BEFORE INSERT OR UPDATE ON mediciones
  FOR EACH ROW EXECUTE FUNCTION calcular_estado_medicion_trigger();

-- Función para generar reporte de progreso por fecha
CREATE OR REPLACE FUNCTION generar_reporte_progreso(fecha_desde date, fecha_hasta date)
RETURNS TABLE (
  fecha date,
  avances_registrados integer,
  mediciones_registradas integer,
  progreso_promedio numeric,
  torres_activas integer
) AS $$
BEGIN
  RETURN QUERY
  WITH fechas AS (
    SELECT generate_series(fecha_desde, fecha_hasta, '1 day'::interval)::date as fecha
  ),
  avances_por_fecha AS (
    SELECT 
      DATE(a.fecha) as fecha,
      COUNT(*) as avances_count,
      ROUND(AVG(a.porcentaje), 2) as progreso_avg,
      COUNT(DISTINCT a.torre) as torres_count
    FROM avances a
    WHERE a.deleted_at IS NULL 
    AND DATE(a.fecha) BETWEEN fecha_desde AND fecha_hasta
    GROUP BY DATE(a.fecha)
  ),
  mediciones_por_fecha AS (
    SELECT 
      DATE(m.fecha) as fecha,
      COUNT(*) as mediciones_count
    FROM mediciones m
    WHERE DATE(m.fecha) BETWEEN fecha_desde AND fecha_hasta
    GROUP BY DATE(m.fecha)
  )
  SELECT 
    f.fecha,
    COALESCE(a.avances_count, 0)::integer,
    COALESCE(m.mediciones_count, 0)::integer,
    COALESCE(a.progreso_avg, 0),
    COALESCE(a.torres_count, 0)::integer
  FROM fechas f
  LEFT JOIN avances_por_fecha a ON f.fecha = a.fecha
  LEFT JOIN mediciones_por_fecha m ON f.fecha = m.fecha
  ORDER BY f.fecha;
END;
$$ LANGUAGE plpgsql;

-- Función para validar integridad de datos
CREATE OR REPLACE FUNCTION validar_integridad_datos()
RETURNS TABLE (
  tabla text,
  problema text,
  cantidad integer,
  severidad text
) AS $$
BEGIN
  -- Avances sin usuario válido
  RETURN QUERY
  SELECT 
    'avances'::text,
    'Avances sin usuario válido'::text,
    COUNT(*)::integer,
    'ALTA'::text
  FROM avances a
  LEFT JOIN usuarios u ON a.usuario_id = u.id
  WHERE a.deleted_at IS NULL AND u.id IS NULL
  HAVING COUNT(*) > 0;
  
  -- Mediciones sin usuario válido
  RETURN QUERY
  SELECT 
    'mediciones'::text,
    'Mediciones sin usuario válido'::text,
    COUNT(*)::integer,
    'ALTA'::text
  FROM mediciones m
  LEFT JOIN usuarios u ON m.usuario_id = u.id
  WHERE u.id IS NULL
  HAVING COUNT(*) > 0;
  
  -- Avances con combinación torre-sector inválida
  RETURN QUERY
  SELECT 
    'avances'::text,
    'Combinaciones torre-sector inválidas'::text,
    COUNT(*)::integer,
    'MEDIA'::text
  FROM avances
  WHERE deleted_at IS NULL 
  AND torre IN ('C', 'H') 
  AND sector = 'Norte'
  HAVING COUNT(*) > 0;
  
  -- Mediciones con valores fuera de rango
  RETURN QUERY
  SELECT 
    'mediciones'::text,
    'Mediciones con valores extremos'::text,
    COUNT(*)::integer,
    'MEDIA'::text
  FROM mediciones
  WHERE estado = 'FALLA'
  HAVING COUNT(*) > 0;
  
  -- Usuarios sin actividad reciente
  RETURN QUERY
  SELECT 
    'usuarios'::text,
    'Usuarios sin actividad en 30 días'::text,
    COUNT(*)::integer,
    'BAJA'::text
  FROM usuarios
  WHERE activo = true 
  AND (ultimo_acceso IS NULL OR ultimo_acceso < NOW() - INTERVAL '30 days')
  HAVING COUNT(*) > 0;
END;
$$ LANGUAGE plpgsql;