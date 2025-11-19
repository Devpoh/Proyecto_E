# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 INSTALAR TODAS LAS DEPENDENCIAS
# ═══════════════════════════════════════════════════════════════════════════════

Write-Host "📦 Instalando dependencias..." -ForegroundColor Green

# Activar venv si no está activado
if (-not $env:VIRTUAL_ENV) {
    Write-Host "🔧 Activando venv..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
}

# Instalar desde requirements.txt
Write-Host "📥 Instalando desde requirements.txt..." -ForegroundColor Cyan
pip install -r requirements.txt

# Verificar instalaciones críticas
Write-Host "`n✅ Verificando instalaciones..." -ForegroundColor Green

$packages = @(
    "django",
    "celery",
    "redis",
    "django_celery_beat",
    "django_celery_results",
    "python-dotenv"
)

foreach ($pkg in $packages) {
    try {
        python -c "import $($pkg.Replace('-', '_'))" 2>$null
        Write-Host "  ✅ $pkg" -ForegroundColor Green
    } catch {
        Write-Host "  ❌ $pkg" -ForegroundColor Red
    }
}

Write-Host "`n🎉 ¡Instalación completada!" -ForegroundColor Green
Write-Host "`n📝 Próximos pasos:" -ForegroundColor Yellow
Write-Host "  1. Ejecutar migraciones: python manage.py migrate"
Write-Host "  2. Iniciar Redis: redis-server"
Write-Host "  3. Iniciar Celery Worker: celery -A config worker -l info"
Write-Host "  4. Iniciar Celery Beat: celery -A config beat -l info"
