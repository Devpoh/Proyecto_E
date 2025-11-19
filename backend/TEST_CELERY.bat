@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM 🧪 TEST CELERY - VERIFICAR QUE TODO FUNCIONA
REM ═══════════════════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

REM Cambiar a directorio del backend
cd /d "%~dp0"

REM Verificar que estamos en el directorio correcto
if not exist "manage.py" (
    echo Error: manage.py no encontrado
    pause
    exit /b 1
)

echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo 🧪 TEST CELERY WORKER
echo ═══════════════════════════════════════════════════════════════════════════════
echo.

echo Iniciando Celery Worker con --pool=solo...
echo.

celery -A config worker -l info --pool=solo

pause
