from datetime import datetime, date
from typing import Optional, Union


def format_date(date_obj: Union[datetime, date, str], format_str: str = "%Y-%m-%d") -> str:
    """Formatear fecha a string"""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
        except ValueError:
            return date_obj
    
    if isinstance(date_obj, (datetime, date)):
        return date_obj.strftime(format_str)
    
    return str(date_obj)


def calculate_percentage(completed: int, total: int) -> float:
    """Calcular porcentaje con manejo de división por cero"""
    if total == 0:
        return 0.0
    return round((completed / total) * 100, 2)


def generate_ubicacion_id(torre: str, piso: int, numero_unidad: str) -> str:
    """Generar identificador de ubicación"""
    return f"{torre}{piso:02d}{numero_unidad}"


def parse_ubicacion_id(ubicacion: str) -> Optional[dict]:
    """Parsear identificador de ubicación"""
    if len(ubicacion) < 4:
        return None
    
    try:
        torre = ubicacion[0]
        piso = int(ubicacion[1:3])
        numero_unidad = ubicacion[3:]
        
        return {
            "torre": torre,
            "piso": piso,
            "numero_unidad": numero_unidad
        }
    except (ValueError, IndexError):
        return None


def sanitize_filename(filename: str) -> str:
    """Sanitizar nombre de archivo"""
    import re
    # Remover caracteres especiales y espacios
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    # Limitar longitud
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = f"{name[:95]}.{ext}" if ext else name[:100]
    
    return filename


def validate_file_type(filename: str, allowed_types: list) -> bool:
    """Validar tipo de archivo por extensión"""
    if not filename:
        return False
    
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    return f".{extension}" in [t.split('/')[-1] for t in allowed_types]