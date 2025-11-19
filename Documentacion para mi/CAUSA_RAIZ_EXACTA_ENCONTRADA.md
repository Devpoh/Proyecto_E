# 🎯 CAUSA RAÍZ EXACTA ENCONTRADA

**Fecha:** 19 de Noviembre, 2025  
**Problema:** Carrito fantasma persiste  
**Causa Raíz:** RACE CONDITION en el timing de logout/login

---

## 🔴 EL PROBLEMA EXACTO

### Flujo Incorrecto (Actual)

```
LOGOUT:
1. logout() se ejecuta en useAuthStore
   ├─ localStorage.removeItem('cart-storage') ✅
   ├─ useCartStore.getState().clearCart() ✅
   └─ set({ isAuthenticated: false }) ✅

2. useSyncCart.useEffect() se dispara
   ├─ if (!isAuthenticated) { clearCart() } ✅
   └─ cartLoadedForUser.clear() ✅

3. PERO AQUÍ ESTÁ EL PROBLEMA:
   ├─ fetchCartFromBackend() se llama DURANTE el logout
   ├─ fetchCartFromBackend() hace GET /api/carrito/
   ├─ Backend devuelve: {items: [p1, p2, p3]}
   ├─ setItems([p1, p2, p3]) se ejecuta
   ├─ localStorage['cart-storage'] = {items: [p1, p2, p3]} ← AQUÍ!
   └─ El carrito se guarda en localStorage DESPUÉS de limpiarse

LOGIN (siguiente):
4. useCartStore se reinicializa
   ├─ loadFromLocalStorage() se llama
   ├─ localStorage['cart-storage'] = {items: [p1, p2, p3]}
   ├─ Carga los 3 productos
   └─ ¡CARRITO FANTASMA!
```

---

## 🔍 ANÁLISIS DETALLADO

### El Culpable: `useCartStore` Initialization

**Archivo:** `useCartStore.ts` línea 59-75

```typescript
const loadFromLocalStorage = () => {
  try {
    const saved = localStorage.getItem('cart-storage');
    if (saved) {
      const parsed = JSON.parse(saved);
      return {
        items: parsed.items || [],
        pending: parsed.pending || {},
      };
    }
  } catch (error) {
    console.error('[useCartStore] Error cargando del localStorage:', error);
  }
  return { items: [], pending: {} };
};

const initialState = loadFromLocalStorage();  // ← Se ejecuta CADA VEZ que se monta
```

**El problema:**
- `useCartStore` se reinicializa CADA VEZ que se monta un componente
- Cuando se reinicializa, carga desde localStorage
- Si localStorage tiene datos, los carga

### El Timing del Problema

```
LOGOUT (t=0ms):
├─ logout() se ejecuta
│  ├─ localStorage.removeItem('cart-storage') ✅
│  └─ set({ isAuthenticated: false })
│
└─ isAuthenticated = false (Zustand actualizado)

SIMULTÁNEAMENTE (t=5ms):
├─ useSyncCart.useEffect() se dispara
│  ├─ if (!isAuthenticated) { clearCart() } ✅
│  └─ cartLoadedForUser.clear() ✅
│
└─ Pero fetchCartFromBackend() ya se estaba ejecutando...

MIENTRAS TANTO (t=10ms):
├─ fetchCartFromBackend() continúa ejecutándose
│  ├─ GET /api/carrito/ (solicitud en vuelo)
│  └─ Esperando respuesta del backend...

BACKEND RESPONDE (t=100ms):
├─ Devuelve: {items: [p1, p2, p3]}
│
└─ setItems([p1, p2, p3]) se ejecuta
   ├─ set({ items: [p1, p2, p3] })
   └─ localStorage['cart-storage'] = {items: [p1, p2, p3]} ← AQUÍ!

LOGIN (t=200ms):
├─ useCartStore se reinicializa
│  ├─ loadFromLocalStorage()
│  ├─ localStorage['cart-storage'] = {items: [p1, p2, p3]}
│  └─ ¡CARRITO FANTASMA!
```

---

## 🎯 POR QUÉ OCURRE

### Causa 1: fetchCartFromBackend() se llama DURANTE logout

**Ubicación:** `useSyncCart.ts` línea 498-515

```typescript
useEffect(() => {
  if (isAuthenticated && user) {
    // Cuando isAuthenticated = false, este useEffect se limpia
    // PERO la solicitud que ya estaba en vuelo continúa
    
    const timer = setTimeout(() => {
      fetchCartFromBackend();  // ← Esta solicitud puede estar en vuelo
      cartLoadedForUser.add(user.id);
    }, 300);

    return () => clearTimeout(timer);
  }
}, [isAuthenticated, user, fetchCartFromBackend]);
```

