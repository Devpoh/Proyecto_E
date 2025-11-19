# 🔬 ANÁLISIS QUIRÚRGICO - PROBLEMA DEL CARRITO

**Fecha:** 7 de Noviembre, 2025  
**Severidad:** 🔴 CRÍTICA  
**Status:** ✅ **SOLUCIONADO**

---

## 🔍 PROBLEMA IDENTIFICADO

### Síntomas Reportados
1. ❌ Al desloguearse, el carrito sigue mostrando productos
2. ❌ Al loguearse con otra cuenta, ve productos de la cuenta anterior
3. ❌ No hay carrito único por usuario

### Causa Raíz

**Arquitectura Anterior (INCORRECTA):**
```
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (React + Zustand)                                  │
├─────────────────────────────────────────────────────────────┤
│ useCartStore (Zustand)                                      │
│ ├─ items: [...]                                             │
│ ├─ localStorage: 'cart-storage'  ← PROBLEMA: Global         │
│ └─ NO sincroniza con backend                                │
│                                                              │
│ Flujo:                                                       │
│ 1. Usuario A agrega producto → localStorage actualizado     │
│ 2. Usuario A cierra sesión → localStorage NO se limpia      │
│ 3. Usuario B inicia sesión → localStorage sigue con items   │
│    de Usuario A                                             │
│ 4. useSyncCart NO existe → NO sincroniza con backend        │
└─────────────────────────────────────────────────────────────┘
```

**Problemas Específicos:**

1. **localStorage Global**
   - No es por usuario
   - Persiste entre sesiones
   - Se comparte entre usuarios

2. **Sin Sincronización**
   - Backend tiene carrito por usuario
   - Frontend NO lo obtiene
   - Desconexión total

3. **Sin Limpieza al Logout**
   - `useAuthStore.logout()` no limpiaba carrito
   - localStorage['cart-storage'] permanecía

4. **Sin Obtención al Login**
   - No había hook para obtener carrito del backend
   - No había sincronización automática

---

## ✅ SOLUCIÓN IMPLEMENTADA

### Arquitectura Nueva (CORRECTA)

```
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (React + Zustand + Sincronización)                 │
├─────────────────────────────────────────────────────────────┤
│ useAuthStore                                                │
│ ├─ isAuthenticated: boolean                                 │
│ ├─ user: User | null                                        │
│ └─ logout(): Limpia localStorage + carrito                  │
│                                                              │
│ useSyncCart (NUEVO)                                         │
│ ├─ fetchCartFromBackend(): Obtiene carrito del servidor     │
│ ├─ syncAddToBackend(): Agrega al backend                    │
│ ├─ syncRemoveFromBackend(): Elimina del backend             │
│ ├─ syncUpdateQuantityBackend(): Actualiza cantidad          │
│ └─ useEffect: Sincroniza al login/logout                    │
│                                                              │
│ useCartStore (Zustand)                                      │
│ ├─ items: [...]                                             │
│ ├─ localStorage: 'cart-storage' (temporal)                  │
│ └─ Se sincroniza con backend automáticamente                │
│                                                              │
│ Flujo:                                                       │
│ 1. Usuario A agrega producto                                │
│    → useAddToCart.handleAddToCart()                         │
│    → addItem() (local)                                      │
│    → syncAddToBackend() (backend)                           │
│                                                              │
│ 2. Usuario A cierra sesión                                  │
│    → useAuthStore.logout()                                  │
│    → Limpia localStorage (tokens + carrito)                 │
│    → useSyncCart limpia carrito local                       │
│                                                              │
│ 3. Usuario B inicia sesión                                  │
│    → useAuthStore.login()                                   │
│    → useSyncCart.fetchCartFromBackend()                     │
│    → Obtiene carrito de Usuario B del backend               │
│    → Zustand actualizado con carrito correcto               │
│                                                              │
│ 4. Usuario B ve su carrito (NO el de Usuario A)             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ BACKEND (Django + DRF)                                      │
├─────────────────────────────────────────────────────────────┤
│ Cart Model                                                  │
│ ├─ user: OneToOneField(User)  ← Por usuario                │
│ ├─ items: CartItem[]                                        │
│ └─ created_at, updated_at                                   │
│                                                              │
│ Endpoints:                                                  │
│ ├─ GET /api/carrito/                                        │
│ │  └─ Obtiene carrito del usuario autenticado               │
│ ├─ POST /api/carrito/agregar/                               │
│ │  └─ Agrega producto (validación de stock)                 │
│ ├─ PUT /api/carrito/items/{id}/                             │
│ │  └─ Actualiza cantidad                                    │
│ ├─ DELETE /api/carrito/items/{id}/                          │
│ │  └─ Elimina item                                          │
│ └─ DELETE /api/carrito/vaciar/                              │
│    └─ Vacía carrito                                         │
│                                                              │
│ Autenticación: JWT (IsAuthenticated)                        │
│ Autorización: Solo su carrito                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 CAMBIOS ESPECÍFICOS

### 1. Nuevo Hook: `useSyncCart.ts`

**Responsabilidades:**
- Sincronizar carrito local con backend
- Obtener carrito al iniciar sesión
- Limpiar carrito al cerrar sesión
- Manejar errores de sincronización

**Métodos:**
```typescript
fetchCartFromBackend()      // GET /api/carrito/
syncAddToBackend()          // POST /api/carrito/agregar/
syncRemoveFromBackend()     // DELETE /api/carrito/items/{id}/
syncUpdateQuantityBackend() // PUT /api/carrito/items/{id}/
```

**Efectos:**
```typescript
// Limpiar carrito cuando se cierra sesión
useEffect(() => {
  if (!isAuthenticated) clearCart();
}, [isAuthenticated])

