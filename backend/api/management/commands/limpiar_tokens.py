"""
═══════════════════════════════════════════════════════════════════════════════
COMANDO - Limpiar Tokens
═══════════════════════════════════════════════════════════════════════════════

Limpia tokens expirados, intentos de login antiguos y tokens en blacklist.
Ejecutar diariamente vía cron: 0 2 * * * cd /ruta/backend && python manage.py limpiar_tokens

Uso: python manage.py limpiar_tokens
"""

from django.core.management.base import BaseCommand
from api.models import RefreshToken, LoginAttempt, TokenBlacklist
import logging

logger = logging.getLogger('security')


class Command(BaseCommand):
    help = 'Limpia tokens expirados, intentos de login antiguos y tokens en blacklist'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias-blacklist',
            type=int,
            default=31,
            help='Eliminar tokens en blacklist más antiguos que X días (default: 31)'
        )
        parser.add_argument(
            '--dias-intentos',
            type=int,
            default=7,
            help='Eliminar intentos de login más antiguos que X días (default: 7)'
        )

    def handle(self, *args, **options):
        self.stdout.write('[CLEANUP] Iniciando limpieza de tokens...\n')
        
        dias_blacklist = options['dias_blacklist']
        dias_intentos = options['dias_intentos']
        
        total_eliminados = 0
        
        # 1. Limpiar tokens expirados
        self.stdout.write('  → Limpiando Refresh Tokens expirados...')
        tokens_count = RefreshToken.limpiar_tokens_expirados()
        
        if tokens_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'    [OK] Se eliminaron {tokens_count} Refresh Tokens expirados')
            )
            logger.info(f'[CLEANUP] Eliminados {tokens_count} Refresh Tokens expirados')
            total_eliminados += tokens_count
        else:
            self.stdout.write(
                self.style.SUCCESS('    [OK] No hay Refresh Tokens expirados para eliminar')
            )
        
        # 2. Limpiar intentos de login antiguos
        self.stdout.write(f'  → Limpiando intentos de login antiguos (>{dias_intentos} días)...')
        attempts_count = LoginAttempt.limpiar_intentos_antiguos(dias=dias_intentos)
        
        if attempts_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'    [OK] Se eliminaron {attempts_count} intentos de login antiguos')
            )
            logger.info(f'[CLEANUP] Eliminados {attempts_count} intentos de login antiguos')
            total_eliminados += attempts_count
        else:
            self.stdout.write(
                self.style.SUCCESS('    [OK] No hay intentos de login antiguos para eliminar')
            )
        
        # 3. Limpiar tokens en blacklist antiguos
        self.stdout.write(f'  → Limpiando tokens en blacklist antiguos (>{dias_blacklist} días)...')
        deleted_count, _ = TokenBlacklist.limpiar_expirados(dias=dias_blacklist)
        
        if deleted_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'    [OK] Se eliminaron {deleted_count} tokens en blacklist antiguos')
            )
            logger.info(f'[CLEANUP] Eliminados {deleted_count} tokens en blacklist antiguos')
            total_eliminados += deleted_count
        else:
            self.stdout.write(
                self.style.SUCCESS('    [OK] No hay tokens en blacklist antiguos para eliminar')
            )
        
        # Resumen
        self.stdout.write(self.style.SUCCESS(f'\n[SUCCESS] Limpieza completada exitosamente'))
        self.stdout.write(self.style.SUCCESS(f'   Total eliminados: {total_eliminados} registros\n'))
