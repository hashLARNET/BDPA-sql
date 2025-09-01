#!/usr/bin/env python3
"""
Script para instalar todas las dependencias del proyecto BDPA Los Encinos
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command: str, description: str) -> bool:
    """Ejecutar comando y mostrar resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✅ {description} completado")
        if result.stdout:
            print(f"   {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}")
        if e.stderr:
            print(f"   Error: {e.stderr.strip()}")
        if e.stdout:
            print(f"   Output: {e.stdout.strip()}")
        return False

def check_python_version() -> bool:
    """Verificar versión de Python"""
    if sys.version_info < (3, 9):
        print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
        print("   Se requiere Python 3.9 o superior")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detectado")
    return True

def create_virtual_environment() -> bool:
    """Crear entorno virtual si no existe"""
    if Path('venv').exists():
        print("✅ Entorno virtual ya existe")
        return True
    
    return run_command(
        f"{sys.executable} -m venv venv",
        "Creando entorno virtual"
    )

def get_activation_command() -> str:
    """Obtener comando de activación según el SO"""
    if os.name == 'nt':  # Windows
        return "venv\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        return "source venv/bin/activate"

def install_dependencies() -> bool:
    """Instalar dependencias"""
    # Comando de activación
    activate_cmd = get_activation_command()
    
    # Actualizar pip primero
    pip_upgrade = f"{activate_cmd} && python -m pip install --upgrade pip"
    if not run_command(pip_upgrade, "Actualizando pip"):
        return False
    
    # Instalar dependencias principales
    install_cmd = f"{activate_cmd} && pip install -r requirements.txt"
    if not run_command(install_cmd, "Instalando dependencias principales"):
        return False
    
    return True

def verify_installation() -> bool:
    """Verificar que las dependencias se instalaron correctamente"""
    print("🔍 Verificando instalación...")
    
    activate_cmd = get_activation_command()
    
    # Lista de paquetes críticos
    critical_packages = [
        'fastapi',
        'uvicorn', 
        'supabase',
        'pydantic',
        'requests',
        'pillow',
        'ttkthemes'
    ]
    
    for package in critical_packages:
        check_cmd = f"{activate_cmd} && python -c \"import {package}; print(f'{package} OK')\""
        if not run_command(check_cmd, f"Verificando {package}"):
            return False
    
    print("✅ Todas las dependencias verificadas")
    return True

def setup_environment_file() -> bool:
    """Configurar archivo .env"""
    if Path('.env').exists():
        print("✅ Archivo .env ya existe")
        return True
    
    if Path('.env.example').exists():
        return run_command(
            "cp .env.example .env" if os.name != 'nt' else "copy .env.example .env",
            "Creando archivo .env desde .env.example"
        )
    else:
        print("❌ .env.example no encontrado")
        return False

def main():
    """Función principal"""
    print("🏗️  BDPA Los Encinos - Instalador de Dependencias")
    print("=" * 60)
    
    # Verificar Python
    if not check_python_version():
        return
    
    print()
    
    # Pasos de instalación
    steps = [
        ("Crear entorno virtual", create_virtual_environment),
        ("Instalar dependencias", install_dependencies),
        ("Verificar instalación", verify_installation),
        ("Configurar archivo .env", setup_environment_file),
    ]
    
    success_count = 0
    for description, func in steps:
        if func():
            success_count += 1
        else:
            print(f"\n❌ Falló: {description}")
            break
        print()
    
    print("=" * 60)
    
    if success_count == len(steps):
        print("🎉 ¡Instalación completada exitosamente!")
        print("\n📋 Próximos pasos:")
        print("1. Configurar variables de entorno en .env")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_KEY") 
        print("   - SUPABASE_SERVICE_KEY")
        print("   - SECRET_KEY")
        print()
        print("2. Configurar base de datos en Supabase:")
        print("   - Ejecutar migraciones desde supabase/migrations/")
        print("   - Configurar buckets de Storage")
        print()
        print("3. Iniciar el sistema:")
        print("   python scripts/start_system.py")
        print()
        print("4. O iniciar componentes por separado:")
        print("   Backend:  python main.py")
        print("   Frontend: cd frontend && python run.py")
        print()
        print("5. Validar configuración:")
        print("   python scripts/validate_setup.py")
        
    else:
        print(f"⚠️  Instalación incompleta: {success_count}/{len(steps)} pasos completados")
        print("Revisa los errores anteriores y vuelve a ejecutar el script")

if __name__ == "__main__":
    main()