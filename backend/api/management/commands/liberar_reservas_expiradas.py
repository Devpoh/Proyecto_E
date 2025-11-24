"""
═══════════════════════════════════════════════════════════════════════════════
MANAGEMENT COMMAND - Liberar Reservas Expiradas
═══════════════════════════════════════════════════════════════════════════════

Comando para liberar automáticamente las reservas de stock que han expirado.

USO:
    python manage.py liberar_reservas_expiradas

Este comando debe ejecutarse periódicamente (cada 5 minutos) mediante:
- Celery Beat (recomendado para producción)
- Cron job (alternativa simple)
- APScheduler

FLUJO:
1. Busca todas las reservas con status='pending' y expires_at < ahora
2. Para cada reserva expirada:
   - Libera el stock (stock_reservado -= cantidad)
   - Marca la reserva como 'expired'
3. Registra el resultado en logs
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import StockReservation
import logging

logger = logging.getLogger('security')


class Command(BaseCommand):
    help = 'Libera automáticamente las reservas de stock que han expirado (TTL)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Mostrar detalles de cada reserva liberada',
        )

    def handle(self, *args, **options):
        verbose = options.get('verbose', False)
        
        self.stdout.write(
            self.style.SUCCESS('[INICIO] Iniciando liberación de reservas expiradas...')
        )
        
        try:
            # Llamar al método de clase para liberar reservas
            count = StockReservation.liberar_reservas_expiradas()
            
            if count > 0:
                mensaje = f'[OK] {count} reservas expiradas liberadas exitosamente'
                self.stdout.write(self.style.SUCCESS(mensaje))
                logger.info(f'[STOCK] {mensaje}')
                
                if verbose:
                    # Mostrar detalles
                    reservas_liberadas = StockReservation.objects.filter(
                        status='expired'
                    ).order_by('-cancelled_at')[:count]
                    
                    for reserva in reservas_liberadas:
                        self.stdout.write(
                            f'  - {reserva.usuario.username}: '
                            f'{reserva.producto.nombre} x{reserva.cantidad}'
                        )
            else:
                mensaje = '[INFO] No hay reservas expiradas para liberar'
                self.stdout.write(self.style.WARNING(mensaje))
                logger.info(f'[STOCK] {mensaje}')
        
        except Exception as e:
            mensaje_error = f'[ERROR] Error al liberar reservas: {str(e)}'
            self.stdout.write(self.style.ERROR(mensaje_error))
            logger.error(f'[STOCK] {mensaje_error}')
            raise
