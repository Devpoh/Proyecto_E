# 🛡️ SISTEMA DE INVENTARIO CON RESERVA DE STOCK

## 📋 Resumen Ejecutivo

Se ha implementado un sistema profesional de gestión de inventario que separa el carrito de compras del inventario real, utilizando un concepto de "Reserva de Stock Temporal" con lógica de Commit/Rollback.

**Problema Resuelto:**
- ❌ Antes: Productos mostraban "agotado" aunque tuvieran stock
- ❌ Antes: Usuarios podían hacer spam de requests y romper el backend
- ✅ Ahora: Stock validado correctamente en tiempo real
- ✅ Ahora: Protección contra ataques DoS de inventario

---

## 🎯 Flujo de Operación

### FASE 1: Agregar al Carrito (SIN RESERVAR)

```
Usuario hace click "Agregar al Carrito"
    ↓
Frontend valida:
  - Autenticación ✓
  - Stock disponible > 0 ✓
  - Cantidad válida (1-999) ✓
  - Debounce (1 segundo) ✓
    ↓
Backend valida:
  - Producto existe ✓
  - Stock disponible >= cantidad ✓
  - Rate limit (30/hora) ✓
    ↓
Resultado:
  - Producto agregado al carrito (es solo una lista de deseos)
  - Stock NO se reserva
  - Otros clientes pueden comprar el mismo producto
```

**Endpoint:** `POST /api/carrito/agregar/`

**Body:**
```json
{
  "product_id": 1,
  "quantity": 5
}
```

**Respuesta (201):**
```json
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "product": { "id": 1, "nombre": "Producto", "imagen_url": "...", "categoria": "..." },
      "quantity": 5,
      "price_at_addition": "99.99",
      "subtotal": 499.95,
      "created_at": "2025-11-09T20:30:00Z",
      "updated_at": "2025-11-09T20:30:00Z"
    }
  ],
  "total": 499.95,
  "total_items": 5,
  "created_at": "2025-11-09T20:30:00Z",
  "updated_at": "2025-11-09T20:30:00Z"
}
```

---

### FASE 2: Checkout (RESERVAR STOCK)

```
Usuario hace click "Proceder al Pago"
    ↓
Frontend envía: POST /api/carrito/checkout/
    ↓
Backend:
  1. Verifica que carrito no esté vacío
  2. Para cada item en el carrito:
     - Valida stock_disponible >= cantidad
     - Crea StockReservation (status='pending')
     - Incrementa stock_reservado
     - Establece TTL de 15 minutos
    ↓
Resultado:
  - Stock RESERVADO (no disponible para otros clientes)
  - Reserva con expiración automática (15 min)
  - Si pago falla → Stock se libera (ROLLBACK)
```

**Endpoint:** `POST /api/carrito/checkout/`

**Respuesta (200):**
```json
{
  "message": "Stock reservado exitosamente",
  "reservas": [
    {
      "id": 1,
      "producto": "Producto A",
      "cantidad": 5,
      "expires_at": "2025-11-09T20:45:00Z"
    }
  ],
  "total_items": 5,
  "ttl_minutos": 15
}
```

**Errores Posibles:**
- `400`: Carrito vacío
- `409`: Stock insuficiente para algún producto

---

### FASE 3: Confirmación de Pago (COMMIT)

```
Pago procesado exitosamente
    ↓
Backend:
  1. Busca StockReservation (status='pending')
  2. Actualiza status='confirmed'
  3. Mueve stock: stock_reservado → stock_vendido
  4. Crea Pedido
  5. Vacía carrito
    ↓
Resultado:
  - Stock permanentemente actualizado
  - Pedido creado
  - Inventario consistente
```

---

### FASE 4: Liberación Automática (ROLLBACK)

```
Si pasan 15 minutos sin confirmar pago
    ↓
Management Command: liberar_reservas_expiradas
    ↓
Backend:
  1. Busca StockReservation (status='pending', expires_at < ahora)
  2. Para cada reserva expirada:
     - Decrementa stock_reservado
     - Actualiza status='expired'
    ↓
Resultado:
  - Stock liberado automáticamente
  - Disponible para otros clientes
  - Reserva marcada como expirada
```

