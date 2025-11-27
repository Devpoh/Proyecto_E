@echo off
echo ============================================================
echo 🔄 Ejecutando Migraciones Django
echo ============================================================
echo.

echo 1. Creando migraciones...
python manage.py makemigrations

echo.
echo 2. Aplicando migraciones...
python manage.py migrate

echo.
echo ============================================================
echo ✅ Migraciones completadas
echo ============================================================
echo.
pause
