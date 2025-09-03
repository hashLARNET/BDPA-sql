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
            print(f"🔐 Intentando autenticar usuario: {username}")
            
            # Intentar primero con función RPC si existe
            try:
                response = supabase_client.rpc('authenticate_user', {
                    'username_param': username,
                    'password_param': password
                }).execute()
                
                if response.data and len(response.data) > 0:
                    auth_result = response.data[0]
                    
                    # Verificar si la autenticación fue exitosa
                    if auth_result.get('success', False):
                        print(f"✅ Autenticación RPC exitosa para: {username}")
                        
                        # Crear objeto Usuario con los datos retornados
                        user_data = {
                            'id': auth_result['user_id'],
                            'username': auth_result['username'],
                            'email': auth_result['email'],
                            'nombre': auth_result['nombre'],
                            'rol': auth_result['rol'],
                            'activo': auth_result['activo'],
                            'ultimo_acceso': auth_result['ultimo_acceso'],
                            'created_at': datetime.utcnow(),
                            'updated_at': datetime.utcnow()
                        }
                        
                        return Usuario(**user_data)
                    else:
                        print(f"❌ Autenticación RPC falló: {auth_result.get('message', 'Error desconocido')}")
                        return None
                        
            except Exception as rpc_error:
                print(f"⚠️ Función RPC no disponible, usando método directo: {rpc_error}")
                
                # Método alternativo: consulta directa a la tabla usuarios
                response = supabase_client.table('usuarios').select('*').eq('username', username).eq('activo', True).execute()
                
                if not response.data or len(response.data) == 0:
                    print(f"❌ Usuario no encontrado: {username}")
                    return None
                
                user_data = response.data[0]
                stored_hash = user_data.get('password_hash')
                
                if not stored_hash:
                    print(f"❌ No hay hash de contraseña para: {username}")
                    return None
                
                # Verificar contraseña
                if AuthService.verify_password(password, stored_hash):
                    print(f"✅ Autenticación directa exitosa para: {username}")
                    
                    # Actualizar último acceso
                    try:
                        supabase_client.table('usuarios').update({
                            'ultimo_acceso': datetime.utcnow().isoformat()
                        }).eq('id', user_data['id']).execute()
                    except:
                        pass  # No crítico si falla la actualización
                    
                    return Usuario(**user_data)
                else:
                    print(f"❌ Contraseña incorrecta para: {username}")
                    return None
                    
        except Exception as e:
            print(f"💥 Error general en autenticación: {e}")
            return None
    
    @staticmethod
    async def change_user_password(user_id: str, old_password: str, new_password: str) -> bool:
        """Cambiar contraseña de usuario"""
        try:
            response = supabase_client.rpc('change_password', {
                'user_id_param': user_id,
                'old_password': old_password,
                'new_password': new_password
            }).execute()
            
            if response.data and len(response.data) > 0:
                result = response.data[0]
                return result.get('success', False)
            
            return False
            
        except Exception as e:
            print(f"Error cambiando contraseña: {e}")
            return False
    
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