// Obtener carrito cuando se inicia sesión
useEffect(() => {
  if (isAuthenticated && user) fetchCartFromBackend();
}, [isAuthenticated, user])
```

### 2. Actualizado: `useAddToCart.ts`

**Antes:**
```typescript
addItem(numericId);  // Solo local
```

**Después:**
```typescript
addItem(numericId);                    // Local
syncAddToBackend(numericId, 1);        // Backend
```

### 3. Actualizado: `useAuthStore.ts`

**Antes:**
```typescript
logout: () => {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('user');
  sessionStorage.removeItem('accessToken');
  sessionStorage.removeItem('user');
  set({ isAuthenticated: false, user: null });
}
```

**Después:**
```typescript
logout: () => {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('user');
  sessionStorage.removeItem('accessToken');
  sessionStorage.removeItem('user');
  localStorage.removeItem('cart-storage');  // ← NUEVO
  set({ isAuthenticated: false, user: null });
}
```

---

## 🧪 VALIDACIÓN

### Prueba 1: Carrito Único por Usuario
✅ Usuario A agrega productos → localStorage actualizado  
✅ Usuario A cierra sesión → localStorage limpiado  
✅ Usuario B inicia sesión → Ve su carrito (vacío o con sus items)  
✅ Usuario B NO ve items de Usuario A  

### Prueba 2: Sincronización Backend
✅ Agregar producto → Backend actualizado  
✅ Eliminar producto → Backend actualizado  
✅ Actualizar cantidad → Backend actualizado  
✅ Obtener carrito → Datos consistentes  

### Prueba 3: Persistencia
✅ Usuario A agrega productos  
✅ Usuario A cierra sesión  
✅ Usuario A inicia sesión nuevamente  
✅ Sus productos siguen en el carrito (guardados en backend)  

---

## 🔐 SEGURIDAD

✅ Autenticación JWT requerida  
✅ Autorización: Solo su carrito  
✅ Validación de stock  
✅ Validación de cantidad  
✅ Precios guardados al momento de agregar  
✅ No se puede manipular carrito de otro usuario  

---

## 📊 COMPARATIVA

| Aspecto | Antes | Después |
|---------|-------|---------|
| Carrito por usuario | ❌ No | ✅ Sí |
| Sincronización | ❌ No | ✅ Automática |
| Limpieza al logout | ❌ No | ✅ Sí |
| Obtención al login | ❌ No | ✅ Sí |
| Persistencia | ❌ No | ✅ Sí (backend) |
| Seguridad | ⚠️ Débil | ✅ Fuerte |

---

## ✨ CONCLUSIÓN

**Problema:** Carrito compartido entre usuarios  
**Causa:** Sin sincronización con backend  
**Solución:** Hook `useSyncCart` + Limpieza al logout  
**Resultado:** Carrito único, sincronizado y seguro  

**Status:** ✅ **SOLUCIONADO 100%**

¡Listo para producción! 🚀
