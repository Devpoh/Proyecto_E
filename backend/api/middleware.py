"""
═══════════════════════════════════════════════════════════════════════════════
🔧 MIDDLEWARE - JWT Authentication & Token Blacklist
═══════════════════════════════════════════════════════════════════════════════

Middleware para autenticar usuarios usando JWT Access Tokens.
Valida que los tokens no estén en la blacklist (logout).

El frontend envía: Authorization: Bearer <jwt_token>
Este middleware verifica el JWT y autentica al usuario automáticamente.
"""

from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from .utils import obtener_usuario_desde_token, extraer_token_desde_header
from .models import TokenBlacklist
import logging

logger = logging.getLogger('security')


class JWTAuthenticationMiddleware:
    """
    Middleware para autenticar usuarios usando JWT.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extraer token JWT del header
        token = extraer_token_desde_header(request)
        
        if token:
            # Verificar y obtener usuario desde el token
            usuario = obtener_usuario_desde_token(token)
            
            if usuario:
                # Autenticar usuario en el request
                request.user = usuario
            else:
                # Token inválido o expirado
                request.user = AnonymousUser()
        else:
            # No hay token
            request.user = AnonymousUser()
        
        response = self.get_response(request)
        return response


class TokenBlacklistMiddleware:
    """
    ═══════════════════════════════════════════════════════════════════════════════
    🛡️ MIDDLEWARE - Token Blacklist Validation
    ═══════════════════════════════════════════════════════════════════════════════
    
    Valida que los tokens no estén en la blacklist (invalidados por logout).
    Se ejecuta DESPUÉS de la autenticación JWT.
    
    Si el token está en blacklist:
    - Retorna 401 Unauthorized
    - Registra el intento en logs de seguridad
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Extraer token del header Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]  # Remover 'Bearer '
            
            # Verificar si está en blacklist
            if TokenBlacklist.esta_en_blacklist(token):
                logger.warning(
                    f'[SECURITY] Token en blacklist usado por {request.user} desde {self.get_client_ip(request)}'
                )
                
                # Retornar 401 Unauthorized
                return JsonResponse({
                    'detail': 'Token ha sido invalidado. Por favor inicia sesión nuevamente.',
                    'code': 'token_blacklisted'
                }, status=401)
        
        response = self.get_response(request)
        return response
    
    @staticmethod
    def get_client_ip(request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
