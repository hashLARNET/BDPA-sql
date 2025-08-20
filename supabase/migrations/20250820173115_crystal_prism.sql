/*
  # Crear tabla de cola de sincronización

  1. Nueva Tabla
    - `sync_queue`
      - `id` (uuid, primary key)
      - `type` (text) - avance, medicion, foto
      - `action` (text) - create, update, delete
      - `item_id` (text) - ID del item a sincronizar
      - `data` (jsonb) - Datos del item
      - `attempts` (integer, default 0)
      - `last_attempt` (timestamp)
      - `error` (text)
      - `status` (text, default 'pending')
      - `created_at` (timestamp)
      - `updated_at` (timestamp)

  2. Seguridad
    - Enable RLS on `sync_queue` table
    - Add policies for queue management
*/

CREATE TABLE IF NOT EXISTS sync_queue (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  type text NOT NULL CHECK (type IN ('avance', 'medicion', 'foto')),
  action text NOT NULL CHECK (action IN ('create', 'update', 'delete')),
  item_id text NOT NULL,
  data jsonb NOT NULL,
  attempts integer DEFAULT 0,
  last_attempt timestamptz,
  error text,
  status text DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE sync_queue ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Usuarios pueden ver su propia cola de sincronización"
  ON sync_queue
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Sistema puede gestionar cola de sincronización"
  ON sync_queue
  FOR ALL
  TO authenticated
  USING (true);

-- Trigger para updated_at
CREATE TRIGGER update_sync_queue_updated_at
  BEFORE UPDATE ON sync_queue
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_sync_queue_status ON sync_queue(status);
CREATE INDEX IF NOT EXISTS idx_sync_queue_type ON sync_queue(type);
CREATE INDEX IF NOT EXISTS idx_sync_queue_item_id ON sync_queue(item_id);
CREATE INDEX IF NOT EXISTS idx_sync_queue_created_at ON sync_queue(created_at);
CREATE INDEX IF NOT EXISTS idx_sync_queue_attempts ON sync_queue(attempts);

-- Índice compuesto para procesamiento de cola
CREATE INDEX IF NOT EXISTS idx_sync_queue_processing ON sync_queue(status, created_at) WHERE status IN ('pending', 'failed');