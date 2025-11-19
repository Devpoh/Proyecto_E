# ✅ FIX - Corrección de Imports

## ❌ Error Encontrado

```
ImportError: cannot import name 'CartWriteThrottle' from 'api.throttles'
```

## ✅ Causa

Los nombres de las clases en `throttles.py` cambiaron de:
- `CartWriteThrottle` → `CartWriteRateThrottle`
- `CheckoutThrottle` → `CheckoutRateThrottle`
- `AuthThrottle` → `AnonLoginRateThrottle`
- `AdminThrottle` → `AdminRateThrottle`

Pero `views.py` y `views_admin.py` seguían usando los nombres antiguos.

## ✅ Correcciones Realizadas

### 1. `backend/api/views.py` (ACTUALIZADO)

**Línea 21**: Cambiar import
```python
# ANTES:
from .throttles import CartWriteThrottle, CheckoutThrottle, AuthThrottle

# DESPUÉS:
from .throttles import CartWriteRateThrottle, CheckoutRateThrottle, AnonLoginRateThrottle
```

**Línea 190**: Actualizar docstring
```python
# ANTES:
✅ Throttle: AuthThrottle (10 requests/hora)

# DESPUÉS:
✅ Throttle: AnonLoginRateThrottle (5 requests/minuto)
```

**Línea 577**: Actualizar throttle_classes
```python
# ANTES:
throttle_classes = [CartWriteThrottle]

# DESPUÉS:
throttle_classes = [CartWriteRateThrottle]
```

**Línea 582-587**: Actualizar get_throttles()
```python
# ANTES:
- checkout: CheckoutThrottle (más restrictivo)
- bulk-update: CartWriteThrottle (estándar)
- resto: CartWriteThrottle (estándar)
...
return [CheckoutThrottle()]

# DESPUÉS:
- checkout: CheckoutRateThrottle (más restrictivo)
- bulk-update: CartWriteRateThrottle (estándar)
- resto: CartWriteRateThrottle (estándar)
...
return [CheckoutRateThrottle()]
```

### 2. `backend/api/views_admin.py` (ACTUALIZADO)

**Línea 25**: Cambiar import
```python
# ANTES:
from .throttles import AdminThrottle

# DESPUÉS:
from .throttles import AdminRateThrottle
```

**Líneas 77, 310, 570**: Actualizar throttle_classes (3 lugares)
```python
# ANTES:
throttle_classes = [AdminThrottle]

# DESPUÉS:
throttle_classes = [AdminRateThrottle]
```

## ✅ Verificación

Todos los imports han sido actualizados. El servidor debería iniciar sin errores.

### Probar:
```bash
cd backend
python manage.py runserver
```

**Esperado**: ✅ Server inicia correctamente sin ImportError

---

## 📊 Resumen de Cambios

| Archivo | Cambios | Estado |
|---------|---------|--------|
| `views.py` | 4 cambios | ✅ |
| `views_admin.py` | 4 cambios | ✅ |
| **Total** | **8 cambios** | **✅** |

---

**¡Corrección completada! 🎉**
