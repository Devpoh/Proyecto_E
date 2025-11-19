"""
═══════════════════════════════════════════════════════════════════════════════
🔐 AUTHENTICATION - JWT Authentication for Django REST Framework
═══════════════════════════════════════════════════════════════════════════════

Clase de autenticación JWT personalizada para DRF.
Compatible con el sistema de Access Token + Refresh Token.

CARACTERÍSTICAS:
- Manejo robusto de expiración de tokens
- Validación completa del JWT
- Mensajes de error claros
- Compatible con el sistema de permisos de DRF
"""

import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from .utils.jwt_utils import verificar_access_token


class JWTAuthentication(BaseAuthentication):
    """
    Autenticación JWT para Django REST Framework.
    
    Extrae el token del header Authorization: Bearer <token>
    y autentica al usuario automáticamente.
    
    FLUJO:
    1. Extrae token del header Authorization
    2. Verifica y decodifica el JWT
    3. Valida que el usuario existe y está activo
    4. Retorna (user, token_payload)
    """
    
    keyword = 'Bearer'
    
    def authenticate(self, request):
        """
        Autentica el request usando JWT.
        
        Args:
            request: Request de Django/DRF
        
        Returns:
            tuple: (user, token_payload) si la autenticación es exitosa
            None: si no hay token (permite acceso anónimo)
        
        Raises:
            AuthenticationFailed: si el token es inválido, expirado o el usuario no existe
        """
        # Extraer token del header Authorization
        auth_header = self.get_authorization_header(request)
        
        if not auth_header:
            # No hay header de autorización, permitir acceso anónimo
            # Las vistas con permission_classes decidirán si es válido
            return None
        
        # Extraer el token del header
        try:
            token = self.extract_token(auth_header)
        except AuthenticationFailed:
            # Si hay error en el formato, lanzar excepción
            # Esto solo pasa si el header está mal formado
            raise
        
        if not token:
            return None
        
        # Verificar y decodificar el token
        payload = verificar_access_token(token)
        
        if not payload:
            # Token inválido o expirado
            # IMPORTANTE: Solo lanzar error si la vista REQUIERE autenticación
            # Si es AllowAny, retornar None para permitir acceso anónimo
            raise AuthenticationFailed({
                'detail': 'Token inválido o expirado',
                'code': 'token_invalid'
            })
        
        # Obtener el usuario desde el payload
        try:
            user_id = payload.get('user_id')
            if not user_id:
                raise AuthenticationFailed({
                    'detail': 'Token no contiene user_id',
                    'code': 'token_invalid'
                })
            
            usuario = User.objects.get(id=user_id)
            
            # Verificar que el usuario esté activo
            if not usuario.is_active:
                raise AuthenticationFailed({
                    'detail': 'Usuario inactivo',
                    'code': 'user_inactive'
                })
            
            # Retornar usuario y payload del token
            # DRF espera una tupla (user, auth)
            return (usuario, payload)
            
        except User.DoesNotExist:
            raise AuthenticationFailed({
                'detail': 'Usuario no encontrado',
                'code': 'user_not_found'
            })
        except AuthenticationFailed:
            # Re-lanzar errores de autenticación
            raise
        except Exception as e:
            raise AuthenticationFailed({
                'detail': f'Error de autenticación: {str(e)}',
                'code': 'authentication_error'
            })
    
    def get_authorization_header(self, request):
        """
        Obtiene el header de autorización del request.
        
        Args:
            request: Request de Django/DRF
        
        Returns:
            str: Header de autorización o None
        """
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        return auth
    
    def extract_token(self, auth_header):
        """
        Extrae el token del header de autorización.
        Formato esperado: 'Bearer <token>'
        
        Args:
            auth_header: String del header Authorization
        
        Returns:
            str: Token extraído o None
        """
        parts = auth_header.split()
        
        if len(parts) == 0:
            # Header vacío
            return None
        
        if parts[0].lower() != self.keyword.lower():
            # No es un token Bearer
            return None
        
        if len(parts) == 1:
            # No hay token después de 'Bearer'
            raise AuthenticationFailed({
                'detail': 'Token no proporcionado',
                'code': 'token_missing'
            })
        
        if len(parts) > 2:
            # Formato inválido
            raise AuthenticationFailed({
                'detail': 'Formato de token inválido. Use: Bearer <token>',
                'code': 'token_format_invalid'
            })
        
        return parts[1]
    
    def authenticate_header(self, request):
        """
        Retorna el string que se usará en el header WWW-Authenticate
        cuando la autenticación falla.
        
        Esto le dice al cliente qué tipo de autenticación se espera.
        """
        return self.keyword
