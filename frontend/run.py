#!/usr/bin/env python3
"""
Script para ejecutar la aplicación BDPA Tkinter
"""

import sys
import os
from pathlib import Path

# Agregar el directorio frontend al path
frontend_dir = Path(__file__).parent
sys.path.insert(0, str(frontend_dir))

# Verificar que el backend esté ejecutándose
def check_backend():
    """Verificar que el backend esté disponible"""
    import requests
    from config import Config
    
    config = Config()
    try:
        response = requests.get(f"{config.API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend disponible")
            return True
        else:
            print(f"⚠️ Backend responde con código {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend no disponible: {e}")
        print(f"   Asegúrate de que el backend esté ejecutándose en {config.API_BASE_URL}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando BDPA - Los Encinos (Frontend Tkinter)")
    print("=" * 60)
    
    # Verificar backend
    if not check_backend():
        print("\n💡 Para iniciar el backend:")
        print("   1. cd al directorio del backend")
        print("   2. python main.py")
        print("\n❌ No se puede continuar sin el backend")
        return
    
    # Importar y ejecutar la aplicación
    try:
        from main import main as app_main
        print("✅ Iniciando interfaz gráfica...")
        app_main()
    except ImportError as e:
        print(f"❌ Error importando la aplicación: {e}")
        print("   Verifica que todas las dependencias estén instaladas")
    except Exception as e:
        print(f"❌ Error ejecutando la aplicación: {e}")

if __name__ == "__main__":
    main()