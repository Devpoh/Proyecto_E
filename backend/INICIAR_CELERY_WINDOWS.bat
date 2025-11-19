@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM 🚀 INICIAR CELERY WORKER EN WINDOWS
REM ═══════════════════════════════════════════════════════════════════════════════
REM
REM Este script inicia el worker de Celery con configuración optimizada para Windows.
REM
REM REQUISITOS:
REM 1. Redis corriendo en localhost:6379
REM 2. Django settings configurados correctamente
REM 3. Entorno virtual activado (opcional, se activa automáticamente)
REM
REM OPCIONES:
REM --pool=solo      = Single process (más estable, recomendado)
REM --pool=threads   = Multithreading (alternativa)
REM -l info          = Log level info
REM -E               = Habilitar task events (para Flower)
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
echo 🚀 INICIANDO CELERY WORKER
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo 📋 Configuración:
echo    - App: config
echo    - Pool: solo (single process, estable en Windows)
echo    - Log Level: info
echo    - Broker: redis://127.0.0.1:6379/0
echo    - Results: redis://127.0.0.1:6379/0
echo.
echo 📝 Tareas registradas:
echo    - api.tasks.liberar_reservas_expiradas
echo    - api.tasks.limpiar_tokens_expirados
echo    - config.celery.debug_task
echo.
echo ⏸️  Presiona Ctrl+C para detener el worker
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo.

REM Iniciar Celery worker con pool=solo (recomendado para Windows)
celery -A config worker -l info --pool=solo

REM Si falla, mostrar error
if errorlevel 1 (
    echo.
    echo ❌ Error al iniciar Celery worker
    echo.
    echo 💡 Soluciones:
    echo    1. Verifica que Redis está corriendo: redis-server
    echo    2. Verifica que estás en el directorio backend
    echo    3. Verifica que el entorno virtual está activado
    echo    4. Intenta con --pool=threads en lugar de --pool=solo
    echo.
    pause
    exit /b 1
)

pause
