"""
Gestor de sesiones para mantener el login del usuario
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

class SessionManager:
    """Gestor de sesiones de usuario"""
    
    def __init__(self):
        self.session_file = Path.home() / '.bdpa_session.json'
    
    def save_session(self, token: str, user_data: Dict[str, Any]):
        """Guardar sesión del usuario"""
        session_data = {
            'token': token,
            'user_data': user_data,
            'timestamp': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=8)).isoformat()  # 8 horas de validez
        }
        
        try:
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            print(f"Error guardando sesión: {e}")
    
    def get_session(self) -> Optional[Dict[str, Any]]:
        """Obtener datos de sesión guardados"""
        try:
            if not self.session_file.exists():
                return None
            
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            # Verificar si la sesión no ha expirado
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                self.clear_session()
                return None
            
            return session_data
        except Exception as e:
            print(f"Error cargando sesión: {e}")
            return None
    
    def has_valid_session(self) -> bool:
        """Verificar si hay una sesión válida"""
        return self.get_session() is not None
    
    def get_token(self) -> Optional[str]:
        """Obtener token de la sesión"""
        session = self.get_session()
        return session['token'] if session else None
    
    def get_user_data(self) -> Optional[Dict[str, Any]]:
        """Obtener datos del usuario de la sesión"""
        session = self.get_session()
        return session['user_data'] if session else None
    
    def clear_session(self):
        """Limpiar sesión guardada"""
        try:
            if self.session_file.exists():
                self.session_file.unlink()
        except Exception as e:
            print(f"Error limpiando sesión: {e}")