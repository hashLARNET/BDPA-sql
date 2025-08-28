from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.auth import LoginRequest, Token
from app.models.usuario import Usuario
from app.services.auth_service import AuthService
from app.config import settings

router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """Iniciar sesión"""
    user = await AuthService.authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token de acceso
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "rol": user.rol
        },
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user.id,
            "username": user.username,
            "nombre": user.nombre,
            "rol": user.rol,
            "activo": user.activo
        }
    )


@router.get("/me", response_model=Usuario)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Obtener información del usuario actual"""
    return await AuthService.get_current_user(credentials.credentials)


@router.post("/logout")
async def logout():
    """Cerrar sesión"""
    # En una implementación JWT stateless, el logout se maneja en el frontend
    # eliminando el token. Aquí podríamos implementar una blacklist si fuera necesario.
    return {"message": "Sesión cerrada exitosamente"}


# Dependencia para obtener usuario actual
async def get_current_active_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Usuario:
    """Dependencia para obtener el usuario actual autenticado"""
    user = await AuthService.get_current_user(credentials.credentials)
    
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    return user


# Dependencia para verificar rol de administrador
async def require_admin(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
    """Dependencia que requiere rol de administrador"""
    if current_user.rol != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )
    return current_user


# Dependencia para verificar rol de supervisor o admin
async def require_supervisor_or_admin(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
    """Dependencia que requiere rol de supervisor o administrador"""
    if current_user.rol not in ["Admin", "Supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de supervisor o administrador"
        )
    return current_user