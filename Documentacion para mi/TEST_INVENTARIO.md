# 🧪 TESTING - SISTEMA DE INVENTARIO

## Abrir otra terminal (NO cierres el servidor)

```bash
# Nueva terminal
cd c:\Users\Alejandro\Desktop\Electro-Isla\backend
```

---

## TEST 1: Obtener Token de Autenticación

```bash
curl -X POST http://localhost:8000/api/login/ ^
  -H "Content-Type: application/json" ^
  -d "{\"username\": \"admin\", \"password\": \"admin123\"}"
```

**Respuesta esperada (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com"
  }
}
```

**Guardar el token:**
```bash
# En PowerShell:
$TOKEN = "tu_access_token_aqui"
```

---

## TEST 2: Verificar Producto con Stock

```bash
curl -X GET http://localhost:8000/api/productos/ ^
  -H "Authorization: Bearer $TOKEN"
```

**Buscar un producto con stock > 0 (ej: "Dokas" con stock_total=222)**

---

## TEST 3: Agregar al Carrito (FASE 1)

```bash
curl -X POST http://localhost:8000/api/carrito/agregar/ ^
  -H "Authorization: Bearer $TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"product_id\": 1, \"quantity\": 5}"
```

**Respuesta esperada (201):**
```json
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "nombre": "Dokas",
        "imagen_url": "...",
        "categoria": "electrodomesticos"
      },
      "quantity": 5,
      "price_at_addition": "99.99",
      "subtotal": 499.95,
      "created_at": "2025-11-09T20:37:00Z",
      "updated_at": "2025-11-09T20:37:00Z"
    }
  ],
  "total": 499.95,
  "total_items": 5,
  "created_at": "2025-11-09T20:37:00Z",
  "updated_at": "2025-11-09T20:37:00Z"
}
```

✅ **Verificar:**
- Status: 201
- Item agregado al carrito
- Stock NO se reservó (stock_reservado = 0)

---

## TEST 4: Verificar Stock NO fue Reservado

```bash
curl -X GET http://localhost:8000/api/productos/1/ ^
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada:**
```json
{
  "id": 1,
  "nombre": "Dokas",
  "stock_total": 222,
  "stock_reservado": 0,
  "stock_vendido": 0,
  "stock_disponible": 222,
  "stock": 222,
  ...
}
```

✅ **Verificar:**
- `stock_disponible` = 222 (sin cambios)
- `stock_reservado` = 0 (no reservado)

---

## TEST 5: Checkout (FASE 2 - Reservar Stock)

```bash
curl -X POST http://localhost:8000/api/carrito/checkout/ ^
  -H "Authorization: Bearer $TOKEN" ^
  -H "Content-Type: application/json"
```

**Respuesta esperada (200):**
```json
{
  "message": "Stock reservado exitosamente",
  "reservas": [
    {
      "id": 1,
      "producto": "Dokas",
      "cantidad": 5,
      "expires_at": "2025-11-09T20:52:00Z"
    }
  ],
  "total_items": 5,
  "ttl_minutos": 15
}
```

✅ **Verificar:**
- Status: 200
- Reserva creada con ID
- TTL: 15 minutos

---

## TEST 6: Verificar Stock FUE Reservado

```bash
curl -X GET http://localhost:8000/api/productos/1/ ^
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada:**
```json
{
  "id": 1,
  "nombre": "Dokas",
  "stock_total": 222,
  "stock_reservado": 5,
  "stock_vendido": 0,
  "stock_disponible": 217,
  "stock": 217,
  ...
}
```

✅ **Verificar:**
- `stock_disponible` = 217 (222 - 5 reservados)
- `stock_reservado` = 5 (RESERVADO)
- Otros clientes solo pueden comprar 217 unidades

---

## TEST 7: Intentar Agregar Más de lo Disponible

```bash
curl -X POST http://localhost:8000/api/carrito/agregar/ ^
  -H "Authorization: Bearer $TOKEN" ^
  -H "Content-Type: application/json" ^
  -d "{\"product_id\": 1, \"quantity\": 220}"
