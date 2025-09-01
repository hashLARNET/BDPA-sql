#!/usr/bin/env python3
"""
Script para iniciar el sistema completo BDPA Los Encinos
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path
from typing import List, Optional

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

class SystemManager:
    """Gestor del sistema completo"""
    
    def __init__(self):
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.running = False
    
    def start_backend(self) -> bool:
        """Iniciar backend FastAPI"""
        print("🚀 Iniciando backend FastAPI...")
        
        try:
            # Verificar que main.py existe
            if not Path('main.py').exists():
                print("❌ main.py no encontrado")
                return False
            
            # Iniciar proceso del backend
            self.backend_process = subprocess.Popen([
                sys.executable, 'main.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Esperar un momento para verificar que inició correctamente
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                print("✅ Backend iniciado correctamente")
                return True
            else:
                stdout, stderr = self.backend_process.communicate()
                print(f"❌ Error iniciando backend:")
                print(f"   STDOUT: {stdout}")
                print(f"   STDERR: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error iniciando backend: {e}")
            return False
    
    def start_frontend(self) -> bool:
        """Iniciar frontend Tkinter"""
        print("🖥️  Iniciando frontend Tkinter...")
        
        try:
            # Verificar que el directorio frontend existe
            frontend_dir = Path('frontend')
            if not frontend_dir.exists():
                print("❌ Directorio frontend no encontrado")
                return False
            
            # Verificar que run.py existe
            run_script = frontend_dir / 'run.py'
            if not run_script.exists():
                print("❌ frontend/run.py no encontrado")
                return False
            
            # Cambiar al directorio frontend
            original_cwd = os.getcwd()
            os.chdir(frontend_dir)
            
            # Iniciar proceso del frontend
            self.frontend_process = subprocess.Popen([
                sys.executable, 'run.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Restaurar directorio original
            os.chdir(original_cwd)
            
            # Esperar un momento para verificar que inició
            time.sleep(2)
            
            if self.frontend_process.poll() is None:
                print("✅ Frontend iniciado correctamente")
                return True
            else:
                stdout, stderr = self.frontend_process.communicate()
                print(f"❌ Error iniciando frontend:")
                print(f"   STDOUT: {stdout}")
                print(f"   STDERR: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error iniciando frontend: {e}")
            return False
    
    def wait_for_backend(self, timeout: int = 30) -> bool:
        """Esperar a que el backend esté disponible"""
        print("⏳ Esperando que el backend esté disponible...")
        
        import requests
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get('http://localhost:8000/health', timeout=2)
                if response.status_code == 200:
                    print("✅ Backend disponible y respondiendo")
                    return True
            except:
                pass
            
            time.sleep(1)
            print(".", end="", flush=True)
        
        print(f"\n❌ Backend no disponible después de {timeout} segundos")
        return False
    
    def stop_processes(self):
        """Detener todos los procesos"""
        print("\n🛑 Deteniendo procesos...")
        
        if self.frontend_process and self.frontend_process.poll() is None:
            print("   Cerrando frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        if self.backend_process and self.backend_process.poll() is None:
            print("   Cerrando backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        print("✅ Procesos detenidos")
    
    def signal_handler(self, signum, frame):
        """Manejar señales del sistema"""
        print(f"\n📡 Señal {signum} recibida")
        self.running = False
        self.stop_processes()
        sys.exit(0)
    
    def run(self):
        """Ejecutar el sistema completo"""
        print("🏗️  BDPA Los Encinos - Iniciador del Sistema")
        print("=" * 60)
        
        # Configurar manejadores de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # 1. Iniciar backend
            if not self.start_backend():
                print("❌ No se pudo iniciar el backend")
                return False
            
            # 2. Esperar que el backend esté disponible
            if not self.wait_for_backend():
                print("❌ Backend no responde")
                self.stop_processes()
                return False
            
            # 3. Iniciar frontend
            if not self.start_frontend():
                print("❌ No se pudo iniciar el frontend")
                self.stop_processes()
                return False
            
            print("\n🎉 Sistema iniciado correctamente!")
            print("📊 Dashboard: http://localhost:8000/docs")
            print("🖥️  Aplicación de escritorio abierta")
            print("\n💡 Credenciales de desarrollo:")
            print("   Usuario: admin")
            print("   Contraseña: password123")
            print("\n⏹️  Presiona Ctrl+C para detener el sistema")
            
            # Mantener el script ejecutándose
            self.running = True
            while self.running:
                # Verificar que los procesos sigan ejecutándose
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ Backend se detuvo inesperadamente")
                    break
                
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("ℹ️  Frontend cerrado por el usuario")
                    break
                
                time.sleep(1)
            
            return True
            
        except KeyboardInterrupt:
            print("\n⏹️  Deteniendo sistema...")
            return True
        except Exception as e:
            print(f"❌ Error ejecutando sistema: {e}")
            return False
        finally:
            self.stop_processes()

def run_validation():
    """Ejecutar validación previa"""
    print("🔍 Validando configuración del sistema...")
    
    # Verificar Python
    python_ok, python_info = check_python_version()
    print(f"{'✅' if python_ok else '❌'} Python: {python_info}")
    
    if not python_ok:
        return False
    
    # Verificar dependencias
    deps_ok, missing_deps = check_dependencies()
    if deps_ok:
        print("✅ Dependencias: Todas instaladas")
    else:
        print(f"❌ Dependencias faltantes: {', '.join(missing_deps)}")
        print("💡 Ejecuta: pip install -r requirements.txt")
        return False
    
    # Verificar .env
    env_ok, env_issues = check_env_file()
    if env_ok:
        print("✅ Configuración: .env correcto")
    else:
        print("❌ Configuración:")
        for issue in env_issues:
            print(f"   - {issue}")
        print("💡 Configura el archivo .env basado en .env.example")
        return False
    
    # Verificar archivos
    files_ok, missing_files = check_file_structure()
    if files_ok:
        print("✅ Archivos: Estructura correcta")
    else:
        print("❌ Archivos faltantes:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True

def main():
    """Función principal"""
    # Validación previa
    if not run_validation():
        print("\n❌ Validación fallida. Corrige los problemas antes de continuar.")
        return
    
    print("\n✅ Validación exitosa. Iniciando sistema...")
    
    # Iniciar sistema
    manager = SystemManager()
    success = manager.run()
    
    if success:
        print("\n👋 Sistema detenido correctamente")
    else:
        print("\n❌ Sistema detenido con errores")

if __name__ == "__main__":
    main()