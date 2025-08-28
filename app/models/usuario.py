from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class RolUsuario(str, Enum):
    ADMIN = "Admin"
    SUPERVISOR = "Supervisor"
    TECNICO = "Tecnico"
    AYUDANTE = "Ayudante"


class UsuarioBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario único")
    email: Optional[EmailStr] = Field(None, description="Correo electrónico del usuario")
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo del usuario")
    rol: RolUsuario = Field(..., description="Rol del usuario en el sistema")
    activo: bool = Field(True, description="Estado activo del usuario")


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6, description="Contraseña del usuario")


class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    rol: Optional[RolUsuario] = None
    activo: Optional[bool] = None


class Usuario(UsuarioBase):
    id: str = Field(..., description="ID único del usuario")
    ultimo_acceso: Optional[datetime] = Field(None, description="Fecha y hora del último acceso")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    class Config:
        from_attributes = True


class UsuarioResponse(BaseModel):
    """Respuesta pública del usuario (sin datos sensibles)"""
    id: str
    username: str
    nombre: str
    rol: RolUsuario
    activo: bool
    ultimo_acceso: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True