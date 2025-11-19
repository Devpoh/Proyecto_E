# 🔴 ANÁLISIS: PRODUCTOS DESAPARECEN AL RECARGAR PÁGINA

## Fecha: 10 de Noviembre 2025, 14:30 UTC-05:00
## Estado: INVESTIGACIÓN

---

## 📋 PROBLEMA REPORTADO

**Síntoma:** Cuando se recarga la página, los productos del carrito desaparecen hasta que no se agrega algo nuevo.

**Pasos para reproducir:**
1. Agregar productos al carrito
2. Recargar la página (F5)
3. Productos desaparecen
4. Agregar un nuevo producto
5. Productos reaparecen

---

## 🔍 ANÁLISIS PROFUNDO

### Problema 1: Optimización de carga única (Línea 483-502)

**Código actual:**
```typescript
useEffect(() => {
  if (isAuthenticated && user) {
    // Verificar si ya se cargó el carrito en esta sesión
    const cartLoadedKey = `cart_loaded_${user.id}`;
    const alreadyLoaded = sessionStorage.getItem(cartLoadedKey);
    
    if (alreadyLoaded) {
      return; // Ya se cargó, no volver a cargar ← PROBLEMA
    }
    
    // Esperar un poco para asegurar que el token está guardado
    const timer = setTimeout(() => {
      fetchCartFromBackend();
      // Marcar como cargado
      sessionStorage.setItem(cartLoadedKey, 'true');
    }, 300);

    return () => clearTimeout(timer);
  }
}, [isAuthenticated, user, fetchCartFromBackend]);
```

**PROBLEMA:**
- La optimización marca `cartLoadedKey = 'true'` en sessionStorage
- Si se recarga la página, el sessionStorage se mantiene (no se limpia)
- El `useEffect` ve que ya está marcado como cargado y NO carga el carrito
- Pero el carrito local está vacío (porque se recargó la página)
- Resultado: Carrito vacío

**Flujo problemático:**
```
1. Usuario agrega productos → Carrito: [A, B, C]
2. sessionStorage.setItem('cart_loaded_1', 'true')
3. Usuario recarga página (F5)
4. sessionStorage persiste (no se limpia)
5. useEffect ve 'cart_loaded_1' = 'true'
6. useEffect retorna sin cargar carrito
7. Carrito local: [] (vacío porque se recargó)
8. Usuario ve carrito vacío
```

### Problema 2: sessionStorage persiste entre recargas

**Comportamiento de sessionStorage:**
- Se limpia cuando se cierra la pestaña
- Se mantiene cuando se recarga la página (F5)
- Se mantiene cuando se navega entre páginas

**En nuestro caso:**
- Al recargar, sessionStorage se mantiene
- Pero el estado local de Zustand se reinicia (vacío)
- Desincronización: sessionStorage dice "ya cargado", pero el carrito está vacío

---

## ✅ SOLUCIONES PROPUESTAS

### Solución 1: Remover la optimización (SIMPLE)

**Cambio:**
```typescript
useEffect(() => {
  if (isAuthenticated && user) {
    // Siempre cargar el carrito del backend
    fetchCartFromBackend();
  }
}, [isAuthenticated, user, fetchCartFromBackend]);
```

**Ventajas:**
- ✅ Simple
- ✅ Siempre sincronizado
- ✅ Funciona correctamente

**Desventajas:**
- ⚠️ Carga el carrito cada vez que `fetchCartFromBackend` cambia
- ⚠️ Puede causar N+1 queries si `fetchCartFromBackend` se recrea frecuentemente

### Solución 2: Usar localStorage en lugar de sessionStorage (RECOMENDADO)

**Idea:**
- sessionStorage se limpia al cerrar pestaña
- Pero persiste entre recargas
- Usar localStorage para persistencia entre sesiones
- Pero limpiar cuando se cierra sesión

