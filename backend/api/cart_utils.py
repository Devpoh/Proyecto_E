"""
Utilidades para el carrito: Rate Limiting y Auditoría
"""
from datetime import timedelta
from django.utils import timezone
from django.core.cache import cache
from .models import CartAuditLog


def get_client_ip(request):
    """Obtener IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Obtener User-Agent del cliente"""
    return request.META.get('HTTP_USER_AGENT', '')


def check_rate_limit(user_id, action, limit=100, window_minutes=60):
    """
    Verificar rate limiting por usuario y acción
    
    Args:
        user_id: ID del usuario
        action: Tipo de acción ('add', 'update', 'remove', 'clear')
        limit: Número máximo de acciones permitidas
        window_minutes: Ventana de tiempo en minutos
    
    Returns:
        (allowed: bool, remaining: int, reset_time: datetime)
    """
    cache_key = f'cart_rate_limit:{user_id}:{action}'
    
    # Obtener contador actual
    current_count = cache.get(cache_key, 0)
    
    if current_count >= limit:
        # Obtener tiempo de reset
        try:
            # Intentar usar ttl() si está disponible (Redis)
            ttl = cache.ttl(cache_key)
            reset_time = timezone.now() + timedelta(seconds=ttl if ttl > 0 else window_minutes * 60)
        except AttributeError:
            # Fallback si ttl() no está disponible (LocMemCache)
            reset_time = timezone.now() + timedelta(minutes=window_minutes)
        return False, 0, reset_time
    
    # Incrementar contador
    new_count = current_count + 1
    cache.set(cache_key, new_count, window_minutes * 60)
    
    remaining = limit - new_count
    reset_time = timezone.now() + timedelta(minutes=window_minutes)
    
    return True, remaining, reset_time


def log_cart_action(user, action, product_id=None, product_name=None, 
                   quantity_before=None, quantity_after=None, price=None,
                   request=None):
    """
    Registrar acción en auditoría del carrito
    
    Args:
        user: Usuario que realizó la acción
        action: Tipo de acción ('add', 'update', 'remove', 'clear')
        product_id: ID del producto (si aplica)
        product_name: Nombre del producto (snapshot)
        quantity_before: Cantidad antes
        quantity_after: Cantidad después
        price: Precio del producto
        request: Request object para obtener IP y User-Agent
    """
    ip_address = None
    user_agent = ''
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
    
    CartAuditLog.objects.create(
        user=user,
        action=action,
        product_id=product_id,
        product_name=product_name or '',
        quantity_before=quantity_before,
        quantity_after=quantity_after,
        price=price,
        ip_address=ip_address,
        user_agent=user_agent,
    )
