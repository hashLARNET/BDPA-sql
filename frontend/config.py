"""
Configuración de la aplicación Tkinter
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración de la aplicación"""
    
    # API Configuration
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
    
    # App Configuration
    APP_TITLE = os.getenv('APP_TITLE', 'BDPA - Los Encinos')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # UI Configuration
    WINDOW_WIDTH = int(os.getenv('WINDOW_WIDTH', '1200'))
    WINDOW_HEIGHT = int(os.getenv('WINDOW_HEIGHT', '800'))
    THEME = os.getenv('THEME', 'arc')
    
    # Paths
    BASE_DIR = Path(__file__).parent
    ASSETS_DIR = BASE_DIR / 'assets'
    TEMP_DIR = BASE_DIR / 'temp'
    
    # Crear directorios si no existen
    ASSETS_DIR.mkdir(exist_ok=True)
    TEMP_DIR.mkdir(exist_ok=True)
    
    # Colores
    COLORS = {
        'primary': '#3b82f6',
        'primary_dark': '#2563eb',
        'success': '#22c55e',
        'warning': '#f59e0b',
        'error': '#ef4444',
        'gray_50': '#f9fafb',
        'gray_100': '#f3f4f6',
        'gray_200': '#e5e7eb',
        'gray_300': '#d1d5db',
        'gray_500': '#6b7280',
        'gray_700': '#374151',
        'gray_900': '#111827'
    }
    
    # Configuración de la obra
    TORRES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    PISOS = [1, 3]
    SECTORES = ['Norte', 'Poniente', 'Oriente']
    TIPOS_ESPACIO = ['unidad', 'sotu', 'shaft', 'lateral', 'antena']
    TIPOS_MEDICION = ['alambrico-t1', 'alambrico-t2', 'coaxial', 'fibra', 'wifi', 'certificacion']
    ROLES = ['Admin', 'Supervisor', 'Tecnico', 'Ayudante']