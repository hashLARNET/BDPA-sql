# Configuración de Supabase para BDPA Los Encinos

## Pasos de Configuración

### 1. Crear Proyecto en Supabase
1. Ve a [supabase.com](https://supabase.com)
2. Crea una nueva organización o usa una existente
3. Crea un nuevo proyecto llamado "BDPA Los Encinos"
4. Anota la URL del proyecto y la clave anónima

### 2. Configurar Variables de Entorno
Copia el archivo `.env.example` a `.env` y completa:

```env
VITE_SUPABASE_URL=https://tu-proyecto.supabase.co
VITE_SUPABASE_ANON_KEY=tu-clave-anonima
VITE_APP_NAME=BDPA - Los Encinos
VITE_OBRA_ID=los-encinos-001
VITE_SYNC_INTERVAL=30000
DATABASE_URL=file:./bdpa.db
```

### 3. Ejecutar Migraciones
En el SQL Editor de Supabase, ejecuta los archivos en este orden:

1. `create_usuarios_table.sql`
2. `create_avances_table.sql`
3. `create_mediciones_table.sql`
4. `create_sync_queue_table.sql`
5. `create_app_config_table.sql`
6. `create_storage_buckets.sql`
7. `create_views_and_functions.sql`
8. `create_rls_helper_functions.sql`
9. `insert_initial_data.sql`

O ejecuta todo de una vez con `seed.sql`.

### 4. Configurar Autenticación
1. Ve a Authentication > Settings
2. Configura los providers que necesites
3. Desactiva "Enable email confirmations" para desarrollo
4. Configura las URLs de redirección si es necesario

### 5. Verificar Storage
1. Ve a Storage
2. Verifica que los buckets `avances-fotos` y `mediciones-docs` estén creados
3. Verifica las políticas de acceso

## Estructura de la Base de Datos

### Tablas Principales
- **usuarios**: Gestión de usuarios y roles
- **avances**: Registro de progreso de obra
- **mediciones**: Mediciones técnicas
- **sync_queue**: Cola de sincronización
- **app_config**: Configuración de la aplicación
- **auditoria**: Registro de cambios

### Vistas
- **vista_progreso_torres**: Progreso por torre
- **vista_mediciones_resumen**: Resumen de mediciones
- **vista_avances_recientes**: Últimos avances

### Funciones
- **calcular_progreso_obra()**: Estadísticas generales
- **obtener_estadisticas_torre(torre)**: Stats por torre
- **obtener_dashboard_data()**: Datos para dashboard
- **limpiar_cola_sync()**: Mantenimiento de cola
- **limpiar_auditoria_antigua()**: Limpieza de logs

## Políticas de Seguridad (RLS)

### Usuarios
- Todos pueden ver usuarios activos
- Solo pueden actualizar su propio perfil
- Solo admins pueden crear/eliminar usuarios

### Avances
- Todos pueden ver avances no eliminados
- Todos pueden crear avances
- Todos pueden actualizar avances
- Solo supervisores/admins pueden eliminar

### Mediciones
- Todos pueden ver mediciones
- Todos pueden crear/actualizar mediciones
- Solo supervisores/admins pueden eliminar

### Storage
- Usuarios autenticados pueden subir/ver archivos
- Solo propietarios pueden eliminar archivos

## Datos Iniciales

### Usuarios de Ejemplo
- **admin** (Admin): Administrador del sistema
- **supervisor1** (Supervisor): Supervisor de obra
- **tecnico1, tecnico2** (Tecnico): Técnicos de campo
- **ayudante1** (Ayudante): Ayudante de obra

### Configuración Inicial
- Configuración específica de Los Encinos
- 1,247 unidades distribuidas en 10 torres
- Torres C y H sin sector Norte
- Intervalos de sincronización configurados

## Mantenimiento

### Limpieza Automática
Ejecuta periódicamente:
```sql
SELECT limpiar_cola_sync(); -- Limpia cola de sincronización
SELECT limpiar_auditoria_antigua(); -- Limpia logs antiguos
```

### Monitoreo
```sql
-- Ver estadísticas generales
SELECT * FROM calcular_progreso_obra();

-- Ver progreso por torre
SELECT * FROM vista_progreso_torres;

-- Ver cola de sincronización
SELECT status, COUNT(*) FROM sync_queue GROUP BY status;
```

## Troubleshooting

### Problemas Comunes
1. **Error de permisos**: Verificar que RLS esté habilitado
2. **Storage no funciona**: Verificar políticas de buckets
3. **Sincronización lenta**: Revisar índices y cola

### Logs Útiles
```sql
-- Ver errores de sincronización
SELECT * FROM sync_queue WHERE status = 'failed';

-- Ver actividad reciente
SELECT * FROM auditoria ORDER BY fecha DESC LIMIT 50;

-- Ver usuarios activos
SELECT username, nombre, rol, ultimo_acceso FROM usuarios WHERE activo = true;
```

## Backup y Restauración

### Backup Manual
1. Ve a Settings > Database
2. Descarga backup completo
3. Guarda en lugar seguro

### Restauración
1. Crea nuevo proyecto
2. Restaura desde backup
3. Ejecuta migraciones si es necesario
4. Verifica configuración

## Seguridad

### Mejores Prácticas
- Rotar claves regularmente
- Monitorear logs de auditoría
- Mantener RLS habilitado
- Validar datos en frontend y backend
- Usar HTTPS siempre

### Configuración de Producción
- Habilitar confirmación por email
- Configurar rate limiting
- Habilitar 2FA para admins
- Configurar alertas de seguridad