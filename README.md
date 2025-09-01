# BDPA Los Encinos - Sistema de Gestión de Obras

Sistema completo de gestión de obras de telecomunicaciones desarrollado en **Python puro**, compuesto por un backend API con FastAPI y una aplicación de escritorio con Tkinter.

## 🏗️ Arquitectura del Sistema

```
BDPA Los Encinos/
├── Backend API (FastAPI)     # Servidor REST con Supabase
├── Frontend Desktop (Tkinter) # Aplicación de escritorio nativa
└── Base de Datos (Supabase)   # PostgreSQL con Storage
```

## 🚀 Características Principales

### **Backend API (FastAPI)**
- **API RESTful** completa con documentación automática
- **Autenticación JWT** para seguridad
- **Integración con Supabase** para base de datos y storage
- **Validación de datos** con Pydantic
- **Manejo de archivos** para fotos de avances
- **Dashboard** con estadísticas en tiempo real
- **Filtros avanzados** para consultas

### **Frontend Desktop (Tkinter)**
- **Interfaz nativa** multiplataforma (Windows, macOS, Linux)
- **Gestión completa** de avances, mediciones y usuarios
- **Autenticación** con recordar sesión
- **Manejo offline** con sincronización automática
- **Subida de fotos** integrada
- **Dashboard visual** con estadísticas

### **Base de Datos (Supabase)**
- **PostgreSQL** con Row Level Security (RLS)
- **Storage** para archivos y fotos
- **Funciones** para cálculos complejos
- **Vistas** optimizadas para consultas
- **Auditoría** completa de cambios

## 📋 Requisitos del Sistema

- **Python 3.9+**
- **Cuenta de Supabase** configurada
- **Conexión a internet** (para comunicación con Supabase)

## 🛠 Instalación Rápida

### 1. **Clonar y Configurar**
```bash
git clone <repository-url>
cd bdpa-los-encinos

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. **Configurar Variables de Entorno**
```bash
cp .env.example .env
# Editar .env con tus credenciales de Supabase
```

### 3. **Configurar Supabase**
1. Crear proyecto en [Supabase](https://supabase.com)
2. Ejecutar migraciones SQL desde `supabase/migrations/`
3. Configurar buckets de Storage
4. Obtener URL y claves del proyecto

### 4. **Ejecutar Aplicaciones**

**Backend (Terminal 1):**
```bash
python main.py
# API disponible en http://localhost:8000
```

**Frontend Desktop (Terminal 2):**
```bash
cd frontend
python run.py
```

## 📚 Documentación Detallada

### **Backend API**
- **Documentación**: `http://localhost:8000/docs` (Swagger UI)
- **Configuración**: Ver `app/config.py`
- **Endpoints**: Ver `app/routers/`
- **Modelos**: Ver `app/models/`

### **Frontend Desktop**
- **Configuración**: Ver `frontend/config.py`
- **Componentes UI**: Ver `frontend/ui/`
- **Servicios**: Ver `frontend/services/`
- **Utilidades**: Ver `frontend/utils/`

### **Base de Datos**
- **Migraciones**: Ver `supabase/migrations/`
- **Configuración**: Ver `README_SUPABASE.md`

## 🔧 Configuración Avanzada

### **Variables de Entorno Principales**
```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# JWT
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_BASE_URL=http://localhost:8000
DEBUG=True

# Frontend
WINDOW_WIDTH=1200
WINDOW_HEIGHT=800
```

### **Estructura de Datos**

#### **Usuarios**
- **Roles**: Admin, Supervisor, Técnico, Ayudante
- **Permisos**: Basados en rol con RLS
- **Autenticación**: JWT con expiración configurable

#### **Avances**
- **Torres**: A-J (10 torres)
- **Pisos**: 1, 3
- **Sectores**: Norte, Poniente, Oriente
- **Tipos**: unidad, sotu, shaft, lateral, antena
- **Progreso**: 0-100%

#### **Mediciones**
- **Tipos**: alámbrico-t1, alámbrico-t2, coaxial, fibra, wifi, certificación
- **Estados**: OK, ADVERTENCIA, FALLA (calculado automáticamente)
- **Rangos**: Validación automática según tipo

