# ═══════════════════════════════════════════════════════════════════════════════
# 🚀 SCRIPT PARA INICIAR TODO - CELERY EN WINDOWS
# ═══════════════════════════════════════════════════════════════════════════════
#
# Este script inicia todos los servicios necesarios para Celery:
# 1. Redis
# 2. PostgreSQL (verificación)
# 3. Django Development Server
# 4. Celery Worker
# 5. Celery Beat
# 6. Flower (opcional)
#
# Uso: .\INICIAR_TODO_CELERY.ps1
#
# ═══════════════════════════════════════════════════════════════════════════════

# Configuración
$BACKEND_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$VENV_PATH = Join-Path $BACKEND_DIR "venv"
$VENV_ACTIVATE = Join-Path $VENV_PATH "Scripts\Activate.ps1"

# Colores para output
$GREEN = "`e[32m"
$RED = "`e[31m"
$YELLOW = "`e[33m"
$BLUE = "`e[34m"
$RESET = "`e[0m"

function Write-Success {
    param([string]$Message)
    Write-Host "$GREEN✓ $Message$RESET"
}

function Write-Error {
    param([string]$Message)
    Write-Host "$RED✗ $Message$RESET"
}

function Write-Warning {
    param([string]$Message)
    Write-Host "$YELLOW⚠ $Message$RESET"
}

function Write-Info {
    param([string]$Message)
    Write-Host "$BLUE→ $Message$RESET"
}

# ═══════════════════════════════════════════════════════════════════════════════
# VERIFICACIONES PREVIAS
# ═══════════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════"
Write-Host "🔍 VERIFICANDO REQUISITOS"
Write-Host "═══════════════════════════════════════════════════════════════════════════════"
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path (Join-Path $BACKEND_DIR "manage.py"))) {
    Write-Error "manage.py no encontrado. Asegúrate de estar en el directorio backend."
    exit 1
}
Write-Success "Directorio backend correcto"

# Verificar Redis
Write-Info "Verificando Redis..."
$redisCheck = netstat -an | Select-String "6379"
if ($redisCheck) {
    Write-Success "Redis está corriendo en puerto 6379"
} else {
    Write-Warning "Redis NO está corriendo en puerto 6379"
    Write-Info "Inicia Redis con: redis-server"
    Read-Host "Presiona Enter cuando Redis esté corriendo"
}

# Verificar PostgreSQL
Write-Info "Verificando PostgreSQL..."
$postgresCheck = netstat -an | Select-String "5432"
if ($postgresCheck) {
    Write-Success "PostgreSQL está corriendo en puerto 5432"
} else {
    Write-Warning "PostgreSQL NO está corriendo en puerto 5432"
    Write-Info "Inicia PostgreSQL desde Services (services.msc)"
    Read-Host "Presiona Enter cuando PostgreSQL esté corriendo"
}

# Verificar entorno virtual
Write-Info "Verificando entorno virtual..."
if (Test-Path $VENV_ACTIVATE) {
    Write-Success "Entorno virtual encontrado"
    & $VENV_ACTIVATE
    Write-Success "Entorno virtual activado"
} else {
    Write-Warning "Entorno virtual no encontrado"
    Write-Info "Creando entorno virtual..."
    python -m venv venv
    & $VENV_ACTIVATE
    Write-Info "Instalando dependencias..."
    pip install -r requirements.txt
    Write-Success "Dependencias instaladas"
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════"
Write-Host "✅ TODAS LAS VERIFICACIONES PASARON"
Write-Host "═══════════════════════════════════════════════════════════════════════════════"
Write-Host ""

# ═══════════════════════════════════════════════════════════════════════════════
# INICIAR SERVICIOS
# ═══════════════════════════════════════════════════════════════════════════════

Write-Host "═══════════════════════════════════════════════════════════════════════════════"
Write-Host "🚀 INICIANDO SERVICIOS"
Write-Host "═══════════════════════════════════════════════════════════════════════════════"
Write-Host ""

# 1. Django Development Server
Write-Info "Iniciando Django Development Server..."
Write-Info "Abriendo nueva ventana para Django..."
$djangoArgs = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-Command", "cd '$BACKEND_DIR'; python manage.py runserver"
)
Start-Process powershell -ArgumentList $djangoArgs -WindowStyle Normal
Write-Success "Django iniciado en http://localhost:8000"
Start-Sleep -Seconds 2

