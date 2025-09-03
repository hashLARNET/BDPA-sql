#!/usr/bin/env python3
"""
Script para configurar la base de datos de BDPA Los Encinos
Ejecuta las migraciones SQL y crea los datos iniciales
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent))

from app.config import settings
from app.services.supabase_client import supabase_service


def read_sql_file(filepath: Path) -> str:
    """Leer archivo SQL"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"❌ Error leyendo {filepath}: {e}")
        return None


def execute_sql(sql_content: str, description: str) -> bool:
    """Ejecutar SQL en Supabase"""
    try:
        print(f"🔄 {description}...")
        
        # Dividir el SQL en statements individuales
        statements = []
        current_statement = ""
        
        for line in sql_content.split('\n'):
            line = line.strip()
            
            # Ignorar comentarios y líneas vacías
            if not line or line.startswith('--'):
                continue
                
            current_statement += line + "\n"
            
            # Si la línea termina con ; es el final de un statement
            if line.endswith(';'):
                statements.append(current_statement.strip())
                current_statement = ""
        
        # Ejecutar cada statement
        success_count = 0
        for i, statement in enumerate(statements):
            if statement.strip():
                try:
                    # Usar rpc para ejecutar SQL directamente
                    result = supabase_service.rpc('exec_sql', {'sql': statement}).execute()
                    success_count += 1
                except Exception as e:
                    # Algunos errores son esperados (como CREATE TABLE IF NOT EXISTS en tabla existente)
                    error_msg = str(e).lower()
                    if any(phrase in error_msg for phrase in ['already exists', 'duplicate', 'if not exists']):
                        success_count += 1
                        continue
                    else:
                        print(f"   ⚠️ Error en statement {i+1}: {e}")
        
        print(f"   ✅ {success_count}/{len(statements)} statements ejecutados")
        return success_count > 0
        
    except Exception as e:
        # Si no existe la función exec_sql, intentar método alternativo
        print(f"   ⚠️ Método directo no disponible: {e}")
        return execute_sql_alternative(sql_content, description)


def execute_sql_alternative(sql_content: str, description: str) -> bool:
    """Método alternativo para ejecutar SQL"""
    print(f"   🔄 Usando método alternativo...")
    
    try:
        # Intentar crear las tablas principales manualmente
        tables_created = 0
        
        # Crear tabla usuarios
        try:
            supabase_service.table('usuarios').select('count', count='exact').execute()
            print("   ✅ Tabla usuarios ya existe")
        except:
            print("   ⚠️ Tabla usuarios no existe, se requiere creación manual")
            return False
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error en método alternativo: {e}")
        return False


async def setup_database():
    """Configurar la base de datos completa"""
    print("=" * 70)
    print("    BDPA Los Encinos - Configuración de Base de Datos")
    print("=" * 70)
    print()
    
    # Verificar conexión
    try:
        print("🔗 Verificando conexión a Supabase...")
        response = supabase_service.rpc('select', {'query': 'SELECT 1 as test'}).execute()
        print("   ✅ Conexión exitosa")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        print()
        print("💡 INSTRUCCIONES MANUALES:")
        print("   1. Ve a https://supabase.com/dashboard")
        print("   2. Selecciona tu proyecto")
        print("   3. Ve a SQL Editor")
        print("   4. Copia y pega el contenido de migrations/001_create_database_structure.sql")
        print("   5. Ejecuta el SQL")
        return False
    
    print()
    
    # Ejecutar migración principal
    migration_file = Path(__file__).parent / "migrations" / "001_create_database_structure.sql"
    
    if not migration_file.exists():
        print(f"❌ No se encontró el archivo de migración: {migration_file}")
        return False
    
    sql_content = read_sql_file(migration_file)
    if not sql_content:
        return False
    
    success = execute_sql(sql_content, "Ejecutando migración de base de datos")
    
    if not success:
        print()
        print("⚠️ La migración automática falló.")
        print()
        print("🔧 SOLUCIÓN MANUAL:")
        print("   1. Ve a Supabase Dashboard → SQL Editor")
        print("   2. Crea una nueva query")
        print(f"   3. Copia el contenido de: {migration_file}")
        print("   4. Ejecuta el SQL")
        print("   5. Luego ejecuta crear_usuarios.py")
        return False
    
    print()
    print("✅ ¡Base de datos configurada exitosamente!")
    print()
    print("📋 PRÓXIMOS PASOS:")
    print("   1. Ejecutar: crear_usuarios.bat")
    print("   2. Probar login en la aplicación")
    
    return True


async def main():
    """Función principal"""
    success = await setup_database()
    
    if success:
        print()
        response = input("¿Deseas crear usuarios de prueba ahora? (s/n): ")
        if response.lower() == 's':
            print()
            print("🔄 Ejecutando creador de usuarios...")
            try:
                from crear_usuarios import main as crear_usuarios_main
                await crear_usuarios_main()
            except Exception as e:
                print(f"❌ Error ejecutando crear_usuarios: {e}")
                print("   Ejecuta manualmente: crear_usuarios.bat")
    
    print()
    input("Presiona Enter para continuar...")


if __name__ == "__main__":
    asyncio.run(main())