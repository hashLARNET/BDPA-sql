-- =============================================================================
-- BDPA Los Encinos - Estructura Completa de Base de Datos
-- Migración 001: Crear todas las tablas necesarias
-- =============================================================================

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- TABLA: usuarios
-- =============================================================================
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    rol VARCHAR(50) NOT NULL CHECK (rol IN ('Admin', 'Supervisor', 'Tecnico', 'Ayudante')),
    activo BOOLEAN DEFAULT TRUE,
    ultimo_acceso TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para usuarios
CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_rol ON usuarios(rol);
CREATE INDEX IF NOT EXISTS idx_usuarios_activo ON usuarios(activo);

-- =============================================================================
-- TABLA: proyectos
-- =============================================================================
CREATE TABLE IF NOT EXISTS proyectos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    ubicacion VARCHAR(255),
    cliente VARCHAR(255),
    fecha_inicio DATE,
    fecha_fin_estimada DATE,
    estado VARCHAR(50) DEFAULT 'activo' CHECK (estado IN ('activo', 'pausado', 'completado', 'cancelado')),
    total_unidades INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- TABLA: torres
-- =============================================================================
CREATE TABLE IF NOT EXISTS torres (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proyecto_id UUID REFERENCES proyectos(id) ON DELETE CASCADE,
    nombre VARCHAR(10) NOT NULL,
    descripcion TEXT,
    tiene_sector_norte BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(proyecto_id, nombre)
);

-- =============================================================================
-- TABLA: espacios
-- =============================================================================
CREATE TABLE IF NOT EXISTS espacios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proyecto_id UUID REFERENCES proyectos(id) ON DELETE CASCADE,
    torre_id UUID REFERENCES torres(id) ON DELETE CASCADE,
    piso INTEGER NOT NULL,
    sector VARCHAR(20) NOT NULL CHECK (sector IN ('Norte', 'Poniente', 'Oriente')),
    numero VARCHAR(10) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('unidad', 'sotu', 'shaft', 'lateral', 'antena')),
    estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'en_progreso', 'completado', 'con_observaciones')),
    observaciones TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(proyecto_id, torre_id, piso, sector, numero)
);

-- Índices para espacios
CREATE INDEX IF NOT EXISTS idx_espacios_proyecto ON espacios(proyecto_id);
CREATE INDEX IF NOT EXISTS idx_espacios_torre ON espacios(torre_id);
CREATE INDEX IF NOT EXISTS idx_espacios_estado ON espacios(estado);
CREATE INDEX IF NOT EXISTS idx_espacios_tipo ON espacios(tipo);

-- =============================================================================
-- TABLA: mediciones
-- =============================================================================
CREATE TABLE IF NOT EXISTS mediciones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    espacio_id UUID REFERENCES espacios(id) ON DELETE CASCADE,
    usuario_id UUID REFERENCES usuarios(id),
    tipo_medicion VARCHAR(30) NOT NULL CHECK (tipo_medicion IN ('alambrico-t1', 'alambrico-t2', 'coaxial', 'fibra', 'wifi', 'certificacion')),
    valor_medido DECIMAL(10,2),
    unidad_medida VARCHAR(10) DEFAULT 'dBm',
    fecha_medicion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    estado VARCHAR(20) DEFAULT 'valida' CHECK (estado IN ('valida', 'fuera_rango', 'requiere_revision')),
    observaciones TEXT,
    archivo_adjunto VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para mediciones
CREATE INDEX IF NOT EXISTS idx_mediciones_espacio ON mediciones(espacio_id);
CREATE INDEX IF NOT EXISTS idx_mediciones_usuario ON mediciones(usuario_id);
CREATE INDEX IF NOT EXISTS idx_mediciones_tipo ON mediciones(tipo_medicion);
CREATE INDEX IF NOT EXISTS idx_mediciones_fecha ON mediciones(fecha_medicion);
CREATE INDEX IF NOT EXISTS idx_mediciones_estado ON mediciones(estado);

-- =============================================================================
-- TABLA: avances
-- =============================================================================
CREATE TABLE IF NOT EXISTS avances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proyecto_id UUID REFERENCES proyectos(id) ON DELETE CASCADE,
    fecha DATE NOT NULL,
    torre VARCHAR(10),
    piso INTEGER,
    sector VARCHAR(20),
    espacios_completados INTEGER DEFAULT 0,
    espacios_totales INTEGER DEFAULT 0,
    porcentaje_avance DECIMAL(5,2) DEFAULT 0.00,
    observaciones TEXT,
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para avances
CREATE INDEX IF NOT EXISTS idx_avances_proyecto ON avances(proyecto_id);
CREATE INDEX IF NOT EXISTS idx_avances_fecha ON avances(fecha);
CREATE INDEX IF NOT EXISTS idx_avances_usuario ON avances(usuario_id);

