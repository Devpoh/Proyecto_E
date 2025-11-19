# 🚀 GUÍA DE DESPLIEGUE - SISTEMA DE INVENTARIO

## ⚠️ IMPORTANTE: PASOS EN ORDEN

Sigue estos pasos **exactamente en este orden**. No saltes ninguno.

---

## PASO 1: Backup de Base de Datos

```bash
# Crear backup antes de hacer cambios
cd backend
pg_dump -U postgres -d electro_isla > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## PASO 2: Aplicar Migraciones

```bash
cd backend

# Aplicar la migración 0019 que crea el sistema de inventario
python manage.py migrate api 0019

# Verificar que se aplicó correctamente
python manage.py showmigrations api
```

**Salida esperada:**
```
[X] 0019_stock_system
```

---

## PASO 3: Actualizar Stock Existente

```bash
# Abrir Django shell
python manage.py shell

# Ejecutar dentro del shell:
from api.models import Producto

# Establecer stock_total = stock actual para todos los productos
for producto in Producto.objects.all():
    producto.stock_total = producto.stock
    producto.save()
    print(f"✓ {producto.nombre}: stock_total={producto.stock_total}")

print(f"\n✓ Total de {Producto.objects.count()} productos actualizados")

# Salir del shell
exit()
```

---

## PASO 4: Verificar Datos

```bash
# Abrir Django shell
python manage.py shell

# Verificar que los datos se actualizaron correctamente
from api.models import Producto

for producto in Producto.objects.all()[:5]:
    print(f"""
    Producto: {producto.nombre}
    - stock_total: {producto.stock_total}
    - stock_reservado: {producto.stock_reservado}
    - stock_vendido: {producto.stock_vendido}
    - stock_disponible: {producto.stock_disponible}
    """)

exit()
```

---

## PASO 5: Configurar Management Command

### Opción A: Cron Job (Recomendado para desarrollo)

```bash
# Editar crontab
crontab -e

# Agregar esta línea (ejecutar cada 5 minutos)
*/5 * * * * cd /ruta/a/backend && python manage.py liberar_reservas_expiradas >> /var/log/electro-isla-reservas.log 2>&1
```

### Opción B: Celery Beat (Recomendado para producción)

```python
# backend/config/celery.py
from celery.schedules import crontab

app.conf.beat_schedule = {
    'liberar-reservas-expiradas': {
        'task': 'api.tasks.liberar_reservas_expiradas',
        'schedule': crontab(minute='*/5'),  # Cada 5 minutos
    },
}
```

---

## PASO 6: Reiniciar Servidor

```bash
# Detener servidor actual
# Ctrl+C en la terminal

# Reiniciar
cd backend
python manage.py runserver
```

---

## PASO 7: Verificar Endpoints

### Test 1: Agregar al Carrito

```bash
# Obtener token (si no lo tienes)
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "tu_usuario", "password": "tu_contraseña"}'

# Guardar el token en variable
TOKEN="tu_token_aqui"

# Test: Agregar al carrito
curl -X POST http://localhost:8000/api/carrito/agregar/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'

# Respuesta esperada (201):
# {
#   "id": 1,
#   "items": [...],
#   "total": 199.98,
#   "total_items": 2,
#   ...
# }
```

### Test 2: Checkout (Reservar Stock)

```bash
# Test: Checkout
curl -X POST http://localhost:8000/api/carrito/checkout/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

# Respuesta esperada (200):
# {
#   "message": "Stock reservado exitosamente",
#   "reservas": [
#     {
#       "id": 1,
#       "producto": "Nombre del Producto",
#       "cantidad": 2,
#       "expires_at": "2025-11-09T20:45:00Z"
#     }
#   ],
#   "total_items": 2,
#   "ttl_minutos": 15
# }
```

### Test 3: Liberar Reservas Expiradas

```bash
# Test manual
python manage.py liberar_reservas_expiradas --verbose

# Respuesta esperada:
# 🔄 Iniciando liberación de reservas expiradas...
# ✅ 0 reservas expiradas liberadas exitosamente
# ℹ️ No hay reservas expiradas para liberar
```

---

## PASO 8: Verificar en Admin

```bash
# Abrir Django admin
# http://localhost:8000/admin/