**Cambio:**
```typescript
useEffect(() => {
  if (isAuthenticated && user) {
    // Usar localStorage en lugar de sessionStorage
    const cartLoadedKey = `cart_loaded_${user.id}`;
    const alreadyLoaded = localStorage.getItem(cartLoadedKey);
    
    if (alreadyLoaded) {
      return; // Ya se cargó en esta sesión
    }
    
    const timer = setTimeout(() => {
      fetchCartFromBackend();
      localStorage.setItem(cartLoadedKey, 'true');
    }, 300);

    return () => clearTimeout(timer);
  }
}, [isAuthenticated, user, fetchCartFromBackend]);

// En logout, limpiar la flag
logout: () => {
  // ... código existente ...
  localStorage.removeItem(`cart_loaded_${user.id}`);  // ← Agregar esto
}
```

**Ventajas:**
- ✅ Persiste entre recargas
- ✅ Se limpia al logout
- ✅ Evita N+1 queries

**Desventajas:**
- ⚠️ Requiere cambio en logout

### Solución 3: Usar un flag en memoria (MÁS SEGURO)

**Idea:**
- Usar una variable global en lugar de sessionStorage
- Se reinicia al recargar (lo que queremos)
- Evita problemas de persistencia

**Cambio:**
```typescript
// Variable global (se reinicia al recargar)
let cartLoadedForUser: Set<number> = new Set();

useEffect(() => {
  if (isAuthenticated && user) {
    // Verificar si ya se cargó en esta sesión
    if (cartLoadedForUser.has(user.id)) {
      return; // Ya se cargó
    }
    
    const timer = setTimeout(() => {
      fetchCartFromBackend();
      cartLoadedForUser.add(user.id);
    }, 300);

    return () => clearTimeout(timer);
  }
}, [isAuthenticated, user, fetchCartFromBackend]);
```

**Ventajas:**
- ✅ Se reinicia al recargar (correcto)
- ✅ Evita N+1 queries en la misma sesión
- ✅ No requiere limpiar en logout

**Desventajas:**
- ⚠️ Se reinicia al recargar (puede ser deseado o no)

---

## 🎯 SOLUCIÓN FINAL RECOMENDADA

**Combinar Solución 1 + Solución 3:**

1. **Remover la optimización de sessionStorage**
   - Simplifica el código
   - Evita desincronización

2. **Agregar un flag en memoria para evitar N+1 queries**
   - Se reinicia al recargar (correcto)
   - Evita múltiples cargas en la misma sesión

**Código:**
```typescript
// Variable global (se reinicia al recargar)
let cartLoadedForUser: Set<number> = new Set();

useEffect(() => {
  if (isAuthenticated && user) {
    // Verificar si ya se cargó en esta sesión
    if (cartLoadedForUser.has(user.id)) {
      return; // Ya se cargó
    }
    
    // Esperar un poco para asegurar que el token está guardado
    const timer = setTimeout(() => {
      fetchCartFromBackend();
      cartLoadedForUser.add(user.id);
    }, 300);

    return () => clearTimeout(timer);
  }
}, [isAuthenticated, user, fetchCartFromBackend]);
```

---

## 🧪 VERIFICACIÓN

### Test 1: Carga inicial
```
1. Agregar productos: [A, B, C]
2. Carrito muestra: [A, B, C] ✅
```

### Test 2: Recarga de página
```
1. Carrito: [A, B, C]
2. Recargar página (F5)
3. Carrito muestra: [A, B, C] ✅
```

### Test 3: Agregar después de recarga
```
1. Carrito: [A, B, C]
2. Recargar página (F5)
3. Carrito muestra: [A, B, C] ✅
4. Agregar D
5. Carrito muestra: [A, B, C, D] ✅
```

---

## 📁 ARCHIVOS A MODIFICAR

- `frontend/electro_isla/src/shared/hooks/useSyncCart.ts`
  - Línea 32-34: Agregar variable global `cartLoadedForUser`
  - Línea 483-502: Cambiar useEffect para usar flag en memoria

---

*Análisis realizado por: Cascade AI Assistant*
*Fecha: 10 de Noviembre 2025, 14:30 UTC-05:00*
