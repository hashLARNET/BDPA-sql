from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, description="Nombre de usuario")
    password: str = Field(..., min_length=6, description="Contraseña")


class Token(BaseModel):
    access_token: str = Field(..., description="Token de acceso JWT")
    token_type: str = Field("bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Tiempo de expiración en segundos")
    user: dict = Field(..., description="Información básica del usuario")


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None
    rol: Optional[str] = None