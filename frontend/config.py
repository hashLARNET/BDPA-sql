"""
Configuración de la aplicación Tkinter
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import List

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración de la aplicación"""
    
    # API Configuration
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY = int(os.getenv('RETRY_DELAY', '1'))
    
    # App Configuration
    APP_TITLE = os.getenv('APP_TITLE', 'BDPA - Los Encinos')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # UI Configuration
    WINDOW_WIDTH = int(os.getenv('WINDOW_WIDTH', '1200'))
    WINDOW_HEIGHT = int(os.getenv('WINDOW_HEIGHT', '800'))
    THEME = os.getenv('THEME', 'arc')
    
    # Font Configuration
    FONT_FAMILY = os.getenv('FONT_FAMILY', 'Arial')
    FONT_SIZE = int(os.getenv('FONT_SIZE', '10'))
    FONT_SIZE_TITLE = int(os.getenv('FONT_SIZE_TITLE', '16'))
    FONT_SIZE_HEADER = int(os.getenv('FONT_SIZE_HEADER', '12'))
    
    # Paths
    BASE_DIR = Path(__file__).parent
    ASSETS_DIR = BASE_DIR / 'assets'
    TEMP_DIR = Path(os.getenv('TEMP_DIR', str(BASE_DIR / 'temp')))
    CACHE_DIR = Path(os.getenv('CACHE_DIR', str(BASE_DIR / 'cache')))
    LOG_DIR = BASE_DIR / 'logs'
    
    # Crear directorios si no existen
    ASSETS_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)
    CACHE_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    
    # Colores
    COLORS = {
        'primary': os.getenv('COLOR_PRIMARY', '#3b82f6'),
        'primary_dark': '#2563eb',
        'success': os.getenv('COLOR_SUCCESS', '#22c55e'),
        'warning': os.getenv('COLOR_WARNING', '#f59e0b'),
        'error': os.getenv('COLOR_ERROR', '#ef4444'),
        'gray_50': '#f9fafb',
        'gray_100': '#f3f4f6',
        'gray_200': '#e5e7eb',
        'gray_300': '#d1d5db',
        'gray_500': os.getenv('COLOR_GRAY', '#6b7280'),
        'gray_700': '#374151',
        'gray_900': '#111827'
    }
    
    # Performance Configuration
    CACHE_DURATION = int(os.getenv('CACHE_DURATION', '300'))  # 5 minutos
    CACHE_MAX_ITEMS = int(os.getenv('CACHE_MAX_ITEMS', '1000'))
    AUTO_REFRESH_INTERVAL = int(os.getenv('AUTO_REFRESH_INTERVAL', '300000'))  # 5 minutos
    
    # UI Features
    SHOW_TOOLTIPS = os.getenv('SHOW_TOOLTIPS', 'True').lower() == 'true'
    ENABLE_ANIMATIONS = os.getenv('ENABLE_ANIMATIONS', 'True').lower() == 'true'
    SHOW_DEBUG_INFO = os.getenv('SHOW_DEBUG_INFO', 'False').lower() == 'true'
    
    # Configuración de la obra
    TORRES = os.getenv('TORRES', 'A,B,C,D,E,F,G,H,I,J').split(',')
    PISOS = [int(p) for p in os.getenv('PISOS', '1,3').split(',')]
    SECTORES = os.getenv('SECTORES', 'Norte,Poniente,Oriente').split(',')
    TIPOS_ESPACIO = os.getenv('TIPOS_ESPACIO', 'unidad,sotu,shaft,lateral,antena').split(',')
    TIPOS_MEDICION = os.getenv('TIPOS_MEDICION', 'alambrico-t1,alambrico-t2,coaxial,fibra,wifi,certificacion').split(',')
    ROLES = os.getenv('ROLES_USUARIO', 'Admin,Supervisor,Tecnico,Ayudante').split(',')
    
    # Configuración específica de Los Encinos
    TORRES_SIN_NORTE = os.getenv('TORRES_SIN_NORTE', 'C,H').split(',')
    TOTAL_UNIDADES = int(os.getenv('TOTAL_UNIDADES', '1247'))
    
    @classmethod
    def get_sectores_para_torre(cls, torre: str) -> List[str]:
        """Obtener sectores válidos para una torre específica"""
        if torre in cls.TORRES_SIN_NORTE:
            return [s for s in cls.SECTORES if s != 'Norte']
        return cls.SECTORES
    
    @classmethod
    def validate_torre_sector(cls, torre: str, sector: str) -> bool:
        """Validar combinación de torre y sector"""
        sectores_validos = cls.get_sectores_para_torre(torre)
        return sector in sectores_validos