# Navegar a:
# - API > Productos: Verificar campos stock_total, stock_reservado, stock_vendido
# - API > Stock Reservations: Ver reservas creadas
```

---

## PASO 9: Monitoreo

### Verificar Reservas Activas

```bash
python manage.py shell

from api.models import StockReservation
from django.utils import timezone

# Reservas pendientes
pendientes = StockReservation.objects.filter(status='pending')
print(f"Reservas pendientes: {pendientes.count()}")

for r in pendientes:
    print(f"  - {r.usuario.username}: {r.producto.nombre} x{r.cantidad}")

# Reservas próximas a expirar
from datetime import timedelta
ahora = timezone.now()
proximas = StockReservation.objects.filter(
    status='pending',
    expires_at__lt=ahora + timedelta(minutes=5),
    expires_at__gte=ahora
)
print(f"\nReservas próximas a expirar: {proximas.count()}")

exit()
```

---

## PASO 10: Frontend - Verificar Stock

El frontend ahora mostrará:

```javascript
// Respuesta del API con nuevo campo
{
  "id": 1,
  "nombre": "Producto",
  "stock": 5,              // Legado: stock_disponible
  "stock_total": 10,       // Total en almacén
  "stock_reservado": 3,    // Reservado en checkouts
  "stock_vendido": 2,      // Ya vendido
  "stock_disponible": 5    // Disponible para comprar
}
```

---

## ✅ Checklist de Verificación

- [ ] Backup de BD creado
- [ ] Migración 0019 aplicada
- [ ] Stock existente actualizado (stock_total = stock)
- [ ] Datos verificados en Django shell
- [ ] Management command configurado (cron o Celery)
- [ ] Servidor reiniciado
- [ ] Test agregar al carrito exitoso (201)
- [ ] Test checkout exitoso (200)
- [ ] Test liberar reservas exitoso
- [ ] Admin muestra nuevos campos
- [ ] Frontend muestra stock_disponible correcto

---

## 🆘 Rollback (Si algo falla)

```bash
# Restaurar backup
psql -U postgres -d electro_isla < backup_YYYYMMDD_HHMMSS.sql

# Revertir migración
cd backend
python manage.py migrate api 0018

# Reiniciar servidor
python manage.py runserver
```

---

## 📊 Monitoreo Continuo

### Logs

```bash
# Ver logs de seguridad
tail -f backend/logs/security.log

# Ver logs de auth
tail -f backend/logs/auth.log

# Ver logs de cron (si usas cron job)
tail -f /var/log/electro-isla-reservas.log
```

### Métricas

```bash
# Ejecutar periódicamente
python manage.py shell

from api.models import Producto, StockReservation
from django.db.models import Sum

# Resumen de inventario
total_stock = Producto.objects.aggregate(Sum('stock_total'))['stock_total__sum']
total_reservado = Producto.objects.aggregate(Sum('stock_reservado'))['stock_reservado__sum']
total_vendido = Producto.objects.aggregate(Sum('stock_vendido'))['stock_vendido__sum']

print(f"""
RESUMEN DE INVENTARIO:
- Total en almacén: {total_stock}
- Total reservado: {total_reservado}
- Total vendido: {total_vendido}
- Disponible: {total_stock - total_reservado - total_vendido}
""")

# Reservas activas
reservas_pendientes = StockReservation.objects.filter(status='pending').count()
print(f"Reservas activas: {reservas_pendientes}")

exit()
```

---

## 🎓 Conclusión

¡Sistema de inventario implementado exitosamente! 

**Próximos pasos:**
1. Monitorear logs durante 24 horas
2. Verificar que las reservas se liberen automáticamente
3. Hacer pruebas de carga si es necesario
4. Documentar cualquier incidencia

**Soporte:**
- Revisar `SISTEMA_INVENTARIO.md` para detalles técnicos
- Revisar logs en `backend/logs/`
- Ejecutar `python manage.py liberar_reservas_expiradas --verbose` manualmente si es necesario
