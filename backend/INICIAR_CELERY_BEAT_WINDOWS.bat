@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM 🕐 INICIAR CELERY BEAT EN WINDOWS
REM ═══════════════════════════════════════════════════════════════════════════════
REM
REM Este script inicia Celery Beat (scheduler) para ejecutar tareas programadas.
REM
REM REQUISITOS:
REM 1. Redis corriendo en localhost:6379
REM 2. Celery worker corriendo en otra terminal
REM 3. Django settings configurados correctamente
REM
REM TAREAS PROGRAMADAS:
REM - liberar-reservas-expiradas: Cada 20 minutos
REM - limpiar-tokens-expirados: Cada hora
REM
REM ═══════════════════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

REM Cambiar a directorio del backend
cd /d "%~dp0"

REM Verificar que estamos en el directorio correcto
if not exist "manage.py" (
    echo ❌ Error: manage.py no encontrado. Asegúrate de estar en el directorio backend.
    pause
    exit /b 1
)

REM Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    echo 🔧 Activando entorno virtual...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo 🔧 Activando entorno virtual...
    call .venv\Scripts\activate.bat
)

REM Verificar que Redis está corriendo
echo 🔍 Verificando Redis...
netstat -an | find "6379" >nul
if errorlevel 1 (
    echo ❌ Error: Redis no está corriendo en localhost:6379
    echo 💡 Inicia Redis con: redis-server
    pause
    exit /b 1
)
echo ✅ Redis está corriendo

REM Mostrar información
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo 🕐 INICIANDO CELERY BEAT (SCHEDULER)
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo 📋 Configuración:
echo    - App: config
echo    - Scheduler: DatabaseScheduler (django_celery_beat)
echo    - Log Level: info
echo    - Broker: redis://127.0.0.1:6379/0
echo.
echo 📅 Tareas Programadas:
echo    - liberar-reservas-expiradas: Cada 20 minutos
echo    - limpiar-tokens-expirados: Cada hora
echo.
echo ⚠️  IMPORTANTE:
echo    - Asegúrate de que el Celery Worker está corriendo en otra terminal
echo    - Usa: INICIAR_CELERY_WINDOWS.bat en otra ventana
echo.
echo ⏸️  Presiona Ctrl+C para detener Beat
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo.

REM Iniciar Celery Beat
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

REM Si falla, mostrar error
if errorlevel 1 (
    echo.
    echo ❌ Error al iniciar Celery Beat
    echo.
    echo 💡 Soluciones:
    echo    1. Verifica que Redis está corriendo: redis-server
    echo    2. Verifica que estás en el directorio backend
    echo    3. Verifica que el entorno virtual está activado
    echo    4. Verifica que el Celery Worker está corriendo
    echo.
    pause
    exit /b 1
)

pause
