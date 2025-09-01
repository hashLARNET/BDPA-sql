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
    
    print(f"🔍 Verificando backend en {config.API_BASE_URL}")
    
    try:
        # Verificar endpoint de salud con timeout más largo
        response = requests.get(f"{config.API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Backend disponible y saludable")
            print(f"   Estado: {health_data.get('status', 'unknown')}")
            print(f"   Base de datos: {health_data.get('database', 'unknown')}")
            return True
        else:
            print(f"⚠️ Backend responde con código {response.status_code}")
            # Intentar endpoint básico como fallback
            try:
                fallback_response = requests.get(f"{config.API_BASE_URL}/", timeout=5)
                if fallback_response.status_code == 200:
                    print("✅ Backend básico disponible")
                    return True
            except:
                pass
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend no disponible: {e}")
        print(f"   Asegúrate de que el backend esté ejecutándose en {config.API_BASE_URL}")
        print("   Comandos para iniciar el backend:")
        print("   1. cd al directorio raíz del proyecto")
        print("   2. python main.py")
        return False

def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
    print("🔍 Verificando dependencias del frontend...")
    
    required_modules = [
        'tkinter',
        'requests', 
        'PIL',
        'dateutil',
        'ttkthemes'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'PIL':
                import PIL
            elif module == 'dateutil':
                import dateutil
            elif module == 'ttkthemes':
                import ttkthemes
            else:
                __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"   ❌ {module}")
    
    if missing_modules:
        print(f"\n💡 Para instalar dependencias faltantes:")
        print(f"   pip install {' '.join(missing_modules)}")
        return False
    
    print("✅ Todas las dependencias están instaladas")
    return True

def main():
    """Función principal"""
    print("🚀 Iniciando BDPA - Los Encinos (Frontend Tkinter)")
    print("=" * 60)
    print(f"🐍 Python {sys.version}")
    print(f"📁 Directorio: {os.getcwd()}")
    print()
    
    # Verificar dependencias
    if not check_dependencies():
        print("\n❌ No se puede continuar sin las dependencias requeridas")
        return
    
    print()
    
    # Verificar backend
    if not check_backend():
        print("\n💡 Para iniciar el backend:")
        print("   1. cd al directorio raíz del proyecto")
        print("   2. python main.py")
        print("   3. Verificar que el archivo .env esté configurado")
        print("\n❌ No se puede continuar sin el backend")
        return
    
    print()
    
    # Importar y ejecutar la aplicación
    try:
        from main import main as app_main
        print("✅ Iniciando interfaz gráfica...")
        print("🖥️  Abriendo ventana principal...")
        app_main()
    except ImportError as e:
        print(f"❌ Error importando la aplicación: {e}")
        print("   Verifica que todas las dependencias estén instaladas")
        print("   Ejecuta: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error ejecutando la aplicación: {e}")
        print("   Revisa los logs para más detalles")

if __name__ == "__main__":
    main()