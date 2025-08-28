from typing import List
from datetime import datetime, date
from fastapi import HTTPException, status

from app.models.dashboard import DashboardSummary, TowerProgress, MedicionesEstado, DashboardData
from app.services.supabase_client import supabase_client
from app.config import settings


class DashboardService:
    """Servicio para datos del dashboard"""
    
    @staticmethod
    async def get_dashboard_summary() -> DashboardSummary:
        """Obtener resumen general del dashboard"""
        try:
            # Obtener estadísticas de avances
            avances_response = supabase_client.table('avances').select('porcentaje, fecha').is_('deleted_at', 'null').execute()
            avances_data = avances_response.data
            
            # Obtener estadísticas de mediciones
            mediciones_response = supabase_client.table('mediciones').select('estado, fecha').execute()
            mediciones_data = mediciones_response.data
            
            # Calcular estadísticas
            total_unidades = settings.TOTAL_UNIDADES
            unidades_completadas = len([a for a in avances_data if a['porcentaje'] == 100])
            porcentaje_general = (unidades_completadas / total_unidades) * 100 if total_unidades > 0 else 0
            
            # Avances y mediciones de hoy
            hoy = date.today()
            avances_hoy = len([a for a in avances_data if datetime.fromisoformat(a['fecha'].replace('Z', '+00:00')).date() == hoy])
            mediciones_hoy = len([m for m in mediciones_data if datetime.fromisoformat(m['fecha'].replace('Z', '+00:00')).date() == hoy])
            
            # Alertas (mediciones con falla)
            alertas_pendientes = len([m for m in mediciones_data if m['estado'] == 'FALLA'])
            
            # Fechas de último avance y medición
            ultimo_avance = None
            ultima_medicion = None
            
            if avances_data:
                ultimo_avance = max([datetime.fromisoformat(a['fecha'].replace('Z', '+00:00')) for a in avances_data])
            
            if mediciones_data:
                ultima_medicion = max([datetime.fromisoformat(m['fecha'].replace('Z', '+00:00')) for m in mediciones_data])
            
            return DashboardSummary(
                total_unidades=total_unidades,
                unidades_completadas=unidades_completadas,
                porcentaje_general=round(porcentaje_general, 2),
                avances_hoy=avances_hoy,
                mediciones_hoy=mediciones_hoy,
                alertas_pendientes=alertas_pendientes,
                ultimo_avance=ultimo_avance,
                ultima_medicion=ultima_medicion
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener resumen del dashboard: {str(e)}"
            )
    
    @staticmethod
    async def get_tower_progress() -> List[TowerProgress]:
        """Obtener progreso por torre"""
        try:
            # Obtener datos usando la vista de Supabase
            response = supabase_client.table('vista_progreso_torres').select('*').execute()
            
            if not response.data:
                # Si no hay datos en la vista, calcular manualmente
                return await DashboardService._calculate_tower_progress_manual()
            
            # Convertir datos de la vista al modelo
            tower_progress = []
            for row in response.data:
                tower_progress.append(TowerProgress(
                    torre=row['torre'],
                    total_avances=row['total_avances'] or 0,
                    progreso_promedio=float(row['progreso_promedio'] or 0),
                    unidades_con_avance=row['unidades_con_avance'] or 0,
                    unidades_completadas=row['unidades_completadas'] or 0,
                    ultimo_avance=datetime.fromisoformat(row['ultimo_avance'].replace('Z', '+00:00')) if row['ultimo_avance'] else None,
                    mediciones_ok=0,  # Se calculará por separado si es necesario
                    mediciones_falla=0
                ))
            
            return tower_progress
            
        except Exception as e:
            # Fallback a cálculo manual
            return await DashboardService._calculate_tower_progress_manual()
    
    @staticmethod
    async def _calculate_tower_progress_manual() -> List[TowerProgress]:
        """Calcular progreso por torre manualmente"""
        try:
            tower_progress = []
            
            for torre in settings.TORRES:
                # Obtener avances de la torre
                avances_response = supabase_client.table('avances').select('porcentaje, fecha, ubicacion').eq('torre', torre).is_('deleted_at', 'null').execute()
                avances_data = avances_response.data
                
                # Obtener mediciones de la torre
                mediciones_response = supabase_client.table('mediciones').select('estado').eq('torre', torre).execute()
                mediciones_data = mediciones_response.data
                
                # Calcular estadísticas
                total_avances = len(avances_data)
                progreso_promedio = sum([a['porcentaje'] for a in avances_data]) / total_avances if total_avances > 0 else 0
                unidades_con_avance = len(set([a['ubicacion'] for a in avances_data]))
                unidades_completadas = len([a for a in avances_data if a['porcentaje'] == 100])
                
                ultimo_avance = None
                if avances_data:
                    ultimo_avance = max([datetime.fromisoformat(a['fecha'].replace('Z', '+00:00')) for a in avances_data])
                
                mediciones_ok = len([m for m in mediciones_data if m['estado'] == 'OK'])
                mediciones_falla = len([m for m in mediciones_data if m['estado'] == 'FALLA'])
                
                tower_progress.append(TowerProgress(
                    torre=torre,
                    total_avances=total_avances,
                    progreso_promedio=round(progreso_promedio, 2),
                    unidades_con_avance=unidades_con_avance,
                    unidades_completadas=unidades_completadas,
                    ultimo_avance=ultimo_avance,
                    mediciones_ok=mediciones_ok,
                    mediciones_falla=mediciones_falla
                ))
            
            return tower_progress
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al calcular progreso por torre: {str(e)}"
            )
    
    @staticmethod
    async def get_mediciones_estado() -> MedicionesEstado:
        """Obtener estado de las mediciones"""
        try:
            response = supabase_client.table('mediciones').select('estado').execute()
            mediciones_data = response.data
            
            ok = len([m for m in mediciones_data if m['estado'] == 'OK'])
            advertencia = len([m for m in mediciones_data if m['estado'] == 'ADVERTENCIA'])
            falla = len([m for m in mediciones_data if m['estado'] == 'FALLA'])
            total = len(mediciones_data)
            
            return MedicionesEstado(
                ok=ok,
                advertencia=advertencia,
                falla=falla,
                total=total
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener estado de mediciones: {str(e)}"
            )
    
    @staticmethod
    async def get_dashboard_data() -> DashboardData:
        """Obtener todos los datos del dashboard"""
        try:
            # Obtener datos en paralelo
            resumen = await DashboardService.get_dashboard_summary()
            progreso_torres = await DashboardService.get_tower_progress()
            mediciones_estado = await DashboardService.get_mediciones_estado()
            
            # Obtener actividad reciente (últimos 10 avances y mediciones)
            actividad_reciente = await DashboardService._get_actividad_reciente()
            
            return DashboardData(
                resumen=resumen,
                progreso_torres=progreso_torres,
                mediciones_estado=mediciones_estado,
                actividad_reciente=actividad_reciente
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener datos del dashboard: {str(e)}"
            )
    
    @staticmethod
    async def _get_actividad_reciente() -> List[dict]:
        """Obtener actividad reciente"""
        try:
            # Obtener últimos avances
            avances_response = supabase_client.table('avances').select('''
                id, fecha, torre, ubicacion, categoria, porcentaje,
                usuarios!avances_usuario_id_fkey(nombre)
            ''').is_('deleted_at', 'null').order('fecha', desc=True).limit(5).execute()
            
            # Obtener últimas mediciones
            mediciones_response = supabase_client.table('mediciones').select('''
                id, fecha, torre, identificador, tipo_medicion, estado,
                usuarios!mediciones_usuario_id_fkey(nombre)
            ''').order('fecha', desc=True).limit(5).execute()
            
            actividad = []
            
            # Procesar avances
            for avance in avances_response.data:
                actividad.append({
                    'tipo': 'avance',
                    'id': avance['id'],
                    'fecha': avance['fecha'],
                    'descripcion': f"Avance {avance['porcentaje']}% en {avance['ubicacion']} - {avance['categoria']}",
                    'usuario': avance['usuarios']['nombre'] if avance['usuarios'] else 'Usuario desconocido',
                    'torre': avance['torre']
                })
            
            # Procesar mediciones
            for medicion in mediciones_response.data:
                actividad.append({
                    'tipo': 'medicion',
                    'id': medicion['id'],
                    'fecha': medicion['fecha'],
                    'descripcion': f"Medición {medicion['tipo_medicion']} en {medicion['identificador']} - {medicion['estado']}",
                    'usuario': medicion['usuarios']['nombre'] if medicion['usuarios'] else 'Usuario desconocido',
                    'torre': medicion['torre']
                })
            
            # Ordenar por fecha descendente
            actividad.sort(key=lambda x: x['fecha'], reverse=True)
            
            return actividad[:10]  # Retornar solo los 10 más recientes
            
        except Exception as e:
            print(f"Error obteniendo actividad reciente: {e}")
            return []