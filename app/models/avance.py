from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TipoEspacio(str, Enum):
    UNIDAD = "unidad"
    SOTU = "sotu"
    SHAFT = "shaft"
    LATERAL = "lateral"
    ANTENA = "antena"


class Sector(str, Enum):
    NORTE = "Norte"
    PONIENTE = "Poniente"
    ORIENTE = "Oriente"


class SyncStatus(str, Enum):
    LOCAL = "local"
    SYNCING = "syncing"
    SYNCED = "synced"
    CONFLICT = "conflict"


class AvanceBase(BaseModel):
    fecha: datetime = Field(..., description="Fecha del avance")
    torre: str = Field(..., pattern="^[A-J]$", description="Torre (A-J)")
    piso: Optional[int] = Field(None, ge=1, le=20, description="Piso (1-20)")
    sector: Optional[Sector] = Field(None, description="Sector de la unidad")
    tipo_espacio: TipoEspacio = Field(..., description="Tipo de espacio")
    ubicacion: str = Field(..., min_length=1, max_length=50, description="Ubicación específica")
    categoria: str = Field(..., min_length=1, max_length=100, description="Categoría del trabajo")
    porcentaje: int = Field(..., ge=0, le=100, description="Porcentaje de avance (0-100)")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones adicionales")


class AvanceCreate(AvanceBase):
    pass


class AvanceUpdate(BaseModel):
    fecha: Optional[datetime] = None
    torre: Optional[str] = Field(None, pattern="^[A-J]$")
    piso: Optional[int] = Field(None, ge=1, le=20)
    sector: Optional[Sector] = None
    tipo_espacio: Optional[TipoEspacio] = None
    ubicacion: Optional[str] = Field(None, min_length=1, max_length=50)
    categoria: Optional[str] = Field(None, min_length=1, max_length=100)
    porcentaje: Optional[int] = Field(None, ge=0, le=100)
    observaciones: Optional[str] = Field(None, max_length=500)


class Avance(AvanceBase):
    id: str = Field(..., description="ID único del avance")
    obra_id: str = Field(..., description="ID de la obra")
    foto_path: Optional[str] = Field(None, description="Ruta local de la foto")
    foto_url: Optional[str] = Field(None, description="URL de la foto en Storage")
    usuario_id: str = Field(..., description="ID del usuario que registró el avance")
    sync_status: SyncStatus = Field(SyncStatus.SYNCED, description="Estado de sincronización")
    last_sync: Optional[datetime] = Field(None, description="Fecha de última sincronización")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")
    deleted_at: Optional[datetime] = Field(None, description="Fecha de eliminación (soft delete)")

    class Config:
        from_attributes = True


class AvanceResponse(BaseModel):
    """Respuesta del avance con información del usuario"""
    id: str
    fecha: datetime
    torre: str
    piso: Optional[int]
    sector: Optional[str]
    tipo_espacio: str
    ubicacion: str
    categoria: str
    porcentaje: int
    observaciones: Optional[str]
    foto_url: Optional[str]
    sync_status: str
    created_at: datetime
    updated_at: datetime
    usuario: Optional[dict] = None  # Información básica del usuario

    class Config:
        from_attributes = True