from typing import Optional
from app.config import settings


def validate_torre(torre: str) -> bool:
    """Validar que la torre sea válida"""
    return torre in settings.TORRES


def validate_piso(piso: int) -> bool:
    """Validar que el piso sea válido"""
    return piso in settings.PISOS


def validate_sector(sector: str) -> bool:
    """Validar que el sector sea válido"""
    return sector in settings.SECTORES


def validate_torre_sector_combination(torre: str, sector: Optional[str]) -> bool:
    """Validar combinación de torre y sector (Torres C y H no tienen sector Norte)"""
    if not sector:
        return True
    
    if torre in ['C', 'H'] and sector == 'Norte':
        return False
    
    return True


def validate_ubicacion_format(ubicacion: str, torre: str, piso: Optional[int]) -> bool:
    """Validar formato de ubicación para unidades"""
    if not piso:
        return True  # Para otros tipos de espacio
    
    # Formato esperado: A101, B205, etc.
    if len(ubicacion) < 4:
        return False
    
    # Verificar que comience con la torre correcta
    if not ubicacion.startswith(torre):
        return False
    
    # Verificar que el piso coincida
    try:
        piso_en_ubicacion = int(ubicacion[1:3])
        return piso_en_ubicacion == piso
    except (ValueError, IndexError):
        return False