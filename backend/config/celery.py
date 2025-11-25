"""
═══════════════════════════════════════════════════════════════════════════════
🚀 CELERY CONFIGURATION
═══════════════════════════════════════════════════════════════════════════════

Configuración de Celery para tareas asincrónicas en segundo plano.

Flujo:
1. Beat (scheduler) programa tareas cada X tiempo
2. Broker (Redis) almacena las tareas pendientes
3. Worker ejecuta las tareas
4. Result backend (Redis) guarda resultados

Uso:
- Desarrollo: celery -A config worker -l info --pool=solo
- Beat: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

⚠️ IMPORTANTE EN WINDOWS:
- Usar --pool=solo para evitar problemas con prefork
- O usar --pool=threads para multithreading
"""

import os
from celery import Celery
from celery.schedules import crontab

# Configurar módulo de settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Crear instancia de Celery
app = Celery('electro_isla')

# Cargar configuración desde Django settings con namespace CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descubrir tareas en todos los apps instalados
app.autodiscover_tasks()

# Configuración de Beat (tareas programadas)
app.conf.beat_schedule = {
    # Liberar reservas expiradas cada 20 minutos
    'liberar-reservas-expiradas': {
        'task': 'api.tasks.liberar_reservas_expiradas',
        'schedule': crontab(minute='*/20'),  # Cada 20 minutos
    },
    # Limpiar tokens expirados cada hora
    'limpiar-tokens-expirados': {
        'task': 'api.tasks.limpiar_tokens_expirados',
        'schedule': crontab(minute=0),  # Cada hora
    },
    # Limpiar códigos de verificación expirados cada 6 horas
    'limpiar-codigos-verificacion': {
        'task': 'api.tasks.limpiar_codigos_verificacion',
        'schedule': crontab(hour='*/6'),  # Cada 6 horas
    },
}

# ✅ Configuración para Windows - CRÍTICA
# El pool 'prefork' no funciona en Windows, usar 'solo' o 'threads'
app.conf.update(
    # Pool: 'solo' = single process (más estable en Windows)
    # Pool: 'threads' = multithreading (alternativa)
    worker_pool='solo',
    
    # Desabilitar prefetch multiplier (causa problemas en Windows)
    worker_prefetch_multiplier=1,
    
    # Max tasks per child (previene memory leaks)
    worker_max_tasks_per_child=1000,
    
    # Acks late (garantiza que la tarea se ejecute)
    task_acks_late=True,
    
    # Disable rate limits (evita problemas en Windows)
    worker_disable_rate_limits=True,
    
    # Timeout para tareas
    task_soft_time_limit=300,  # 5 minutos
    task_time_limit=600,  # 10 minutos (hard limit)
)

@app.task(bind=True)
def debug_task(self):
    """Tarea de debug para verificar que Celery funciona"""
    print(f'Request: {self.request!r}')
