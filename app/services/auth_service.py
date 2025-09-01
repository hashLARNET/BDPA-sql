from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.config import settings
from app.models.auth import TokenData
from app.models.usuario import Usuario
from app.services.supabase_client import supabase_client

# Configuración de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Servicio de autenticación"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar contraseña"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generar hash de contraseña"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        """Crear token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> TokenData:
        """Verificar y decodificar token JWT"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudieron validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            rol: str = payload.get("rol")
            
            if username is None:
                raise credentials_exception
                
            token_data = TokenData(username=username, user_id=user_id, rol=rol)
            return token_data
        except JWTError:
            raise credentials_exception
    
    @staticmethod
    async def authenticate_user(username: str, password: str) -> Optional[Usuario]:
        """Autenticar usuario"""
        try:
            # Buscar usuario por username
            response = supabase_client.table('usuarios').select('*').eq('username', username).eq('activo', True).execute()
            
            if not response.data:
                return None
            
            user_data = response.data[0]
            
            # LIMITACIÓN CRÍTICA: El esquema actual de Supabase no incluye una columna 
            # para contraseñas hasheadas en la tabla 'usuarios'. Para implementar 
            # seguridad adecuada, se requiere:
            # 1. Agregar columna 'password_hash' a la tabla usuarios
            # 2. Migrar usuarios existentes con contraseñas hasheadas
            # 3. Actualizar esta función para usar verify_password()
            #
            # Implementación temporal para desarrollo:
            if 'password_hash' in user_data and user_data['password_hash']:
                # Si existe hash en BD, usar verificación segura
                if AuthService.verify_password(password, user_data['password_hash']):
                    # Actualizar último acceso
                    supabase_client.table('usuarios').update({
                        'ultimo_acceso': datetime.utcnow().isoformat()
                    }).eq('id', user_data['id']).execute()
                    
                    return Usuario(**user_data)
            else:
                # Fallback temporal para desarrollo (INSEGURO)
                # TODO: ELIMINAR en producción una vez implementado el esquema de contraseñas
                if password == "password123":
                    # Actualizar último acceso
                    supabase_client.table('usuarios').update({
                        'ultimo_acceso': datetime.utcnow().isoformat()
                    }).eq('id', user_data['id']).execute()
                    
                    return Usuario(**user_data)
            
            return None
            
        except Exception as e:
            print(f"Error en autenticación: {e}")
            return None
    
    @staticmethod
    async def get_current_user(token: str) -> Usuario:
        """Obtener usuario actual desde token"""
        token_data = AuthService.verify_token(token)
        
        try:
            response = supabase_client.table('usuarios').select('*').eq('id', token_data.user_id).eq('activo', True).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no encontrado"
                )
            
            return Usuario(**response.data[0])
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error al obtener usuario"
            )