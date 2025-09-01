from typing import List, Optional
from fastapi import HTTPException, status

from app.models.usuario import Usuario, UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.services.supabase_client import supabase_client
from app.services.auth_service import AuthService


class UsuarioService:
    """Servicio para gestión de usuarios"""
    
    @staticmethod
    async def get_all_usuarios() -> List[UsuarioResponse]:
        """Obtener todos los usuarios"""
        try:
            response = supabase_client.table('usuarios').select('*').eq('activo', True).order('nombre').execute()
            
            return [UsuarioResponse(**user) for user in response.data]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener usuarios: {str(e)}"
            )
    
    @staticmethod
    async def get_usuario_by_id(usuario_id: str) -> Optional[UsuarioResponse]:
        """Obtener usuario por ID"""
        try:
            response = supabase_client.table('usuarios').select('*').eq('id', usuario_id).execute()
            
            if not response.data:
                return None
            
            return UsuarioResponse(**response.data[0])
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener usuario: {str(e)}"
            )
    
    @staticmethod
    async def create_usuario(usuario_data: UsuarioCreate) -> UsuarioResponse:
        """Crear nuevo usuario"""
        try:
            # Verificar si el username ya existe
            existing = supabase_client.table('usuarios').select('id').eq('username', usuario_data.username).execute()
            
            if existing.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre de usuario ya existe"
                )
            
            # LIMITACIÓN CRÍTICA: El esquema actual de Supabase no incluye una columna 
            # para contraseñas hasheadas en la tabla 'usuarios'. Para implementar 
            # seguridad adecuada, se requiere:
            # 1. Agregar columna 'password_hash' a la tabla usuarios
            # 2. Usar AuthService.get_password_hash() para hashear contraseñas
            # 3. Almacenar solo el hash, nunca la contraseña en texto plano
            #
            # Implementación temporal (INSEGURA):
            user_dict = usuario_data.dict()
            password = user_dict.pop('password')  # Extraer contraseña
            
            # TODO: Una vez que se agregue la columna password_hash a la tabla usuarios:
            # user_dict['password_hash'] = AuthService.get_password_hash(password)
            #
            # Por ahora, la contraseña no se almacena (todos los usuarios usan "password123")
            # ESTO ES INSEGURO Y DEBE CAMBIARSE EN PRODUCCIÓN
            
            response = supabase_client.table('usuarios').insert(user_dict).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al crear usuario"
                )
            
            return UsuarioResponse(**response.data[0])
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear usuario: {str(e)}"
            )
    
    @staticmethod
    async def update_usuario(usuario_id: str, usuario_data: UsuarioUpdate) -> Optional[UsuarioResponse]:
        """Actualizar usuario"""
        try:
            # Filtrar campos None
            update_data = {k: v for k, v in usuario_data.dict().items() if v is not None}
            
            if not update_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No hay datos para actualizar"
                )
            
            response = supabase_client.table('usuarios').update(update_data).eq('id', usuario_id).execute()
            
            if not response.data:
                return None
            
            return UsuarioResponse(**response.data[0])
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al actualizar usuario: {str(e)}"
            )
    
    @staticmethod
    async def delete_usuario(usuario_id: str) -> bool:
        """Desactivar usuario (soft delete)"""
        try:
            response = supabase_client.table('usuarios').update({'activo': False}).eq('id', usuario_id).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al desactivar usuario: {str(e)}"
            )