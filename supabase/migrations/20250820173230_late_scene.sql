/*
  # Script de inicialización completa de Supabase para BDPA Los Encinos
  
  Este script debe ejecutarse después de crear el proyecto en Supabase
  para configurar toda la estructura de base de datos.
*/

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Ejecutar todas las migraciones en orden
\i migrations/create_usuarios_table.sql
\i migrations/create_avances_table.sql
\i migrations/create_mediciones_table.sql
\i migrations/create_sync_queue_table.sql
\i migrations/create_app_config_table.sql
\i migrations/create_storage_buckets.sql
\i migrations/create_views_and_functions.sql
\i migrations/create_rls_helper_functions.sql
\i migrations/insert_initial_data.sql

-- Mensaje de confirmación
DO $$
BEGIN
  RAISE NOTICE 'Base de datos BDPA Los Encinos configurada correctamente';
  RAISE NOTICE 'Total de tablas creadas: %', (
    SELECT COUNT(*) 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_type = 'BASE TABLE'
  );
  RAISE NOTICE 'Total de usuarios iniciales: %', (SELECT COUNT(*) FROM usuarios);
  RAISE NOTICE 'Configuración completada exitosamente';
END $$;