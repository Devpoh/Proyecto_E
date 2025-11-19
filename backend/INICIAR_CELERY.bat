@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM 🚀 SCRIPT PARA INICIAR CELERY WORKER
REM ═══════════════════════════════════════════════════════════════════════════════

echo.
echo [CELERY WORKER] Iniciando Celery 5.5.3...
echo.

REM Iniciar Celery worker con logging detallado
celery -A config worker -l info

echo.
echo ✅ Celery worker iniciado
echo.
pause