---

## 📊 Estructura de Datos

### Modelo Producto

```python
class Producto(models.Model):
    # ... campos existentes ...
    
    # ✅ NUEVO: Sistema de inventario separado
    stock_total = IntegerField()        # Stock físico total
    stock_reservado = IntegerField()    # Stock apartado en Checkout
    stock_vendido = IntegerField()      # Stock ya vendido
    stock = IntegerField()              # Legado: se calcula automáticamente
    
    @property
    def stock_disponible(self):
        """Stock disponible = total - reservado - vendido"""
        return max(0, self.stock_total - self.stock_reservado - self.stock_vendido)
```

### Modelo StockReservation (NUEVO)

```python
class StockReservation(models.Model):
    usuario = ForeignKey(User)
    producto = ForeignKey(Producto)
    cantidad = PositiveIntegerField()
    status = CharField(choices=['pending', 'confirmed', 'cancelled', 'expired'])
    
    created_at = DateTimeField(auto_now_add=True)
    expires_at = DateTimeField()  # TTL: 15 minutos
    confirmed_at = DateTimeField(null=True)
    cancelled_at = DateTimeField(null=True)
    
    ip_address = GenericIPAddressField(null=True)
    user_agent = TextField()
```

---

## 🔒 Capas de Seguridad

### Capa 1: Frontend - Validación Inmediata

```typescript
// useAddToCart.ts
if (stock <= 0) {
  toast.error('Este producto está agotado');
  return;
}

if (quantity > stock) {
  toast.error(`Solo hay ${stock} unidades disponibles`);
  return;
}

// Debounce: máximo 1 request/segundo por producto
if (requestDebounceMap.has(numericId)) {
  return;
}
```

### Capa 2: Frontend - Rate Limiting

```typescript
// Máximo 30 agregaciones/hora por usuario
// Máximo 1 segundo entre requests del mismo producto
```

### Capa 3: Backend - Rate Limiting

```python
# settings.py
'DEFAULT_THROTTLE_RATES': {
    'anon': '100/hour',
    'user': '10000/hour',  # Para compras en bulk
    'admin': '10000/hour'
}

# views.py - Endpoint agregar
allowed, remaining, reset_time = check_rate_limit(
    request.user.id, 
    'add',
    limit=30,  # 30 agregaciones/hora
    window_minutes=60
)
```

### Capa 4: Backend - Validación de Stock

```python
# views.py - Endpoint agregar
if product.stock_disponible < quantity:
    return Response(
        {'error': f'Stock insuficiente. Disponible: {product.stock_disponible}'},
        status=status.HTTP_400_BAD_REQUEST
    )
```

### Capa 5: Backend - Transacciones Atómicas

```python
# views.py - Endpoint checkout
try:
    for item in cart.items.all():
        # Crear reserva
        reserva = StockReservation.crear_reserva(...)
        # Actualizar stock
        producto.stock_reservado += cantidad
        producto.save()
except Exception as e:
    # ROLLBACK: Liberar todas las reservas
    for reserva in reservas:
        producto.stock_reservado -= reserva.cantidad
        producto.save()
```

---

## ⚙️ Instalación y Configuración

### 1. Aplicar Migraciones

```bash
cd backend
python manage.py migrate api
```

Esto creará:
- Campos `stock_total`, `stock_reservado`, `stock_vendido` en Producto
- Tabla `stock_reservations`
- Índices para optimización

### 2. Configurar Management Command

El comando `liberar_reservas_expiradas` debe ejecutarse periódicamente:

**Opción A: Celery Beat (Recomendado para producción)**

```python
# config/celery.py
from celery.schedules import crontab

app.conf.beat_schedule = {
    'liberar-reservas-expiradas': {
        'task': 'api.tasks.liberar_reservas_expiradas',
        'schedule': crontab(minute='*/5'),  # Cada 5 minutos
    },
}
```

