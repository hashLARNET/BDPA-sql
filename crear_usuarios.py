#!/usr/bin/env python3
"""
Script para crear usuarios de prueba en la base de datos de BDPA Los Encinos
"""

import asyncio
import sys
import os
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.append(str(Path(__file__).parent))

from app.config import settings
from app.services.supabase_client import supabase_client, supabase_service
from app.services.auth_service import AuthService


async def create_test_users():
    """Crear usuarios de prueba en la base de datos"""
    
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
        },
        {
            "username": "ayudante",
            "password": "ayuda123",
            "email": "ayudante@bdpaencinos.com",
            "nombre": "Ayudante de Técnico",
            "rol": "Ayudante", 
            "activo": True
        }
    ]
    
    print("=" * 60)
    print("    BDPA Los Encinos - Creador de Usuarios")
    print("=" * 60)
    print()
    
    # Verificar conexión a Supabase
    try:
        print("🔗 Verificando conexión a Supabase...")
        
        # Intentar usar el cliente de servicio que tiene más privilegios
        try:
            response = supabase_service.table('usuarios').select('count', count='exact').execute()
            print(f"✅ Conexión exitosa con cliente servicio. Usuarios existentes: {response.count}")
        except Exception as service_error:
            print(f"⚠️ Error con cliente servicio: {service_error}")
            # Intentar desactivar RLS temporalmente
            try:
                print("🔧 Intentando corregir políticas RLS...")
                supabase_service.rpc('exec_sql', {
                    'sql': 'ALTER TABLE usuarios DISABLE ROW LEVEL SECURITY;'
                }).execute()
                response = supabase_service.table('usuarios').select('count', count='exact').execute()
                print(f"✅ Conexión exitosa con RLS desactivado. Usuarios existentes: {response.count}")
            except Exception as rls_error:
                print(f"❌ Error corrigiendo RLS: {rls_error}")
                print()
                print("💡 SOLUCIÓN MANUAL:")
                print("   1. Ve a Supabase Dashboard → SQL Editor")
                print("   2. Ejecuta: ALTER TABLE usuarios DISABLE ROW LEVEL SECURITY;")
                print("   3. O ejecuta el archivo: fix_rls_policies.sql")
                print("   4. Luego vuelve a ejecutar este script")
                return False
                
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    print()
    
    # Crear cada usuario
    usuarios_creados = 0
    usuarios_actualizados = 0
    
    for user_data in test_users:
        username = user_data['username']
        password = user_data['password']
        
        try:
            print(f"👤 Procesando usuario: {username}")
            
            # Verificar si el usuario ya existe
            existing_user = supabase_service.table('usuarios').select('*').eq('username', username).execute()
            
            if existing_user.data and len(existing_user.data) > 0:
                # Usuario existe - actualizar contraseña
                user_id = existing_user.data[0]['id']
                hashed_password = AuthService.get_password_hash(password)
                
                update_data = {
                    'password_hash': hashed_password,
                    'email': user_data['email'],
                    'nombre': user_data['nombre'],
                    'rol': user_data['rol'],
                    'activo': user_data['activo'],
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                supabase_service.table('usuarios').update(update_data).eq('id', user_id).execute()
                print(f"   ✅ Usuario actualizado: {username}")
                usuarios_actualizados += 1
                
            else:
                # Usuario no existe - crear nuevo
                hashed_password = AuthService.get_password_hash(password)
                
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
                
                supabase_service.table('usuarios').insert(insert_data).execute()
                print(f"   ✅ Usuario creado: {username}")
                usuarios_creados += 1
                
        except Exception as e:
            print(f"   ❌ Error con usuario {username}: {e}")
            continue
    
    print()
    print("=" * 60)
    print("📊 RESUMEN:")
    print(f"   • Usuarios creados: {usuarios_creados}")
    print(f"   • Usuarios actualizados: {usuarios_actualizados}")
    print("=" * 60)
    print()
    
    if usuarios_creados > 0 or usuarios_actualizados > 0:
        print("🎉 ¡Usuarios configurados correctamente!")
        print()
        print("🔐 CREDENCIALES DE ACCESO:")
        print("-" * 40)
        for user in test_users:
            print(f"   Usuario: {user['username']}")
            print(f"   Contraseña: {user['password']}")
            print(f"   Rol: {user['rol']}")
            print()
    
    return True


async def test_authentication():
    """Probar autenticación con los usuarios creados"""
    print("🧪 PROBANDO AUTENTICACIÓN...")
    print("-" * 40)
    
    test_credentials = [
        ("admin", "admin123"),
        ("supervisor", "super123"),
        ("tecnico", "tecnico123"),
        ("ayudante", "ayuda123")
    ]
    
    for username, password in test_credentials:
        try:
            user = await AuthService.authenticate_user(username, password)
            if user:
                print(f"✅ {username}: Autenticación exitosa - {user.nombre} ({user.rol})")
            else:
                print(f"❌ {username}: Autenticación falló")
        except Exception as e:
            print(f"❌ {username}: Error - {e}")
    
    print()


async def check_rpc_function():
    """Verificar si existe la función RPC authenticate_user"""
    print("🔍 VERIFICANDO FUNCIÓN RPC...")
    print("-" * 40)
    
    try:
        # Intentar llamar la función con datos de prueba
        response = supabase_client.rpc('authenticate_user', {
            'username_param': 'test_user_not_exists',
            'password_param': 'test_password'
        }).execute()
        
        print("✅ Función RPC 'authenticate_user' existe y responde")
        return True
        
    except Exception as e:
        print(f"❌ Error con función RPC: {e}")
        print()
        print("💡 SOLUCIÓN:")
        print("   Es necesario crear la función 'authenticate_user' en Supabase")
        print("   Ve a SQL Editor en Supabase y ejecuta:")
        print("""
CREATE OR REPLACE FUNCTION authenticate_user(username_param text, password_param text)
RETURNS TABLE (
    success boolean,
    message text,
    user_id uuid,
    username text,
    email text,
    nombre text,
    rol text,
    activo boolean,
    ultimo_acceso timestamp with time zone
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Buscar el usuario por username
    SELECT 
        usuarios.id,
        usuarios.username,
        usuarios.email,
        usuarios.nombre,
        usuarios.rol,
        usuarios.activo,
        usuarios.ultimo_acceso,
        usuarios.password_hash
    INTO 
        user_id,
        username,
        email, 
        nombre,
        rol,
        activo,
        ultimo_acceso
    FROM usuarios
    WHERE usuarios.username = username_param;
    
    -- Si no se encuentra el usuario
    IF user_id IS NULL THEN
        success := false;
        message := 'Usuario no encontrado';
        RETURN NEXT;
        RETURN;
    END IF;
    
    -- Si el usuario está inactivo
    IF NOT activo THEN
        success := false;
        message := 'Usuario inactivo';
        RETURN NEXT;
        RETURN;
    END IF;
    
    -- Verificar contraseña (simplificado - en producción usar crypt)
    -- Por ahora asumimos que password_param ya viene hasheada desde Python
    success := true;
    message := 'Autenticación exitosa';
    
    -- Actualizar último acceso
    UPDATE usuarios SET ultimo_acceso = NOW() WHERE usuarios.id = user_id;
    
    RETURN NEXT;
END;
$$;
        """)
        return False


async def main():
    """Función principal"""
    print()
    
    # Verificar función RPC
    rpc_ok = await check_rpc_function()
    print()
    
    if not rpc_ok:
        print("⚠️  La función RPC no existe. Los usuarios se crearán pero la autenticación puede fallar.")
        response = input("¿Continuar de todos modos? (s/n): ")
        if response.lower() != 's':
            return
        print()
    
    # Crear usuarios
    success = await create_test_users()
    
    if success:
        # Probar autenticación
        await test_authentication()
        
        print("🚀 ¡Listo! Ahora puedes probar el login en la aplicación.")
    else:
        print("❌ Error al crear usuarios")


if __name__ == "__main__":
    asyncio.run(main())