from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.models.usuario import Usuario, UsuarioCreate, UsuarioUpdate, UsuarioResponse
from app.services.usuario_service import UsuarioService
from app.routers.auth import get_current_active_user, require_admin

router = APIRouter()


@router.get("/", response_model=List[UsuarioResponse])
async def get_usuarios(current_user: Usuario = Depends(get_current_active_user)):
    """Obtener lista de usuarios"""
    return await UsuarioService.get_all_usuarios()


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def get_usuario(
    usuario_id: str,
    current_user: Usuario = Depends(get_current_active_user)
):
    """Obtener usuario por ID"""
    usuario = await UsuarioService.get_usuario_by_id(usuario_id)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return usuario


@router.post("/", response_model=UsuarioResponse)
async def create_usuario(
    usuario_data: UsuarioCreate,
    current_user: Usuario = Depends(require_admin)
):
    """Crear nuevo usuario (solo admins)"""
    return await UsuarioService.create_usuario(usuario_data)


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(
    usuario_id: str,
    usuario_data: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_active_user)
):
    """Actualizar usuario"""
    # Los usuarios solo pueden actualizar su propio perfil, excepto los admins
    if current_user.rol != "Admin" and current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes actualizar tu propio perfil"
        )
    
    usuario = await UsuarioService.update_usuario(usuario_id, usuario_data)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return usuario


@router.delete("/{usuario_id}")
async def delete_usuario(
    usuario_id: str,
    current_user: Usuario = Depends(require_admin)
):
    """Desactivar usuario (solo admins)"""
    success = await UsuarioService.delete_usuario(usuario_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return {"message": "Usuario desactivado exitosamente"}