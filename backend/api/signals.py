"""
═══════════════════════════════════════════════════════════════════════════════
🔌 SIGNALS - Eventos automáticos del sistema
═══════════════════════════════════════════════════════════════════════════════

Maneja eventos automáticos como:
- Limpiar carrito al logout
- Invalidar caché al cambiar productos
- Registrar auditoría de cambios
"""

import logging
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_out
from .models import Cart

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# 🛒 CARRITO - SIGNALS
# ═══════════════════════════════════════════════════════════════════════════════

@receiver(user_logged_out)
def limpiar_carrito_al_logout(sender, request, user, **kwargs):
    """
    ✅ FALLBACK: Limpiar carrito cuando el usuario se desloguea
    
    Este signal se dispara cuando el usuario se desloguea.
    Limpia todos los items del carrito como fallback de seguridad.
    
    Nota: El frontend también llama a DELETE /api/carrito/vaciar/
    Este signal es un fallback automático en caso de que falle el frontend.
    
    Args:
        sender: La clase que envía la señal
        request: El request HTTP
        user: El usuario que se deslogueó
        **kwargs: Argumentos adicionales
    """
    try:
        # Buscar el carrito del usuario
        cart = Cart.objects.filter(user=user).first()
        
        if cart:
            # Obtener cantidad de items antes de limpiar (para logging)
            items_count = cart.items.count()
            
            # Eliminar todos los items del carrito
            cart.items.all().delete()
            
            # Logging
            logger.info(
                f'[SIGNAL] Carrito limpiado al logout: '
                f'Usuario={user.username} | Items eliminados={items_count}'
            )
    except Exception as error:
        logger.error(
            f'[SIGNAL] Error limpiando carrito al logout: '
            f'Usuario={user.username if user else "Unknown"} | Error={error}'
        )
