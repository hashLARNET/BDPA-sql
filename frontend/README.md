# BDPA Los Encinos - Frontend Tkinter

Aplicación de escritorio desarrollada en Python con Tkinter para la gestión de obras de telecomunicaciones.

## 🚀 Características

- **Interfaz Nativa**: Aplicación de escritorio con Tkinter
- **Multiplataforma**: Funciona en Windows, macOS y Linux
- **Gestión Completa**: Avances, mediciones, usuarios y dashboard
- **Autenticación**: Login seguro con JWT
- **Offline Ready**: Manejo de errores de conexión
- **Fácil Instalación**: Sin dependencias complejas

## 📋 Requisitos

- Python 3.9+
- Backend API ejecutándose (FastAPI)
- Conexión a internet (para comunicación con API)

## 🛠 Instalación

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd bdpa-los-encinos/frontend
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
# Editar .env con la URL de tu API
```

5. **Ejecutar la aplicación**
```bash
python run.py
```

## 📚 Estructura del Proyecto

```
frontend/
├── main.py                 # Punto de entrada principal
├── config.py              # Configuración de la aplicación
├── run.py                 # Script de ejecución con verificaciones
├── services/              # Servicios de comunicación
│   ├── __init__.py
│   └── api_client.py      # Cliente para API REST
├── utils/                 # Utilidades
│   ├── __init__.py
│   ├── session_manager.py # Gestión de sesiones
│   ├── validators.py      # Validadores de formularios
│   └── formatters.py      # Formateadores de datos
├── ui/                    # Componentes de interfaz
│   ├── __init__.py
│   ├── login_window.py    # Ventana de login
│   ├── main_window.py     # Ventana principal
│   ├── dashboard_tab.py   # Pestaña de dashboard
│   ├── avances_tab.py     # Pestaña de avances
│   ├── mediciones_tab.py  # Pestaña de mediciones
│   └── usuarios_tab.py    # Pestaña de usuarios
└── assets/                # Recursos (iconos, imágenes)
```

## 🎯 Funcionalidades

### **🔐 Autenticación**
- Login con usuario y contraseña
- Recordar sesión automáticamente
- Logout seguro
- Verificación de token

### **📊 Dashboard**
- Estadísticas generales de la obra
- Progreso por torres
- Actividad reciente
- Indicadores visuales

### **📈 Gestión de Avances**
- Crear nuevos avances con fotografías
- Filtrar por torre, piso, fecha
- Editar y eliminar avances
- Exportar datos (futuro)

### **📏 Gestión de Mediciones**
- Registrar mediciones técnicas
- Tipos: alámbrico, coaxial, fibra, WiFi, certificación
- Validación automática de rangos
- Estados: OK, Advertencia, Falla

### **👥 Gestión de Usuarios** (Solo Admins)
- Crear y editar usuarios
- Asignar roles y permisos
- Activar/desactivar usuarios
- Ver historial de accesos

## 🔧 Configuración

### **Variables de Entorno (.env)**
```env
# API Configuration
API_BASE_URL=http://localhost:8000