**El problema:**
- Cuando `isAuthenticated` cambia a false, el useEffect se limpia
- PERO si `fetchCartFromBackend()` ya estaba en vuelo, continúa
- La solicitud GET llega al backend
- El backend devuelve el carrito
- `setItems()` se ejecuta y guarda en localStorage

### Causa 2: setItems() guarda en localStorage

**Ubicación:** `useCartStore.ts` línea 85-89

```typescript
setItems: (items: CartItem[]) => {
  set({ items });
  // Guardar en localStorage
  saveToLocalStorage(get());  // ← Guarda en localStorage
},
```

**El problema:**
- `setItems()` siempre guarda en localStorage
- No verifica si el usuario está logueado
- Si se ejecuta durante logout, guarda los datos que se acaban de limpiar

### Causa 3: useCartStore se reinicializa al login

**Ubicación:** `useCartStore.ts` línea 57-75

```typescript
export const useCartStore = create<CartState>((set, get) => {
  const loadFromLocalStorage = () => {
    // Carga desde localStorage
  };

  const initialState = loadFromLocalStorage();  // ← Se ejecuta al crear el store
  
  return {
    items: initialState.items,  // ← Carga los datos de localStorage
    // ...
  };
});
```

**El problema:**
- Cada vez que se monta un componente que usa `useCartStore`, se reinicializa
- La reinicialización carga desde localStorage
- Si localStorage tiene datos, los carga

---

## 🔧 SOLUCIÓN

### Opción 1: Cancelar fetchCartFromBackend() al logout

```typescript
// En useSyncCart.ts
useEffect(() => {
  if (isAuthenticated && user) {
    const controller = new AbortController();
    const timer = setTimeout(() => {
      fetchCartFromBackend(controller.signal);
      cartLoadedForUser.add(user.id);
    }, 300);

    return () => {
      clearTimeout(timer);
      controller.abort();  // ← Cancelar si se desloguea
    };
  }
}, [isAuthenticated, user, fetchCartFromBackend]);
```

**Ventaja:** Evita que se ejecute fetchCartFromBackend() durante logout  
**Desventaja:** Más complejo

### Opción 2: No guardar en localStorage si no está autenticado

```typescript
// En useCartStore.ts
setItems: (items: CartItem[]) => {
  set({ items });
  // Solo guardar si está autenticado
  const { isAuthenticated } = useAuthStore.getState();
  if (isAuthenticated) {
    saveToLocalStorage(get());
  }
},
```

**Ventaja:** Simple y directo  
**Desventaja:** Requiere verificar autenticación en cada setItems()

### Opción 3: Limpiar localStorage DESPUÉS de que se cargue el carrito

```typescript
// En logout()
logout: () => {
  // NO limpiar localStorage aquí
  // Dejar que useSyncCart lo haga
  
  // Limpiar Zustand
  useCartStore.getState().clearCart();
  
  // Limpiar estado
  set({ isAuthenticated: false, user: null, accessToken: null });
}

// En useSyncCart.ts useEffect
useEffect(() => {
  if (!isAuthenticated) {
    clearCart();
    // Limpiar localStorage DESPUÉS de que se complete clearCart()
    localStorage.removeItem('cart-storage');
    localStorage.removeItem('cart-backup');
    cartLoadedForUser.clear();
  }
}, [isAuthenticated, clearCart]);
```

**Ventaja:** Garantiza que se limpia después  
**Desventaja:** Duplica limpieza

### Opción 4: RECOMENDADA - Usar AbortController + No guardar si no autenticado

```typescript
// Combinar Opción 1 + Opción 2
// 1. Cancelar fetchCartFromBackend() al logout
// 2. No guardar en localStorage si no está autenticado
```

---

## ✅ RECOMENDACIÓN FINAL

**Usar Opción 4 (Combinada):**

1. **En `useSyncCart.ts`:** Usar AbortController para cancelar solicitudes al logout
2. **En `useCartStore.ts`:** Verificar autenticación antes de guardar en localStorage

Esto garantiza:
- ✅ Las solicitudes se cancelan al logout
- ✅ Los datos no se guardan en localStorage si no está autenticado
- ✅ El carrito se limpia correctamente
- ✅ No hay race conditions

---

**Análisis completado:** 19 de Noviembre, 2025  
**Causa Raíz:** RACE CONDITION en timing de logout/login  
**Solución:** Opción 4 (AbortController + Verificación de autenticación)  
**Estado:** Listo para implementar
