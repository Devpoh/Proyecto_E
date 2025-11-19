# ===============================================================================
# Script PowerShell para configurar tarea programada de limpieza de tokens
# ===============================================================================
# 
# INSTRUCCIONES:
# 1. Abre PowerShell como Administrador
# 2. Navega a la carpeta del backend: cd "C:\Users\Alejandro\Desktop\Electro-Isla\backend"
# 3. Ejecuta: .\configurar_tarea_programada.ps1
# 
# La tarea se ejecutara automaticamente cada dia a las 3:00 AM
# ===============================================================================

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host "Configurando Tarea Programada - Limpieza de Tokens" -ForegroundColor Cyan
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si se está ejecutando como administrador
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[ERROR] Este script debe ejecutarse como Administrador" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor:" -ForegroundColor Yellow
    Write-Host "1. Cierra esta ventana" -ForegroundColor Yellow
    Write-Host "2. Abre PowerShell como Administrador (clic derecho -> Ejecutar como administrador)" -ForegroundColor Yellow
    Write-Host "3. Navega a esta carpeta y ejecuta el script nuevamente" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

# Configuración de la tarea
$taskName = "ElectroIsla_LimpiarTokens"
$scriptPath = Join-Path $PSScriptRoot "limpiar_tokens_auto.bat"
$logFolder = Join-Path $PSScriptRoot "logs"

# Crear carpeta de logs si no existe
if (-not (Test-Path $logFolder)) {
    New-Item -ItemType Directory -Path $logFolder | Out-Null
    Write-Host "[OK] Carpeta de logs creada: $logFolder" -ForegroundColor Green
}

# Verificar si el script existe
if (-not (Test-Path $scriptPath)) {
    Write-Host "[ERROR] No se encontro el archivo limpiar_tokens_auto.bat" -ForegroundColor Red
    Write-Host "   Ruta esperada: $scriptPath" -ForegroundColor Yellow
    pause
    exit 1
}

# Eliminar tarea existente si ya existe
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($existingTask) {
    Write-Host "[AVISO] La tarea '$taskName' ya existe. Eliminando..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Write-Host "[OK] Tarea anterior eliminada" -ForegroundColor Green
}

# Crear acción (ejecutar el script batch)
$action = New-ScheduledTaskAction -Execute $scriptPath

# Crear trigger (ejecutar diariamente a las 3:00 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At 3:00AM

# Crear configuración de la tarea
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -DontStopOnIdleEnd

# Crear principal (ejecutar con el usuario actual)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest

# Registrar la tarea
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "Limpia tokens de refresco expirados e intentos de login antiguos de Electro Isla" | Out-Null
    
    Write-Host ""
    Write-Host "[EXITO] Tarea programada configurada exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Detalles de la tarea:" -ForegroundColor Cyan
    Write-Host "   - Nombre: $taskName" -ForegroundColor White
    Write-Host "   - Frecuencia: Diariamente a las 3:00 AM" -ForegroundColor White
    Write-Host "   - Script: $scriptPath" -ForegroundColor White
    Write-Host "   - Logs: $logFolder\limpieza_tokens.log" -ForegroundColor White
    Write-Host ""
    Write-Host "Para verificar la tarea:" -ForegroundColor Cyan
    Write-Host "   1. Abre 'Programador de tareas' (taskschd.msc)" -ForegroundColor White
    Write-Host "   2. Busca '$taskName' en la biblioteca de tareas" -ForegroundColor White
    Write-Host ""
    Write-Host "Para probar la tarea manualmente:" -ForegroundColor Cyan
    Write-Host "   Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para eliminar la tarea:" -ForegroundColor Cyan
    Write-Host "   Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false" -ForegroundColor Yellow
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "[ERROR] al crear la tarea programada:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    pause
    exit 1
}

Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""
pause