```

**Respuesta esperada (400):**
```json
{
  "error": "Stock insuficiente. Disponible: 217",
  "available": 217,
  "requested": 220
}
```

✅ **Verificar:**
- Status: 400
- Mensaje claro: solo hay 217 disponibles
- Stock NO se afecta

---

## TEST 8: Rate Limiting (Spam Protection)

Ejecutar 31 veces en rápida sucesión:

```bash
# PowerShell script
for ($i = 1; $i -le 35; $i++) {
  Write-Host "Request $i..."
  curl -X POST http://localhost:8000/api/carrito/agregar/ `
    -H "Authorization: Bearer $TOKEN" `
    -H "Content-Type: application/json" `
    -d "{`"product_id`": 2, `"quantity`": 1}" | Select-Object -First 1
  Start-Sleep -Milliseconds 100
}
```

**Respuesta esperada (después de 30 requests):**
```json
{
  "error": "Límite de solicitudes excedido. Intenta más tarde.",
  "reset_time": "2025-11-09T21:37:25Z"
}
```

✅ **Verificar:**
- Status: 429 (Too Many Requests)
- Rate limit activado después de 30 agregaciones/hora

---

## TEST 9: Liberar Reservas Expiradas

Abrir OTRA terminal:

```bash
cd c:\Users\Alejandro\Desktop\Electro-Isla\backend
python manage.py liberar_reservas_expiradas --verbose
```

**Respuesta esperada:**
```
🔄 Iniciando liberación de reservas expiradas...
ℹ️ No hay reservas expiradas para liberar
```

✅ **Verificar:**
- Comando ejecuta sin errores
- Reservas pendientes no se liberan (TTL no expiró)

---

## TEST 10: Simular Expiración Manual

```bash
# En Django shell
python manage.py shell

from api.models import StockReservation
from django.utils import timezone
from datetime import timedelta

# Obtener la reserva
reserva = StockReservation.objects.filter(status='pending').first()

# Cambiar expires_at al pasado
reserva.expires_at = timezone.now() - timedelta(minutes=1)
reserva.save()

print(f"Reserva expirada: {reserva}")
exit()
```

Ahora ejecutar el comando:

```bash
python manage.py liberar_reservas_expiradas --verbose
```

**Respuesta esperada:**
```
🔄 Iniciando liberación de reservas expiradas...
✅ 1 reservas expiradas liberadas exitosamente
  - admin: Dokas x5
```

✅ **Verificar:**
- Reserva liberada
- Stock_reservado vuelve a 0

---

## TEST 11: Verificar Stock Liberado

```bash
curl -X GET http://localhost:8000/api/productos/1/ ^
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada:**
```json
{
  "id": 1,
  "nombre": "Dokas",
  "stock_total": 222,
  "stock_reservado": 0,
  "stock_vendido": 0,
  "stock_disponible": 222,
  "stock": 222,
  ...
}
```

✅ **Verificar:**
- `stock_disponible` = 222 (volvió a 222)
- `stock_reservado` = 0 (liberado)
- Otros clientes pueden comprar nuevamente

---

## 📊 Resumen de Tests

| Test | Objetivo | Status |
|------|----------|--------|
| 1 | Obtener token | ✅ |
| 2 | Verificar producto | ✅ |
| 3 | Agregar al carrito | ✅ |
| 4 | Stock NO reservado | ✅ |
| 5 | Checkout (reservar) | ✅ |
| 6 | Stock SÍ reservado | ✅ |
| 7 | Rechazar cantidad > disponible | ✅ |
| 8 | Rate limiting | ✅ |
| 9 | Liberar reservas expiradas | ✅ |
| 10 | Simular expiración | ✅ |
| 11 | Verificar stock liberado | ✅ |

---

## 🎓 Conclusión

Si todos los tests pasan:

✅ **Sistema de inventario funcionando perfectamente**
✅ **Stock separado de carrito**
✅ **Reservas con TTL automático**
✅ **Protección contra DoS**
✅ **Listo para producción**

---

## 🆘 Si algo falla

1. Revisar logs del servidor
2. Ejecutar: `python manage.py showmigrations api`
3. Verificar: `python manage.py shell` → `from api.models import Producto, StockReservation`
4. Revisar documentación en `SISTEMA_INVENTARIO.md`