## 🧪 Testing y Desarrollo

### **Probar Backend**
```bash
# Verificar salud de la API
python scripts/test_api.py

# Ejecutar con recarga automática
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **Probar Frontend**
```bash
cd frontend
python run.py
```

### **Credenciales de Desarrollo**
- **Usuario**: `admin`
- **Contraseña**: `password123` (temporal)

## 🚀 Despliegue

### **Backend (Producción)**
```bash
# Con Gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Con Docker
docker build -t bdpa-api .
docker run -p 8000:8000 bdpa-api

# Con Docker Compose
docker-compose up -d
```

### **Frontend (Distribución)**
```bash
# Crear ejecutable
pip install pyinstaller
pyinstaller --onefile --windowed --name "BDPA-Los-Encinos" frontend/main.py
```

## 📊 Funcionalidades Principales

### **Dashboard**
- Estadísticas generales de la obra
- Progreso por torres en tiempo real
- Indicadores de mediciones (OK/Falla)
- Actividad reciente del equipo

### **Gestión de Avances**
- Registro de progreso con fotografías
- Filtros por torre, piso, fecha, categoría
- Validación automática de datos
- Sincronización con servidor

### **Gestión de Mediciones**
- Mediciones técnicas especializadas
- Cálculo automático de estados
- Validación de rangos por tipo
- Exportación de reportes

### **Gestión de Usuarios**
- Creación y edición de usuarios (Admin)
- Asignación de roles y permisos
- Historial de accesos
- Activación/desactivación

## 🔐 Seguridad

### **Autenticación**
- JWT con expiración configurable
- Verificación de tokens en cada request
- Logout seguro con limpieza de sesión

### **Autorización**
- Row Level Security (RLS) en Supabase
- Permisos basados en roles
- Validación en backend y frontend

### **Datos**
- Validación estricta con Pydantic
- Sanitización de inputs
- Auditoría completa de cambios

## 🔧 Mantenimiento

### **Logs y Monitoreo**
```sql
-- Ver actividad reciente
SELECT * FROM auditoria ORDER BY fecha DESC LIMIT 50;

-- Ver estadísticas generales
SELECT * FROM calcular_progreso_obra();

-- Limpiar datos antiguos
SELECT limpiar_auditoria_antigua();
SELECT limpiar_cola_sync();
```

### **Backup y Restauración**
- Backup automático de Supabase
- Exportación de datos en JSON
- Restauración desde backup

## 🐛 Troubleshooting

### **Problemas Comunes**

1. **"Backend no disponible"**
   - Verificar que FastAPI esté ejecutándose en puerto 8000
   - Comprobar variables de entorno en `.env`
   - Verificar conexión con Supabase

2. **"Error de autenticación"**
   - Verificar credenciales de usuario
   - Comprobar configuración JWT
   - Revisar políticas RLS en Supabase

3. **"Error de sincronización"**
   - Verificar conexión a internet
   - Comprobar estado de Supabase
   - Revisar logs de la aplicación

### **Verificaciones de Salud**
```bash
# Verificar backend
curl http://localhost:8000/health

# Verificar conexión Supabase
python -c "from app.services.supabase_client import supabase_client; print(supabase_client.table('usuarios').select('count').execute())"

# Probar autenticación
python scripts/test_api.py
```

## 📞 Soporte y Contribución

### **Estructura del Código**
- **Backend**: Arquitectura modular con separación clara de responsabilidades
- **Frontend**: Componentes reutilizables con gestión de estado
- **Base de Datos**: Esquema normalizado con optimizaciones

### **Mejores Prácticas**
- Validación en múltiples capas
- Manejo de errores robusto
- Logging comprehensivo
- Testing automatizado

### **Contribuir**
1. Fork del proyecto
2. Crear rama para feature
3. Implementar cambios con tests
4. Crear Pull Request

---

**BDPA Los Encinos** - Sistema Integral de Gestión de Obras de Telecomunicaciones  
*Desarrollado con Python, FastAPI, Tkinter y Supabase*