/*
  # Optimizaciones de rendimiento y índices adicionales

  1. Índices compuestos para consultas frecuentes
  2. Optimización de vistas existentes
  3. Funciones de estadísticas mejoradas
  4. Configuración de autovacuum
*/

-- Índices compuestos para consultas frecuentes en avances
CREATE INDEX IF NOT EXISTS idx_avances_dashboard_stats 
  ON avances(obra_id, deleted_at, porcentaje) 
  WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_avances_torre_fecha 
  ON avances(torre, fecha DESC) 
  WHERE deleted_at IS NULL;

CREATE INDEX IF NOT EXISTS idx_avances_usuario_fecha 
  ON avances(usuario_id, fecha DESC) 
  WHERE deleted_at IS NULL;

-- Índices compuestos para mediciones
CREATE INDEX IF NOT EXISTS idx_mediciones_dashboard_stats 
  ON mediciones(obra_id, estado, fecha DESC);

CREATE INDEX IF NOT EXISTS idx_mediciones_torre_tipo 
  ON mediciones(torre, tipo_medicion, estado);

CREATE INDEX IF NOT EXISTS idx_mediciones_usuario_fecha 
  ON mediciones(usuario_id, fecha DESC);

-- Optimizar vista de progreso por torres
CREATE OR REPLACE VIEW vista_progreso_torres AS
SELECT 
  torre,
  COUNT(*) as total_avances,
  ROUND(AVG(porcentaje), 2) as progreso_promedio,
  COUNT(DISTINCT ubicacion) as unidades_con_avance,
  COUNT(CASE WHEN porcentaje = 100 THEN 1 END) as unidades_completadas,
  MAX(fecha) as ultimo_avance,
  -- Agregar estadísticas de mediciones
  COALESCE(m.mediciones_ok, 0) as mediciones_ok,
  COALESCE(m.mediciones_falla, 0) as mediciones_falla
FROM avances a
LEFT JOIN (
  SELECT 
    torre,
    COUNT(CASE WHEN estado = 'OK' THEN 1 END) as mediciones_ok,
    COUNT(CASE WHEN estado = 'FALLA' THEN 1 END) as mediciones_falla
  FROM mediciones
  GROUP BY torre
) m ON a.torre = m.torre
WHERE a.deleted_at IS NULL
GROUP BY torre, m.mediciones_ok, m.mediciones_falla
ORDER BY torre;

-- Función optimizada para dashboard
CREATE OR REPLACE FUNCTION obtener_dashboard_data_optimizado()
RETURNS json AS $$
DECLARE
  result json;
  total_unidades_const integer := 1247;
BEGIN
  WITH stats AS (
    SELECT 
      COUNT(*) as total_avances,
      COUNT(CASE WHEN porcentaje = 100 THEN 1 END) as unidades_completadas,
      ROUND(AVG(porcentaje), 2) as progreso_promedio,
      COUNT(CASE WHEN DATE(fecha) = CURRENT_DATE THEN 1 END) as avances_hoy,
      MAX(fecha) as ultimo_avance
    FROM avances 
    WHERE deleted_at IS NULL
  ),
  mediciones_stats AS (
    SELECT 
      COUNT(CASE WHEN estado = 'OK' THEN 1 END) as mediciones_ok,
      COUNT(CASE WHEN estado = 'ADVERTENCIA' THEN 1 END) as mediciones_advertencia,
      COUNT(CASE WHEN estado = 'FALLA' THEN 1 END) as mediciones_falla,
      COUNT(CASE WHEN DATE(fecha) = CURRENT_DATE THEN 1 END) as mediciones_hoy,
      MAX(fecha) as ultima_medicion
    FROM mediciones
  ),
  torres_stats AS (
    SELECT json_object_agg(
      torre, 
      json_build_object(
        'progreso_promedio', ROUND(AVG(porcentaje), 2),
        'total_avances', COUNT(*),
        'unidades_completadas', COUNT(CASE WHEN porcentaje = 100 THEN 1 END),
        'ultimo_avance', MAX(fecha)
      )
    ) as torres_data
    FROM avances 
    WHERE deleted_at IS NULL
    GROUP BY torre
  )
  SELECT json_build_object(
    'resumen_general', json_build_object(
      'total_unidades', total_unidades_const,
      'unidades_completadas', s.unidades_completadas,
      'porcentaje_general', ROUND((s.unidades_completadas::numeric / total_unidades_const) * 100, 2),
      'avances_hoy', s.avances_hoy,
      'mediciones_hoy', ms.mediciones_hoy,
      'alertas_pendientes', ms.mediciones_falla,
      'ultimo_avance', s.ultimo_avance,
      'ultima_medicion', ms.ultima_medicion
    ),
    'progreso_torres', ts.torres_data,
    'mediciones_estado', json_build_object(
      'ok', ms.mediciones_ok,
      'advertencia', ms.mediciones_advertencia,
      'falla', ms.mediciones_falla,
      'total', ms.mediciones_ok + ms.mediciones_advertencia + ms.mediciones_falla
    )
  ) INTO result
  FROM stats s, mediciones_stats ms, torres_stats ts;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener actividad reciente optimizada
