"""
═══════════════════════════════════════════════════════════════════════════════
🔄 CACHE MANAGER - Gestión Robusta de Caché con Invalidación Explícita
═══════════════════════════════════════════════════════════════════════════════

Implementa estrategia Cache-Aside con invalidación explícita para:
1. Datos Desactualizados (Cache Staleness)
2. Invalidación Explícita después de cambios
3. TTL (Time To Live) configurable
4. Monitoreo de aciertos/fallos
"""

from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger('cache_manager')


class CacheManager:
    """
    Gestor de caché con invalidación explícita y TTL configurable
    
    Estrategia: Cache-Aside
    - Lectura: Intentar caché → Si falla, ir a BD → Guardar en caché
    - Escritura: Escribir en BD → Invalidar caché
    """
    
    # TTL por tipo de dato (en segundos)
    TTL_CONFIG = {
        'estadisticas_ventas': 300,        # 5 minutos - datos volátiles
        'estadisticas_usuarios': 600,      # 10 minutos - menos volátiles
        'productos_vendidos': 300,         # 5 minutos - muy volátil
        'metodos_pago': 600,               # 10 minutos
        'perfil_usuario': 3600,            # 1 hora - relativamente estable
        'lista_productos': 300,            # 5 minutos - volátil
    }
    
    @staticmethod
    def get(cache_key, fetch_func=None, ttl=None):
        """
        Obtener dato del caché o de la fuente original
        
        Args:
            cache_key: Clave única del caché
            fetch_func: Función que obtiene el dato de la fuente original
            ttl: Tiempo de vida en segundos (si None, usa TTL_CONFIG)
        
        Returns:
            Dato del caché o de la fuente original
        """
        # Intentar obtener del caché
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            logger.info(f"✅ Cache HIT: {cache_key}")
            return cached_data
        
        # Cache MISS - obtener de la fuente original
        logger.warning(f"❌ Cache MISS: {cache_key}")
        
        if fetch_func is None:
            return None
        
        # Ejecutar función para obtener datos
        data = fetch_func()
        
        # Guardar en caché con TTL
        if data is not None:
            ttl = ttl or CacheManager.TTL_CONFIG.get(cache_key, 300)
            cache.set(cache_key, data, ttl)
            logger.info(f"💾 Guardado en caché: {cache_key} (TTL: {ttl}s)")
        
        return data
    
    @staticmethod
    def invalidate(cache_keys):
        """
        Invalidar uno o múltiples registros de caché
        
        Args:
            cache_keys: String o lista de strings con claves a invalidar
        """
        if isinstance(cache_keys, str):
            cache_keys = [cache_keys]
        
        for key in cache_keys:
            cache.delete(key)
            logger.info(f"🗑️  Invalidado caché: {key}")
    
    @staticmethod
    def invalidate_pattern(pattern):
        """
        Invalidar todos los registros que coincidan con un patrón
        
        Args:
            pattern: Patrón de clave (ej: 'estadisticas_*')
        
        Nota: Requiere Redis o similar. Con LocMemCache no funciona.
        """
        try:
            # Intenta con Redis (si está disponible)
            cache.delete_pattern(pattern)
            logger.info(f"🗑️  Invalidado patrón: {pattern}")
        except AttributeError:
            # LocMemCache no soporta delete_pattern
            logger.warning(f"⚠️  delete_pattern no soportado en este backend de caché")
    
    @staticmethod
    def clear_all():
        """Limpiar todo el caché (usar con cuidado)"""
        cache.clear()
        logger.warning("🗑️  TODO el caché ha sido limpiado")
    
    @staticmethod
    def get_stats():
        """
        Obtener estadísticas del caché
        
        Returns:
            dict con información de aciertos/fallos
        """
        stats_key = '_cache_stats'
        stats = cache.get(stats_key, {
            'hits': 0,
            'misses': 0,
            'invalidations': 0,
            'last_updated': None
        })
        return stats


# ═══════════════════════════════════════════════════════════════════════════════
# INVALIDACIÓN EXPLÍCITA - Señales para invalidar caché después de cambios
# ═══════════════════════════════════════════════════════════════════════════════

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from ..models import Producto, Pedido, UserProfile


@receiver(post_save, sender=Producto)
def invalidate_producto_cache(sender, instance, created, **kwargs):
    """
    Invalidar caché cuando se crea o actualiza un Producto
    
    Estrategia: Write-through
    - Escribir en BD (ya hecho por Django)
    - Invalidar caché relacionado
    """
    cache_keys_to_invalidate = [
        'estadisticas_ventas',
        'productos_vendidos',
        'lista_productos',
        f'producto_{instance.id}',
    ]
    
    CacheManager.invalidate(cache_keys_to_invalidate)
    
    action = "creado" if created else "actualizado"
    logger.info(f"📦 Producto {action}: {instance.nombre} - Caché invalidado")


@receiver(post_delete, sender=Producto)
def invalidate_producto_delete_cache(sender, instance, **kwargs):
    """Invalidar caché cuando se elimina un Producto"""
    cache_keys_to_invalidate = [
        'estadisticas_ventas',
        'productos_vendidos',
        'lista_productos',
    ]
    
    CacheManager.invalidate(cache_keys_to_invalidate)
    logger.info(f"📦 Producto eliminado: {instance.nombre} - Caché invalidado")


@receiver(post_save, sender=Pedido)
def invalidate_pedido_cache(sender, instance, created, **kwargs):
    """
    Invalidar caché cuando se crea o actualiza un Pedido
    
    Importante: Los pedidos afectan las estadísticas de ventas
    """
    cache_keys_to_invalidate = [
        'estadisticas_ventas',
        'metodos_pago',
    ]
    
    CacheManager.invalidate(cache_keys_to_invalidate)
    
    action = "creado" if created else "actualizado"
    logger.info(f"📋 Pedido {action}: {instance.id} - Caché invalidado")


@receiver(post_save, sender=UserProfile)
def invalidate_user_cache(sender, instance, created, **kwargs):
    """Invalidar caché cuando se crea o actualiza un UserProfile"""
    cache_keys_to_invalidate = [
        'estadisticas_usuarios',
        f'user_profile_{instance.user.id}',
    ]
    
    CacheManager.invalidate(cache_keys_to_invalidate)
    
    action = "creado" if created else "actualizado"
    logger.info(f"👤 UserProfile {action}: {instance.user.username} - Caché invalidado")


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN RECOMENDADA EN settings.py
# ═══════════════════════════════════════════════════════════════════════════════

"""
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'electro_isla',
        'TIMEOUT': 300,  # TTL por defecto: 5 minutos
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'cache_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/cache.log',
        },
    },
    'loggers': {
        'cache_manager': {
            'handlers': ['cache_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
"""
