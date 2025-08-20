/*
  # Crear tabla de configuración de aplicación

  1. Nueva Tabla
    - `app_config`
      - `id` (text, primary key, default 'app-config')
      - `last_sync` (timestamp)
      - `is_online` (boolean, default false)
      - `settings` (jsonb) - Configuraciones de la app
      - `created_at` (timestamp)
      - `updated_at` (timestamp)

  2. Seguridad
    - Enable RLS on `app_config` table
    - Add policies for configuration management
*/

CREATE TABLE IF NOT EXISTS app_config (
  id text PRIMARY KEY DEFAULT 'app-config',
  last_sync timestamptz,
  is_online boolean DEFAULT false,
  settings jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE app_config ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Usuarios pueden ver configuración"
  ON app_config
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Solo admins pueden actualizar configuración"
  ON app_config
  FOR UPDATE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE id::text = auth.uid()::text 
      AND rol = 'Admin'
    )
  );

CREATE POLICY "Sistema puede insertar configuración inicial"
  ON app_config
  FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- Trigger para updated_at
CREATE TRIGGER update_app_config_updated_at
  BEFORE UPDATE ON app_config
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Insertar configuración inicial
INSERT INTO app_config (id, settings) 
VALUES (
  'app-config', 
  '{
    "syncInterval": 30000,
    "autoSync": true,
    "compressionLevel": 6,
    "maxRetries": 3,
    "obraId": "los-encinos-001",
    "version": "1.0.0"
  }'::jsonb
) ON CONFLICT (id) DO NOTHING;