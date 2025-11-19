# 🔧 FIX - Productos No Cargan en la Página Principal

## 🔍 PROBLEMA

Los productos no aparecen en la página principal (HomePage) aunque el backend está funcionando correctamente.

## 🎯 CAUSA

El frontend está llamando a: `GET /api/carrusel/`

Este endpoint busca productos con:
- `en_carrusel=True` ✅ (marcado para mostrar en carrusel)
- `activo=True` ✅ (producto activo)

**Si NO hay productos con estas características, el carrusel estará vacío.**

---

## ✅ SOLUCIÓN (3 Opciones)

### Opción 1: Script Automático (RECOMENDADO)

```bash
cd backend
python fix_productos.py
```

**Este script:**
1. ✅ Verifica cuántos productos hay
2. ✅ Activa todos los productos inactivos
3. ✅ Marca los primeros 5 productos para el carrusel
4. ✅ Muestra resumen final

**Resultado esperado:**
```
🔍 VERIFICANDO ESTADO DE PRODUCTOS
════════════════════════════════════════════════════════════════════════════════

📊 Total de productos en BD: 15
✅ Productos activos: 15
❌ Productos inactivos: 0
🎠 Productos en carrusel: 5

════════════════════════════════════════════════════════════════════════════════
✅ VERIFICACIÓN COMPLETADA
════════════════════════════════════════════════════════════════════════════════

📊 ESTADO FINAL:
   • Total: 15
   • Activos: 15
   • En carrusel: 5

✨ Los productos deberían aparecer en el frontend ahora.
```

---

### Opción 2: Django Admin (Manual)

```
1. Ir a http://localhost:8000/admin/
2. Login con tu usuario admin
3. Ir a "Productos"
4. Para cada producto:
   ✅ Marcar "Activo"
   ✅ Marcar "En carrusel" (al menos 5)
5. Guardar
```

---

### Opción 3: Django Shell (Avanzado)

```bash
cd backend
python manage.py shell
```

```python
from api.models import Producto

# Activar todos los productos
Producto.objects.all().update(activo=True)

# Marcar primeros 5 para carrusel
Producto.objects.all().order_by('id')[:5].update(en_carrusel=True)

# Verificar
print(f"Activos: {Producto.objects.filter(activo=True).count()}")
print(f"En carrusel: {Producto.objects.filter(en_carrusel=True).count()}")

exit()
```

---

## 🔄 Después de Aplicar la Solución

### 1. Limpiar Cache (si está habilitado)

```bash
# En Django shell
from django.core.cache import cache
cache.clear()
```

### 2. Recargar el Frontend

```
1. Presiona F5 en el navegador (o Ctrl+Shift+R para limpiar cache)
2. Los productos deberían aparecer en la página principal
```

### 3. Verificar en la API

```bash
# Abrir en navegador o Postman
http://localhost:8000/api/carrusel/

# Deberías ver:
{
  "count": 5,
  "data": [
    {
      "id": 1,
      "nombre": "Producto 1",
      "precio": "99.99",
      "imagen_url": "...",
      "en_carrusel": true,
      "activo": true,
      ...
    },
    ...
  ]
}
```

---

## 📊 Flujo Completo

```
Frontend (HomePage)
    ↓
useProductosCarrusel()
    ↓
GET /api/carrusel/
    ↓
Backend busca: Producto.objects.filter(en_carrusel=True, activo=True)
    ↓
Si hay productos → Mostrar en carrusel ✅
Si NO hay → Mostrar "Cargando productos..." ❌
```

---

## 🚨 Checklist

- [ ] Ejecuté `python fix_productos.py` O actualicé manualmente en Django Admin
- [ ] Verifiqué que hay productos con `en_carrusel=True`
- [ ] Verifiqué que hay productos con `activo=True`
- [ ] Limpié el cache del navegador (F5 o Ctrl+Shift+R)
- [ ] Los productos aparecen en la página principal ✅

---

## ❓ Si Aún No Funciona

### 1. Verificar que hay productos en BD

```bash
cd backend
python manage.py shell
from api.models import Producto
print(f"Total: {Producto.objects.count()}")
exit()
```

Si retorna `0`, necesitas crear productos primero.

### 2. Verificar que el endpoint funciona

```bash
curl http://localhost:8000/api/carrusel/
```

Deberías ver JSON con productos.

### 3. Revisar logs del backend

En la terminal donde corre `python manage.py runserver`, busca errores.

### 4. Limpiar caché de Django

```bash
cd backend
python manage.py shell
from django.core.cache import cache
cache.clear()
exit()
```

---

## ✨ Resultado Final

Una vez aplicada la solución:
- ✅ Productos aparecen en la página principal
- ✅ Carrusel funciona correctamente
- ✅ Todos los productos están activos
- ✅ Frontend y backend sincronizados

**¡Listo! Tu página principal debería mostrar los productos ahora.** 🎉
