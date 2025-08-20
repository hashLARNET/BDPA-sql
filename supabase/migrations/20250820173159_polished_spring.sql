/*
  # Insertar datos iniciales

  1. Usuario administrador inicial
  2. Configuración inicial de la aplicación
  3. Datos de ejemplo para desarrollo (opcional)
*/

-- Insertar usuario administrador inicial
INSERT INTO usuarios (id, username, email, nombre, rol, activo)
VALUES (
  gen_random_uuid(),
  'admin',
  'admin@losencinos.com',
  'Administrador Sistema',
  'Admin',
  true
) ON CONFLICT (username) DO NOTHING;

-- Insertar usuarios de ejemplo para desarrollo
INSERT INTO usuarios (username, email, nombre, rol, activo) VALUES
  ('supervisor1', 'supervisor@losencinos.com', 'Juan Supervisor', 'Supervisor', true),
  ('tecnico1', 'tecnico1@losencinos.com', 'María Técnico', 'Tecnico', true),
  ('tecnico2', 'tecnico2@losencinos.com', 'Carlos Técnico', 'Tecnico', true),
  ('ayudante1', 'ayudante@losencinos.com', 'Pedro Ayudante', 'Ayudante', true)
ON CONFLICT (username) DO NOTHING;

-- Insertar algunos avances de ejemplo para desarrollo
DO $$
DECLARE
  admin_id uuid;
  tecnico_id uuid;
BEGIN
  -- Obtener IDs de usuarios
  SELECT id INTO admin_id FROM usuarios WHERE username = 'admin' LIMIT 1;
  SELECT id INTO tecnico_id FROM usuarios WHERE username = 'tecnico1' LIMIT 1;
  
  -- Insertar avances de ejemplo si los usuarios existen
  IF admin_id IS NOT NULL AND tecnico_id IS NOT NULL THEN
    INSERT INTO avances (
      fecha, torre, piso, sector, tipo_espacio, ubicacion, categoria, 
      porcentaje, observaciones, usuario_id
    ) VALUES
      (NOW() - INTERVAL '1 day', 'A', 1, 'Oriente', 'unidad', 'A101', 'Cableado alámbrico T1', 100, 'Completado sin observaciones', tecnico_id),
      (NOW() - INTERVAL '1 day', 'A', 1, 'Oriente', 'unidad', 'A102', 'Cableado alámbrico T1', 75, 'En progreso', tecnico_id),
      (NOW() - INTERVAL '2 hours', 'A', 1, 'Oriente', 'unidad', 'A103', 'Instalación PAU', 50, 'Iniciado hoy', admin_id),
      (NOW() - INTERVAL '3 hours', 'B', 1, 'Norte', 'unidad', 'B106', 'Cableado alámbrico T1', 100, 'Completado', tecnico_id),
      (NOW() - INTERVAL '4 hours', 'B', 1, 'Norte', 'unidad', 'B107', 'Fibra Óptica', 25, 'Iniciado', admin_id);
  END IF;
END $$;

-- Insertar mediciones de ejemplo
DO $$
DECLARE
  admin_id uuid;
  tecnico_id uuid;
BEGIN
  -- Obtener IDs de usuarios
  SELECT id INTO admin_id FROM usuarios WHERE username = 'admin' LIMIT 1;
  SELECT id INTO tecnico_id FROM usuarios WHERE username = 'tecnico1' LIMIT 1;
  
  -- Insertar mediciones de ejemplo si los usuarios existen
  IF admin_id IS NOT NULL AND tecnico_id IS NOT NULL THEN
    INSERT INTO mediciones (
      fecha, torre, piso, identificador, tipo_medicion, valores, estado, usuario_id, observaciones
    ) VALUES
      (NOW() - INTERVAL '1 day', 'A', 1, 'A101', 'alambrico-t1', '{"alambricoT1": 65.5}', 'OK', tecnico_id, 'Medición dentro de rango'),
      (NOW() - INTERVAL '2 hours', 'A', 1, 'A102', 'coaxial', '{"coaxial": 72.3}', 'OK', admin_id, 'Nivel óptimo'),
      (NOW() - INTERVAL '3 hours', 'B', 1, 'B106', 'wifi', '{"wifi": -45}', 'OK', tecnico_id, 'Señal excelente'),
      (NOW() - INTERVAL '4 hours', 'B', 1, 'B107', 'fibra', '{"potenciaTx": -12.5, "potenciaRx": -15.2, "atenuacion": 0.3}', 'OK', admin_id, 'Fibra en perfecto estado'),
      (NOW() - INTERVAL '5 hours', 'A', 1, 'A103', 'alambrico-t2', '{"alambricoT2": 78.5}', 'ADVERTENCIA', tecnico_id, 'Nivel alto, revisar');
  END IF;
END $$;

-- Actualizar configuración con datos específicos de Los Encinos
UPDATE app_config 
SET settings = jsonb_set(
  settings,
  '{obra}',
  '{
    "nombre": "Los Encinos",
    "direccion": "Santiago, Chile",
    "totalUnidades": 1247,
    "torres": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
    "pisos": [1, 3],
    "sectores": ["Norte", "Poniente", "Oriente"],
    "torresEspeciales": {
      "C": {"sectores": ["Poniente", "Oriente"]},
      "H": {"sectores": ["Poniente", "Oriente"]}
    }
  }'::jsonb
)
WHERE id = 'app-config';