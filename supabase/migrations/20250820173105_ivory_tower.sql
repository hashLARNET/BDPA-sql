/*
  # Crear tabla de mediciones

  1. Nueva Tabla
    - `mediciones`
      - `id` (uuid, primary key)
      - `obra_id` (text, default 'los-encinos-001')
      - `fecha` (timestamp)
      - `torre` (text) - A, B, C, D, E, F, G, H, I, J
      - `piso` (integer) - 1, 3
      - `identificador` (text) - Unidad específica
      - `tipo_medicion` (text) - Tipo de medición
      - `valores` (jsonb) - Valores de medición
      - `estado` (text) - OK, ADVERTENCIA, FALLA
      - `usuario_id` (uuid, foreign key)
      - `observaciones` (text, optional)
      - `sync_status` (text, default 'synced')
      - `created_at` (timestamp)
      - `updated_at` (timestamp)

  2. Seguridad
    - Enable RLS on `mediciones` table
    - Add policies for CRUD operations
    - Add indexes for performance
*/

CREATE TABLE IF NOT EXISTS mediciones (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  obra_id text DEFAULT 'los-encinos-001',
  fecha timestamptz NOT NULL,
  torre text NOT NULL CHECK (torre IN ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J')),
  piso integer NOT NULL CHECK (piso IN (1, 3)),
  identificador text NOT NULL,
  tipo_medicion text NOT NULL CHECK (tipo_medicion IN ('alambrico-t1', 'alambrico-t2', 'coaxial', 'fibra', 'wifi', 'certificacion')),
  valores jsonb NOT NULL,
  estado text NOT NULL CHECK (estado IN ('OK', 'ADVERTENCIA', 'FALLA')),
  usuario_id uuid REFERENCES usuarios(id) ON DELETE SET NULL,
  observaciones text,
  sync_status text DEFAULT 'synced' CHECK (sync_status IN ('local', 'synced')),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE mediciones ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Usuarios pueden ver todas las mediciones"
  ON mediciones
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Usuarios pueden crear mediciones"
  ON mediciones
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "Usuarios pueden actualizar mediciones"
  ON mediciones
  FOR UPDATE
  TO authenticated
  USING (auth.uid() IS NOT NULL);

CREATE POLICY "Solo supervisores y admins pueden eliminar mediciones"
  ON mediciones
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
CREATE TRIGGER update_mediciones_updated_at
  BEFORE UPDATE ON mediciones
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_mediciones_obra_id ON mediciones(obra_id);
CREATE INDEX IF NOT EXISTS idx_mediciones_fecha ON mediciones(fecha);
CREATE INDEX IF NOT EXISTS idx_mediciones_torre_piso ON mediciones(torre, piso);
CREATE INDEX IF NOT EXISTS idx_mediciones_identificador ON mediciones(identificador);
CREATE INDEX IF NOT EXISTS idx_mediciones_tipo ON mediciones(tipo_medicion);
CREATE INDEX IF NOT EXISTS idx_mediciones_estado ON mediciones(estado);
CREATE INDEX IF NOT EXISTS idx_mediciones_usuario_id ON mediciones(usuario_id);
CREATE INDEX IF NOT EXISTS idx_mediciones_sync_status ON mediciones(sync_status);

-- Índice GIN para búsquedas en JSONB
CREATE INDEX IF NOT EXISTS idx_mediciones_valores_gin ON mediciones USING GIN (valores);

-- Índice compuesto para búsquedas comunes
CREATE INDEX IF NOT EXISTS idx_mediciones_torre_piso_identificador ON mediciones(torre, piso, identificador);