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
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Convertir ALLOWED_ORIGINS de string a lista si es necesario
        if isinstance(self.ALLOWED_ORIGINS, str):
            self.ALLOWED_ORIGINS = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# Instancia global de configuración
settings = Settings()