"""
Cliente para comunicación con la API FastAPI
"""

import requests
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
import os

class APIClient:
    """Cliente para interactuar with la API FastAPI"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token = None
        
        # Configurar headers por defecto
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def set_token(self, token: str):
        """Configurar token de autenticación"""
        self.token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
    
    def clear_token(self):
        """Limpiar token de autenticación"""
        self.token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Realizar petición HTTP"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            raise APIException(f"Error de conexión: {str(e)}")
    
    def _handle_response(self, response: requests.Response) -> Dict[Any, Any]:
        """Manejar respuesta de la API"""
        try:
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 201:
                return response.json()
            elif response.status_code == 204:
                return {}
            elif response.status_code == 401:
                raise APIException("No autorizado. Token inválido o expirado.")
            elif response.status_code == 403:
                raise APIException("Acceso denegado. Permisos insuficientes.")
            elif response.status_code == 404:
                raise APIException("Recurso no encontrado.")
            elif response.status_code == 422:
                error_detail = response.json().get('detail', 'Error de validación')
                raise APIException(f"Error de validación: {error_detail}")
            else:
                error_msg = response.json().get('detail', f'Error HTTP {response.status_code}')
                raise APIException(error_msg)
        except json.JSONDecodeError:
            raise APIException(f"Error HTTP {response.status_code}: {response.text}")
    
    # Métodos de autenticación
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Iniciar sesión"""
        data = {
            'username': username,
            'password': password
        }
        response = self._make_request('POST', '/auth/login', json=data)
        return self._handle_response(response)
    
    def get_current_user(self) -> Dict[str, Any]:
        """Obtener usuario actual"""
        response = self._make_request('GET', '/auth/me')
        return self._handle_response(response)
    
    def verify_token(self) -> bool:
        """Verificar si el token es válido"""
        try:
            self.get_current_user()
            return True
        except:
            return False
    
    # Métodos de usuarios
    def get_usuarios(self) -> List[Dict[str, Any]]:
        """Obtener lista de usuarios"""
        response = self._make_request('GET', '/usuarios/')
        return self._handle_response(response)
    
    def create_usuario(self, usuario_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nuevo usuario"""
        response = self._make_request('POST', '/usuarios/', json=usuario_data)
        return self._handle_response(response)
    
    # Métodos de avances
    def get_avances(self, **filters) -> List[Dict[str, Any]]:
        """Obtener lista de avances con filtros"""
        params = {k: v for k, v in filters.items() if v is not None}
        response = self._make_request('GET', '/avances/', params=params)
        return self._handle_response(response)
    
    def get_avance(self, avance_id: str) -> Dict[str, Any]:
        """Obtener avance por ID"""
        response = self._make_request('GET', f'/avances/{avance_id}')
        return self._handle_response(response)
    
    def create_avance(self, avance_data: Dict[str, Any], foto_path: Optional[str] = None) -> Dict[str, Any]:
        """Crear nuevo avance"""
        if foto_path and os.path.exists(foto_path):
            # Subir con archivo
            files = {'foto': open(foto_path, 'rb')}
            data = {k: str(v) for k, v in avance_data.items()}
            
            # Cambiar content-type para form-data
            headers = dict(self.session.headers)
            if 'Content-Type' in headers:
                del headers['Content-Type']
            
            response = self._make_request('POST', '/avances/with-form', data=data, files=files, headers=headers)
            files['foto'].close()
        else:
            # Subir sin archivo
            response = self._make_request('POST', '/avances/', json=avance_data)
        
        return self._handle_response(response)
    
    def update_avance(self, avance_id: str, avance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar avance"""
        response = self._make_request('PUT', f'/avances/{avance_id}', json=avance_data)
        return self._handle_response(response)
    
    def delete_avance(self, avance_id: str) -> Dict[str, Any]:
        """Eliminar avance"""
        response = self._make_request('DELETE', f'/avances/{avance_id}')
        return self._handle_response(response)
    
    # Métodos de mediciones
    def get_mediciones(self, **filters) -> List[Dict[str, Any]]:
        """Obtener lista de mediciones con filtros"""
        params = {k: v for k, v in filters.items() if v is not None}
        response = self._make_request('GET', '/mediciones/', params=params)
        return self._handle_response(response)
    
    def get_medicion(self, medicion_id: str) -> Dict[str, Any]:
        """Obtener medición por ID"""
        response = self._make_request('GET', f'/mediciones/{medicion_id}')
        return self._handle_response(response)
    
    def create_medicion(self, medicion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nueva medición"""
        response = self._make_request('POST', '/mediciones/', json=medicion_data)
        return self._handle_response(response)
    
    def update_medicion(self, medicion_id: str, medicion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Actualizar medición"""
        response = self._make_request('PUT', f'/mediciones/{medicion_id}', json=medicion_data)
        return self._handle_response(response)
    
    def delete_medicion(self, medicion_id: str) -> Dict[str, Any]:
        """Eliminar medición"""
        response = self._make_request('DELETE', f'/mediciones/{medicion_id}')
        return self._handle_response(response)
    
    # Métodos de dashboard
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Obtener resumen del dashboard"""
        response = self._make_request('GET', '/dashboard/summary')
        return self._handle_response(response)
    
    def get_tower_progress(self) -> List[Dict[str, Any]]:
        """Obtener progreso por torre"""
        response = self._make_request('GET', '/dashboard/tower-progress')
        return self._handle_response(response)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obtener todos los datos del dashboard"""
        response = self._make_request('GET', '/dashboard/')
        return self._handle_response(response)

class APIException(Exception):
    """Excepción personalizada para errores de API"""
    pass