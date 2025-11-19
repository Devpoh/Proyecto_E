@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM 🚀 INSTALAR TODAS LAS DEPENDENCIAS - WINDOWS
REM ═══════════════════════════════════════════════════════════════════════════════

echo.
echo 📦 Instalando dependencias desde requirements.txt...
echo.

REM Activar venv
call venv\Scripts\activate.bat

REM Instalar dependencias
pip install -r requirements.txt

echo.
echo ✅ ¡Instalación completada!
echo.
echo 📝 Próximos pasos:
echo   1. Ejecutar migraciones: python manage.py migrate
echo   2. Ejecutar migraciones de Celery: python manage.py migrate django_celery_beat
echo   3. Iniciar Redis: redis-server
echo   4. En otra terminal - Celery Worker: celery -A config worker -l info
echo   5. En otra terminal - Celery Beat: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
echo.
pause
