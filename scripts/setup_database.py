#!/usr/bin/env python3
"""
Script completo para configurar la base de datos de BDPA Los Encinos
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def verify_supabase_connection():
    """Verificar conexión con Supabase"""
    try:
        from app.services.supabase_client import supabase_client
        
        # Test básico de conexión
        response = supabase_client.table('usuarios').select('count').execute()
        
        print("✅ Conexión con Supabase establecida")
        return True, supabase_client
        
    except Exception as e:
        print(f"❌ Error conectando con Supabase: {e}")
        print("💡 Verifica las variables SUPABASE_URL y SUPABASE_KEY en .env")
        return False, None

async def check_existing_tables(client) -> Dict[str, bool]:
    """Verificar qué tablas ya existen"""
    print("🔍 Verificando tablas existentes...")
    
    tables_to_check = ['usuarios', 'avances', 'mediciones', 'sync_queue', 'app_config', 'auditoria']
    existing_tables = {}
    
    for table in tables_to_check:
        try:
            response = client.table(table).select('count').limit(1).execute()
            existing_tables[table] = True
            print(f"   ✅ {table}")
        except:
            existing_tables[table] = False
            print(f"   ❌ {table}")
    
    return existing_tables

async def check_storage_buckets(client) -> Dict[str, bool]:
    """Verificar buckets de Storage"""
    print("🗂️  Verificando buckets de Storage...")
    
    try:
        buckets = client.storage.list_buckets()
        bucket_names = [b.name for b in buckets] if buckets else []
        
        required_buckets = ['avances-fotos', 'mediciones-docs']
        bucket_status = {}
        
        for bucket in required_buckets:
            exists = bucket in bucket_names
            bucket_status[bucket] = exists
            print(f"   {'✅' if exists else '❌'} {bucket}")
        
        return bucket_status
        
    except Exception as e:
        print(f"❌ Error verificando Storage: {e}")
        return {}

async def test_database_functions(client) -> Dict[str, bool]:
    """Probar funciones de la base de datos"""
    print("🧪 Probando funciones de la base de datos...")
    
    functions_to_test = {
        'calcular_progreso_obra': {},
        'obtener_dashboard_data': {},
        'is_admin': {},
        'hash_password': {'password': 'test123'},
        'authenticate_user': {'username_param': 'admin', 'password_param': 'password123'}
    }
    
    function_status = {}
    
    for func_name, params in functions_to_test.items():
        try:
            if params:
                response = client.rpc(func_name, params).execute()
            else:
                response = client.rpc(func_name).execute()
            
            function_status[func_name] = True
            print(f"   ✅ {func_name}")
            
        except Exception as e:
            function_status[func_name] = False
            print(f"   ❌ {func_name}: {str(e)[:50]}...")
    
    return function_status

async def verify_user_authentication(client):
    """Verificar que la autenticación de usuarios funcione"""
    print("🔐 Verificando autenticación de usuarios...")
    
    try:
        # Probar autenticación con usuario admin
        response = client.rpc('authenticate_user', {
            'username_param': 'admin',
            'password_param': 'password123'
        }).execute()
        
        if response.data and len(response.data) > 0:
            auth_result = response.data[0]
            if auth_result.get('success'):
                print("   ✅ Autenticación funcionando correctamente")
                print(f"   👤 Usuario: {auth_result.get('nombre')} ({auth_result.get('rol')})")
                return True
            else:
                print(f"   ❌ Autenticación falló: {auth_result.get('message')}")
                return False
        else:
            print("   ❌ No se recibió respuesta de autenticación")
            return False
            
    except Exception as e:
        print(f"   ❌ Error probando autenticación: {e}")
        return False

async def verify_password_security(client):
    """Verificar que las funciones de contraseña funcionen"""
    print("🔒 Verificando seguridad de contraseñas...")
    
    try:
        # Probar hash de contraseña
        hash_response = client.rpc('hash_password', {'password': 'test123'}).execute()
        
        if hash_response.data:
            password_hash = hash_response.data
            print("   ✅ Función de hash funcionando")
            
            # Probar verificación de contraseña
            verify_response = client.rpc('verify_password', {
                'password': 'test123',
                'hash': password_hash
            }).execute()
            
            if verify_response.data:
                print("   ✅ Función de verificación funcionando")
                return True
            else:
                print("   ❌ Función de verificación falló")
                return False
        else:
            print("   ❌ Función de hash falló")
            return False
            
    except Exception as e:
        print(f"   ❌ Error probando seguridad de contraseñas: {e}")
        return False

async def run_database_setup():
    """Ejecutar configuración completa de la base de datos"""
    print("🗃️  BDPA Los Encinos - Configuración de Base de Datos")
    print("=" * 60)
    
    # 1. Verificar conexión
    connection_ok, client = await verify_supabase_connection()
    if not connection_ok:
        return False
    
    print()
    
    # 2. Verificar tablas existentes
    existing_tables = await check_existing_tables(client)
    tables_ok = all(existing_tables.values())
    
    if not tables_ok:
        print("\n⚠️  Algunas tablas no existen. Ejecuta primero las migraciones base:")
        print("   1. Ve a tu proyecto Supabase")
        print("   2. Ejecuta las migraciones desde supabase/migrations/")
        print("   3. Vuelve a ejecutar este script")
        return False
    
    print()
    
    # 3. Verificar Storage
    bucket_status = await check_storage_buckets(client)
    storage_ok = all(bucket_status.values())
    
    if not storage_ok:
        print("\n⚠️  Algunos buckets de Storage no existen")
        print("💡 Ejecuta la migración create_storage_buckets.sql")
    
    print()
    
    # 4. Probar funciones
    function_status = await test_database_functions(client)
    
    print()
    
    # 5. Verificar autenticación
    auth_ok = await verify_user_authentication(client)
    
    print()
    
    # 6. Verificar seguridad de contraseñas
    password_ok = await verify_password_security(client)
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 Resumen de Verificación:")
    
    checks = [
        ("Conexión Supabase", connection_ok),
        ("Tablas Base", tables_ok),
        ("Storage Buckets", storage_ok),
        ("Autenticación", auth_ok),
        ("Seguridad Contraseñas", password_ok)
    ]
    
    passed = 0
    for check_name, status in checks:
        print(f"   {'✅' if status else '❌'} {check_name}")
        if status:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(checks)} verificaciones pasaron")
    
    if passed == len(checks):
        print("\n🎉 ¡Base de datos configurada correctamente!")
        print("✅ El sistema está listo para usar")
        
        # Mostrar información adicional
        print("\n📋 Información del Sistema:")
        try:
            # Obtener estadísticas
            stats_response = client.rpc('obtener_estadisticas_backup').execute()
            if stats_response.data:
                stats = stats_response.data
                usuarios_stats = stats.get('usuarios', {})
                print(f"   👥 Usuarios: {usuarios_stats.get('total', 0)} total, {usuarios_stats.get('activos', 0)} activos")
                
                avances_stats = stats.get('avances', {})
                print(f"   📈 Avances: {avances_stats.get('total', 0)} total, {avances_stats.get('completados', 0)} completados")
                
                mediciones_stats = stats.get('mediciones', {})
                print(f"   📏 Mediciones: {mediciones_stats.get('total', 0)} total")
        except:
            pass
        
        return True
    else:
        print(f"\n⚠️  Se encontraron {len(checks) - passed} problemas")
        print("🔧 Revisa los errores anteriores y:")
        print("   - Ejecuta las migraciones faltantes manualmente")
        print("   - Verifica la configuración de Supabase")
        print("   - Contacta al equipo de desarrollo si persisten los problemas")
        
        return False

def show_migration_instructions():
    """Mostrar instrucciones detalladas para migraciones"""
    print("\n📚 Instrucciones Detalladas para Migraciones:")
    print("=" * 60)
    print()
    print("🔧 Opción 1: Ejecución Automática")
    print("   python scripts/run_migrations.py")
    print()
    print("🔧 Opción 2: Ejecución Manual en Supabase")
    print("   1. Ve a https://supabase.com/dashboard")
    print("   2. Selecciona tu proyecto")
    print("   3. Ve a SQL Editor")
    print("   4. Ejecuta en orden:")
    print("      - supabase/migrations/add_password_security.sql")
    print("      - supabase/migrations/optimize_performance.sql")
    print("      - supabase/migrations/add_validation_functions.sql")
    print("      - supabase/migrations/create_backup_functions.sql")
    print()
    print("🔧 Opción 3: Verificación Completa")
    print("   python scripts/setup_database.py")
    print()
    print("💡 Después de ejecutar las migraciones:")
    print("   - Las contraseñas estarán hasheadas de forma segura")
    print("   - Nuevas funciones de validación estarán disponibles")
    print("   - El rendimiento estará optimizado")
    print("   - Funciones de backup estarán configuradas")

def main():
    """Función principal"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        show_migration_instructions()
        return
    
    try:
        success = asyncio.run(run_database_setup())
        
        if success:
            print("\n🚀 ¡Sistema listo para usar!")
            print("   Backend: python main.py")
            print("   Frontend: cd frontend && python run.py")
        else:
            print("\n🔧 Configuración incompleta")
            show_migration_instructions()
            
    except KeyboardInterrupt:
        print("\n⏹️  Configuración cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()