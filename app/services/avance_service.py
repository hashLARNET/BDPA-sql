from typing import List, Optional
from datetime import datetime, date
from fastapi import HTTPException, status, UploadFile
import uuid

from app.models.avance import Avance, AvanceCreate, AvanceUpdate, AvanceResponse
from app.services.supabase_client import supabase_client
from app.config import settings


class AvanceService:
    """Servicio para gestión de avances"""
    
    @staticmethod
    async def get_all_avances(
        torre: Optional[str] = None,
        piso: Optional[int] = None,
        sector: Optional[str] = None,
        tipo_espacio: Optional[str] = None,
        categoria: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        search: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AvanceResponse]:
        """Obtener avances con filtros"""
        try:
            query = supabase_client.table('avances').select('''
                *,
                usuarios!avances_usuario_id_fkey(id, nombre, username, rol)
            ''').is_('deleted_at', 'null')
            
            # Aplicar filtros
            if torre:
                query = query.eq('torre', torre)
            if piso:
                query = query.eq('piso', piso)
            if sector:
                query = query.eq('sector', sector)
            if tipo_espacio:
                query = query.eq('tipo_espacio', tipo_espacio)
            if categoria:
                query = query.ilike('categoria', f'%{categoria}%')
            if fecha_desde:
                query = query.gte('fecha', fecha_desde.isoformat())
            if fecha_hasta:
                query = query.lte('fecha', fecha_hasta.isoformat())
            if search:
                query = query.or_(f'ubicacion.ilike.%{search}%,observaciones.ilike.%{search}%')
            
            # Ordenar y paginar
            response = query.order('fecha', desc=True).range(offset, offset + limit - 1).execute()
            
            # Formatear respuesta
            avances = []
            for avance_data in response.data:
                usuario_data = avance_data.pop('usuarios', None)
                avance_response = AvanceResponse(**avance_data)
                if usuario_data:
                    avance_response.usuario = {
                        'id': usuario_data['id'],
                        'nombre': usuario_data['nombre'],
                        'username': usuario_data['username'],
                        'rol': usuario_data['rol']
                    }
                avances.append(avance_response)
            
            return avances
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener avances: {str(e)}"
            )
    
    @staticmethod
    async def get_avance_by_id(avance_id: str) -> Optional[AvanceResponse]:
        """Obtener avance por ID"""
        try:
            response = supabase_client.table('avances').select('''
                *,
                usuarios!avances_usuario_id_fkey(id, nombre, username, rol)
            ''').eq('id', avance_id).is_('deleted_at', 'null').execute()
            
            if not response.data:
                return None
            
            avance_data = response.data[0]
            usuario_data = avance_data.pop('usuarios', None)
            avance_response = AvanceResponse(**avance_data)
            
            if usuario_data:
                avance_response.usuario = {
                    'id': usuario_data['id'],
                    'nombre': usuario_data['nombre'],
                    'username': usuario_data['username'],
                    'rol': usuario_data['rol']
                }
            
            return avance_response
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener avance: {str(e)}"
            )
    
    @staticmethod
    async def create_avance(avance_data: AvanceCreate, usuario_id: str, foto: Optional[UploadFile] = None) -> AvanceResponse:
        """Crear nuevo avance"""
        try:
            # Preparar datos del avance
            avance_dict = avance_data.dict()
            avance_dict.update({
                'obra_id': settings.OBRA_ID,
                'usuario_id': usuario_id,
                'sync_status': 'synced'
            })
            
            # Subir foto si se proporciona
            if foto:
                foto_url = await AvanceService._upload_foto(foto, usuario_id)
                avance_dict['foto_url'] = foto_url
            
            # Insertar en base de datos
            response = supabase_client.table('avances').insert(avance_dict).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al crear avance"
                )
            
            # Obtener avance completo con usuario
            return await AvanceService.get_avance_by_id(response.data[0]['id'])
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear avance: {str(e)}"
            )
    
    @staticmethod
    async def update_avance(avance_id: str, avance_data: AvanceUpdate) -> Optional[AvanceResponse]:
        """Actualizar avance"""
        try:
            # Filtrar campos None
            update_data = {k: v for k, v in avance_data.dict().items() if v is not None}
            
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No hay datos para actualizar"
                )
            
            update_data['sync_status'] = 'synced'
            
            response = supabase_client.table('avances').update(update_data).eq('id', avance_id).is_('deleted_at', 'null').execute()
            
            if not response.data:
                return None
            
            return await AvanceService.get_avance_by_id(avance_id)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar avance: {str(e)}"
            )
    
    @staticmethod
    async def delete_avance(avance_id: str) -> bool:
        """Eliminar avance (soft delete)"""
        try:
            response = supabase_client.table('avances').update({
                'deleted_at': datetime.utcnow().isoformat(),
                'sync_status': 'synced'
            }).eq('id', avance_id).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al eliminar avance: {str(e)}"
            )
    
    @staticmethod
    async def _upload_foto(foto: UploadFile, usuario_id: str) -> str:
        """Subir foto a Supabase Storage"""
        try:
            # Validar tipo de archivo
            if foto.content_type not in settings.ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Tipo de archivo no permitido"
                )
            
            # Validar tamaño
            if foto.size > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Archivo demasiado grande"
                )
            
            # Generar nombre único
            file_extension = foto.filename.split('.')[-1] if foto.filename else 'jpg'
            file_name = f"{uuid.uuid4()}.{file_extension}"
            file_path = f"los-encinos/{datetime.now().year}/{datetime.now().month:02d}/avances/{file_name}"
            
            # Leer contenido del archivo
            file_content = await foto.read()
            
            # Subir a Supabase Storage
            response = supabase_client.storage.from_('avances-fotos').upload(file_path, file_content)
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al subir foto"
                )
            
            # Obtener URL pública
            public_url = supabase_client.storage.from_('avances-fotos').get_public_url(file_path)
            
            return public_url
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al subir foto: {str(e)}"
            )