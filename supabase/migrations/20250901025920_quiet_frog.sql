/*
  # Funciones de backup y restauración

  1. Funciones de exportación
    - Exportar datos de avances
    - Exportar datos de mediciones
    - Exportar configuración

  2. Funciones de importación
    - Importar datos desde JSON
    - Validar datos importados

  3. Funciones de backup
    - Crear backup completo
    - Restaurar desde backup
*/

-- Función para exportar avances a JSON
CREATE OR REPLACE FUNCTION exportar_avances(fecha_desde date DEFAULT NULL, fecha_hasta date DEFAULT NULL)
RETURNS json AS $$
DECLARE
  result json;
BEGIN
  WITH avances_export AS (
    SELECT 
      a.*,
      u.username as usuario_username,
      u.nombre as usuario_nombre,
      u.rol as usuario_rol
    FROM avances a
    LEFT JOIN usuarios u ON a.usuario_id = u.id
    WHERE a.deleted_at IS NULL
    AND (fecha_desde IS NULL OR DATE(a.fecha) >= fecha_desde)
    AND (fecha_hasta IS NULL OR DATE(a.fecha) <= fecha_hasta)
    ORDER BY a.fecha DESC
  )
  SELECT json_build_object(
    'metadata', json_build_object(
      'exported_at', NOW(),
      'total_records', COUNT(*),
      'fecha_desde', fecha_desde,
      'fecha_hasta', fecha_hasta,
      'version', '1.0.0'
    ),
    'data', json_agg(row_to_json(avances_export))
  ) INTO result
  FROM avances_export;
  
  RETURN COALESCE(result, '{"metadata": {"total_records": 0}, "data": []}'::json);
END;
$$ LANGUAGE plpgsql;

-- Función para exportar mediciones a JSON
CREATE OR REPLACE FUNCTION exportar_mediciones(fecha_desde date DEFAULT NULL, fecha_hasta date DEFAULT NULL)
RETURNS json AS $$
DECLARE
  result json;
BEGIN
  WITH mediciones_export AS (
    SELECT 
      m.*,
      u.username as usuario_username,
      u.nombre as usuario_nombre,
      u.rol as usuario_rol
    FROM mediciones m
    LEFT JOIN usuarios u ON m.usuario_id = u.id
    WHERE (fecha_desde IS NULL OR DATE(m.fecha) >= fecha_desde)
    AND (fecha_hasta IS NULL OR DATE(m.fecha) <= fecha_hasta)
    ORDER BY m.fecha DESC
  )
  SELECT json_build_object(
    'metadata', json_build_object(
      'exported_at', NOW(),
      'total_records', COUNT(*),
      'fecha_desde', fecha_desde,
      'fecha_hasta', fecha_hasta,
      'version', '1.0.0'
    ),
    'data', json_agg(row_to_json(mediciones_export))
  ) INTO result
  FROM mediciones_export;
  
  RETURN COALESCE(result, '{"metadata": {"total_records": 0}, "data": []}'::json);
END;
$$ LANGUAGE plpgsql;

-- Función para crear backup completo
CREATE OR REPLACE FUNCTION crear_backup_completo()
RETURNS json AS $$
DECLARE
  result json;
BEGIN
  SELECT json_build_object(
    'metadata', json_build_object(
      'backup_created_at', NOW(),
      'version', '1.0.0',
      'obra_id', 'los-encinos-001'
    ),
    'usuarios', (
      SELECT json_agg(
        json_build_object(
          'id', id,
          'username', username,
          'email', email,
          'nombre', nombre,
          'rol', rol,
          'activo', activo,
          'created_at', created_at
        )
      )
      FROM usuarios
    ),
    'avances', (
      SELECT json_agg(row_to_json(a))
      FROM (
        SELECT * FROM avances WHERE deleted_at IS NULL ORDER BY fecha DESC
      ) a
    ),
    'mediciones', (
      SELECT json_agg(row_to_json(m))
      FROM (
        SELECT * FROM mediciones ORDER BY fecha DESC
      ) m
    ),
    'configuracion', (
      SELECT row_to_json(ac) FROM app_config ac WHERE id = 'app-config'
    )
  ) INTO result;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener estadísticas de backup
CREATE OR REPLACE FUNCTION obtener_estadisticas_backup()
RETURNS json AS $$
DECLARE
  result json;
