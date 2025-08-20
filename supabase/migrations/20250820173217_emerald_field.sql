/*
  # Funciones auxiliares para RLS y seguridad

  1. Funciones de validación de roles
  2. Funciones de auditoría
  3. Triggers de auditoría
*/

-- Función para verificar si el usuario es admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS boolean AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM usuarios 
    WHERE id::text = auth.uid()::text 
    AND rol = 'Admin' 
    AND activo = true
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para verificar si el usuario es supervisor o admin
CREATE OR REPLACE FUNCTION is_supervisor_or_admin()
RETURNS boolean AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1 FROM usuarios 
    WHERE id::text = auth.uid()::text 
    AND rol IN ('Admin', 'Supervisor') 
    AND activo = true
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Función para obtener el rol del usuario actual
CREATE OR REPLACE FUNCTION get_user_role()
RETURNS text AS $$
DECLARE
  user_role text;
BEGIN
  SELECT rol INTO user_role 
  FROM usuarios 
  WHERE id::text = auth.uid()::text 
  AND activo = true;
  
  RETURN COALESCE(user_role, 'guest');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Tabla de auditoría
CREATE TABLE IF NOT EXISTS auditoria (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tabla text NOT NULL,
  operacion text NOT NULL,
  registro_id text NOT NULL,
  datos_anteriores jsonb,
  datos_nuevos jsonb,
  usuario_id uuid,
  fecha timestamptz DEFAULT now(),
  ip_address inet,
  user_agent text
);

-- Enable RLS en auditoría
ALTER TABLE auditoria ENABLE ROW LEVEL SECURITY;

-- Policy para auditoría (solo admins pueden ver)
CREATE POLICY "Solo admins pueden ver auditoría"
  ON auditoria
  FOR SELECT
  TO authenticated
  USING (is_admin());

-- Función genérica de auditoría
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    INSERT INTO auditoria (tabla, operacion, registro_id, datos_anteriores, usuario_id)
    VALUES (TG_TABLE_NAME, TG_OP, OLD.id::text, to_jsonb(OLD), auth.uid());
    RETURN OLD;
  ELSIF TG_OP = 'UPDATE' THEN
    INSERT INTO auditoria (tabla, operacion, registro_id, datos_anteriores, datos_nuevos, usuario_id)
    VALUES (TG_TABLE_NAME, TG_OP, NEW.id::text, to_jsonb(OLD), to_jsonb(NEW), auth.uid());
    RETURN NEW;
  ELSIF TG_OP = 'INSERT' THEN
    INSERT INTO auditoria (tabla, operacion, registro_id, datos_nuevos, usuario_id)
    VALUES (TG_TABLE_NAME, TG_OP, NEW.id::text, to_jsonb(NEW), auth.uid());
    RETURN NEW;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Triggers de auditoría para tablas importantes
CREATE TRIGGER audit_usuarios
  AFTER INSERT OR UPDATE OR DELETE ON usuarios
  FOR EACH ROW EXECUTE FUNCTION audit_trigger();

CREATE TRIGGER audit_avances
  AFTER INSERT OR UPDATE OR DELETE ON avances
  FOR EACH ROW EXECUTE FUNCTION audit_trigger();

CREATE TRIGGER audit_mediciones
  AFTER INSERT OR UPDATE OR DELETE ON mediciones
  FOR EACH ROW EXECUTE FUNCTION audit_trigger();

-- Función para limpiar auditoría antigua
CREATE OR REPLACE FUNCTION limpiar_auditoria_antigua()
RETURNS integer AS $$
DECLARE
  deleted_count integer;
BEGIN
  DELETE FROM auditoria 
  WHERE fecha < NOW() - INTERVAL '90 days';
  
  GET DIAGNOSTICS deleted_count = ROW_COUNT;
  RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Índices para auditoría
CREATE INDEX IF NOT EXISTS idx_auditoria_tabla ON auditoria(tabla);
CREATE INDEX IF NOT EXISTS idx_auditoria_fecha ON auditoria(fecha);
CREATE INDEX IF NOT EXISTS idx_auditoria_usuario_id ON auditoria(usuario_id);
CREATE INDEX IF NOT EXISTS idx_auditoria_registro_id ON auditoria(registro_id);