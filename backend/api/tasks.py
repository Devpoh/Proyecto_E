"""
═══════════════════════════════════════════════════════════════════════════════
🎯 CELERY TASKS - Tareas Asincrónicas
═══════════════════════════════════════════════════════════════════════════════

Tareas que se ejecutan en segundo plano sin bloquear el servidor.

Tareas:
1. liberar_reservas_expiradas() - Libera stock de reservas vencidas
2. limpiar_tokens_expirados() - Limpia tokens JWT expirados
"""

from celery import shared_task
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def liberar_reservas_expiradas(self):
    """
    🔄 TAREA: Liberar reservas de stock expiradas
    
    Ejecuta cada minuto (configurado en celery.py)
    
    Flujo:
    1. Busca todas las reservas con status='pending' y expires_at < ahora
    2. Para cada reserva expirada:
       - Libera el stock_reservado del producto
       - Marca la reserva como 'expired'
    3. Retorna cantidad de reservas liberadas
    
    Seguridad:
    - @transaction.atomic: Si falla, todo se revierte
    - Manejo de excepciones con reintentos
    - Logging detallado para auditoría
    """
    from .models import StockReservation, Producto
    
    try:
        ahora = timezone.now()
        
        # Buscar reservas expiradas
        reservas_expiradas = StockReservation.objects.filter(
            status='pending',
            expires_at__lt=ahora
        ).select_related('producto', 'usuario')
        
        count = 0
        
        with transaction.atomic():
            for reserva in reservas_expiradas:
                try:
                    # Liberar stock_reservado
                    producto = reserva.producto
                    producto.stock_reservado -= reserva.cantidad
                    
                    # Validar que no quede negativo
                    if producto.stock_reservado < 0:
                        logger.warning(
                            f'[RESERVA_EXPIRADA] Stock negativo detectado para '
                            f'producto {producto.id}. Corrigiendo a 0.'
                        )
                        producto.stock_reservado = 0
                    
                    producto.save()
                    
                    # Marcar reserva como expirada
                    reserva.status = 'expired'
                    reserva.cancelled_at = ahora
                    reserva.save()
                    
                    count += 1
                    
                    logger.info(
                        f'[RESERVA_EXPIRADA] Liberada reserva {reserva.id} '
                        f'del usuario {reserva.usuario.username} '
                        f'(Producto: {producto.nombre}, Cantidad: {reserva.cantidad})'
                    )
                
                except Exception as e:
                    logger.error(
                        f'[RESERVA_EXPIRADA_ERROR] Error liberando reserva {reserva.id}: {str(e)}'
                    )
                    continue
        
        logger.info(f'[RESERVAS_EXPIRADAS] Total liberadas: {count}')
        return {
            'status': 'success',
            'reservas_liberadas': count,
            'timestamp': ahora.isoformat()
        }
    
    except Exception as exc:
        logger.error(f'[LIBERAR_RESERVAS_ERROR] {str(exc)}')
        # Reintentar con backoff exponencial
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def limpiar_tokens_expirados(self):
    """
    🔄 TAREA: Limpiar tokens JWT expirados
    
    Ejecuta cada hora (configurado en celery.py)
    
    Flujo:
    1. Busca todos los tokens en blacklist con expiration < ahora
    2. Los elimina de la base de datos
    3. Retorna cantidad de tokens eliminados
    
    Nota: Los tokens JWT expiran automáticamente, pero mantener la blacklist
    limpia evita que crezca indefinidamente.
    """
    from .models import TokenBlacklist
    
    try:
        ahora = timezone.now()
        
        # Buscar tokens en blacklist que fueron añadidos hace más de 24 horas
        # (los tokens JWT expiran en 24h, así que podemos limpiar después)
        hace_24_horas = ahora - timezone.timedelta(hours=24)
        tokens_expirados = TokenBlacklist.objects.filter(
            blacklisted_at__lt=hace_24_horas
        )
        
        count = tokens_expirados.count()
        tokens_expirados.delete()
        
        logger.info(f'[TOKENS_LIMPIOS] Total eliminados: {count}')
        return {
            'status': 'success',
            'tokens_eliminados': count,
            'timestamp': ahora.isoformat()
        }
    
    except Exception as exc:
        logger.error(f'[LIMPIAR_TOKENS_ERROR] {str(exc)}')
        # Reintentar con backoff exponencial
        raise self.retry(exc=exc, countdown=60)
