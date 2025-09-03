#!/usr/bin/env python3
"""
Script simplificado para crear usuarios - SIN RLS
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent))

from app.config import settings
from app.services.supabase_client import supabase_service
from app.services.auth_service import AuthService


async def create_users_simple():
    """Crear usuarios usando INSERT directo sin RLS"""
    
    # Usuarios de prueba
    test_users = [
        {
            "username": "admin",
            "password": "admin123",
            "email": "admin@bdpaencinos.com",
            "nombre": "Administrador BDPA",
            "rol": "Admin",
            "activo": True
        },
        {
            "username": "supervisor",
            "password": "super123", 
            "email": "supervisor@bdpaencinos.com",
            "nombre": "Supervisor de Obra",
            "rol": "Supervisor",
            "activo": True
        },
        {
            "username": "tecnico",
            "password": "tecnico123",
            "email": "tecnico@bdpaencinos.com",
            "nombre": "Técnico de Campo",
            "rol": "Tecnico", 
            "activo": True
        }
    ]
    
    print("=" * 60)
    print("    BDPA - Creador Simple de Usuarios")
    print("=" * 60)
    print()
    
    usuarios_creados = 0
    
    for user_data in test_users:
        username = user_data['username']
        password = user_data['password']
        
        try:
            print(f"👤 Creando usuario: {username}")
            
            # Hash de la contraseña
            hashed_password = AuthService.get_password_hash(password)
            
            # Usar SQL directo para evitar problemas RLS
            sql = f"""
            INSERT INTO usuarios (username, password_hash, email, nombre, rol, activo, created_at, updated_at)
            VALUES ('{username}', '{hashed_password}', '{user_data['email']}', '{user_data['nombre']}', '{user_data['rol']}', {user_data['activo']}, NOW(), NOW())
            ON CONFLICT (username) 
            DO UPDATE SET 
                password_hash = EXCLUDED.password_hash,
                email = EXCLUDED.email,
                nombre = EXCLUDED.nombre,
                rol = EXCLUDED.rol,
                activo = EXCLUDED.activo,
                updated_at = NOW();
            """
            
            # Ejecutar SQL usando RPC si está disponible
            try:
                supabase_service.rpc('exec_sql', {'sql': sql}).execute()
                print(f"   ✅ Usuario {username} procesado correctamente")
                usuarios_creados += 1
            except Exception as rpc_error:
                # Si no existe exec_sql, usar el cliente con privilegios de servicio
                print(f"   ⚠️ RPC no disponible, usando método directo...")
                
                # Crear datos para inserción directa
                insert_data = {
                    'username': username,
                    'password_hash': hashed_password,
                    'email': user_data['email'],
                    'nombre': user_data['nombre'],
                    'rol': user_data['rol'],
                    'activo': user_data['activo'],
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                # Intentar upsert
                result = supabase_service.table('usuarios').upsert(insert_data, on_conflict='username').execute()
                print(f"   ✅ Usuario {username} procesado (método directo)")
                usuarios_creados += 1
                
        except Exception as e:
            print(f"   ❌ Error con usuario {username}: {e}")
            continue
    
    print()
    print("=" * 60)
    print(f"📊 Usuarios procesados: {usuarios_creados}")
    print("=" * 60)
    print()
    
    if usuarios_creados > 0:
        print("🎉 ¡Usuarios creados correctamente!")
        print()
        print("🔐 CREDENCIALES DE ACCESO:")
        print("-" * 40)
        for user in test_users:
            print(f"   Usuario: {user['username']}")
            print(f"   Contraseña: {user['password']}")
            print(f"   Rol: {user['rol']}")
            print()
    
    return usuarios_creados > 0


async def main():
    """Función principal"""
    print()
    
    success = await create_users_simple()
    
    if success:
        print("🚀 ¡Listo! Ahora puedes probar el login en la aplicación.")
        
        # Probar una autenticación rápida
        try:
            print()
            print("🧪 Probando autenticación...")
            user = await AuthService.authenticate_user("admin", "admin123")
            if user:
                print("✅ Prueba de autenticación exitosa")
            else:
                print("⚠️ La autenticación falló - revisar configuración")
        except Exception as e:
            print(f"⚠️ Error probando autenticación: {e}")
    else:
        print("❌ Error al crear usuarios")
    
    print()
    input("Presiona Enter para continuar...")


if __name__ == "__main__":
    asyncio.run(main())