@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM 🚀 SCRIPT PARA INICIAR CELERY BEAT (Tareas Programadas)
REM ═══════════════════════════════════════════════════════════════════════════════

echo.
echo [CELERY BEAT] Iniciando Celery Beat 5.5.3...
echo.

REM Iniciar Celery beat con scheduler de Django
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

echo.
echo ✅ Celery beat iniciado
echo.
pause
