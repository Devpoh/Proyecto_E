# ⏱️ ANÁLISIS DE TIMING DETALLADO

**Objetivo:** Entender exactamente cuándo ocurren los cambios

---

## 🔴 ESCENARIO: Usuario se desloguea y se loguea nuevamente

### Timeline Exacto

```
T=0ms: Usuario hace click en "Cerrar Sesión"
├─ logout() se ejecuta
│  ├─ T=0ms: localStorage.removeItem('cart-storage') ✅
│  ├─ T=1ms: useCartStore.getState().clearCart()
│  │  └─ localStorage.removeItem('cart-storage') ✅
│  ├─ T=2ms: set({ isAuthenticated: false, user: null, accessToken: null })
│  │  └─ Zustand se actualiza
│  └─ T=3ms: api.delete('/carrito/vaciar/') se envía (sin await)
│     └─ Solicitud en vuelo...
│
└─ Zustand notifica a todos los subscribers que isAuthenticated cambió

T=5ms: useSyncCart.useEffect() se dispara
├─ if (!isAuthenticated) { ✅ true
│  ├─ clearCart() se ejecuta
│  │  └─ localStorage limpio de nuevo
│  ├─ cartLoadedForUser.clear()
│  ├─ isCartLoading = false
│  └─ cartLoadPromise = null
│
└─ Componentes que usan useCartStore se re-renderizan
   └─ cartItemCount = 0

T=10ms: Usuario hace click en "Iniciar Sesión"
├─ Navega a /login
└─ Componentes se desmontan

T=50ms: Usuario ingresa credenciales y hace click en "Iniciar Sesión"
├─ loginApi.loginUser() se ejecuta
├─ POST /api/auth/login/ se envía
└─ Esperando respuesta...

T=100ms: Backend responde al login
├─ Devuelve: { accessToken: "...", user: {...} }
├─ useAuthStore.setLogin(token, user) se ejecuta
│  ├─ set({ isAuthenticated: true, user, accessToken })
│  └─ Zustand se actualiza
│
└─ Zustand notifica a todos los subscribers

T=105ms: useSyncCart.useEffect() se dispara (porque isAuthenticated cambió)
├─ if (isAuthenticated && user) { ✅ true
│  ├─ if (cartLoadedForUser.has(user.id)) { ✅ false (porque se limpió)
│  ├─ setTimeout(() => {
│  │  ├─ fetchCartFromBackend()
│  │  └─ cartLoadedForUser.add(user.id)
│  │ }, 300)
│  └─ Timer se inicia
│
└─ Componentes que usan useCartStore se re-renderizan
   └─ cartItemCount = 0 (porque localStorage está limpio)

T=405ms: Timer se ejecuta (300ms después)
├─ fetchCartFromBackend() se ejecuta
│  ├─ isCartLoading = true
│  ├─ GET /api/carrito/ se envía
│  └─ Esperando respuesta...
│
└─ Componentes se re-renderizan
   └─ cartItemCount = 0 (todavía)

T=450ms: Backend responde a GET /api/carrito/
├─ Devuelve: { items: [], total: 0 } ← Carrito vacío ✅
├─ setItems([]) se ejecuta
│  ├─ set({ items: [] })
│  ├─ const { isAuthenticated } = useAuthStore.getState()
│  ├─ isAuthenticated = true ✅
│  └─ saveToLocalStorage(get()) ✅ Guarda carrito vacío
│
└─ Componentes se re-renderizan
   └─ cartItemCount = 0 ✅

RESULTADO: ✅ CARRITO VACÍO
```

---

## 🔴 PERO SI HAY UNA SOLICITUD EN VUELO...

### Escenario: GET /api/carrito/ se envía DURANTE logout

```
T=0ms: logout() se ejecuta
├─ localStorage.removeItem('cart-storage')
├─ set({ isAuthenticated: false })
└─ api.delete('/carrito/vaciar/') se envía

T=5ms: useSyncCart.useEffect() se dispara
├─ clearCart()
└─ cartLoadedForUser.clear()

T=50ms: Usuario se loguea nuevamente
├─ setLogin(token, user)
└─ set({ isAuthenticated: true })

T=55ms: useSyncCart.useEffect() se dispara
├─ setTimeout(() => fetchCartFromBackend(), 300)
└─ Timer se inicia

T=100ms: PERO AQUÍ ESTÁ EL PROBLEMA
├─ Si hay una solicitud GET /api/carrito/ que se envió ANTES del logout
├─ Y esa solicitud llega AHORA (después del logout pero antes del login)
├─ Entonces setItems() se ejecuta
│  ├─ const { isAuthenticated } = useAuthStore.getState()
│  ├─ isAuthenticated = false (porque todavía no se logueó)
│  └─ NO guarda en localStorage ✅
│
└─ Pero si la solicitud llega DESPUÉS del login:
   ├─ const { isAuthenticated } = useAuthStore.getState()
   ├─ isAuthenticated = true
   └─ saveToLocalStorage(get()) ✅ Guarda en localStorage

T=405ms: fetchCartFromBackend() se ejecuta
├─ GET /api/carrito/ se envía
└─ Esperando respuesta...

T=450ms: Backend responde
├─ Devuelve: { items: [], total: 0 }
├─ setItems([]) se ejecuta
│  ├─ isAuthenticated = true
│  └─ saveToLocalStorage(get()) ✅ Guarda carrito vacío
│
└─ ✅ CARRITO VACÍO
```

---

## 🎯 EL PROBLEMA REAL

El problema es que `useCartStore` se REINICIALIZA cuando se monta un componente que lo usa.

Cuando se reinicializa, carga desde localStorage:

```typescript
const loadFromLocalStorage = () => {
  const saved = localStorage.getItem('cart-storage');
  if (saved) {
    return JSON.parse(saved);
  }
  return { items: [], pending: {} };
};

const initialState = loadFromLocalStorage();  // ← Se ejecuta al crear el store
```

Si localStorage tiene datos, los carga INMEDIATAMENTE, antes de que `fetchCartFromBackend()` se ejecute.

---

## ✅ SOLUCIÓN

El problema es que `useCartStore` carga desde localStorage al inicializarse.

**Opción 1:** No cargar desde localStorage al inicializarse
- Ventaja: Evita carrito fantasma
- Desventaja: Pierde datos si se recarga la página

**Opción 2:** Cargar desde localStorage SOLO si está autenticado
- Ventaja: Mantiene datos al recargar
- Desventaja: Más complejo

**Opción 3:** Limpiar localStorage INMEDIATAMENTE al logout
- Ventaja: Simple
- Desventaja: Ya se hace

**Opción 4:** RECOMENDADA - Usar AbortController para cancelar solicitudes al logout
- Ventaja: Evita que se guarden datos durante logout
- Desventaja: Más complejo

---

**Análisis completado:** 19 de Noviembre, 2025
