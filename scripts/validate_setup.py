#!/usr/bin/env python3
"""
Script para validar la configuración completa del proyecto BDPA Los Encinos
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def check_python_version() -> Tuple[bool, str]:
    """Verificar versión de Python"""
    if sys.version_info < (3, 9):
        return False, f"Python {sys.version_info.major}.{sys.version_info.minor} detectado. Se requiere Python 3.9+"
    return True, f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def check_dependencies() -> Tuple[bool, List[str]]:
    """Verificar dependencias instaladas"""
    required_packages = [
        'fastapi', 'uvicorn', 'supabase', 'pydantic', 'jose', 'passlib',
        'tkinter', 'requests', 'PIL', 'ttkthemes'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            elif package == 'jose':
                import jose
            elif package == 'ttkthemes':
                import ttkthemes
            else:
                __import__(package)
        except ImportError:
            missing.append(package)
    
    return len(missing) == 0, missing

def check_env_file() -> Tuple[bool, List[str]]:
    """Verificar archivo .env"""
    env_path = Path('.env')
    if not env_path.exists():
        return False, ["Archivo .env no existe"]
    
    required_vars = [
        'SUPABASE_URL', 'SUPABASE_KEY', 'SUPABASE_SERVICE_KEY', 'SECRET_KEY'
    ]
    
    missing_vars = []
    env_vars = {}
    
    try:
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    except Exception as e:
        return False, [f"Error leyendo .env: {e}"]
    
    for var in required_vars:
        if var not in env_vars or not env_vars[var]:
            missing_vars.append(var)
    
    issues = []
    if missing_vars:
        issues.append(f"Variables faltantes: {', '.join(missing_vars)}")
    
    # Validaciones específicas
    if 'SECRET_KEY' in env_vars and len(env_vars['SECRET_KEY']) < 32:
        issues.append("SECRET_KEY debe tener al menos 32 caracteres")
    
    if 'SUPABASE_URL' in env_vars and not env_vars['SUPABASE_URL'].startswith('https://'):
        issues.append("SUPABASE_URL debe ser una URL HTTPS válida")
    
    return len(issues) == 0, issues

def check_file_structure() -> Tuple[bool, List[str]]:
    """Verificar estructura de archivos"""
    required_files = [
        'main.py',
        'requirements.txt',
        'app/__init__.py',
        'app/config.py',
        'app/models/__init__.py',
        'app/routers/__init__.py',
        'app/services/__init__.py',
        'frontend/main.py',
        'frontend/config.py',
        'frontend/run.py',
        'frontend/services/api_client.py',
        'frontend/ui/main_window.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    return len(missing_files) == 0, missing_files

async def check_backend_connection() -> Tuple[bool, str]:
    """Verificar conexión con el backend"""
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get('http://localhost:8000/health', timeout=5)
            if response.status_code == 200:
                data = response.json()
                return True, f"Backend disponible - {data.get('status', 'unknown')}"
            else:
                return False, f"Backend responde con código {response.status_code}"
    except Exception as e:
        return False, f"Backend no disponible: {str(e)}"

async def check_supabase_connection() -> Tuple[bool, str]:
    """Verificar conexión con Supabase"""
    try:
        from app.services.supabase_client import supabase_client
        
        # Test básico de conexión
        response = supabase_client.table('usuarios').select('count').execute()
        usuarios_count = len(response.data) if response.data else 0
        
        # Verificar buckets de Storage
        buckets = supabase_client.storage.list_buckets()
        bucket_names = [b.name for b in buckets] if buckets else []
        
        required_buckets = ['avances-fotos', 'mediciones-docs']
        missing_buckets = [b for b in required_buckets if b not in bucket_names]
        
        if missing_buckets:
            return False, f"Buckets faltantes: {', '.join(missing_buckets)}"
        
        return True, f"Supabase conectado - {usuarios_count} usuarios, {len(bucket_names)} buckets"
        
    except Exception as e:
        return False, f"Error conectando con Supabase: {str(e)}"

def print_section(title: str):
    """Imprimir sección con formato"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print('='*60)

def print_result(check_name: str, success: bool, details: Any):
    """Imprimir resultado de verificación"""
    status = "✅" if success else "❌"
    print(f"{status} {check_name}")
    
    if isinstance(details, str):
        print(f"   {details}")
    elif isinstance(details, list):
        for detail in details:
            print(f"   - {detail}")

async def main():
    """Función principal de validación"""
    print("🚀 BDPA Los Encinos - Validación de Configuración")
    print("Sistema de Gestión de Obras de Telecomunicaciones")
    
    # Lista de verificaciones
    checks = []
    
    # 1. Verificar Python
    print_section("Verificación del Entorno")
    python_ok, python_info = check_python_version()
    print_result("Versión de Python", python_ok, python_info)
    checks.append(("Python", python_ok))
    
    # 2. Verificar dependencias
    deps_ok, missing_deps = check_dependencies()
    if missing_deps:
        print_result("Dependencias", deps_ok, [f"Faltantes: {', '.join(missing_deps)}"])
    else:
        print_result("Dependencias", deps_ok, "Todas las dependencias instaladas")
    checks.append(("Dependencias", deps_ok))
    
    # 3. Verificar archivo .env
    env_ok, env_issues = check_env_file()
    print_result("Archivo .env", env_ok, env_issues if env_issues else "Configuración correcta")
    checks.append(("Configuración", env_ok))
    
    # 4. Verificar estructura de archivos
    files_ok, missing_files = check_file_structure()
    if missing_files:
        print_result("Estructura de archivos", files_ok, [f"Faltantes: {', '.join(missing_files)}"])
    else:
        print_result("Estructura de archivos", files_ok, "Todos los archivos presentes")
    checks.append(("Archivos", files_ok))
    
    # 5. Verificar conexiones (solo si configuración básica está OK)
    if env_ok:
        print_section("Verificación de Conexiones")
        
        # Backend
        backend_ok, backend_info = await check_backend_connection()
        print_result("Backend API", backend_ok, backend_info)
        checks.append(("Backend", backend_ok))
        
        # Supabase
        supabase_ok, supabase_info = await check_supabase_connection()
        print_result("Supabase", supabase_ok, supabase_info)
        checks.append(("Supabase", supabase_ok))
    
    # Resumen final
    print_section("Resumen de Validación")
    
    passed = sum(1 for _, success in checks if success)
    total = len(checks)
    
    print(f"📊 Resultado: {passed}/{total} verificaciones pasaron")
    
    if passed == total:
        print("\n🎉 ¡Configuración completa y correcta!")
        print("✅ El sistema está listo para usar")
        print("\n🚀 Próximos pasos:")
        print("   1. Ejecutar backend: python main.py")
        print("   2. Ejecutar frontend: cd frontend && python run.py")
        print("   3. Login con: admin / password123")
    else:
        print(f"\n⚠️  Se encontraron {total - passed} problemas")
        print("🔧 Revisa los errores anteriores y:")
        
        if not deps_ok:
            print("   - Instala dependencias: pip install -r requirements.txt")
        if not env_ok:
            print("   - Configura archivo .env basado en .env.example")
        if not files_ok:
            print("   - Verifica que todos los archivos estén presentes")
        
        print("\n💡 Ejecuta este script nuevamente después de corregir los problemas")

if __name__ == "__main__":
    asyncio.run(main())