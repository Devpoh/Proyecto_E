import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User


# Configuración de tiempos de expiración
ACCESS_TOKEN_LIFETIME = timedelta(minutes=15)  # 15 minutos
REFRESH_TOKEN_LIFETIME = timedelta(hours=2)    # 2 horas (en lugar de 30 días)


def get_secret_key():
    """Obtiene la clave secreta de Django settings"""
    return settings.SECRET_KEY


def generar_access_token(usuario):
    """
    Genera un Access Token JWT para un usuario.
    
    Args:
        usuario: Instancia del modelo User
    
    Returns:
        str: Token JWT firmado
    """
    now = datetime.utcnow()
    
    # Payload mínimo para reducir tamaño del token
    payload = {
        'user_id': usuario.id,
        'username': usuario.username,
        'email': usuario.email,
        'rol': usuario.profile.rol if hasattr(usuario, 'profile') else 'cliente',
        'iat': now,  # Issued at
        'exp': now + ACCESS_TOKEN_LIFETIME,  # Expiration
        'type': 'access'  # Tipo de token
    }
    
    # Generar token JWT
    token = jwt.encode(
        payload,
        get_secret_key(),
        algorithm='HS256'
    )
    
    return token


def verificar_access_token(token):
    """
    Verifica y decodifica un Access Token JWT.
    Valida que todos los claims requeridos estén presentes.
    
    Args:
        token: Token JWT a verificar
    
    Returns:
        dict: Payload del token si es válido
        None: Si el token es inválido o expirado
    """
    import logging
    logger = logging.getLogger('security')
    
    try:
        payload = jwt.decode(
            token,
            get_secret_key(),
            algorithms=['HS256']
        )
        
        # Validar que sea un access token
        if payload.get('type') != 'access':
            logger.warning('[JWT] Token no es de tipo access')
            return None
        
        # Validar claims requeridos
        claims_requeridos = ['user_id', 'username', 'email', 'rol', 'iat', 'exp']
        for claim in claims_requeridos:
            if claim not in payload:
                logger.warning(f'[JWT] Token sin claim requerido: {claim}')
                return None
        
        # Validar que user_id sea un entero válido
        if not isinstance(payload.get('user_id'), int) or payload.get('user_id') <= 0:
            logger.warning('[JWT] user_id inválido en token')
            return None
        
        # Validar que username sea una cadena no vacía
        if not isinstance(payload.get('username'), str) or not payload.get('username').strip():
            logger.warning('[JWT] username inválido en token')
            return None
        
        # Validar que rol sea válido
        roles_validos = ['cliente', 'mensajero', 'trabajador', 'admin']
        if payload.get('rol') not in roles_validos:
            logger.warning(f'[JWT] rol inválido en token: {payload.get("rol")}')
            return None
        
        return payload
    
    except jwt.ExpiredSignatureError:
        # Token expirado
        logger.debug('[JWT] Token expirado')
        return None
    except jwt.InvalidTokenError as e:
        # Token inválido
        logger.warning(f'[JWT] Token inválido: {str(e)}')
        return None
    except Exception:
        # Cualquier otro error
        return None


def obtener_usuario_desde_token(token):
    """
    Obtiene el usuario desde un Access Token.
    
    Args:
        token: Token JWT
    
    Returns:
        User: Instancia del usuario si el token es válido
        None: Si el token es inválido o el usuario no existe
    """
    payload = verificar_access_token(token)
    
    if not payload:
        return None
    
    try:
        usuario = User.objects.get(id=payload['user_id'])
        return usuario
    except User.DoesNotExist:
        return None


def extraer_token_desde_header(request):
    """
    Extrae el token JWT desde el header Authorization.
    Soporta formato: 'Bearer <token>'
    
    Args:
        request: Objeto request de Django
    
    Returns:
        str: Token extraído o None
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    
    if auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    
    return None


def obtener_info_request(request):
    """
    Extrae información del request para auditoría.
    
    Args:
        request: Objeto request de Django
    
    Returns:
        dict: Diccionario con user_agent e ip_address
    """
    # Obtener User-Agent
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Obtener IP (considerando proxies)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0].strip()
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    
    return {
        'user_agent': user_agent[:500],  # Limitar longitud
        'ip_address': ip_address
    }