**Opción B: Cron Job (Simple)**

```bash
# Agregar a crontab
*/5 * * * * cd /path/to/backend && python manage.py liberar_reservas_expiradas
```

**Opción C: Manual (Desarrollo)**

```bash
python manage.py liberar_reservas_expiradas --verbose
```

### 3. Actualizar Datos Existentes

Para productos existentes, necesitas establecer `stock_total`:

```python
# En Django shell
from api.models import Producto

for producto in Producto.objects.all():
    producto.stock_total = producto.stock
    producto.save()
```

---

## 📈 Monitoreo

### Verificar Reservas Pendientes

```python
from api.models import StockReservation
from django.utils import timezone

# Reservas activas
pendientes = StockReservation.objects.filter(status='pending')

# Reservas próximas a expirar (< 5 minutos)
ahora = timezone.now()
proximas_expirar = StockReservation.objects.filter(
    status='pending',
    expires_at__lt=ahora + timedelta(minutes=5),
    expires_at__gte=ahora
)
```

### Verificar Stock

```python
from api.models import Producto

producto = Producto.objects.get(id=1)
print(f"Total: {producto.stock_total}")
print(f"Reservado: {producto.stock_reservado}")
print(f"Vendido: {producto.stock_vendido}")
print(f"Disponible: {producto.stock_disponible}")
```

---

## 🧪 Pruebas

### Test: Agregar al Carrito

```bash
curl -X POST http://localhost:8000/api/carrito/agregar/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 5
  }'
```

### Test: Checkout

```bash
curl -X POST http://localhost:8000/api/carrito/checkout/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json"
```

### Test: Liberar Reservas

```bash
python manage.py liberar_reservas_expiradas --verbose
```

---

## 🚨 Troubleshooting

### Problema: "Stock insuficiente" aunque hay stock

**Causa:** Hay reservas pendientes de otros usuarios

**Solución:** Esperar a que expiren (15 minutos) o ejecutar:
```bash
python manage.py liberar_reservas_expiradas
```

### Problema: Stock negativo

**Causa:** Bug en la lógica de reserva

**Solución:** Ejecutar script de corrección:
```python
from api.models import Producto

for producto in Producto.objects.all():
    if producto.stock_disponible < 0:
        producto.stock_reservado = max(0, producto.stock_total - producto.stock_vendido)
        producto.save()
```

### Problema: Reservas no se liberan

**Causa:** Management command no se ejecuta

**Solución:** Verificar cron/Celery y ejecutar manualmente:
```bash
python manage.py liberar_reservas_expiradas --verbose
```

---

## 📚 Referencias

- **Modelo:** Commit/Rollback (Transacciones ACID)
- **Patrón:** Saga Pattern (Transacciones distribuidas)
- **TTL:** Time To Live (Expiración automática)
- **Rate Limiting:** Throttling (Protección contra DoS)

---

## ✅ Checklist de Implementación

- [x] Agregar campos a modelo Producto
- [x] Crear modelo StockReservation
- [x] Crear migración de base de datos
- [x] Actualizar endpoint agregar (FASE 1)
- [x] Crear endpoint checkout (FASE 2)
- [x] Crear management command para liberar reservas
- [x] Actualizar serializers
- [x] Actualizar frontend (validación de stock)
- [x] Documentación completa
- [ ] Tests unitarios (pendiente)
- [ ] Tests de integración (pendiente)

---

## 🎓 Conclusión

El sistema ahora es **robusto, escalable y seguro**:

✅ **Separación clara:** Carrito ≠ Inventario Real
✅ **Transacciones atómicas:** Commit/Rollback automático
✅ **Protección contra DoS:** Rate limiting en múltiples capas
✅ **Experiencia de usuario:** Stock actualizado en tiempo real
✅ **Auditoría completa:** Registro de todas las operaciones

**Resultado:** Usuarios legítimos pueden comprar sin problemas, mientras que ataques de fuerza son bloqueados automáticamente.
