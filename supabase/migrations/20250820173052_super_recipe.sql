/*
  # Crear tabla de avances

  1. Nueva Tabla
    - `avances`
      - `id` (uuid, primary key)
      - `obra_id` (text, default 'los-encinos-001')
      - `fecha` (timestamp)
      - `torre` (text) - A, B, C, D, E, F, G, H, I, J
      - `piso` (integer) - 1, 3
      - `sector` (text, optional) - Norte, Poniente, Oriente
      - `tipo_espacio` (text) - unidad, sotu, shaft, lateral, antena
      - `ubicacion` (text) - Identificador específico
      - `categoria` (text) - Categoría de trabajo
      - `porcentaje` (integer, 0-100)
      - `foto_path` (text, optional) - Ruta local
      - `foto_url` (text, optional) - URL en Storage
      - `observaciones` (text, optional)
      - `usuario_id` (uuid, foreign key)
      - `sync_status` (text, default 'synced')
      - `last_sync` (timestamp)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)
      - `deleted_at` (timestamp, optional) - Soft delete

  2. Seguridad
    - Enable RLS on `avances` table
    - Add policies for CRUD operations
    - Add indexes for performance
*/

CREATE TABLE IF NOT EXISTS avances (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  obra_id text DEFAULT 'los-encinos-001',
  fecha timestamptz NOT NULL,
  torre text NOT NULL CHECK (torre IN ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')),
  piso integer CHECK (piso IN (1, 3)),
  sector text CHECK (sector IN ('Norte', 'Poniente', 'Oriente')),
  tipo_espacio text NOT NULL CHECK (tipo_espacio IN ('unidad', 'sotu', 'shaft', 'lateral', 'antena')),
  ubicacion text NOT NULL,
  categoria text NOT NULL,
  porcentaje integer NOT NULL CHECK (porcentaje >= 0 AND porcentaje <= 100),
  foto_path text,
  foto_url text,
  observaciones text,
  usuario_id uuid REFERENCES usuarios(id) ON DELETE SET NULL,
  sync_status text DEFAULT 'synced' CHECK (sync_status IN ('local', 'syncing', 'synced', 'conflict')),
  last_sync timestamptz,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now(),
  deleted_at timestamptz
);

-- Enable RLS
ALTER TABLE avances ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Usuarios pueden ver todos los avances no eliminados"
  ON avances
  FOR SELECT
  TO authenticated
  USING (deleted_at IS NULL);

CREATE POLICY "Usuarios pueden crear avances"
  ON avances
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "Usuarios pueden actualizar avances"
  ON avances
  FOR UPDATE
  TO authenticated
  USING (auth.uid() IS NOT NULL);

CREATE POLICY "Solo supervisores y admins pueden eliminar avances"
  ON avances
  FOR DELETE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE id::text = auth.uid()::text 
      AND rol IN ('Admin', 'Supervisor')
    )
  );

-- Trigger para updated_at
CREATE TRIGGER update_avances_updated_at
  BEFORE UPDATE ON avances
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_avances_obra_id ON avances(obra_id);
CREATE INDEX IF NOT EXISTS idx_avances_fecha ON avances(fecha);
CREATE INDEX IF NOT EXISTS idx_avances_torre_piso ON avances(torre, piso);
CREATE INDEX IF NOT EXISTS idx_avances_ubicacion ON avances(ubicacion);
CREATE INDEX IF NOT EXISTS idx_avances_usuario_id ON avances(usuario_id);
CREATE INDEX IF NOT EXISTS idx_avances_sync_status ON avances(sync_status);
CREATE INDEX IF NOT EXISTS idx_avances_deleted_at ON avances(deleted_at);

-- Índice compuesto para búsquedas comunes
CREATE INDEX IF NOT EXISTS idx_avances_torre_piso_sector ON avances(torre, piso, sector) WHERE deleted_at IS NULL;