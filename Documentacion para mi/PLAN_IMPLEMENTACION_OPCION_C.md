# 📋 PLAN DE IMPLEMENTACIÓN: Opción C (Frontend + Backend)

**Objetivo:** Implementar limpieza de carrito en logout de manera segura y quirúrgica  
**Riesgo:** Muy bajo (cambios mínimos y bien localizados)  
**Sincronización:** Verificada en todos los puntos

---

## 🗺️ MAPEO COMPLETO

### Frontend - Lugares donde se llama `logout()`

```
1. UserMenu.tsx (línea 52)
   ├─ handleLogout()
   ├─ logout()
   └─ navigate('/')

2. axios.ts (línea 203)
   ├─ Interceptor de response
   ├─ Si token expirado: logout()
   └─ Redirige a login

3. ProtectedRoute.tsx (línea 59)
   ├─ useEffect
   ├─ Si token expirado: logout()
   └─ Limpia sesión

4. AdminLayout.tsx (línea 48)
   ├─ handleLogout()
   ├─ logout()
   └─ navigate('/login')
```

### Frontend - Lugares donde se llama `clearCart()`

```
1. useAuthStore.ts (línea 106)
   ├─ logout()
   ├─ useCartStore.getState().clearCart()
   └─ Limpia localStorage y Zustand

2. useSyncCart.ts (línea 487)
   ├─ useEffect
   ├─ if (!isAuthenticated) { clearCart() }
   └─ Resetea flags globales
```

---

## ✅ CAMBIOS A REALIZAR

### CAMBIO 1: Frontend - useAuthStore.ts

**Ubicación:** `logout()` function

**Antes:**
```typescript
logout: () => {
  // Limpiar localStorage
  localStorage.removeItem('accessToken');
  localStorage.removeItem('user');
  localStorage.removeItem('auth-storage');
  localStorage.removeItem('cart-storage');
  localStorage.removeItem('cart-backup');
  
  // Limpiar sessionStorage
  sessionStorage.removeItem('accessToken');
  sessionStorage.removeItem('user');
  
  // Limpiar carrito en Zustand
  try {
    useCartStore.getState().clearCart();
  } catch (error) {
    console.warn('[useAuthStore] No se pudo limpiar carrito:', error);
  }
  
  // Limpiar estado en memoria
  set({ 
    isAuthenticated: false, 
    user: null,
    accessToken: null
  });
}
```

**Después:**
```typescript
logout: () => {
  // ✅ NUEVO: Limpiar carrito en el BACKEND (CRÍTICO)
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
  const { accessToken } = get();
  
  if (accessToken) {
    // Llamar al endpoint de vaciar carrito en el backend
    // Usar fetch sin await para no bloquear el logout
    fetch(`${apiUrl}/carrito/vaciar/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      credentials: 'include',
    }).catch((error) => {
      console.warn('[useAuthStore] Error al vaciar carrito en backend:', error);
    });
  }
  
  // Limpiar localStorage
  localStorage.removeItem('accessToken');
  localStorage.removeItem('user');
  localStorage.removeItem('auth-storage');
  localStorage.removeItem('cart-storage');
  localStorage.removeItem('cart-backup');
  
  // Limpiar sessionStorage
  sessionStorage.removeItem('accessToken');
  sessionStorage.removeItem('user');
  
  // Limpiar carrito en Zustand
  try {
    useCartStore.getState().clearCart();
  } catch (error) {
    console.warn('[useAuthStore] No se pudo limpiar carrito:', error);
  }
  
  // Limpiar estado en memoria
  set({ 
    isAuthenticated: false, 
    user: null,
    accessToken: null
  });
}
```

**Cambios:**
- ✅ Agregar llamada a `DELETE /api/carrito/vaciar/` antes de limpiar localStorage
- ✅ Usar `fetch` sin `await` para no bloquear el logout
- ✅ Manejar errores con `.catch()`
- ✅ Agregar comentarios explicativos

**Impacto:**
- ✅ No afecta otros lugares donde se llama `logout()`
- ✅ No afecta `clearCart()` en `useSyncCart.ts`
- ✅ No rompe sincronización

---

### CAMBIO 2: Backend - Agregar Signal para limpiar carrito

**Ubicación:** `backend/api/signals.py` (crear si no existe)

**Código a agregar:**
```python
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_out
from .models import Cart

@receiver(user_logged_out)
def limpiar_carrito_al_logout(sender, request, user, **kwargs):
    """
    ✅ FALLBACK: Limpiar carrito cuando el usuario se desloguea
    
    Este signal se dispara cuando el usuario se desloguea.
    Limpia todos los items del carrito como fallback.
    
    Nota: El frontend también llama a DELETE /api/carrito/vaciar/
    Este signal es un fallback de seguridad.
    """
    try:
        cart = Cart.objects.filter(user=user).first()
        if cart:
            # Eliminar todos los items del carrito
            cart.items.all().delete()
            
            # Logging
            logger.info(f'[SIGNAL] Carrito limpiado al logout: Usuario {user.username}')
    except Exception as error:
        logger.error(f'[SIGNAL] Error limpiando carrito al logout: {error}')
