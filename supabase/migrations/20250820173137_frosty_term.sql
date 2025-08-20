/*
  # Crear vistas y funciones útiles

  1. Vistas
    - `vista_progreso_torres` - Progreso por torre
    - `vista_mediciones_resumen` - Resumen de mediciones
    - `vista_avances_recientes` - Avances recientes

  2. Funciones
    - `calcular_progreso_obra()` - Calcular progreso general
    - `obtener_estadisticas_torre(torre)` - Estadísticas por torre
    - `limpiar_cola_sync()` - Limpiar cola de sincronización
*/

-- Vista: Progreso por torres
CREATE OR REPLACE VIEW vista_progreso_torres AS
SELECT 
  torre,
  COUNT(*) as total_avances,
  AVG(porcentaje) as progreso_promedio,
  COUNT(DISTINCT ubicacion) as unidades_con_avance,
  MAX(fecha) as ultimo_avance,
  COUNT(CASE WHEN porcentaje = 100 THEN 1 END) as unidades_completadas
FROM avances 
WHERE deleted_at IS NULL
GROUP BY torre
ORDER BY torre;

-- Vista: Resumen de mediciones
CREATE OR REPLACE VIEW vista_mediciones_resumen AS
SELECT 
  torre,
  piso,
  tipo_medicion,
  COUNT(*) as total_mediciones,
  COUNT(CASE WHEN estado = 'OK' THEN 1 END) as mediciones_ok,
  COUNT(CASE WHEN estado = 'ADVERTENCIA' THEN 1 END) as mediciones_advertencia,
  COUNT(CASE WHEN estado = 'FALLA' THEN 1 END) as mediciones_falla,
  MAX(fecha) as ultima_medicion
FROM mediciones
GROUP BY torre, piso, tipo_medicion
ORDER BY torre, piso, tipo_medicion;

-- Vista: Avances recientes
CREATE OR REPLACE VIEW vista_avances_recientes AS
SELECT 
  a.id,
  a.fecha,
  a.torre,
  a.piso,
  a.sector,
  a.ubicacion,
  a.categoria,
  a.porcentaje,
  a.observaciones,
  u.nombre as usuario_nombre,
  u.rol as usuario_rol
FROM avances a
LEFT JOIN usuarios u ON a.usuario_id = u.id
WHERE a.deleted_at IS NULL
ORDER BY a.fecha DESC, a.created_at DESC
LIMIT 50;

-- Función: Calcular progreso general de la obra
CREATE OR REPLACE FUNCTION calcular_progreso_obra()
RETURNS TABLE (
  total_unidades integer,
  unidades_con_avance integer,
  progreso_promedio numeric,
  unidades_completadas integer,
  porcentaje_completado numeric
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    1247 as total_unidades, -- Total de unidades en Los Encinos
    COUNT(DISTINCT ubicacion)::integer as unidades_con_avance,
    ROUND(AVG(porcentaje), 2) as progreso_promedio,
    COUNT(CASE WHEN porcentaje = 100 THEN 1 END)::integer as unidades_completadas,
    ROUND((COUNT(CASE WHEN porcentaje = 100 THEN 1 END)::numeric / 1247) * 100, 2) as porcentaje_completado
  FROM avances 
  WHERE deleted_at IS NULL;
END;
$$ LANGUAGE plpgsql;

-- Función: Obtener estadísticas por torre
CREATE OR REPLACE FUNCTION obtener_estadisticas_torre(torre_param text)
RETURNS TABLE (
  torre text,
  total_avances integer,
  progreso_promedio numeric,
  unidades_con_avance integer,
  unidades_completadas integer,
  ultimo_avance timestamptz,
  mediciones_ok integer,
  mediciones_falla integer
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    torre_param as torre,
    COUNT(a.*)::integer as total_avances,
    ROUND(AVG(a.porcentaje), 2) as progreso_promedio,
    COUNT(DISTINCT a.ubicacion)::integer as unidades_con_avance,
    COUNT(CASE WHEN a.porcentaje = 100 THEN 1 END)::integer as unidades_completadas,
    MAX(a.fecha) as ultimo_avance,
    COUNT(CASE WHEN m.estado = 'OK' THEN 1 END)::integer as mediciones_ok,
    COUNT(CASE WHEN m.estado = 'FALLA' THEN 1 END)::integer as mediciones_falla
  FROM avances a
  LEFT JOIN mediciones m ON a.torre = m.torre
  WHERE a.torre = torre_param AND a.deleted_at IS NULL
  GROUP BY torre_param;
END;
$$ LANGUAGE plpgsql;

-- Función: Limpiar cola de sincronización
CREATE OR REPLACE FUNCTION limpiar_cola_sync()
RETURNS integer AS $$
DECLARE
  deleted_count integer;
BEGIN
  -- Eliminar items completados más antiguos de 7 días
  DELETE FROM sync_queue 
  WHERE status = 'completed' 
  AND created_at < NOW() - INTERVAL '7 days';
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  
  -- Resetear items fallidos con más de 24 horas
  UPDATE sync_queue 
  SET status = 'pending', attempts = 0, error = NULL
  WHERE status = 'failed' 
  AND last_attempt < NOW() - INTERVAL '24 hours';
  
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Función: Obtener dashboard data
CREATE OR REPLACE FUNCTION obtener_dashboard_data()
RETURNS json AS $$
DECLARE
  result json;
BEGIN
  SELECT json_build_object(
    'resumen_general', (
      SELECT json_build_object(
        'total_unidades', 1247,
        'unidades_completadas', COUNT(CASE WHEN porcentaje = 100 THEN 1 END),
        'porcentaje_general', ROUND(AVG(porcentaje), 2),
        'avances_hoy', COUNT(CASE WHEN DATE(fecha) = CURRENT_DATE THEN 1 END)
      )
      FROM avances WHERE deleted_at IS NULL
    ),
    'progreso_torres', (
      SELECT json_object_agg(torre, ROUND(AVG(porcentaje), 2))
      FROM avances 
      WHERE deleted_at IS NULL
      GROUP BY torre
    ),
    'mediciones_estado', (
      SELECT json_build_object(
        'ok', COUNT(CASE WHEN estado = 'OK' THEN 1 END),
        'advertencia', COUNT(CASE WHEN estado = 'ADVERTENCIA' THEN 1 END),
        'falla', COUNT(CASE WHEN estado = 'FALLA' THEN 1 END)
      )
      FROM mediciones
    )
  ) INTO result;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql;