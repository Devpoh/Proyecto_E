@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM 🚀 SCRIPT DE OPTIMIZACIÓN DE RENDIMIENTO
REM ═══════════════════════════════════════════════════════════════════════════════

echo.
echo [1/4] Aplicando migraciones de índices...
python manage.py migrate

echo.
echo [2/4] Limpiando caché...
python manage.py shell -c "from django.core.cache import cache; cache.clear(); print('✅ Caché limpiado')"

echo.
echo [3/4] Recolectando archivos estáticos...
python manage.py collectstatic --noinput

echo.
echo [4/4] Iniciando servidor Django...
python manage.py runserver 0.0.0.0:8000

echo.
echo ✅ OPTIMIZACIÓN COMPLETADA
echo.
echo 📊 CAMBIOS REALIZADOS:
echo   ✅ Celery deshabilitado (CELERY_ALWAYS_EAGER = True)
echo   ✅ N+1 queries arregladas (prefetch_related en carrusel)
echo   ✅ Índices agregados en BD (en_carrusel, activo, categoria)
echo   ✅ Caché limpiado
echo.
echo 🎯 PRÓXIMOS PASOS:
echo   1. Probar la web en http://localhost:5173
echo   2. Medir tiempo de carga en DevTools (Network tab)
echo   3. Comparar con antes (debería ser 5-10x más rápido)
echo.
pause
