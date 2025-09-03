from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Información de la aplicación
    APP_NAME: str = "BDPA - Los Encinos API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Configuración de Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_KEY: str
    DATABASE_URL: str
    
    # Configuración JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configuración CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080"
    ]
    
    # Configuración de archivos
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # Configuración de la obra
    OBRA_ID: str = "los-encinos-001"
    TOTAL_UNIDADES: int = 1247
    TORRES: List[str] = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]
    PISOS: List[int] = [1, 3]
    SECTORES: List[str] = ["Norte", "Poniente", "Oriente"]
    
    # Configuración de performance
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    QUERY_TIMEOUT: int = 30
    
    # Configuración de logs
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "bdpa.log"
    
    # Configuración de seguridad
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60
    
    # Configuración de producción
    PRODUCTION: bool = False
    SSL_VERIFY: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Convertir ALLOWED_ORIGINS de string a lista si es necesario
        if isinstance(self.ALLOWED_ORIGINS, str):
            self.ALLOWED_ORIGINS = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        
        # Validar configuración crítica
        self._validate_config()
    
    def _validate_config(self):
        """Validar configuración crítica"""
        if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY debe tener al menos 32 caracteres")
        
        if not self.SUPABASE_URL or not self.SUPABASE_URL.startswith('https://'):
            raise ValueError("SUPABASE_URL debe ser una URL HTTPS válida")
        
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY es requerida")
    
    @property
    def is_development(self) -> bool:
        """Verificar si está en modo desarrollo"""
        return self.DEBUG and not self.PRODUCTION
    
    @property
    def cors_origins(self) -> List[str]:
        """Obtener orígenes CORS como lista"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS


# Instancia global de configuración
settings = Settings()