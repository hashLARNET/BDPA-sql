from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.config import settings
from app.routers import auth, avances, mediciones, dashboard, usuarios
from app.services.supabase_client import supabase_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    # Startup
    print(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Modo debug: {'Habilitado' if settings.DEBUG else 'Deshabilitado'}")
    print(f"CORS habilitado para: {', '.join(settings.ALLOWED_ORIGINS)}")
    
    # Verificar conexión con Supabase
    try:
        # Test de conexión más robusto
        response = supabase_client.table('usuarios').select('count').execute()
        usuarios_count = len(response.data) if response.data else 0
        print("✅ Conexión con Supabase establecida")
        print(f"📊 Usuarios en sistema: {usuarios_count}")
        
        # Verificar buckets de Storage
        try:
            buckets = supabase_client.storage.list_buckets()
            bucket_names = [b.name for b in buckets] if buckets else []
            if 'avances-fotos' in bucket_names and 'mediciones-docs' in bucket_names:
                print("✅ Buckets de Storage configurados correctamente")
            else:
                print("⚠️  Algunos buckets de Storage no están configurados")
        except Exception as storage_error:
            print(f"⚠️  Error verificando Storage: {storage_error}")
            
    except Exception as e:
        print(f"❌ Error crítico conectando con Supabase: {e}")
        print("💡 Verifica las variables SUPABASE_URL y SUPABASE_KEY en .env")
    
    yield
    
    # Shutdown
    print("🛑 Cerrando aplicación BDPA Los Encinos")
    print("👋 ¡Hasta luego!")


# Crear instancia de FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API backend para la gestión de obras de telecomunicaciones - Los Encinos",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Manejador global de excepciones
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Error interno del servidor",
            "status_code": 500
        }
    )

# Rutas principales
@app.get("/")
async def root():
    return {
        "message": f"Bienvenido a {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "online"
    }

@app.get("/health")
async def health_check():
    """Endpoint de verificación de salud"""
    try:
        # Verificar conexión con Supabase
        response = supabase_client.table('usuarios').select('count').execute()
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )

# Incluir routers
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["Usuarios"])
app.include_router(avances.router, prefix="/avances", tags=["Avances"])
app.include_router(mediciones.router, prefix="/mediciones", tags=["Mediciones"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )