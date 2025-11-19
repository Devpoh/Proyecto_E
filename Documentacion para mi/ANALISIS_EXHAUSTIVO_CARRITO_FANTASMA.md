# 🔍 ANÁLISIS EXHAUSTIVO: Carrito Fantasma - Investigación Completa

**Objetivo:** Entender EXACTAMENTE por qué reaparecen los productos del carrito  
**Metodología:** Rastrear TODOS los flujos sin hacer cambios

---

## 📊 ARQUITECTURA DEL CARRITO

### Backend (Django)

```
Modelo: Cart (OneToOneField con User)
├─ user: Usuario propietario
├─ created_at: Fecha de creación
├─ updated_at: Última actualización
└─ items: Relación con CartItem (ForeignKey)

Modelo: CartItem
├─ cart: Referencia a Cart
├─ product: Producto
├─ quantity: Cantidad
├─ price_at_addition: Precio al agregar
├─ created_at: Fecha de agregación
└─ updated_at: Última actualización
```

**Base de datos:** PostgreSQL  
**Tabla:** carts, cart_items

### Frontend (React)

```
Zustand Store: useCartStore
├─ items: CartItem[]
├─ pending: Record<number, number>
├─ isSyncing: boolean
├─ retryCount: number
└─ localStorage: 'cart-storage', 'cart-backup'

Context: CartContext (LEGACY - no se usa)
├─ cartItems: CartItem[]
├─ addToCart()
├─ removeFromCart()
└─ clearCart()
```

---

## 🔄 FLUJO COMPLETO: LOGIN → AGREGAR → LOGOUT → LOGIN

### FASE 1: LOGIN

**Frontend:**
```
1. Usuario hace login
   ├─ POST /api/auth/login/
   ├─ Backend devuelve: {accessToken, user, refreshToken (cookie)}
   ├─ Frontend: useAuthStore.login(user, token)
   │  ├─ set({ isAuthenticated: true, user, accessToken })
   │  └─ Token guardado en memoria (Zustand)
   └─ useSyncCart.fetchCartFromBackend() se llama (useEffect)

2. fetchCartFromBackend()
   ├─ GET /api/carrito/
   ├─ Backend: Cart.objects.get_or_create(user=request.user)
   │  ├─ Si existe: devuelve carrito existente
   │  └─ Si NO existe: crea carrito vacío
   ├─ Backend devuelve: {id, items: [], total: 0}
   ├─ Frontend: useCartStore.setItems([])
   └─ localStorage['cart-storage'] = {items: [], pending: {}}
```

**Backend:**
```
1. GET /api/carrito/
   ├─ Autenticación: IsAuthenticated ✅
   ├─ Query: Cart.objects.get_or_create(user=request.user)
   │  ├─ Busca: SELECT * FROM carts WHERE user_id = X
   │  ├─ Si existe: devuelve ese carrito
   │  └─ Si NO existe: INSERT INTO carts (user_id) VALUES (X)
   ├─ Prefetch: items__product
   │  └─ SELECT * FROM cart_items WHERE cart_id = Y
   └─ Serializa y devuelve
```

---

### FASE 2: AGREGAR PRODUCTOS

**Frontend:**
```
1. Usuario agrega producto
   ├─ handleAddToCart(productId)
   ├─ syncAddToBackend(productId, quantity)
   │  ├─ POST /api/carrito/agregar/
   │  ├─ Body: {product_id: 1, quantity: 1}
   │  └─ Backend devuelve: {items: [{...}], total: X}
   ├─ useCartStore.setItems([...])
   └─ localStorage['cart-storage'] = {items: [...], pending: {}}

2. Repite para 3 productos
   ├─ useCartStore.items = [p1, p2, p3]
   └─ localStorage['cart-storage'] = {items: [p1, p2, p3]}
```

**Backend:**
```
1. POST /api/carrito/agregar/
   ├─ Autenticación: IsAuthenticated ✅
   ├─ Query: Cart.objects.get_or_create(user=request.user)
   │  └─ Obtiene el carrito del usuario
   ├─ Crea: CartItem(cart=cart, product=producto, quantity=1)
   ├─ Guarda en BD
   └─ Devuelve carrito actualizado

2. Repite para 3 productos
   ├─ BD: INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (Y, 1, 1)
   ├─ BD: INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (Y, 2, 1)
   ├─ BD: INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (Y, 3, 1)
   └─ Carrito en BD tiene 3 items
```