-- =============================================================================
-- TABLA: configuracion
-- =============================================================================
CREATE TABLE IF NOT EXISTS configuracion (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clave VARCHAR(100) UNIQUE NOT NULL,
    valor TEXT NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(20) DEFAULT 'string' CHECK (tipo IN ('string', 'number', 'boolean', 'json', 'array')),
    categoria VARCHAR(50) DEFAULT 'general',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- FUNCIONES AUXILIARES
-- =============================================================================

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para actualizar updated_at
CREATE TRIGGER trigger_usuarios_updated_at 
    BEFORE UPDATE ON usuarios 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_proyectos_updated_at 
    BEFORE UPDATE ON proyectos 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_torres_updated_at 
    BEFORE UPDATE ON torres 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_espacios_updated_at 
    BEFORE UPDATE ON espacios 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_mediciones_updated_at 
    BEFORE UPDATE ON mediciones 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_avances_updated_at 
    BEFORE UPDATE ON avances 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_configuracion_updated_at 
    BEFORE UPDATE ON configuracion 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- FUNCIÓN DE AUTENTICACIÓN
-- =============================================================================
CREATE OR REPLACE FUNCTION authenticate_user(username_param text, password_param text)
RETURNS TABLE (
    success boolean,
    message text,
    user_id uuid,
    username text,
    email text,
    nombre text,
    rol text,
    activo boolean,
    ultimo_acceso timestamp with time zone
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    stored_hash text;
    user_record RECORD;
BEGIN
    -- Buscar el usuario por username
    SELECT * INTO user_record
    FROM usuarios 
    WHERE usuarios.username = username_param AND usuarios.activo = true;
    
    -- Si no se encuentra el usuario
    IF user_record.id IS NULL THEN
        success := false;
        message := 'Usuario no encontrado o inactivo';
        RETURN NEXT;
        RETURN;
    END IF;
    
    -- En un entorno real, aquí verificaríamos el hash de la contraseña
    -- Por simplicidad en desarrollo, permitimos cualquier contraseña
    -- TODO: Implementar verificación real de password con crypt()
    
    success := true;
    message := 'Autenticación exitosa';
    user_id := user_record.id;
    username := user_record.username;
    email := user_record.email;
    nombre := user_record.nombre;
    rol := user_record.rol;
    activo := user_record.activo;
    ultimo_acceso := user_record.ultimo_acceso;
    
    -- Actualizar último acceso
    UPDATE usuarios SET ultimo_acceso = NOW() WHERE usuarios.id = user_record.id;
    
    RETURN NEXT;
END;
$$;

-- =============================================================================
-- POLÍTICAS RLS (Row Level Security)
-- =============================================================================

-- Habilitar RLS en todas las tablas
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE proyectos ENABLE ROW LEVEL SECURITY;
ALTER TABLE torres ENABLE ROW LEVEL SECURITY;
ALTER TABLE espacios ENABLE ROW LEVEL SECURITY;
ALTER TABLE mediciones ENABLE ROW LEVEL SECURITY;
ALTER TABLE avances ENABLE ROW LEVEL SECURITY;
ALTER TABLE configuracion ENABLE ROW LEVEL SECURITY;

-- Políticas para usuarios (solo administradores pueden gestionar usuarios)
CREATE POLICY "Usuarios pueden ver sus propios datos" ON usuarios
    FOR SELECT USING (auth.uid()::text = id::text OR 
                     EXISTS(SELECT 1 FROM usuarios WHERE usuarios.id::text = auth.uid()::text AND usuarios.rol = 'Admin'));

CREATE POLICY "Solo admins pueden insertar usuarios" ON usuarios
    FOR INSERT WITH CHECK (EXISTS(SELECT 1 FROM usuarios WHERE usuarios.id::text = auth.uid()::text AND usuarios.rol = 'Admin'));

CREATE POLICY "Solo admins pueden actualizar usuarios" ON usuarios
    FOR UPDATE USING (EXISTS(SELECT 1 FROM usuarios WHERE usuarios.id::text = auth.uid()::text AND usuarios.rol = 'Admin'));

-- Políticas más permisivas para las otras tablas (ajustar según necesidades)
CREATE POLICY "Lectura general" ON proyectos FOR SELECT USING (true);
CREATE POLICY "Lectura general" ON torres FOR SELECT USING (true);
CREATE POLICY "Lectura general" ON espacios FOR SELECT USING (true);
CREATE POLICY "Lectura general" ON mediciones FOR SELECT USING (true);
CREATE POLICY "Lectura general" ON avances FOR SELECT USING (true);
CREATE POLICY "Lectura general" ON configuracion FOR SELECT USING (true);

-- =============================================================================
-- COMENTARIOS EN TABLAS
-- =============================================================================
COMMENT ON TABLE usuarios IS 'Usuarios del sistema BDPA Los Encinos';
COMMENT ON TABLE proyectos IS 'Proyectos de construcción';
COMMENT ON TABLE torres IS 'Torres de cada proyecto';
COMMENT ON TABLE espacios IS 'Espacios individuales (unidades, sotu, etc.)';
COMMENT ON TABLE mediciones IS 'Mediciones técnicas realizadas en cada espacio';
COMMENT ON TABLE avances IS 'Registro de avances diarios del proyecto';
COMMENT ON TABLE configuracion IS 'Configuraciones del sistema';

-- =============================================================================
-- MENSAJE DE CONFIRMACIÓN
-- =============================================================================
DO $$
BEGIN
    RAISE NOTICE '✅ Base de datos BDPA Los Encinos creada exitosamente';
    RAISE NOTICE '📋 Tablas creadas: usuarios, proyectos, torres, espacios, mediciones, avances, configuracion';
    RAISE NOTICE '🔧 Funciones creadas: authenticate_user, update_updated_at_column';
    RAISE NOTICE '🛡️ RLS habilitado en todas las tablas';
    RAISE NOTICE '📝 Siguiente paso: Ejecutar crear_usuarios.py para poblar datos iniciales';
END $$;