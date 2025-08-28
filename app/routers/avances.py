from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form

from app.models.avance import AvanceCreate, AvanceUpdate, AvanceResponse
from app.models.usuario import Usuario
from app.services.avance_service import AvanceService
from app.routers.auth import get_current_active_user, require_supervisor_or_admin

router = APIRouter()


@router.get("/", response_model=List[AvanceResponse])
async def get_avances(
    torre: Optional[str] = Query(None, description="Filtrar por torre"),
    piso: Optional[int] = Query(None, description="Filtrar por piso"),
    sector: Optional[str] = Query(None, description="Filtrar por sector"),
    tipo_espacio: Optional[str] = Query(None, description="Filtrar por tipo de espacio"),
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta"),
    search: Optional[str] = Query(None, description="Búsqueda en ubicación y observaciones"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación"),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Obtener lista de avances con filtros"""
    return await AvanceService.get_all_avances(
        torre=torre,
        piso=piso,
        sector=sector,
        tipo_espacio=tipo_espacio,
        categoria=categoria,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        search=search,
        limit=limit,
        offset=offset
    )


@router.get("/{avance_id}", response_model=AvanceResponse)
async def get_avance(
    avance_id: str,
    current_user: Usuario = Depends(get_current_active_user)
):
    """Obtener avance por ID"""
    avance = await AvanceService.get_avance_by_id(avance_id)
    
    if not avance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avance no encontrado"
        )
    
    return avance


@router.post("/", response_model=AvanceResponse)
async def create_avance(
    avance_data: AvanceCreate,
    foto: Optional[UploadFile] = File(None),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Crear nuevo avance"""
    return await AvanceService.create_avance(
        avance_data=avance_data,
        usuario_id=current_user.id,
        foto=foto
    )


@router.post("/with-form", response_model=AvanceResponse)
async def create_avance_with_form(
    fecha: str = Form(...),
    torre: str = Form(...),
    piso: Optional[int] = Form(None),
    sector: Optional[str] = Form(None),
    tipo_espacio: str = Form(...),
    ubicacion: str = Form(...),
    categoria: str = Form(...),
    porcentaje: int = Form(...),
    observaciones: Optional[str] = Form(None),
    foto: Optional[UploadFile] = File(None),
    current_user: Usuario = Depends(get_current_active_user)
):
    """Crear nuevo avance usando form-data (para subida de archivos)"""
    from datetime import datetime
    
    # Convertir fecha string a datetime
    try:
        fecha_dt = datetime.fromisoformat(fecha.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido"
        )
    
    # Crear objeto AvanceCreate
    avance_data = AvanceCreate(
        fecha=fecha_dt,
        torre=torre,
        piso=piso,
        sector=sector,
        tipo_espacio=tipo_espacio,
        ubicacion=ubicacion,
        categoria=categoria,
        porcentaje=porcentaje,
        observaciones=observaciones
    )
    
    return await AvanceService.create_avance(
        avance_data=avance_data,
        usuario_id=current_user.id,
        foto=foto
    )


@router.put("/{avance_id}", response_model=AvanceResponse)
async def update_avance(
    avance_id: str,
    avance_data: AvanceUpdate,
    current_user: Usuario = Depends(get_current_active_user)
):
    """Actualizar avance"""
    avance = await AvanceService.update_avance(avance_id, avance_data)
    
    if not avance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avance no encontrado"
        )
    
    return avance


@router.delete("/{avance_id}")
async def delete_avance(
    avance_id: str,
    current_user: Usuario = Depends(require_supervisor_or_admin)
):
    """Eliminar avance (soft delete) - Solo supervisores y admins"""
    success = await AvanceService.delete_avance(avance_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Avance no encontrado"
        )
    
    return {"message": "Avance eliminado exitosamente"}