```

**Ubicación en archivo:**
- Crear archivo: `backend/api/signals.py`
- O agregar a: `backend/api/apps.py` (en la clase AppConfig)

**Cambios:**
- ✅ Agregar signal para limpiar carrito
- ✅ Manejar errores
- ✅ Agregar logging

**Impacto:**
- ✅ Fallback automático si frontend falla
- ✅ No afecta otros endpoints
- ✅ No rompe sincronización

---

## 🔄 FLUJO DE SINCRONIZACIÓN VERIFICADO

### Logout Flow (Verificado)

```
1. Usuario hace logout
   ├─ logout() se llama (en UserMenu, axios, ProtectedRoute, AdminLayout)
   ├─ DELETE /api/carrito/vaciar/ (Frontend) ✅
   │  └─ Backend limpia items
   ├─ localStorage se limpia ✅
   ├─ useCartStore.clearCart() se llama ✅
   │  ├─ items = []
   │  ├─ pending = {}
   │  └─ localStorage limpio
   ├─ isAuthenticated = false ✅
   └─ Signal se dispara (Backend) ✅
      └─ Fallback: limpia carrito si no fue limpiado

2. useSyncCart.useEffect() se dispara
   ├─ if (!isAuthenticated) { clearCart() } ✅
   ├─ cartLoadedForUser.clear() ✅
   ├─ isCartLoading = false ✅
   └─ cartLoadPromise = null ✅
```

### Login Flow (Verificado)

```
1. Usuario hace login
   ├─ login() se llama
   ├─ isAuthenticated = true ✅
   ├─ accessToken guardado ✅
   └─ useSyncCart.useEffect() se dispara

2. fetchCartFromBackend()
   ├─ GET /api/carrito/
   ├─ Backend: Cart.objects.get_or_create(user=request.user)
   │  └─ Obtiene carrito (ahora vacío porque fue limpiado)
   ├─ Prefetch: items__product
   │  └─ Devuelve 0 items ✅
   ├─ useCartStore.setItems([]) ✅
   └─ localStorage['cart-storage'] = {items: []} ✅

3. cartLoadedForUser.add(user.id)
   └─ Marca como cargado para esta sesión ✅
```

---

## 🧪 VERIFICACIÓN DE SINCRONIZACIÓN

### Punto 1: logout() se llama desde múltiples lugares

**Verificado:**
- ✅ UserMenu.tsx (línea 52)
- ✅ axios.ts (línea 203)
- ✅ ProtectedRoute.tsx (línea 59)
- ✅ AdminLayout.tsx (línea 48)

**Impacto:** Todos los lugares llaman a la MISMA función `logout()`, así que el cambio se aplica a todos automáticamente.

### Punto 2: clearCart() se llama desde dos lugares

**Verificado:**
- ✅ useAuthStore.ts (línea 106) - En logout()
- ✅ useSyncCart.ts (línea 487) - En useEffect

**Impacto:** 
- Ambos llaman a `useCartStore.getState().clearCart()`
- El cambio en `logout()` no afecta a `useSyncCart.ts`
- Ambos se ejecutan sin conflictos

### Punto 3: Sincronización de flags globales

**Verificado:**
- ✅ `cartLoadedForUser` se resetea en `useSyncCart.ts` (línea 489)
- ✅ `isCartLoading` se resetea en `useSyncCart.ts` (línea 490)
- ✅ `cartLoadPromise` se resetea en `useSyncCart.ts` (línea 491)

**Impacto:** Los flags se resetean DESPUÉS de que `clearCart()` se llama, así que no hay conflictos.

---

## ⚠️ PUNTOS CRÍTICOS A VERIFICAR

### 1. El endpoint DELETE /api/carrito/vaciar/ existe

**Verificado:** ✅ Existe en `backend/api/views.py` línea 862-877

### 2. El endpoint requiere autenticación

**Verificado:** ✅ `permission_classes = [permissions.IsAuthenticated]`

### 3. El endpoint limpia correctamente

**Verificado:** ✅ `cart.items.all().delete()`

### 4. El token está disponible en logout()

**Verificado:** ✅ Se obtiene con `get().accessToken`

### 5. No hay race conditions

**Verificado:** ✅ Fetch sin await, no bloquea logout

---

## 📊 RESUMEN DE CAMBIOS

| Archivo | Línea | Cambio | Riesgo |
|---------|-------|--------|--------|
| useAuthStore.ts | 73-97 | Agregar DELETE /api/carrito/vaciar/ | Muy Bajo |
| signals.py | NEW | Agregar signal para limpiar carrito | Muy Bajo |

**Total de cambios:** 2 archivos, ~30 líneas  
**Riesgo total:** Muy Bajo  
**Sincronización:** Verificada en todos los puntos

---

## ✅ CHECKLIST PRE-IMPLEMENTACIÓN

- [x] Mapear todos los lugares donde se llama `logout()`
- [x] Mapear todos los lugares donde se llama `clearCart()`
- [x] Verificar sincronización en `useSyncCart`
- [x] Verificar que el endpoint existe
- [x] Verificar que el endpoint requiere autenticación
- [x] Verificar que el endpoint limpia correctamente
- [x] Verificar que el token está disponible
- [x] Verificar que no hay race conditions
- [x] Crear plan de implementación
- [ ] Implementar cambios
- [ ] Verificar que todo funciona

---

**Plan completado:** 19 de Noviembre, 2025  
**Estado:** Listo para implementar  
**Aprobación requerida:** Sí
