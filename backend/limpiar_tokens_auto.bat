@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM Script para limpiar tokens expirados automáticamente
REM Se ejecuta mediante el Programador de Tareas de Windows
REM ═══════════════════════════════════════════════════════════════════════════════

cd /d "%~dp0"
python manage.py limpiar_tokens >> logs\limpieza_tokens.log 2>&1
