#!/usr/bin/env python3
"""
Script para probar la API de BDPA Los Encinos
"""

import asyncio
import httpx
import json
from datetime import datetime


BASE_URL = "http://localhost:8000"


async def test_health():
    """Probar endpoint de salud"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"✅ Health check: {response.status_code}")
            print(f"   Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False


async def test_login():
    """Probar login"""
    async with httpx.AsyncClient() as client:
        try:
            login_data = {
                "username": "admin",
                "password": "password123"
            }
            response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
            print(f"✅ Login: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Token: {data['access_token'][:20]}...")
                return data['access_token']
            else:
                print(f"   Error: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return None


async def test_protected_endpoint(token):
    """Probar endpoint protegido"""
    if not token:
        print("❌ No token available for protected endpoint test")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/auth/me", headers=headers)
            print(f"✅ Protected endpoint (/auth/me): {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"   User: {user_data['nombre']} ({user_data['rol']})")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Protected endpoint test failed: {e}")
            return False


async def test_usuarios_endpoint(token):
    """Probar endpoint de usuarios"""
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/usuarios/", headers=headers)
            print(f"✅ Usuarios endpoint: {response.status_code}")
            
            if response.status_code == 200:
                usuarios = response.json()
                print(f"   Found {len(usuarios)} usuarios")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Usuarios endpoint test failed: {e}")
            return False


async def test_dashboard_endpoint(token):
    """Probar endpoint de dashboard"""
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/dashboard/summary", headers=headers)
            print(f"✅ Dashboard endpoint: {response.status_code}")
            
            if response.status_code == 200:
                dashboard_data = response.json()
                print(f"   Total unidades: {dashboard_data.get('total_unidades', 'N/A')}")
                print(f"   Porcentaje general: {dashboard_data.get('porcentaje_general', 'N/A')}%")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Dashboard endpoint test failed: {e}")
            return False


async def test_create_avance(token):
    """Probar creación de avance"""
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    avance_data = {
        "fecha": datetime.now().isoformat(),
        "torre": "A",
        "piso": 1,
        "sector": "Oriente",
        "tipo_espacio": "unidad",
        "ubicacion": "A101",
        "categoria": "Cableado alámbrico T1",
        "porcentaje": 75,
        "observaciones": "Avance de prueba desde API test"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{BASE_URL}/avances/", json=avance_data, headers=headers)
            print(f"✅ Create avance: {response.status_code}")
            
            if response.status_code == 200:
                avance = response.json()
                print(f"   Created avance ID: {avance['id']}")
                return avance['id']
            else:
                print(f"   Error: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Create avance test failed: {e}")
            return None


async def main():
    """Función principal de testing"""
    print("🧪 Probando API de BDPA Los Encinos")
    print("=" * 50)
    
    # Lista de pruebas
    tests = []
    
    # Test 1: Health check
    health_ok = await test_health()
    tests.append(("Health Check", health_ok))
    
    if not health_ok:
        print("❌ API no está disponible. Verifica que esté ejecutándose en http://localhost:8000")
        return
    
    print()
    
    # Test 2: Login
    token = await test_login()
    tests.append(("Login", token is not None))
    print()
    
    # Test 3: Protected endpoint
    protected_ok = await test_protected_endpoint(token)
    tests.append(("Protected Endpoint", protected_ok))
    print()
    
    # Test 4: Usuarios endpoint
    usuarios_ok = await test_usuarios_endpoint(token)
    tests.append(("Usuarios Endpoint", usuarios_ok))
    print()
    
    # Test 5: Dashboard endpoint
    dashboard_ok = await test_dashboard_endpoint(token)
    tests.append(("Dashboard Endpoint", dashboard_ok))
    print()
    
    # Test 6: Create avance
    avance_id = await test_create_avance(token)
    tests.append(("Create Avance", avance_id is not None))
    print()
    
    # Resumen
    print("=" * 50)
    print("📊 Resumen de pruebas:")
    
    passed = 0
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(tests)} pruebas pasaron")
    
    if passed == len(tests):
        print("🎉 ¡Todas las pruebas pasaron! La API está funcionando correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa la configuración y los logs de la API.")


if __name__ == "__main__":
    asyncio.run(main())