CREATE OR REPLACE FUNCTION obtener_actividad_reciente(limite integer DEFAULT 10)
RETURNS json AS $$
DECLARE
  result json;
BEGIN
  WITH actividad AS (
    -- Avances recientes
    SELECT 
      'avance' as tipo,
      a.id::text,
      a.fecha,
      CONCAT('Avance ', a.porcentaje, '% en ', a.ubicacion, ' - ', a.categoria) as descripcion,
      u.nombre as usuario,
      a.torre
    FROM avances a
    LEFT JOIN usuarios u ON a.usuario_id = u.id
    WHERE a.deleted_at IS NULL
    
    UNION ALL
    
    -- Mediciones recientes
    SELECT 
      'medicion' as tipo,
      m.id::text,
      m.fecha,
      CONCAT('Medición ', m.tipo_medicion, ' en ', m.identificador, ' - ', m.estado) as descripcion,
      u.nombre as usuario,
      m.torre
    FROM mediciones m
    LEFT JOIN usuarios u ON m.usuario_id = u.id
    
    ORDER BY fecha DESC
    LIMIT limite
  )
  SELECT json_agg(
    json_build_object(
      'tipo', tipo,
      'id', id,
      'fecha', fecha,
      'descripcion', descripcion,
      'usuario', COALESCE(usuario, 'Usuario desconocido'),
      'torre', torre
    )
  ) INTO result
  FROM actividad;
  
  RETURN COALESCE(result, '[]'::json);
END;
$$ LANGUAGE plpgsql;

-- Función para estadísticas de usuario
CREATE OR REPLACE FUNCTION obtener_estadisticas_usuario(user_id_param uuid)
RETURNS json AS $$
DECLARE
  result json;
BEGIN
  WITH user_stats AS (
    SELECT 
      COUNT(CASE WHEN a.id IS NOT NULL THEN 1 END) as total_avances,
      COUNT(CASE WHEN m.id IS NOT NULL THEN 1 END) as total_mediciones,
      COUNT(CASE WHEN a.porcentaje = 100 THEN 1 END) as avances_completados,
      COUNT(CASE WHEN m.estado = 'OK' THEN 1 END) as mediciones_ok,
      MAX(GREATEST(a.fecha, m.fecha)) as ultima_actividad
    FROM usuarios u
    LEFT JOIN avances a ON u.id = a.usuario_id AND a.deleted_at IS NULL
    LEFT JOIN mediciones m ON u.id = m.usuario_id
    WHERE u.id = user_id_param
  )
  SELECT json_build_object(
    'total_avances', total_avances,
    'total_mediciones', total_mediciones,
    'avances_completados', avances_completados,
    'mediciones_ok', mediciones_ok,
    'ultima_actividad', ultima_actividad
  ) INTO result
  FROM user_stats;
  
  RETURN COALESCE(result, '{}'::json);
END;
$$ LANGUAGE plpgsql;

-- Configurar autovacuum para tablas principales
ALTER TABLE usuarios SET (
  autovacuum_vacuum_scale_factor = 0.1,
  autovacuum_analyze_scale_factor = 0.05
);

ALTER TABLE avances SET (
  autovacuum_vacuum_scale_factor = 0.1,
  autovacuum_analyze_scale_factor = 0.05
);

ALTER TABLE mediciones SET (
  autovacuum_vacuum_scale_factor = 0.1,
  autovacuum_analyze_scale_factor = 0.05
);

-- Función de mantenimiento general
CREATE OR REPLACE FUNCTION ejecutar_mantenimiento_db()
RETURNS json AS $$
DECLARE
  result json;
  auditoria_limpiada integer;
  auth_logs_limpiados integer;
  sync_queue_limpiada integer;
BEGIN
  -- Ejecutar tareas de limpieza
  SELECT limpiar_auditoria_antigua() INTO auditoria_limpiada;
  SELECT limpiar_auth_logs_antiguos() INTO auth_logs_limpiados;
  SELECT limpiar_cola_sync() INTO sync_queue_limpiada;
  
  -- Actualizar estadísticas de tablas
  ANALYZE usuarios;
  ANALYZE avances;
  ANALYZE mediciones;
  
  SELECT json_build_object(
    'timestamp', NOW(),
    'auditoria_limpiada', auditoria_limpiada,
    'auth_logs_limpiados', auth_logs_limpiados,
    'sync_queue_limpiada', sync_queue_limpiada,
    'estadisticas_actualizadas', true
  ) INTO result;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;