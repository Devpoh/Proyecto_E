# ═══════════════════════════════════════════════════════════════════════════════
# 🧪 Run All Tests - Frontend Security Improvements
# ═══════════════════════════════════════════════════════════════════════════════
# 
# Script para ejecutar todos los tests de seguridad en Windows PowerShell
# 
# Uso:
#   .\run-all-tests.ps1
#
# O desde npm:
#   npm run test:all
#

Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🧪 FRONTEND SECURITY TESTS - SUITE COMPLETA" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Colores
$successColor = "Green"
$errorColor = "Red"
$infoColor = "Cyan"

# Contadores
$passedTests = 0
$failedTests = 0

# Función para ejecutar test
function Invoke-Test {
    param(
        [string]$TestName,
        [string]$TestFile
    )
    
    Write-Host "▶ Ejecutando: $TestName" -ForegroundColor $infoColor
    Write-Host "  Archivo: $TestFile" -ForegroundColor Gray
    Write-Host ""
    
    npm test -- $TestFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ $TestName - PASSED" -ForegroundColor $successColor
        $script:passedTests++
    } else {
        Write-Host "❌ $TestName - FAILED" -ForegroundColor $errorColor
        $script:failedTests++
    }
    
    Write-Host ""
    Write-Host "───────────────────────────────────────────────────────────────────────────────" -ForegroundColor Gray
    Write-Host ""
}

# Ejecutar tests
Invoke-Test "JWT Utilities Tests" "jwt.test.ts"
Invoke-Test "Storage Tests" "storage.test.ts"
Invoke-Test "CSRF Protection Tests" "csrf.test.ts"

# Resumen
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📊 RESUMEN DE RESULTADOS" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Tests Pasados:  " -NoNewline
Write-Host "$passedTests" -ForegroundColor $successColor

Write-Host "Tests Fallidos: " -NoNewline
Write-Host "$failedTests" -ForegroundColor $(if ($failedTests -eq 0) { $successColor } else { $errorColor })

Write-Host ""

if ($failedTests -eq 0) {
    Write-Host "✅ ¡TODOS LOS TESTS PASARON!" -ForegroundColor $successColor
    Write-Host ""
    Write-Host "🎉 Frontend Security Improvements - VALIDADO" -ForegroundColor $successColor
} else {
    Write-Host "❌ Algunos tests fallaron. Revisa los errores arriba." -ForegroundColor $errorColor
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
