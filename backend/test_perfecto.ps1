# TEST PERFECTO - Carrito Completamente Funcional

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST PERFECTO - Carrito" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$BASE_URL = "http://localhost:8000/api"

# PASO 1: Login
Write-Host "[1] Login..." -ForegroundColor Yellow

$loginBody = @{
    username = "testuser"
    password = "testpass123"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$BASE_URL/auth/login/" `
        -Method POST `
        -Headers @{"Content-Type" = "application/json"} `
        -Body $loginBody `
        -ErrorAction Stop

    $token = $loginResponse.accessToken
    Write-Host "[OK] Login exitoso" -ForegroundColor Green
    Write-Host "Token: $($token.Substring(0, 20))..." -ForegroundColor Gray
} catch {
    Write-Host "[ERROR] Login fallido" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# PASO 2: Obtener carrito actual
Write-Host "[2] Obteniendo carrito actual..." -ForegroundColor Yellow

try {
    $cartResponse = Invoke-RestMethod -Uri "$BASE_URL/carrito/" `
        -Method GET `
        -Headers @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        } `
        -ErrorAction Stop

    Write-Host "[OK] Carrito obtenido" -ForegroundColor Green
    Write-Host "Items actuales: $($cartResponse.total_items)" -ForegroundColor Gray
    Write-Host "Total: $($cartResponse.total)" -ForegroundColor Gray
    
    # Mostrar items
    if ($cartResponse.items.Count -gt 0) {
        Write-Host "Productos en carrito:" -ForegroundColor Gray
        foreach ($item in $cartResponse.items) {
            Write-Host "  - Producto $($item.product.id): $($item.product.nombre) x $($item.quantity)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "[ERROR] Error al obtener carrito" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# PASO 3: Obtener lista de productos disponibles
Write-Host "[3] Obteniendo productos disponibles..." -ForegroundColor Yellow

try {
    $productosResponse = Invoke-RestMethod -Uri "$BASE_URL/productos/" `
        -Method GET `
        -Headers @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        } `
        -ErrorAction Stop

    $productos = $productosResponse.results
    
    if ($productos.Count -gt 0) {
        Write-Host "[OK] Productos disponibles:" -ForegroundColor Green
        foreach ($prod in $productos | Select-Object -First 3) {
            Write-Host "  - ID: $($prod.id), Nombre: $($prod.nombre), Stock: $($prod.stock)" -ForegroundColor Gray
        }
        $productoId = $productos[0].id
        Write-Host "Usando producto ID: $productoId para agregar" -ForegroundColor Yellow
    } else {
        Write-Host "[ERROR] No hay productos disponibles" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Error al obtener productos" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# PASO 4: Agregar producto al carrito
Write-Host "[4] Agregando producto $productoId al carrito..." -ForegroundColor Yellow

$addBody = @{
    product_id = $productoId
    quantity = 1
} | ConvertTo-Json

Write-Host "Body: $addBody" -ForegroundColor Gray

try {
    $addResponse = Invoke-RestMethod -Uri "$BASE_URL/carrito/agregar/" `
        -Method POST `
        -Headers @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        } `
        -Body $addBody `
        -ErrorAction Stop

    Write-Host "[OK] Producto agregado" -ForegroundColor Green
    Write-Host "Items en carrito: $($addResponse.total_items)" -ForegroundColor Gray
    Write-Host "Total: $($addResponse.total)" -ForegroundColor Gray
} catch {
    Write-Host "[ERROR] Error al agregar producto" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    # Intentar leer el body del error
    try {
        $errorBody = $_.Exception.Response.Content | ConvertFrom-Json
        Write-Host "Detalles: $($errorBody | ConvertTo-Json)" -ForegroundColor Red
    } catch {}
    
    exit 1
}

Write-Host ""

# PASO 5: Obtener carrito nuevamente
Write-Host "[5] Obteniendo carrito nuevamente..." -ForegroundColor Yellow

try {
    $cartResponse2 = Invoke-RestMethod -Uri "$BASE_URL/carrito/" `
        -Method GET `
        -Headers @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        } `
        -ErrorAction Stop

    Write-Host "[OK] Carrito obtenido" -ForegroundColor Green
    Write-Host "Items: $($cartResponse2.total_items)" -ForegroundColor Gray
    Write-Host "Total: $($cartResponse2.total)" -ForegroundColor Gray
} catch {
    Write-Host "[ERROR] Error al obtener carrito" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[OK] TEST COMPLETADO" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
