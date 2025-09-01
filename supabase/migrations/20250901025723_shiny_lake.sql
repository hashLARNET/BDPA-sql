/*
  # Agregar seguridad de contraseñas a la tabla usuarios

  1. Cambios en la tabla usuarios
    - Agregar columna `password_hash` para almacenar contraseñas hasheadas
    - Agregar columna `password_reset_token` para recuperación de contraseñas
    - Agregar columna `password_reset_expires` para expiración de tokens

  2. Funciones de autenticación
    - `hash_password(password)` - Hashear contraseña
    - `verify_password(password, hash)` - Verificar contraseña
    - `generate_reset_token()` - Generar token de recuperación

  3. Seguridad
    - Actualizar políticas RLS para incluir autenticación por contraseña
    - Agregar función para cambio de contraseña
    - Agregar auditoría de intentos de login
*/

-- Agregar columnas de seguridad a la tabla usuarios
DO $$
BEGIN
  -- Agregar password_hash si no existe
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'usuarios' AND column_name = 'password_hash'
  ) THEN
    ALTER TABLE usuarios ADD COLUMN password_hash text;
  END IF;

  -- Agregar password_reset_token si no existe
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'usuarios' AND column_name = 'password_reset_token'
  ) THEN
    ALTER TABLE usuarios ADD COLUMN password_reset_token text;
  END IF;

  -- Agregar password_reset_expires si no existe
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'usuarios' AND column_name = 'password_reset_expires'
  ) THEN
    ALTER TABLE usuarios ADD COLUMN password_reset_expires timestamptz;
  END IF;

  -- Agregar intentos_login_fallidos si no existe
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'usuarios' AND column_name = 'intentos_login_fallidos'
  ) THEN
    ALTER TABLE usuarios ADD COLUMN intentos_login_fallidos integer DEFAULT 0;
  END IF;

  -- Agregar bloqueado_hasta si no existe
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'usuarios' AND column_name = 'bloqueado_hasta'
  ) THEN
    ALTER TABLE usuarios ADD COLUMN bloqueado_hasta timestamptz;
  END IF;
END $$;

-- Función para hashear contraseñas usando pgcrypto
CREATE OR REPLACE FUNCTION hash_password(password text)
RETURNS text AS $$
BEGIN
  RETURN crypt(password, gen_salt('bf', 12));
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para verificar contraseñas
CREATE OR REPLACE FUNCTION verify_password(password text, hash text)
RETURNS boolean AS $$
BEGIN
  RETURN hash = crypt(password, hash);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para generar token de recuperación
CREATE OR REPLACE FUNCTION generate_reset_token()
RETURNS text AS $$
BEGIN
  RETURN encode(gen_random_bytes(32), 'hex');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para autenticar usuario (para usar desde la aplicación)
CREATE OR REPLACE FUNCTION authenticate_user(username_param text, password_param text)
RETURNS TABLE (
  user_id uuid,
  username text,
  email text,
  nombre text,
  rol text,
  activo boolean,
  ultimo_acceso timestamptz,
  success boolean,
  message text
) AS $$
DECLARE
  user_record usuarios%ROWTYPE;
  is_blocked boolean := false;
BEGIN
  -- Buscar usuario
  SELECT * INTO user_record 
  FROM usuarios 
  WHERE username = username_param AND activo = true;
  
  -- Verificar si el usuario existe
  IF NOT FOUND THEN
    RETURN QUERY SELECT 
      NULL::uuid, NULL::text, NULL::text, NULL::text, NULL::text, 
      NULL::boolean, NULL::timestamptz, false, 'Usuario no encontrado o inactivo';
    RETURN;
  END IF;
  
  -- Verificar si está bloqueado
  IF user_record.bloqueado_hasta IS NOT NULL AND user_record.bloqueado_hasta > NOW() THEN
    RETURN QUERY SELECT 
      NULL::uuid, NULL::text, NULL::text, NULL::text, NULL::text, 
      NULL::boolean, NULL::timestamptz, false, 'Usuario temporalmente bloqueado';
    RETURN;
  END IF;
  
  -- Verificar contraseña
  IF user_record.password_hash IS NOT NULL THEN
    -- Usar verificación segura si existe hash
    IF NOT verify_password(password_param, user_record.password_hash) THEN
      -- Incrementar intentos fallidos
      UPDATE usuarios 
      SET 
        intentos_login_fallidos = COALESCE(intentos_login_fallidos, 0) + 1,
        bloqueado_hasta = CASE 
          WHEN COALESCE(intentos_login_fallidos, 0) + 1 >= 5 
          THEN NOW() + INTERVAL '15 minutes'
          ELSE NULL
        END
      WHERE id = user_record.id;
      
      RETURN QUERY SELECT 
        NULL::uuid, NULL::text, NULL::text, NULL::text, NULL::text, 
        NULL::boolean, NULL::timestamptz, false, 'Contraseña incorrecta';
      RETURN;
    END IF;
  ELSE
    -- Fallback temporal para desarrollo (INSEGURO)
    IF password_param != 'password123' THEN
      RETURN QUERY SELECT 
        NULL::uuid, NULL::text, NULL::text, NULL::text, NULL::text, 
        NULL::boolean, NULL::timestamptz, false, 'Contraseña incorrecta';
      RETURN;
    END IF;
  END IF;
  
  -- Login exitoso - actualizar datos
  UPDATE usuarios 
  SET 
    ultimo_acceso = NOW(),
    intentos_login_fallidos = 0,
    bloqueado_hasta = NULL
  WHERE id = user_record.id;
  
  -- Retornar datos del usuario
  RETURN QUERY SELECT 
    user_record.id,
    user_record.username,
    user_record.email,
    user_record.nombre,
    user_record.rol,
    user_record.activo,
    NOW(),
    true,
    'Login exitoso';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para cambiar contraseña