---

### FASE 3: LOGOUT

**Frontend (ACTUAL):**
```
1. Usuario hace logout
   ├─ useAuthStore.logout()
   │  ├─ localStorage.removeItem('cart-storage')
   │  ├─ localStorage.removeItem('cart-backup')
   │  ├─ useCartStore.clearCart()
   │  │  ├─ set({ items: [], pending: {} })
   │  │  ├─ localStorage.removeItem('cart-storage')
   │  │  └─ localStorage.removeItem('cart-backup')
   │  ├─ set({ isAuthenticated: false, user: null, accessToken: null })
   │  └─ ❌ NO LLAMA A DELETE /api/carrito/vaciar/
   └─ useSyncCart.useEffect() se dispara
      ├─ if (!isAuthenticated) { clearCart() }
      ├─ cartLoadedForUser.clear()
      ├─ isCartLoading = false
      └─ cartLoadPromise = null

2. Estado después del logout
   ├─ Frontend: useCartStore.items = [] ✅
   ├─ Frontend: localStorage['cart-storage'] = null ✅
   ├─ Backend: Cart en BD sigue con 3 items ❌ PROBLEMA
   └─ Backend: CartItem en BD sigue con 3 items ❌ PROBLEMA
```

**Backend (ACTUAL):**
```
1. Usuario hace logout
   ├─ POST /api/auth/logout/
   ├─ Backend invalida token
   ├─ ❌ NO LIMPIA EL CARRITO
   └─ Carrito en BD sigue con 3 items

2. Estado después del logout
   ├─ BD: SELECT * FROM carts WHERE user_id = X
   │  └─ Devuelve carrito con 3 items
   └─ BD: SELECT * FROM cart_items WHERE cart_id = Y
      └─ Devuelve 3 items
```

---

### FASE 4: LOGIN NUEVAMENTE

**Frontend:**
```
1. Usuario hace login nuevamente
   ├─ POST /api/auth/login/
   ├─ Backend devuelve: {accessToken, user, refreshToken (cookie)}
   ├─ Frontend: useAuthStore.login(user, token)
   ├─ useSyncCart.fetchCartFromBackend() se llama
   │  ├─ GET /api/carrito/
   │  ├─ Backend devuelve: {items: [p1, p2, p3], total: X} ❌ PROBLEMA
   │  ├─ Frontend: useCartStore.setItems([p1, p2, p3])
   │  └─ localStorage['cart-storage'] = {items: [p1, p2, p3]}
   └─ ¡REAPARECEN LOS PRODUCTOS!

2. Estado después del login
   ├─ Frontend: useCartStore.items = [p1, p2, p3] ❌ FANTASMA
   ├─ Frontend: localStorage['cart-storage'] = {items: [p1, p2, p3]} ❌ FANTASMA
   └─ Backend: BD sigue con 3 items ❌ FANTASMA
```

**Backend:**
```
1. GET /api/carrito/
   ├─ Autenticación: IsAuthenticated ✅
   ├─ Query: Cart.objects.get_or_create(user=request.user)
   │  ├─ Busca: SELECT * FROM carts WHERE user_id = X
   │  ├─ Encuentra el carrito anterior (no fue eliminado)
   │  └─ Devuelve ese carrito
   ├─ Prefetch: items__product
   │  └─ SELECT * FROM cart_items WHERE cart_id = Y
   │     └─ Devuelve los 3 items anteriores
   └─ Serializa y devuelve {items: [p1, p2, p3]}
```

---

## 🎯 CAUSA RAÍZ IDENTIFICADA

### El Problema

1. **Backend:** El carrito NO se limpia en la BD cuando el usuario se desloguea
2. **Frontend:** NO llama a `DELETE /api/carrito/vaciar/` cuando se desloguea
3. **Resultado:** Cuando el usuario se loguea nuevamente, obtiene el carrito anterior

### Por qué sucede

```
Cart es OneToOneField con User
├─ Cada usuario tiene UN carrito único
├─ El carrito se crea con get_or_create()
├─ Si el carrito existe, se reutiliza
└─ Si el carrito NO se limpia, persiste en la BD
```

---

## 🔍 PUNTOS DE INVESTIGACIÓN ADICIONALES

### 1. ¿Hay caché involucrado?

**Encontrado en settings.py:**
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    },
    'sessions': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
