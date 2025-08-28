from typing import List, Optional
from datetime import datetime, date
from fastapi import HTTPException, status

from app.models.medicion import Medicion, MedicionCreate, MedicionUpdate, MedicionResponse, EstadoMedicion, TipoMedicion
from app.services.supabase_client import supabase_client
from app.config import settings


class MedicionService:
    """Servicio para gestión de mediciones"""
    
    # Rangos de medición para validación automática
    RANGOS_MEDICION = {
        'alambrico': {'min': 45, 'max': 75},
        'coaxial': {'min': 45, 'max': 75},
        'fibra_potencia': {'min': -30, 'max': -8},
        'wifi': {'min': -80, 'max': -30}
    }
    
    @staticmethod
    def _calcular_estado_medicion(tipo_medicion: TipoMedicion, valores: dict) -> EstadoMedicion:
        """Calcular estado automático de la medición basado en valores"""
        try:
            if tipo_medicion == TipoMedicion.CERTIFICACION:
                cert_value = valores.get('certificacion')
                if cert_value == 'RECHAZADO':
                    return EstadoMedicion.FALLA
                elif cert_value == 'APROBADO_CON_OBSERVACIONES':
                    return EstadoMedicion.ADVERTENCIA
                else:
                    return EstadoMedicion.OK
            
            estados = []
            
            # Validar según tipo de medición
            if tipo_medicion in [TipoMedicion.ALAMBRICO_T1, TipoMedicion.ALAMBRICO_T2]:
                valor_key = 'alambrico_t1' if tipo_medicion == TipoMedicion.ALAMBRICO_T1 else 'alambrico_t2'
                valor = valores.get(valor_key)
                if valor is not None:
                    estados.append(MedicionService._validar_rango(valor, 'alambrico'))
            
            elif tipo_medicion == TipoMedicion.COAXIAL:
                valor = valores.get('coaxial')
                if valor is not None:
                    estados.append(MedicionService._validar_rango(valor, 'coaxial'))
            
            elif tipo_medicion == TipoMedicion.FIBRA:
                potencia_tx = valores.get('potencia_tx')
                potencia_rx = valores.get('potencia_rx')
                if potencia_tx is not None:
                    estados.append(MedicionService._validar_rango(potencia_tx, 'fibra_potencia'))
                if potencia_rx is not None:
                    estados.append(MedicionService._validar_rango(potencia_rx, 'fibra_potencia'))
            
            elif tipo_medicion == TipoMedicion.WIFI:
                valor = valores.get('wifi')
                if valor is not None:
                    estados.append(MedicionService._validar_rango(valor, 'wifi'))
            
            # Determinar estado final
            if EstadoMedicion.FALLA in estados:
                return EstadoMedicion.FALLA
            elif EstadoMedicion.ADVERTENCIA in estados:
                return EstadoMedicion.ADVERTENCIA
            else:
                return EstadoMedicion.OK
                
        except Exception:
            return EstadoMedicion.OK
    
    @staticmethod
    def _validar_rango(valor: float, tipo_rango: str) -> EstadoMedicion:
        """Validar si un valor está en el rango correcto"""
        rango = MedicionService.RANGOS_MEDICION.get(tipo_rango)
        if not rango:
            return EstadoMedicion.OK
        
        min_val, max_val = rango['min'], rango['max']
        
        if valor < min_val or valor > max_val:
            return EstadoMedicion.FALLA
        elif valor < min_val + 5 or valor > max_val - 5:  # Zona de advertencia
            return EstadoMedicion.ADVERTENCIA
        else:
            return EstadoMedicion.OK
    
    @staticmethod
    async def get_all_mediciones(
        torre: Optional[str] = None,
        piso: Optional[int] = None,
        tipo_medicion: Optional[str] = None,
        estado: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[MedicionResponse]:
        """Obtener mediciones con filtros"""
        try:
            query = supabase_client.table('mediciones').select('''
                *,
                usuarios!mediciones_usuario_id_fkey(id, nombre, username, rol)
            ''')
            
            # Aplicar filtros
            if torre:
                query = query.eq('torre', torre)
            if piso:
                query = query.eq('piso', piso)
            if tipo_medicion:
                query = query.eq('tipo_medicion', tipo_medicion)
            if estado:
                query = query.eq('estado', estado)
            if fecha_desde:
                query = query.gte('fecha', fecha_desde.isoformat())
            if fecha_hasta:
                query = query.lte('fecha', fecha_hasta.isoformat())
            if search:
                query = query.or_(f'identificador.ilike.%{search}%,observaciones.ilike.%{search}%')
            
            # Ordenar y paginar
            response = query.order('fecha', desc=True).range(offset, offset + limit - 1).execute()
            
            # Formatear respuesta
            mediciones = []
            for medicion_data in response.data:
                usuario_data = medicion_data.pop('usuarios', None)
                medicion_response = MedicionResponse(**medicion_data)
                if usuario_data:
                    medicion_response.usuario = {
                        'id': usuario_data['id'],
                        'nombre': usuario_data['nombre'],
                        'username': usuario_data['username'],
                        'rol': usuario_data['rol']
                    }
                mediciones.append(medicion_response)
            
            return mediciones
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener mediciones: {str(e)}"
            )
    
    @staticmethod
    async def get_medicion_by_id(medicion_id: str) -> Optional[MedicionResponse]:
        """Obtener medición por ID"""
        try:
            response = supabase_client.table('mediciones').select('''
                *,
                usuarios!mediciones_usuario_id_fkey(id, nombre, username, rol)
            ''').eq('id', medicion_id).execute()
            
            if not response.data:
                return None
            
            medicion_data = response.data[0]
            usuario_data = medicion_data.pop('usuarios', None)
            medicion_response = MedicionResponse(**medicion_data)
            
            if usuario_data:
                medicion_response.usuario = {
                    'id': usuario_data['id'],
                    'nombre': usuario_data['nombre'],
                    'username': usuario_data['username'],
                    'rol': usuario_data['rol']
                }
            
            return medicion_response
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener medición: {str(e)}"
            )
    
    @staticmethod
    async def create_medicion(medicion_data: MedicionCreate, usuario_id: str) -> MedicionResponse:
        """Crear nueva medición"""
        try:
            # Preparar datos de la medición
            medicion_dict = medicion_data.dict()
            valores_dict = medicion_dict.pop('valores')
            
            # Calcular estado automáticamente
            estado = MedicionService._calcular_estado_medicion(
                medicion_data.tipo_medicion, 
                valores_dict
            )
            
            medicion_dict.update({
                'obra_id': settings.OBRA_ID,
                'usuario_id': usuario_id,
                'valores': valores_dict,
                'estado': estado.value,
                'sync_status': 'synced'
            })
            
            # Insertar en base de datos
            response = supabase_client.table('mediciones').insert(medicion_dict).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al crear medición"
                )
            
            # Obtener medición completa con usuario
            return await MedicionService.get_medicion_by_id(response.data[0]['id'])
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear medición: {str(e)}"
            )
    
    @staticmethod
    async def update_medicion(medicion_id: str, medicion_data: MedicionUpdate) -> Optional[MedicionResponse]:
        """Actualizar medición"""
        try:
            # Filtrar campos None
            update_data = {k: v for k, v in medicion_data.dict().items() if v is not None}
            
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No hay datos para actualizar"
                )
            
            # Si se actualizan valores, recalcular estado
            if 'valores' in update_data and 'tipo_medicion' in update_data:
                estado = MedicionService._calcular_estado_medicion(
                    update_data['tipo_medicion'],
                    update_data['valores']
                )
                update_data['estado'] = estado.value
            
            update_data['sync_status'] = 'synced'
            
            response = supabase_client.table('mediciones').update(update_data).eq('id', medicion_id).execute()
            
            if not response.data:
                return None
            
            return await MedicionService.get_medicion_by_id(medicion_id)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar medición: {str(e)}"
            )
    
    @staticmethod
    async def delete_medicion(medicion_id: str) -> bool:
        """Eliminar medición"""
        try:
            response = supabase_client.table('mediciones').delete().eq('id', medicion_id).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar medición: {str(e)}"
            )