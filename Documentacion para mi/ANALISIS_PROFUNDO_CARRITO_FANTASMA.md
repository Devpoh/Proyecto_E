# 🔍 ANÁLISIS PROFUNDO: Carrito Fantasma - Causa Raíz

## Problema Identificado

El carrito fantasma persiste porque hay un **flag global que nunca se limpia**.

---

## 🔴 CAUSA RAÍZ

### En `useSyncCart.ts` línea 38:

```typescript
// OPTIMIZACIÓN: Rastrear usuarios cuyo carrito ya se cargó en esta sesión
// Se reinicia al recargar la página (lo que queremos)
let cartLoadedForUser: Set<number> = new Set();
```

Este flag es **GLOBAL** y nunca se limpia cuando el usuario se desloguea.

---

## 📊 FLUJO PROBLEMÁTICO

```
SESIÓN 1:
1. Usuario A se loguea (id=1)
   ├─ cartLoadedForUser = Set() (vacío)
   ├─ fetchCartFromBackend() se llama ✅
   ├─ cartLoadedForUser.add(1) → Set(1)
   └─ Carrito cargado del backend ✅

2. Usuario A agrega productos
   ├─ useCartStore.items = [p1, p2, p3]
   ├─ localStorage['cart-storage'] = {items: [p1, p2, p3]}
   └─ Carrito sincronizado ✅

3. Usuario A se desloguea
   ├─ clearCart() se llama
   ├─ useCartStore.items = []
   ├─ localStorage.removeItem('cart-storage')
   └─ cartLoadedForUser = Set(1) ← ⚠️ NO SE LIMPIA

SESIÓN 2:
4. Usuario A se loguea nuevamente
   ├─ isAuthenticated = true
   ├─ cartLoadedForUser.has(1) = TRUE ← ⚠️ PROBLEMA
   ├─ fetchCartFromBackend() NO se llama ❌
   └─ Carrito del backend NO se obtiene

5. useCartStore se inicializa
   ├─ loadFromLocalStorage() se llama
   ├─ localStorage['cart-storage'] = null (fue limpiado)
   ├─ Retorna { items: [], pending: {} }
   └─ Carrito vacío en memoria ✅

6. Usuario agrega 1 producto
   ├─ useCartStore.items = [p4]
   ├─ localStorage['cart-storage'] = {items: [p4]}
   └─ Carrito tiene 1 producto ✅

7. Usuario recarga página
   ├─ useCartStore se reinicializa
   ├─ loadFromLocalStorage() se llama
   ├─ localStorage['cart-storage'] = {items: [p4]}
   ├─ useCartStore.items = [p4]
   └─ Carrito tiene 1 producto ✅

PERO ESPERA... ¿DE DÓNDE VIENEN LOS PRODUCTOS FANTASMA?
```

---

## 🔍 INVESTIGACIÓN ADICIONAL

El problema es más sutil. Voy a rastrear el localStorage:

### Paso 1: Usuario se desloguea
```typescript
// En useSyncCart.ts línea 487
if (!isAuthenticated) {
  clearCart();  // ← Llama a useCartStore.clearCart()
}
```

### Paso 2: useCartStore.clearCart()
```typescript
// En useCartStore.ts línea 137-140
clearCart: () => {
  set({ items: [], pending: {} });
  localStorage.removeItem('cart-storage');  // ← Se remueve
}
```

### Paso 3: Usuario se loguea nuevamente
```typescript
// En useCartStore.ts línea 59-73
const loadFromLocalStorage = () => {
  try {
    const saved = localStorage.getItem('cart-storage');  // ← null
    if (saved) {
      // No entra aquí
    }
  } catch (error) {
    console.error('[useCartStore] Error cargando del localStorage:', error);
  }
  return { items: [], pending: {} };  // ← Retorna vacío
};
```

---

## 🤔 PERO ENTONCES... ¿POR QUÉ REAPARECEN?

Hay OTRO localStorage que no estamos limpiando:

### En `useCartSync.ts` línea 220:
```typescript
// 2. Guardar en localStorage como backup
localStorage.setItem('cart-backup', JSON.stringify(newPending));
```

**¡AQUÍ ESTÁ!** Hay un `cart-backup` en localStorage que NO se limpia cuando se desloguea.

---

## 🎯 SOLUCIÓN

Necesitamos limpiar TODOS los localStorage relacionados con el carrito:

1. `cart-storage` - ✅ Se limpia en `clearCart()`
2. `cart-backup` - ❌ NO se limpia
3. Resetear el flag `cartLoadedForUser` - ❌ NO se resetea

---

## 📋 CHECKLIST DE LIMPIEZA

Cuando el usuario se desloguea, limpiar:
- [ ] `localStorage['cart-storage']`
- [ ] `localStorage['cart-backup']`
- [ ] Flag `cartLoadedForUser` (remover usuario)
- [ ] Flag `isCartLoading`
- [ ] Flag `cartLoadPromise`

---

## 🔧 SOLUCIÓN PROPUESTA

### Opción 1: Limpiar en `clearCart()`
```typescript
clearCart: () => {
  set({ items: [], pending: {} });
  localStorage.removeItem('cart-storage');
  localStorage.removeItem('cart-backup');  // ← AGREGAR
}
```

### Opción 2: Limpiar en `useSyncCart` cuando se desloguea
```typescript
useEffect(() => {
  if (!isAuthenticated) {
    clearCart();
    localStorage.removeItem('cart-backup');  // ← AGREGAR
    // Resetear flags globales
    isCartLoading = false;
    cartLoadPromise = null;
    cartLoadedForUser.clear();  // ← AGREGAR
  }
}, [isAuthenticated, clearCart]);
```

### Opción 3: Ambas (más seguro)
```typescript
// En useCartStore.clearCart()
clearCart: () => {
  set({ items: [], pending: {} });
  localStorage.removeItem('cart-storage');
  localStorage.removeItem('cart-backup');  // ← AGREGAR
}

// En useSyncCart useEffect
useEffect(() => {
  if (!isAuthenticated) {
    clearCart();
    // Resetear flags globales
    cartLoadedForUser.clear();  // ← AGREGAR
  }
}, [isAuthenticated, clearCart]);
```

---

## ✅ RECOMENDACIÓN

**Usar Opción 3** (ambas) porque:
1. Es más seguro (limpia en dos niveles)
2. No depende de que se llame desde un solo lugar
3. Maneja edge cases

---

## 🧪 VERIFICACIÓN

Después de implementar:

1. Loguearse
2. Agregar 3 productos
3. Desloguearse
4. Verificar en DevTools:
   - `localStorage['cart-storage']` → null ✅
   - `localStorage['cart-backup']` → null ✅
5. Loguearse nuevamente
6. Verificar:
   - Carrito vacío ✅
7. Agregar 1 producto
8. Verificar:
   - Carrito tiene solo 1 producto ✅
   - NO reaparecen productos ✅

---

**Análisis completado:** 18 de Noviembre, 2025  
**Causa Raíz:** `localStorage['cart-backup']` no se limpia + flag global no se resetea  
**Solución:** Limpiar ambos localStorage + resetear flags