BEGIN
  SELECT json_build_object(
    'usuarios', json_build_object(
      'total', (SELECT COUNT(*) FROM usuarios),
      'activos', (SELECT COUNT(*) FROM usuarios WHERE activo = true),
      'por_rol', (
        SELECT json_object_agg(rol, count)
        FROM (
          SELECT rol, COUNT(*) as count 
          FROM usuarios 
          WHERE activo = true 
          GROUP BY rol
        ) roles
      )
    ),
    'avances', json_build_object(
      'total', (SELECT COUNT(*) FROM avances WHERE deleted_at IS NULL),
      'completados', (SELECT COUNT(*) FROM avances WHERE deleted_at IS NULL AND porcentaje = 100),
      'por_torre', (
        SELECT json_object_agg(torre, count)
        FROM (
          SELECT torre, COUNT(*) as count 
          FROM avances 
          WHERE deleted_at IS NULL 
          GROUP BY torre
        ) torres
      ),
      'ultimo_mes', (
        SELECT COUNT(*) 
        FROM avances 
        WHERE deleted_at IS NULL 
        AND fecha >= NOW() - INTERVAL '30 days'
      )
    ),
    'mediciones', json_build_object(
      'total', (SELECT COUNT(*) FROM mediciones),
      'por_estado', (
        SELECT json_object_agg(estado, count)
        FROM (
          SELECT estado, COUNT(*) as count 
          FROM mediciones 
          GROUP BY estado
        ) estados
      ),
      'por_tipo', (
        SELECT json_object_agg(tipo_medicion, count)
        FROM (
          SELECT tipo_medicion, COUNT(*) as count 
          FROM mediciones 
          GROUP BY tipo_medicion
        ) tipos
      ),
      'ultimo_mes', (
        SELECT COUNT(*) 
        FROM mediciones 
        WHERE fecha >= NOW() - INTERVAL '30 days'
      )
    ),
    'storage', json_build_object(
      'buckets_configurados', (
        SELECT COUNT(*) 
        FROM storage.buckets 
        WHERE name IN ('avances-fotos', 'mediciones-docs')
      )
    )
  ) INTO result;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Función para validar datos antes de importar
CREATE OR REPLACE FUNCTION validar_datos_importacion(datos_json json)
RETURNS TABLE (
  tabla text,
  registro_id text,
  campo text,
  error text,
  severidad text
) AS $$
DECLARE
  avance_record json;
  medicion_record json;
BEGIN
  -- Validar avances
  FOR avance_record IN SELECT json_array_elements(datos_json->'avances')
  LOOP
    -- Validar torre
    IF NOT (avance_record->>'torre' IN ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')) THEN
      RETURN QUERY SELECT 
        'avances'::text,
        avance_record->>'id',
        'torre'::text,
        'Torre inválida: ' || (avance_record->>'torre'),
        'ALTA'::text;
    END IF;
    
    -- Validar porcentaje
    IF (avance_record->>'porcentaje')::integer < 0 OR (avance_record->>'porcentaje')::integer > 100 THEN
      RETURN QUERY SELECT 
        'avances'::text,
        avance_record->>'id',
        'porcentaje'::text,
        'Porcentaje fuera de rango: ' || (avance_record->>'porcentaje'),
        'ALTA'::text;
    END IF;
    
    -- Validar combinación torre-sector
    IF NOT validar_torre_sector(avance_record->>'torre', avance_record->>'sector') THEN
      RETURN QUERY SELECT 
        'avances'::text,
        avance_record->>'id',
        'sector'::text,
        'Combinación torre-sector inválida',
        'MEDIA'::text;
    END IF;
  END LOOP;
  
  -- Validar mediciones
  FOR medicion_record IN SELECT json_array_elements(datos_json->'mediciones')
  LOOP
    -- Validar torre
    IF NOT (medicion_record->>'torre' IN ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')) THEN
      RETURN QUERY SELECT 
        'mediciones'::text,
        medicion_record->>'id',
        'torre'::text,
        'Torre inválida: ' || (medicion_record->>'torre'),
        'ALTA'::text;
    END IF;
    
    -- Validar tipo de medición
    IF NOT (medicion_record->>'tipo_medicion' IN ('alambrico-t1', 'alambrico-t2', 'coaxial', 'fibra', 'wifi', 'certificacion')) THEN
      RETURN QUERY SELECT 
        'mediciones'::text,
        medicion_record->>'id',
        'tipo_medicion'::text,
        'Tipo de medición inválido: ' || (medicion_record->>'tipo_medicion'),
        'ALTA'::text;
    END IF;
  END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Función para limpiar datos huérfanos
CREATE OR REPLACE FUNCTION limpiar_datos_huerfanos()
RETURNS json AS $$
DECLARE
  result json;
  avances_limpiados integer;
  mediciones_limpiadas integer;
BEGIN
  -- Limpiar avances sin usuario válido (soft delete)
  UPDATE avances 
  SET deleted_at = NOW()
  WHERE deleted_at IS NULL 
  AND usuario_id NOT IN (SELECT id FROM usuarios WHERE activo = true);
  
  GET DIAGNOSTICS avances_limpiados = ROW_COUNT;
  
  -- Limpiar mediciones sin usuario válido
  DELETE FROM mediciones 
  WHERE usuario_id NOT IN (SELECT id FROM usuarios WHERE activo = true);
  
  GET DIAGNOSTICS mediciones_limpiadas = ROW_COUNT;
  
  SELECT json_build_object(
    'timestamp', NOW(),
    'avances_limpiados', avances_limpiados,
    'mediciones_limpiadas', mediciones_limpiadas,
    'mensaje', 'Limpieza de datos huérfanos completada'
  ) INTO result;
  
  RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;