```

**Análisis:**
- ✅ Redis está configurado
- ✅ Hay CacheManager para estadísticas
- ❌ El carrito NO está siendo cacheado (no hay @cache decorators)
- ❌ No hay cache_key para carrito

**Conclusión:** El caché NO es el problema

---

### 2. ¿Hay signals o hooks que limpien el carrito?

**Búsqueda:** `@receiver`, `post_save`, `post_delete` en models.py

**Encontrado:**
- ✅ Signals para invalidar caché de productos
- ✅ Signals para invalidar caché de pedidos
- ❌ NO hay signals para limpiar carrito al logout

**Conclusión:** No hay limpieza automática del carrito

---

### 3. ¿El endpoint vaciar funciona?

**Código del endpoint:**
```python
@action(detail=False, methods=['delete'], url_path='vaciar')
def vaciar(self, request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()  # ← Elimina todos los items
    serializer = CartSerializer(cart)
    return Response(serializer.data)
```

**Análisis:**
- ✅ El endpoint existe
- ✅ Elimina todos los items con `cart.items.all().delete()`
- ✅ Devuelve el carrito vacío
- ❌ El frontend NO lo llama

**Conclusión:** El endpoint funciona, pero no se usa

---

### 4. ¿Hay problema de timing o race conditions?

**Frontend flow:**
```
logout() → clearCart() → set({ isAuthenticated: false })
                            ↓
                      useSyncCart.useEffect() se dispara
                            ↓
                      if (!isAuthenticated) { clearCart() }
```

**Análisis:**
- ✅ El timing parece correcto
- ✅ Los useEffect se disparan en el orden correcto
- ❌ Pero el backend NO se limpia

**Conclusión:** No es un problema de timing en el frontend

---

### 5. ¿Hay problema de sesiones o autenticación?

**Backend authentication:**
```python
permission_classes = [permissions.IsAuthenticated]
```

**Análisis:**
- ✅ El endpoint requiere autenticación
- ✅ El usuario está autenticado
- ✅ El carrito se obtiene correctamente
- ❌ Pero el carrito anterior persiste

**Conclusión:** No es un problema de autenticación

---

## 📋 CHECKLIST DE INVESTIGACIÓN

- [x] Revisar arquitectura del carrito (frontend y backend)
- [x] Rastrear flujo completo de login → agregar → logout → login
- [x] Verificar si hay caché involucrado
- [x] Verificar si hay signals o hooks
- [x] Verificar si el endpoint vaciar funciona
- [x] Verificar si hay race conditions
- [x] Verificar autenticación
- [ ] Verificar si hay middleware que interfiera
- [ ] Verificar si hay serializers que cacheen datos
- [ ] Verificar logs del backend para entender qué sucede

---

## 🎯 CONCLUSIÓN PRELIMINAR

### Causa Raíz Confirmada

El carrito reaparece porque:

1. **Backend:** El carrito se guarda en la BD con los items
2. **Frontend:** NO llama a `DELETE /api/carrito/vaciar/` al logout
3. **Resultado:** La BD nunca se limpia
4. **Consecuencia:** Al login siguiente, el backend devuelve el carrito anterior

### Soluciones Posibles

**Opción A:** Frontend llama a `DELETE /api/carrito/vaciar/` en logout
- Pros: Simple, rápido
- Contras: Requiere cambio en frontend

**Opción B:** Backend limpia automáticamente al logout
- Pros: Automático, seguro
- Contras: Requiere cambio en backend

**Opción C:** Usar signal para limpiar al logout
- Pros: Automático, limpio
- Contras: Más complejo

**Opción D:** Usar middleware para limpiar
- Pros: Intercepta todos los logouts
- Contras: Más overhead

---

## 📊 RECOMENDACIÓN

**Usar Opción A + Opción C:**

1. **Frontend:** Llamar a `DELETE /api/carrito/vaciar/` en logout (rápido)
2. **Backend:** Agregar signal para limpiar carrito al logout (fallback)

Esto proporciona:
- ✅ Limpieza inmediata en el frontend
- ✅ Fallback automático en el backend
- ✅ Máxima seguridad

---

**Análisis completado:** 19 de Noviembre, 2025  
**Causa Raíz:** Backend no limpia carrito + Frontend no llama endpoint  
**Próximo paso:** Implementar solución después de aprobación del usuario
