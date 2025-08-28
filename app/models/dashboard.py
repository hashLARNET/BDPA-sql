from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class DashboardSummary(BaseModel):
    """Resumen general del dashboard"""
    total_unidades: int = Field(..., description="Total de unidades en la obra")
    unidades_completadas: int = Field(..., description="Unidades completadas (100%)")
    porcentaje_general: float = Field(..., description="Porcentaje general de avance")
    avances_hoy: int = Field(..., description="Avances registrados hoy")
    mediciones_hoy: int = Field(..., description="Mediciones registradas hoy")
    alertas_pendientes: int = Field(..., description="Mediciones con fallas")
    ultimo_avance: Optional[datetime] = Field(None, description="Fecha del último avance")
    ultima_medicion: Optional[datetime] = Field(None, description="Fecha de la última medición")


class TowerProgress(BaseModel):
    """Progreso por torre"""
    torre: str = Field(..., description="Identificador de la torre")
    total_avances: int = Field(..., description="Total de avances registrados")
    progreso_promedio: float = Field(..., description="Progreso promedio de la torre")
    unidades_con_avance: int = Field(..., description="Unidades con al menos un avance")
    unidades_completadas: int = Field(..., description="Unidades completadas (100%)")
    ultimo_avance: Optional[datetime] = Field(None, description="Fecha del último avance")
    mediciones_ok: int = Field(0, description="Mediciones en estado OK")
    mediciones_falla: int = Field(0, description="Mediciones en estado FALLA")


class MedicionesEstado(BaseModel):
    """Estado de las mediciones"""
    ok: int = Field(..., description="Mediciones OK")
    advertencia: int = Field(..., description="Mediciones con advertencia")
    falla: int = Field(..., description="Mediciones con falla")
    total: int = Field(..., description="Total de mediciones")


class DashboardData(BaseModel):
    """Datos completos del dashboard"""
    resumen: DashboardSummary
    progreso_torres: List[TowerProgress]
    mediciones_estado: MedicionesEstado
    actividad_reciente: List[dict] = Field(default_factory=list, description="Actividad reciente")