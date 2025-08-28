from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.models.medicion import MedicionCreate, MedicionUpdate, MedicionResponse
from app.models.usuario import Usuario
from app.services.medicion_service import MedicionService
from app.routers.auth import get_current_active_user, require_supervisor_or_admin

router = APIRouter()


@router.get("/", response_model=List[MedicionResponse])
async def get_mediciones(
    torre: Optional[str] = Query(None, description="Filtrar por torre"),
    piso: Optional[int] = Query(None, description="Filtrar por piso"),
    tipo_medicion: Optional[str] = Query(None, description="Filtrar por tipo de medición"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta"),
    search: Optional[str] = Query(None, description="Búsqueda en identificador y observaciones"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Obtener lista de mediciones con filtros"""
    return await MedicionService.get_all_mediciones(
        torre=torre,
        piso=piso,
        tipo_medicion=tipo_medicion,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        search=search,
        limit=limit,
        offset=offset
    )


@router.get("/{medicion_id}", response_model=MedicionResponse)
async def get_medicion(
    medicion_id: str,
    current_user: Usuario = Depends(get_current_active_user)
):
    """Obtener medición por ID"""
    medicion = await MedicionService.get_medicion_by_id(medicion_id)
    
    if not medicion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medición no encontrada"
        )
    
    return medicion


@router.post("/", response_model=MedicionResponse)
async def create_medicion(
    medicion_data: MedicionCreate,
    current_user: Usuario = Depends(get_current_active_user)
):
    """Crear nueva medición"""
    return await MedicionService.create_medicion(
        medicion_data=medicion_data,
        usuario_id=current_user.id
    )


@router.put("/{medicion_id}", response_model=MedicionResponse)
async def update_medicion(
    medicion_id: str,
    medicion_data: MedicionUpdate,
    current_user: Usuario = Depends(get_current_active_user)
):
    """Actualizar medición"""
    medicion = await MedicionService.update_medicion(medicion_id, medicion_data)
    
    if not medicion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medición no encontrada"
        )
    
    return medicion


@router.delete("/{medicion_id}")
async def delete_medicion(
    medicion_id: str,
    current_user: Usuario = Depends(require_supervisor_or_admin)
):
    """Eliminar medición - Solo supervisores y admins"""
    success = await MedicionService.delete_medicion(medicion_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medición no encontrada"
        )
    
    return {"message": "Medición eliminada exitosamente"}


@router.get("/tipos/rangos")
async def get_rangos_medicion(current_user: Usuario = Depends(get_current_active_user)):
    """Obtener rangos de medición para validación en frontend"""
    return {
        "rangos": MedicionService.RANGOS_MEDICION,
        "tipos": [
            {"value": "alambrico-t1", "label": "Alámbrico T1", "unidad": "dBμV"},
            {"value": "alambrico-t2", "label": "Alámbrico T2", "unidad": "dBμV"},
            {"value": "coaxial", "label": "Coaxial", "unidad": "dBμV"},
            {"value": "fibra", "label": "Fibra Óptica", "unidad": "dBm"},
            {"value": "wifi", "label": "WiFi", "unidad": "dBm"},
            {"value": "certificacion", "label": "Certificación", "unidad": "Estado"}
        ]
    }