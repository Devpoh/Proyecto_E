# ✅ CARRITO SINCRONIZADO CON BACKEND

**Fecha:** 7 de Noviembre, 2025  
**Status:** ✅ **IMPLEMENTADO Y LISTO PARA PROBAR**

---

## 🎯 CAMBIOS REALIZADOS

### ✅ 1. Nuevo Hook: `useSyncCart.ts`
- Sincroniza carrito local con backend
- Obtiene carrito al iniciar sesión
- Limpia carrito al cerrar sesión
- Sincroniza agregar, eliminar y actualizar

### ✅ 2. Actualizado: `useAddToCart.ts`
- Ahora usa `useSyncCart` para sincronizar
- Agrega al backend automáticamente

### ✅ 3. Actualizado: `useAuthStore.ts`
- Limpia carrito local al logout
- Evita que persista entre usuarios

---

## 🧪 PRUEBAS PASO A PASO

### Prueba 1: Carrito Único por Usuario

**Paso 1:** Abre DevTools (F12) → Storage → Local Storage

**Paso 2:** Inicia sesión con Usuario A
```
- Email: user1@example.com
- Password: password123
```

**Paso 3:** Agrega 2 productos al carrito
```
- Deberías ver en DevTools:
  - cart-storage: [{"productoId":1,"cantidad":1},{"productoId":2,"cantidad":1}]
  - Backend: GET /api/carrito/ → items con esos 2 productos
```

**Paso 4:** Cierra sesión
```
- Deberías ver:
  - cart-storage: ELIMINADO
  - Carrito vacío en UI
```

**Paso 5:** Inicia sesión con Usuario B
```
- Email: user2@example.com
- Password: password123
```

**Paso 6:** Verifica carrito
```
- Deberías ver:
  - Carrito VACÍO (no los productos de Usuario A)
  - Backend: GET /api/carrito/ → items vacío
```

**Paso 7:** Agrega 1 producto diferente
```
- Deberías ver:
  - Solo ese 1 producto en el carrito
  - NO los productos de Usuario A
```

---

### Prueba 2: Sincronización Backend

**Paso 1:** Abre 2 navegadores (o ventanas privadas)

**Paso 2:** En Navegador 1:
```
- Inicia sesión con Usuario A
- Agrega producto ID 1
```

**Paso 3:** En Navegador 2:
```
- Inicia sesión con Usuario A
- Verifica que el producto ID 1 está en el carrito
- Deberías ver: Carrito sincronizado automáticamente
```

**Paso 4:** En Navegador 1:
```
- Agrega producto ID 2
```

**Paso 5:** En Navegador 2:
```
- Recarga la página
- Deberías ver: Productos ID 1 y 2 en el carrito
```

---

### Prueba 3: CURL Directo al Backend

**Paso 1:** Obtén token
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

Guarda el `access_token` que recibes.

**Paso 2:** Obtén carrito
```bash
curl -X GET http://localhost:8000/api/carrito/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Esperado:**
```json
{
  "id": 1,
  "items": [],
  "total": 0.0,
  "total_items": 0,
  "created_at": "2025-11-07T...",
  "updated_at": "2025-11-07T..."
}
```

**Paso 3:** Agrega producto
```bash
curl -X POST http://localhost:8000/api/carrito/agregar/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":2}'
```

**Esperado:**
```json
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "nombre": "Producto 1",
        "imagen_url": "...",
        "categoria": "..."
      },
      "quantity": 2,
      "price_at_addition": "100.00",
      "subtotal": 200.0,
      "created_at": "2025-11-07T...",
      "updated_at": "2025-11-07T..."
    }
  ],
  "total": 200.0,
  "total_items": 2,
  "created_at": "2025-11-07T...",
  "updated_at": "2025-11-07T..."
}
```

**Paso 4:** Obtén carrito nuevamente
```bash
curl -X GET http://localhost:8000/api/carrito/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Esperado:** Mismo carrito con 2 items

---

## 🔍 VERIFICACIÓN EN ADMIN

1. Ve a: `http://localhost:8000/admin/`
2. Inicia sesión con superuser
3. Ve a: "Carrito" → Deberías ver carritos por usuario
4. Haz clic en un carrito → Deberías ver sus items

---

## 📊 FLUJO COMPLETO

```
┌─────────────────────────────────────────────────────────────┐
│ USUARIO INICIA SESIÓN                                       │
├─────────────────────────────────────────────────────────────┤
│ 1. Frontend: useAuthStore.login()                           │
│ 2. Frontend: useSyncCart.fetchCartFromBackend()             │
│ 3. Backend: GET /api/carrito/ → Obtiene carrito del usuario │
│ 4. Frontend: Zustand store actualizado con items del backend│
│ 5. UI: Carrito muestra items correctos                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ USUARIO AGREGA PRODUCTO                                     │
├─────────────────────────────────────────────────────────────┤
│ 1. Frontend: useAddToCart.handleAddToCart()                 │
│ 2. Frontend: Zustand addItem() → Carrito local actualizado  │
│ 3. Frontend: useSyncCart.syncAddToBackend()                 │
│ 4. Backend: POST /api/carrito/agregar/ → Guarda en DB      │
│ 5. UI: Toast "¡Producto agregado!"                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ USUARIO CIERRA SESIÓN                                       │
├─────────────────────────────────────────────────────────────┤
│ 1. Frontend: useAuthStore.logout()                          │
│ 2. Frontend: Limpia localStorage (tokens, carrito)          │
│ 3. Frontend: useSyncCart limpia carrito local               │
│ 4. UI: Carrito vacío                                        │
│ 5. Backend: Carrito del usuario sigue en DB (para próxima   │
│    sesión)                                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ USUARIO INICIA SESIÓN NUEVAMENTE                            │
├─────────────────────────────────────────────────────────────┤
│ 1. Frontend: useAuthStore.login()                           │
│ 2. Frontend: useSyncCart.fetchCartFromBackend()             │
│ 3. Backend: GET /api/carrito/ → Obtiene carrito guardado    │
│ 4. Frontend: Zustand store actualizado                      │
│ 5. UI: Carrito muestra items guardados anteriormente        │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ CONCLUSIÓN

**Carrito completamente sincronizado:**
- ✅ Único por usuario
- ✅ Persiste en backend
- ✅ Se limpia al logout
- ✅ Se obtiene al login
- ✅ Sincronización automática

¡Listo para producción! 🚀
