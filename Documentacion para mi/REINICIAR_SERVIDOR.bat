@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM Script para reiniciar el servidor Django
REM ═══════════════════════════════════════════════════════════════════════════════

echo.
echo ╔═══════════════════════════════════════════════════════════════════════════════╗
echo ║                    REINICIANDO SERVIDOR DJANGO                               ║
echo ╚═══════════════════════════════════════════════════════════════════════════════╝
echo.

REM Cambiar al directorio del backend
cd /d c:\Users\Alejandro\Desktop\Electro-Isla\backend

REM Matar procesos Python existentes
echo [1/3] Deteniendo procesos Python existentes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak

REM Limpiar archivos de caché
echo [2/3] Limpiando archivos de caché...
del /s /q __pycache__ 2>nul
del /s /q *.pyc 2>nul

REM Iniciar el servidor
echo [3/3] Iniciando servidor Django...
echo.
python manage.py runserver 0.0.0.0:8000

pause
