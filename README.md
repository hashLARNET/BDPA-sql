# BDPA Los Encinos - Backend API

Sistema de gestión de obras de telecomunicaciones desarrollado en Python con FastAPI.

## 🚀 Características

- **API RESTful** completa con FastAPI
- **Autenticación JWT** para seguridad
- **Integración con Supabase** para base de datos y storage
- **Validación de datos** con Pydantic
- **Documentación automática** con Swagger/OpenAPI
- **Manejo de archivos** para fotos de avances
- **Dashboard** con estadísticas en tiempo real
- **Filtros avanzados** para consultas
- **Manejo de errores** robusto

## 📋 Requisitos

- Python 3.9+
- Cuenta de Supabase configurada
- Base de datos PostgreSQL (via Supabase)

## 🛠 Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd bdpa-los-encinos-backend
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus credenciales de Supabase
```

5. **Ejecutar la aplicación**
```bash
python main.py
```

La API estará disponible en `http://localhost:8000`

## 📚 Documentación de la API

Una vez ejecutando la aplicación, puedes acceder a:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` basado en `.env.example`:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-role-key

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
APP_NAME=BDPA - Los Encinos API
APP_VERSION=1.0.0
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Configuración de Supabase

1. Crea un proyecto en [Supabase](https://supabase.com)
2. Ejecuta las migraciones SQL ubicadas en `supabase/migrations/`
3. Configura los buckets de Storage:
   - `avances-fotos` para fotos de avances
   - `mediciones-docs` para documentos de mediciones

## 📖 Endpoints Principales

### Autenticación
- `POST /auth/login` - Iniciar sesión
- `GET /auth/me` - Obtener usuario actual
- `POST /auth/logout` - Cerrar sesión

### Usuarios
- `GET /usuarios/` - Listar usuarios
- `POST /usuarios/` - Crear usuario (Admin)
- `GET /usuarios/{id}` - Obtener usuario
- `PUT /usuarios/{id}` - Actualizar usuario
- `DELETE /usuarios/{id}` - Desactivar usuario (Admin)

### Avances
- `GET /avances/` - Listar avances con filtros
- `POST /avances/` - Crear avance
- `GET /avances/{id}` - Obtener avance
- `PUT /avances/{id}` - Actualizar avance
- `DELETE /avances/{id}` - Eliminar avance (Supervisor/Admin)

### Mediciones
- `GET /mediciones/` - Listar mediciones con filtros
- `POST /mediciones/` - Crear medición
- `GET /mediciones/{id}` - Obtener medición
- `PUT /mediciones/{id}` - Actualizar medición
- `DELETE /mediciones/{id}` - Eliminar medición (Supervisor/Admin)

### Dashboard
- `GET /dashboard/` - Datos completos del dashboard
- `GET /dashboard/summary` - Resumen general
- `GET /dashboard/tower-progress` - Progreso por torre
- `GET /dashboard/mediciones-estado` - Estado de mediciones

## 🏗 Estructura del Proyecto

```
app/
├── __init__.py
├── config.py              # Configuración de la aplicación
├── main.py                # Punto de entrada
├── models/                # Modelos Pydantic
│   ├── __init__.py
│   ├── auth.py
│   ├── usuario.py
│   ├── avance.py
│   ├── medicion.py
│   └── dashboard.py
├── routers/               # Endpoints de la API
│   ├── __init__.py
│   ├── auth.py
│   ├── usuarios.py
│   ├── avances.py
│   ├── mediciones.py
│   └── dashboard.py
├── services/              # Lógica de negocio
│   ├── __init__.py
│   ├── supabase_client.py
│   ├── auth_service.py
│   ├── usuario_service.py
│   ├── avance_service.py
│   ├── medicion_service.py
│   └── dashboard_service.py
└── utils/                 # Utilidades
    ├── __init__.py
    ├── validators.py
    └── helpers.py
```

## 🔐 Autenticación y Autorización

La API utiliza JWT (JSON Web Tokens) para autenticación:

1. **Login**: `POST /auth/login` con username/password
2. **Token**: Incluir en header `Authorization: Bearer <token>`
3. **Roles**: Admin, Supervisor, Técnico, Ayudante

### Permisos por Rol

- **Admin**: Acceso completo
- **Supervisor**: Gestión de avances/mediciones + eliminación
- **Técnico**: Crear/editar avances y mediciones
- **Ayudante**: Solo lectura y creación básica

## 📊 Modelos de Datos

### Usuario
```python
{
  "id": "uuid",
  "username": "string",
  "nombre": "string", 
  "rol": "Admin|Supervisor|Tecnico|Ayudante",
  "activo": true,
  "ultimo_acceso": "datetime"
}
```

### Avance
```python
{
  "id": "uuid",
  "fecha": "datetime",
  "torre": "A-J",
  "piso": 1-20,
  "sector": "Norte|Poniente|Oriente",
  "tipo_espacio": "unidad|sotu|shaft|lateral|antena",
  "ubicacion": "string",
  "categoria": "string",
  "porcentaje": 0-100,
  "foto_url": "string",
  "observaciones": "string"
}
```

### Medición
```python
{
  "id": "uuid",
  "fecha": "datetime",
  "torre": "A-J",
  "piso": 1-20,
  "identificador": "string",
  "tipo_medicion": "alambrico-t1|alambrico-t2|coaxial|fibra|wifi|certificacion",
  "valores": {...},
  "estado": "OK|ADVERTENCIA|FALLA",
  "observaciones": "string"
}
```

## 🧪 Testing

Para ejecutar las pruebas:

```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio httpx

# Ejecutar pruebas
pytest
```

## 🚀 Despliegue

### Desarrollo
```bash
python main.py
```

### Producción
```bash
# Con Gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Con Docker
docker build -t bdpa-api .
docker run -p 8000:8000 bdpa-api
```

## 📝 Notas de Desarrollo

### Validación Automática de Mediciones

La API calcula automáticamente el estado de las mediciones basado en rangos predefinidos:

- **Alámbrico/Coaxial**: 45-75 dBμV
- **Fibra Óptica**: -30 a -8 dBm
- **WiFi**: -80 a -30 dBm

### Subida de Archivos

Las fotos de avances se suben automáticamente a Supabase Storage con:
- Validación de tipo de archivo
- Límite de tamaño (10MB)
- Nombres únicos con UUID
- Organización por fecha

### Filtros Avanzados

Todos los endpoints de listado soportan filtros múltiples:
- Por torre, piso, sector
- Por rango de fechas
- Búsqueda de texto
- Paginación con limit/offset

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 📞 Soporte

Para soporte técnico o preguntas:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo

---

**BDPA Los Encinos** - Sistema de Gestión de Obras de Telecomunicaciones
```