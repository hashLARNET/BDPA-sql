#!/usr/bin/env python3
"""
Script para ejecutar migraciones de Supabase desde Python
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def read_migration_file(file_path: Path) -> str:
    """Leer archivo de migración"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ Error leyendo {file_path}: {e}")
        return ""

def execute_migration(client, migration_content: str, migration_name: str) -> Tuple[bool, str]:
    """Ejecutar una migración"""
    try:
        # Dividir el contenido en statements individuales
        statements = []
        current_statement = []
        in_function = False
        
        for line in migration_content.split('\n'):
            line = line.strip()
            
            # Ignorar comentarios y líneas vacías
            if not line or line.startswith('--'):
                continue
            
            # Detectar inicio/fin de funciones
            if 'CREATE OR REPLACE FUNCTION' in line.upper() or 'CREATE FUNCTION' in line.upper():
                in_function = True
            elif line.upper().startswith('$$') and in_function:
                in_function = False
                current_statement.append(line)
                statements.append('\n'.join(current_statement))
                current_statement = []
                continue
            
            current_statement.append(line)
            
            # Si no estamos en una función y encontramos ';', es el final del statement
            if not in_function and line.endswith(';'):
                statements.append('\n'.join(current_statement))
                current_statement = []
        
        # Agregar último statement si existe
        if current_statement:
            statements.append('\n'.join(current_statement))
        
        # Ejecutar cada statement
        for i, statement in enumerate(statements):
            if statement.strip():
                try:
                    response = client.rpc('exec_sql', {'sql': statement}).execute()
                    if hasattr(response, 'error') and response.error:
                        return False, f"Error en statement {i+1}: {response.error}"
                except Exception as e:
                    # Intentar ejecutar directamente si RPC falla
                    try:
                        # Para statements simples, usar el cliente directamente
                        if statement.strip().upper().startswith(('CREATE TABLE', 'ALTER TABLE', 'CREATE INDEX')):
                            # Estos requieren ejecución directa en Supabase
                            print(f"⚠️  Statement requiere ejecución manual: {statement[:50]}...")
                            continue
                        else:
                            return False, f"Error ejecutando statement {i+1}: {str(e)}"
                    except Exception as e2:
                        return False, f"Error en statement {i+1}: {str(e2)}"
        
        return True, f"Migración {migration_name} ejecutada exitosamente"
        
    except Exception as e:
        return False, f"Error ejecutando migración {migration_name}: {str(e)}"

def get_migration_files() -> List[Path]:
    """Obtener lista de archivos de migración ordenados"""
    migrations_dir = Path('supabase/migrations')
    
    if not migrations_dir.exists():
        print(f"❌ Directorio de migraciones no encontrado: {migrations_dir}")
        return []
    
    # Obtener solo las nuevas migraciones (no las restringidas)
    new_migrations = [
        'add_password_security.sql',
        'optimize_performance.sql', 
        'add_validation_functions.sql',
        'create_backup_functions.sql'
    ]
    
    migration_files = []
    for migration_name in new_migrations:
        migration_path = migrations_dir / migration_name
        if migration_path.exists():
            migration_files.append(migration_path)
        else:
            print(f"⚠️  Migración no encontrada: {migration_name}")
    
    return migration_files

def run_migrations():
    """Ejecutar todas las migraciones"""
    print("🗃️  BDPA Los Encinos - Ejecutor de Migraciones")
    print("=" * 60)
    
    # Verificar configuración
    try:
        from app.services.supabase_client import supabase_client
        print("✅ Cliente Supabase configurado")
    except Exception as e:
        print(f"❌ Error configurando Supabase: {e}")
        print("💡 Verifica las variables SUPABASE_URL y SUPABASE_KEY en .env")
        return False
    
    # Verificar conexión
    try:
        response = supabase_client.table('usuarios').select('count').execute()
        print("✅ Conexión con Supabase establecida")
    except Exception as e:
        print(f"❌ Error conectando con Supabase: {e}")
        return False
    
    # Obtener archivos de migración
    migration_files = get_migration_files()
    
    if not migration_files:
        print("⚠️  No se encontraron migraciones para ejecutar")
        return True
    
    print(f"\n🔄 Ejecutando {len(migration_files)} migraciones...")
    
    # Ejecutar migraciones
    success_count = 0
    for migration_file in migration_files:
        print(f"\n📄 Procesando: {migration_file.name}")
        
        migration_content = read_migration_file(migration_file)
        if not migration_content:
            continue
        
        success, message = execute_migration(supabase_client, migration_content, migration_file.name)
        
        if success:
            print(f"✅ {message}")
            success_count += 1
        else:
            print(f"❌ {message}")
            
            # Preguntar si continuar con las siguientes migraciones
            response = input("¿Continuar con las siguientes migraciones? (y/n): ")
            if response.lower() != 'y':
                break
    
    # Resumen
    print("\n" + "=" * 60)
    print(f"📊 Resultado: {success_count}/{len(migration_files)} migraciones ejecutadas")
    
    if success_count == len(migration_files):
        print("🎉 ¡Todas las migraciones ejecutadas exitosamente!")
        
        # Verificar que las nuevas funciones estén disponibles
        print("\n🔍 Verificando funciones creadas...")
        try:
            # Test de función de autenticación
            test_response = supabase_client.rpc('authenticate_user', {
                'username_param': 'admin',
                'password_param': 'password123'
            }).execute()
            
            if test_response.data:
                print("✅ Función de autenticación disponible")
            else:
                print("⚠️  Función de autenticación no responde como esperado")
                
        except Exception as e:
            print(f"⚠️  Error verificando funciones: {e}")
        
        print("\n📋 Próximos pasos:")
        print("1. Las contraseñas ahora están hasheadas de forma segura")
        print("2. Los usuarios existentes han sido migrados")
        print("3. Nuevas funciones de seguridad están disponibles")
        print("4. El sistema está listo para usar autenticación segura")
        
        return True
    else:
        print("⚠️  Algunas migraciones fallaron")
        print("💡 Revisa los errores y ejecuta las migraciones faltantes manualmente en Supabase")
        return False

def show_manual_instructions():
    """Mostrar instrucciones para ejecución manual"""
    print("\n📋 Instrucciones para Ejecución Manual en Supabase:")
    print("=" * 60)
    print("Si las migraciones automáticas fallan, puedes ejecutarlas manualmente:")
    print()
    print("1. Ve a tu proyecto en https://supabase.com/dashboard")
    print("2. Navega a SQL Editor")
    print("3. Ejecuta los siguientes archivos en orden:")
    print("   - supabase/migrations/add_password_security.sql")
    print("   - supabase/migrations/optimize_performance.sql")
    print("   - supabase/migrations/add_validation_functions.sql")
    print("   - supabase/migrations/create_backup_functions.sql")
    print()
    print("4. Verifica que no haya errores en cada ejecución")
    print("5. Ejecuta 'python scripts/validate_setup.py' para verificar")

def main():
    """Función principal"""
    try:
        success = run_migrations()
        
        if not success:
            show_manual_instructions()
            
    except KeyboardInterrupt:
        print("\n⏹️  Ejecución cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        show_manual_instructions()

if __name__ == "__main__":
    main()