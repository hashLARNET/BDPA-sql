#!/usr/bin/env python3
"""
Script de configuración inicial para BDPA Los Encinos Backend
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e.stderr}")
        return False


def check_python_version():
    """Verificar versión de Python"""
    if sys.version_info < (3, 9):
        print("❌ Se requiere Python 3.9 o superior")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True


def create_virtual_environment():
    """Crear entorno virtual"""
    if not os.path.exists("venv"):
        return run_command("python -m venv venv", "Creando entorno virtual")
    else:
        print("✅ Entorno virtual ya existe")
        return True


def activate_and_install_dependencies():
    """Activar entorno virtual e instalar dependencias"""
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate && pip install -r requirements.txt"
    else:  # Unix/Linux/macOS
        activate_cmd = "source venv/bin/activate && pip install -r requirements.txt"
    
    return run_command(activate_cmd, "Instalando dependencias")


def create_env_file():
    """Crear archivo .env si no existe"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            run_command("cp .env.example .env", "Creando archivo .env")
            print("⚠️  Recuerda configurar las variables de entorno en .env")
            return True
        else:
            print("❌ No se encontró .env.example")
            return False
    else:
        print("✅ Archivo .env ya existe")
        return True


def check_supabase_connection():
    """Verificar conexión con Supabase"""
    print("🔄 Verificando configuración de Supabase...")
    
    # Leer variables de entorno
    env_vars = {}
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    env_vars[key] = value
    
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = [var for var in required_vars if var not in env_vars or not env_vars[var]]
    
    if missing_vars:
        print(f"⚠️  Variables faltantes en .env: {', '.join(missing_vars)}")
        return False
    
    print("✅ Variables de Supabase configuradas")
    return True


def main():
    """Función principal de configuración"""
    print("🚀 Configurando BDPA Los Encinos Backend")
    print("=" * 50)
    
    steps = [
        ("Verificar versión de Python", check_python_version),
        ("Crear entorno virtual", create_virtual_environment),
        ("Instalar dependencias", activate_and_install_dependencies),
        ("Crear archivo .env", create_env_file),
        ("Verificar configuración de Supabase", check_supabase_connection),
    ]
    
    success_count = 0
    for description, func in steps:
        if func():
            success_count += 1
        print()
    
    print("=" * 50)
    if success_count == len(steps):
        print("🎉 Configuración completada exitosamente!")
        print("\n📋 Próximos pasos:")
        print("1. Configurar las variables de entorno en .env")
        print("2. Ejecutar las migraciones de Supabase")
        print("3. Ejecutar: python main.py")
        print("4. Visitar: http://localhost:8000/docs")
    else:
        print(f"⚠️  Configuración parcial: {success_count}/{len(steps)} pasos completados")
        print("Revisa los errores anteriores y vuelve a ejecutar el script")


if __name__ == "__main__":
    main()