# 2. Celery Worker
Write-Info "Iniciando Celery Worker..."
Write-Info "Abriendo nueva ventana para Celery Worker..."
$workerArgs = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-Command", "cd '$BACKEND_DIR'; celery -A config worker -l info --pool=solo"
)
Start-Process powershell -ArgumentList $workerArgs -WindowStyle Normal
Write-Success "Celery Worker iniciado"
Start-Sleep -Seconds 2

# 3. Celery Beat
Write-Info "Iniciando Celery Beat..."
Write-Info "Abriendo nueva ventana para Celery Beat..."
$beatArgs = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-Command", "cd '$BACKEND_DIR'; celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"
)
Start-Process powershell -ArgumentList $beatArgs -WindowStyle Normal
Write-Success "Celery Beat iniciado"
Start-Sleep -Seconds 2

# 4. Flower (opcional)
Write-Host ""
$flowerChoice = Read-Host "¿Deseas iniciar Flower (monitor de Celery)? (s/n)"
if ($flowerChoice -eq "s" -or $flowerChoice -eq "S") {
    Write-Info "Iniciando Flower..."
    Write-Info "Abriendo nueva ventana para Flower..."
    $flowerArgs = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-Command", "cd '$BACKEND_DIR'; celery -A config flower"
    )
    Start-Process powershell -ArgumentList $flowerArgs -WindowStyle Normal
    Write-Success "Flower iniciado en http://localhost:5555"
    Start-Sleep -Seconds 2
}

# ═══════════════════════════════════════════════════════════════════════════════
# RESUMEN
# ═══════════════════════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════"
Write-Host "✅ TODOS LOS SERVICIOS INICIADOS"
Write-Host "═══════════════════════════════════════════════════════════════════════════════"
Write-Host ""
Write-Host "$GREEN📋 SERVICIOS ACTIVOS:$RESET"
Write-Host "  1. Django Development Server"
Write-Host "     URL: http://localhost:8000"
Write-Host "     Terminal: Nueva ventana"
Write-Host ""
Write-Host "  2. Celery Worker"
Write-Host "     Pool: solo (single process)"
Write-Host "     Terminal: Nueva ventana"
Write-Host ""
Write-Host "  3. Celery Beat (Scheduler)"
Write-Host "     Scheduler: DatabaseScheduler"
Write-Host "     Terminal: Nueva ventana"
Write-Host ""

if ($flowerChoice -eq "s" -or $flowerChoice -eq "S") {
    Write-Host "  4. Flower (Monitor)"
    Write-Host "     URL: http://localhost:5555"
    Write-Host "     Terminal: Nueva ventana"
    Write-Host ""
}

Write-Host "$YELLOW⚠️  IMPORTANTE:$RESET"
Write-Host "  - Asegúrate de que Redis está corriendo"
Write-Host "  - Asegúrate de que PostgreSQL está corriendo"
Write-Host "  - Cada servicio está en una ventana separada"
Write-Host "  - Usa Ctrl+C en cada ventana para detener"
Write-Host ""

Write-Host "$BLUE📚 DOCUMENTACIÓN:$RESET"
Write-Host "  - Guía completa: CELERY_WINDOWS_GUIA_COMPLETA.md"
Write-Host "  - Configuración: config/celery.py"
Write-Host "  - Tareas: api/tasks.py"
Write-Host ""

Write-Host "$GREEN🎉 ¡LISTO PARA DESARROLLAR!$RESET"
Write-Host ""

# Mantener la ventana abierta
Read-Host "Presiona Enter para cerrar esta ventana"