# App Configuration
APP_TITLE=BDPA - Los Encinos
WINDOW_WIDTH=1200
WINDOW_HEIGHT=800
THEME=arc
```

### **Configuración de Roles**
- **Admin**: Acceso completo
- **Supervisor**: Gestión + eliminación
- **Técnico**: Crear/editar avances y mediciones
- **Ayudante**: Solo lectura y creación básica

## 🚀 Uso

### **1. Iniciar la Aplicación**
```bash
python run.py
```

### **2. Login**
- Usuario: `admin`
- Contraseña: `password123` (temporal)

### **3. Navegación**
- **Dashboard**: Vista general del proyecto
- **Avances**: Registrar progreso de obra
- **Mediciones**: Registrar mediciones técnicas
- **Usuarios**: Gestionar usuarios (solo admins)

### **4. Funciones Principales**

#### **Registrar Avance**
1. Ir a pestaña "Avances"
2. Clic en "➕ Nuevo Avance"
3. Completar formulario
4. Opcionalmente agregar foto
5. Guardar

#### **Registrar Medición**
1. Ir a pestaña "Mediciones"
2. Clic en "➕ Nueva Medición"
3. Seleccionar tipo de medición
4. Ingresar valores
5. El sistema calcula automáticamente el estado
6. Guardar

## 🎨 Interfaz de Usuario

### **Características de la UI**
- **Diseño Limpio**: Interfaz moderna y profesional
- **Navegación por Pestañas**: Organización clara
- **Filtros Avanzados**: Búsqueda y filtrado eficiente
- **Indicadores Visuales**: Estados y progreso claros
- **Responsive**: Se adapta a diferentes tamaños de ventana

### **Componentes Principales**
- **TreeView**: Listas de datos con columnas ordenables
- **Formularios**: Validación en tiempo real
- **Diálogos Modales**: Para crear/editar registros
- **Barras de Progreso**: Indicadores visuales
- **Botones de Acción**: Operaciones principales

## 🔄 Comunicación con API

### **Cliente API**
- **Autenticación JWT**: Tokens seguros
- **Manejo de Errores**: Respuestas claras al usuario
- **Timeouts**: Evita bloqueos de la aplicación
- **Retry Logic**: Reintenta operaciones fallidas

### **Endpoints Utilizados**
```python
# Autenticación
POST /auth/login
GET /auth/me

# Avances
GET /avances/
POST /avances/
PUT /avances/{id}
DELETE /avances/{id}

# Mediciones
GET /mediciones/
POST /mediciones/
PUT /mediciones/{id}
DELETE /mediciones/{id}

# Dashboard
GET /dashboard/
GET /dashboard/summary
GET /dashboard/tower-progress

# Usuarios
GET /usuarios/
POST /usuarios/
PUT /usuarios/{id}
```

## 🧪 Testing

### **Verificar Conexión**
```bash
python -c "from services.api_client import APIClient; client = APIClient('http://localhost:8000'); print('✅ Conexión OK' if client._make_request('GET', '/health').status_code == 200 else '❌ Error')"
```

### **Test de Login**
```bash
python -c "from services.api_client import APIClient; client = APIClient('http://localhost:8000'); print(client.login('admin', 'password123'))"
```

## 📦 Distribución

### **Crear Ejecutable (PyInstaller)**
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "BDPA-Los-Encinos" main.py
```

### **Crear Instalador (Windows)**
```bash
# Usar NSIS o Inno Setup para crear instalador
```

## 🔧 Desarrollo

### **Agregar Nueva Funcionalidad**
1. Crear endpoint en el backend
2. Agregar método en `api_client.py`
3. Crear/modificar componente UI
4. Agregar validaciones necesarias
5. Probar funcionalidad

### **Estructura de Componentes**
```python
class NuevoTab:
    def __init__(self, parent, api_client, user_data):
        self.create_widgets()
        self.refresh_data()
    
    def create_widgets(self):
        # Crear interfaz
        pass
    
    def refresh_data(self):
        # Cargar datos en hilo separado
        threading.Thread(target=self.load_data, daemon=True).start()
```

## 🐛 Troubleshooting

### **Problemas Comunes**

1. **"Backend no disponible"**
   - Verificar que el backend esté ejecutándose
   - Comprobar URL en `.env`
   - Verificar firewall/antivirus

2. **"Error de autenticación"**
   - Verificar credenciales
   - Comprobar que el token no haya expirado
   - Reiniciar la aplicación

3. **"Error de conexión"**
   - Verificar conexión a internet
   - Comprobar que el servidor esté accesible
   - Revisar logs del backend

4. **Interfaz no responde**
   - Operaciones largas se ejecutan en hilos separados
   - Verificar que no haya bucles infinitos
   - Reiniciar la aplicación

## 📞 Soporte

Para soporte técnico:
- Revisar logs de la aplicación
- Verificar estado del backend
- Comprobar configuración de red
- Contactar al equipo de desarrollo

---

**BDPA Los Encinos** - Aplicación de Escritorio para Gestión de Obras de Telecomunicaciones