from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


class TipoMedicion(str, Enum):
    ALAMBRICO_T1 = "alambrico-t1"
    ALAMBRICO_T2 = "alambrico-t2"
    COAXIAL = "coaxial"
    FIBRA = "fibra"
    WIFI = "wifi"
    CERTIFICACION = "certificacion"


class EstadoMedicion(str, Enum):
    OK = "OK"
    ADVERTENCIA = "ADVERTENCIA"
    FALLA = "FALLA"


class EstadoCertificacion(str, Enum):
    APROBADO = "APROBADO"
    APROBADO_CON_OBSERVACIONES = "APROBADO_CON_OBSERVACIONES"
    RECHAZADO = "RECHAZADO"


class ValoresMedicion(BaseModel):
    """Valores de medición según el tipo"""
    alambrico_t1: Optional[float] = Field(None, description="Nivel alámbrico T1 (dBμV)")
    alambrico_t2: Optional[float] = Field(None, description="Nivel alámbrico T2 (dBμV)")
    coaxial: Optional[float] = Field(None, description="Nivel coaxial (dBμV)")
    potencia_tx: Optional[float] = Field(None, description="Potencia TX (dBm)")
    potencia_rx: Optional[float] = Field(None, description="Potencia RX (dBm)")
    atenuacion: Optional[float] = Field(None, description="Atenuación (dB)")
    wifi: Optional[float] = Field(None, description="Nivel WiFi (dBm)")
    certificacion: Optional[EstadoCertificacion] = Field(None, description="Estado de certificación")

    class Config:
        use_enum_values = True


class MedicionBase(BaseModel):
    fecha: datetime = Field(..., description="Fecha de la medición")
    torre: str = Field(..., pattern="^[A-J]$", description="Torre (A-J)")
    piso: int = Field(..., ge=1, le=20, description="Piso (1-20)")
    identificador: str = Field(..., min_length=1, max_length=20, description="Identificador de la unidad")
    tipo_medicion: TipoMedicion = Field(..., description="Tipo de medición")
    valores: ValoresMedicion = Field(..., description="Valores de la medición")
    observaciones: Optional[str] = Field(None, max_length=500, description="Observaciones adicionales")

    @field_validator('valores')
    @classmethod
    def validate_valores_por_tipo(cls, v, info):
        """Validar que los valores correspondan al tipo de medición"""
        if 'tipo_medicion' not in info.data:
            return v
        
        tipo = info.data['tipo_medicion']
        
        if tipo == TipoMedicion.ALAMBRICO_T1 and v.alambrico_t1 is None:
            raise ValueError("Se requiere valor alámbrico T1")
        elif tipo == TipoMedicion.ALAMBRICO_T2 and v.alambrico_t2 is None:
            raise ValueError("Se requiere valor alámbrico T2")
        elif tipo == TipoMedicion.COAXIAL and v.coaxial is None:
            raise ValueError("Se requiere valor coaxial")
        elif tipo == TipoMedicion.FIBRA and (v.potencia_tx is None or v.potencia_rx is None):
            raise ValueError("Se requieren valores de potencia TX y RX para fibra")
        elif tipo == TipoMedicion.WIFI and v.wifi is None:
            raise ValueError("Se requiere valor WiFi")
        elif tipo == TipoMedicion.CERTIFICACION and v.certificacion is None:
            raise ValueError("Se requiere estado de certificación")
        
        return v


class MedicionCreate(MedicionBase):
    pass


class MedicionUpdate(BaseModel):
    fecha: Optional[datetime] = None
    torre: Optional[str] = Field(None, pattern="^[A-J]$")
    piso: Optional[int] = Field(None, ge=1, le=20)
    identificador: Optional[str] = Field(None, min_length=1, max_length=20)
    tipo_medicion: Optional[TipoMedicion] = None
    valores: Optional[ValoresMedicion] = None
    observaciones: Optional[str] = Field(None, max_length=500)


class Medicion(MedicionBase):
    id: str = Field(..., description="ID único de la medición")
    obra_id: str = Field(..., description="ID de la obra")
    estado: EstadoMedicion = Field(..., description="Estado de la medición")
    usuario_id: str = Field(..., description="ID del usuario que registró la medición")
    sync_status: str = Field("synced", description="Estado de sincronización")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    class Config:
        from_attributes = True


class MedicionResponse(BaseModel):
    """Respuesta de la medición con información del usuario"""
    id: str
    fecha: datetime
    torre: str
    piso: int
    identificador: str
    tipo_medicion: str
    valores: Dict[str, Any]
    estado: str
    observaciones: Optional[str]
    sync_status: str
    created_at: datetime
    updated_at: datetime
    usuario: Optional[dict] = None  # Información básica del usuario

    class Config:
        from_attributes = True