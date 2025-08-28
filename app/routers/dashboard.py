from typing import List
from fastapi import APIRouter, Depends

from app.models.dashboard import DashboardSummary, TowerProgress, MedicionesEstado, DashboardData
from app.models.usuario import Usuario
from app.services.dashboard_service import DashboardService
from app.routers.auth import get_current_active_user

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(current_user: Usuario = Depends(get_current_active_user)):
    """Obtener resumen general del dashboard"""
    return await DashboardService.get_dashboard_summary()


@router.get("/tower-progress", response_model=List[TowerProgress])
async def get_tower_progress(current_user: Usuario = Depends(get_current_active_user)):
    """Obtener progreso por torre"""
    return await DashboardService.get_tower_progress()


@router.get("/mediciones-estado", response_model=MedicionesEstado)
async def get_mediciones_estado(current_user: Usuario = Depends(get_current_active_user)):
    """Obtener estado de las mediciones"""
    return await DashboardService.get_mediciones_estado()


@router.get("/", response_model=DashboardData)
async def get_dashboard_data(current_user: Usuario = Depends(get_current_active_user)):
    """Obtener todos los datos del dashboard"""
    return await DashboardService.get_dashboard_data()


@router.get("/stats")
async def get_dashboard_stats(current_user: Usuario = Depends(get_current_active_user)):
    """Obtener estadísticas adicionales del dashboard"""
    try:
        # Usar la función de Supabase para obtener estadísticas
        from app.services.supabase_client import supabase_client
        
        response = supabase_client.rpc('obtener_dashboard_data').execute()
        
        if response.data:
            return response.data
        else:
            # Fallback a datos básicos
            summary = await DashboardService.get_dashboard_summary()
            tower_progress = await DashboardService.get_tower_progress()
            mediciones_estado = await DashboardService.get_mediciones_estado()
            
            return {
                "resumen_general": summary.dict(),
                "progreso_torres": {tp.torre: tp.progreso_promedio for tp in tower_progress},
                "mediciones_estado": mediciones_estado.dict()
            }
            
    except Exception as e:
        # En caso de error, devolver datos básicos
        summary = await DashboardService.get_dashboard_summary()
        return {
            "resumen_general": summary.dict(),
            "progreso_torres": {},
            "mediciones_estado": {"ok": 0, "advertencia": 0, "falla": 0, "total": 0}
        }