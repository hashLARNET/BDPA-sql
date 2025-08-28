"""
Validadores para formularios
"""

import re
from typing import Optional, List
from datetime import datetime

class Validators:
    """Clase con métodos de validación"""
    
    @staticmethod
    def validate_required(value: str, field_name: str) -> Optional[str]:
        """Validar campo requerido"""
        if not value or not value.strip():
            return f"{field_name} es requerido"
        return None
    
    @staticmethod
    def validate_email(email: str) -> Optional[str]:
        """Validar formato de email"""
        if not email:
            return None
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return "Formato de email inválido"
        return None
    
    @staticmethod
    def validate_username(username: str) -> Optional[str]:
        """Validar nombre de usuario"""
        if not username:
            return "Nombre de usuario es requerido"
        
        if len(username) < 3:
            return "Nombre de usuario debe tener al menos 3 caracteres"
        
        if len(username) > 50:
            return "Nombre de usuario no puede tener más de 50 caracteres"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return "Nombre de usuario solo puede contener letras, números y guiones bajos"
        
        return None
    
    @staticmethod
    def validate_password(password: str) -> Optional[str]:
        """Validar contraseña"""
        if not password:
            return "Contraseña es requerida"
        
        if len(password) < 6:
            return "Contraseña debe tener al menos 6 caracteres"
        
        return None
    
    @staticmethod
    def validate_percentage(value: str) -> Optional[str]:
        """Validar porcentaje (0-100)"""
        try:
            percentage = int(value)
            if percentage < 0 or percentage > 100:
                return "Porcentaje debe estar entre 0 y 100"
            return None
        except ValueError:
            return "Porcentaje debe ser un número entero"
    
    @staticmethod
    def validate_torre(torre: str, torres_validas: List[str]) -> Optional[str]:
        """Validar torre"""
        if not torre:
            return "Torre es requerida"
        
        if torre not in torres_validas:
            return f"Torre debe ser una de: {', '.join(torres_validas)}"
        
        return None
    
    @staticmethod
    def validate_piso(piso: str, pisos_validos: List[int]) -> Optional[str]:
        """Validar piso"""
        try:
            piso_int = int(piso)
            if piso_int not in pisos_validos:
                return f"Piso debe ser uno de: {', '.join(map(str, pisos_validos))}"
            return None
        except ValueError:
            return "Piso debe ser un número"
    
    @staticmethod
    def validate_medicion_value(value: str, tipo_medicion: str) -> Optional[str]:
        """Validar valor de medición según el tipo"""
        if not value:
            return "Valor es requerido"
        
        try:
            val = float(value)
            
            # Rangos de validación según tipo
            if tipo_medicion in ['alambrico-t1', 'alambrico-t2', 'coaxial']:
                if val < 0 or val > 100:
                    return "Valor debe estar entre 0 y 100 dBμV"
            elif tipo_medicion == 'fibra':
                if val < -50 or val > 0:
                    return "Valor debe estar entre -50 y 0 dBm"
            elif tipo_medicion == 'wifi':
                if val < -100 or val > -10:
                    return "Valor debe estar entre -100 y -10 dBm"
            
            return None
        except ValueError:
            return "Valor debe ser un número"
    
    @staticmethod
    def validate_date(date_str: str) -> Optional[str]:
        """Validar formato de fecha"""
        if not date_str:
            return "Fecha es requerida"
        
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return None
        except ValueError:
            return "Formato de fecha inválido (YYYY-MM-DD)"