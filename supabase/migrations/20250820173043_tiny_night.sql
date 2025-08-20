/*
  # Crear tabla de usuarios

  1. Nueva Tabla
    - `usuarios`
      - `id` (uuid, primary key)
      - `username` (text, unique)
      - `email` (text, unique, optional)
      - `nombre` (text)
      - `rol` (text) - Admin, Supervisor, Tecnico, Ayudante
      - `activo` (boolean, default true)
      - `ultimo_acceso` (timestamp)
      - `created_at` (timestamp)
      - `updated_at` (timestamp)

  2. Seguridad
    - Enable RLS on `usuarios` table
    - Add policy for authenticated users to read all users
    - Add policy for users to update their own data
    - Add policy for admins to manage all users
*/

CREATE TABLE IF NOT EXISTS usuarios (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  username text UNIQUE NOT NULL,
  email text UNIQUE,
  nombre text NOT NULL,
  rol text NOT NULL CHECK (rol IN ('Admin', 'Supervisor', 'Tecnico', 'Ayudante')),
  activo boolean DEFAULT true,
  ultimo_acceso timestamptz,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Enable RLS
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Usuarios pueden ver todos los usuarios"
  ON usuarios
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Usuarios pueden actualizar su propio perfil"
  ON usuarios
  FOR UPDATE
  TO authenticated
  USING (auth.uid()::text = id::text);

CREATE POLICY "Solo admins pueden crear usuarios"
  ON usuarios
  FOR INSERT
  TO authenticated
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE id::text = auth.uid()::text 
      AND rol = 'Admin'
    )
  );

CREATE POLICY "Solo admins pueden eliminar usuarios"
  ON usuarios
  FOR DELETE
  TO authenticated
  USING (
    EXISTS (
      SELECT 1 FROM usuarios 
      WHERE id::text = auth.uid()::text 
      AND rol = 'Admin'
    )
  );

-- Trigger para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_usuarios_updated_at
  BEFORE UPDATE ON usuarios
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
CREATE INDEX IF NOT EXISTS idx_usuarios_rol ON usuarios(rol);
CREATE INDEX IF NOT EXISTS idx_usuarios_activo ON usuarios(activo);