CREATE OR REPLACE FUNCTION change_password(user_id_param uuid, old_password text, new_password text)
RETURNS TABLE (success boolean, message text) AS $$
DECLARE
  user_record usuarios%ROWTYPE;
BEGIN
  -- Buscar usuario
  SELECT * INTO user_record FROM usuarios WHERE id = user_id_param AND activo = true;
  
  IF NOT FOUND THEN
    RETURN QUERY SELECT false, 'Usuario no encontrado';
    RETURN;
  END IF;
  
  -- Verificar contraseña actual
  IF user_record.password_hash IS NOT NULL THEN
    IF NOT verify_password(old_password, user_record.password_hash) THEN
      RETURN QUERY SELECT false, 'Contraseña actual incorrecta';
      RETURN;
    END IF;
  ELSE
    -- Fallback temporal
    IF old_password != 'password123' THEN
      RETURN QUERY SELECT false, 'Contraseña actual incorrecta';
      RETURN;
    END IF;
  END IF;
  
  -- Actualizar contraseña
  UPDATE usuarios 
  SET password_hash = hash_password(new_password)
  WHERE id = user_id_param;
  
  RETURN QUERY SELECT true, 'Contraseña actualizada exitosamente';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Migrar usuarios existentes con contraseñas hasheadas
DO $$
BEGIN
  -- Solo migrar si no tienen password_hash
  UPDATE usuarios 
  SET password_hash = hash_password('password123')
  WHERE password_hash IS NULL;
  
  RAISE NOTICE 'Usuarios migrados con contraseña temporal hasheada';
END $$;

-- Crear tabla de logs de autenticación
CREATE TABLE IF NOT EXISTS auth_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  username text NOT NULL,
  ip_address inet,
  user_agent text,
  success boolean NOT NULL,
  error_message text,
  created_at timestamptz DEFAULT now()
);

-- Enable RLS en auth_logs
ALTER TABLE auth_logs ENABLE ROW LEVEL SECURITY;

-- Policy para auth_logs (solo admins pueden ver)
CREATE POLICY "Solo admins pueden ver logs de autenticación"
  ON auth_logs
  FOR SELECT
  TO authenticated
  USING (is_admin());

-- Función para registrar intento de login
CREATE OR REPLACE FUNCTION log_auth_attempt(
  username_param text,
  ip_param inet DEFAULT NULL,
  user_agent_param text DEFAULT NULL,
  success_param boolean DEFAULT false,
  error_param text DEFAULT NULL
)
RETURNS void AS $$
BEGIN
  INSERT INTO auth_logs (username, ip_address, user_agent, success, error_message)
  VALUES (username_param, ip_param, user_agent_param, success_param, error_param);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_usuarios_password_hash ON usuarios(password_hash) WHERE password_hash IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_usuarios_reset_token ON usuarios(password_reset_token) WHERE password_reset_token IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_usuarios_bloqueado ON usuarios(bloqueado_hasta) WHERE bloqueado_hasta IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_auth_logs_username ON auth_logs(username);
CREATE INDEX IF NOT EXISTS idx_auth_logs_created_at ON auth_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_auth_logs_success ON auth_logs(success);

-- Función para limpiar logs de autenticación antiguos
CREATE OR REPLACE FUNCTION limpiar_auth_logs_antiguos()
RETURNS integer AS $$
DECLARE
  deleted_count integer;
BEGIN
  DELETE FROM auth_logs 
  WHERE created_at < NOW() - INTERVAL '30 days';
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;