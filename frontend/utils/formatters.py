"""
Formateadores para mostrar datos en la UI
"""

from datetime import datetime
from typing import Any, Optional

class Formatters:
    """Clase con métodos de formateo"""
    
    @staticmethod
    def format_date(date_str: str, format_type: str = 'short') -> str:
        """Formatear fecha"""
        try:
            if isinstance(date_str, str):
                # Manejar diferentes formatos de fecha
                if 'T' in date_str:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            else:
                date_obj = date_str
            
            if format_type == 'short':
                return date_obj.strftime('%d/%m/%Y')
            elif format_type == 'long':
                return date_obj.strftime('%d de %B de %Y')
            elif format_type == 'datetime':
                return date_obj.strftime('%d/%m/%Y %H:%M')
            else:
                return date_obj.strftime('%d/%m/%Y')
        except:
            return date_str
    
    @staticmethod
    def format_percentage(value: Any) -> str:
        """Formatear porcentaje"""
        try:
            return f"{float(value):.1f}%"
        except:
            return "0.0%"
    
    @staticmethod
    def format_role(role: str) -> str:
        """Formatear rol de usuario"""
        role_names = {
            'Admin': 'Administrador',
            'Supervisor': 'Supervisor',
            'Tecnico': 'Técnico',
            'Ayudante': 'Ayudante'
        }
        return role_names.get(role, role)
    
    @staticmethod
    def format_tipo_espacio(tipo: str) -> str:
        """Formatear tipo de espacio"""
        tipos = {
            'unidad': 'Unidad',
            'sotu': 'SOTU',
            'shaft': 'Shaft',
            'lateral': 'Lateral',
            'antena': 'Antena'
        }
        return tipos.get(tipo, tipo.title())
    
    @staticmethod
    def format_tipo_medicion(tipo: str) -> str:
        """Formatear tipo de medición"""
        tipos = {
            'alambrico-t1': 'Alámbrico T1',
            'alambrico-t2': 'Alámbrico T2',
            'coaxial': 'Coaxial',
            'fibra': 'Fibra Óptica',
            'wifi': 'WiFi',
            'certificacion': 'Certificación'
        }
        return tipos.get(tipo, tipo.title())
    
    @staticmethod
    def format_estado_medicion(estado: str) -> str:
        """Formatear estado de medición"""
        estados = {
            'OK': '✅ OK',
            'ADVERTENCIA': '⚠️ Advertencia',
            'FALLA': '❌ Falla'
        }
        return estados.get(estado, estado)
    
    @staticmethod
    def format_sync_status(status: str) -> str:
        """Formatear estado de sincronización"""
        estados = {
            'local': '📱 Local',
            'syncing': '🔄 Sincronizando',
            'synced': '✅ Sincronizado',
            'conflict': '⚠️ Conflicto'
        }
        return estados.get(status, status)
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Formatear tamaño de archivo"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 50) -> str:
        """Truncar texto si es muy largo"""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."