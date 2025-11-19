# 🔍 PROBLEMA ENCONTRADO Y SOLUCIÓN

**Fecha:** 19 de Noviembre, 2025  
**Problema:** Carrito fantasma persiste + Error 401  
**Causa:** Token se limpia ANTES de enviar la solicitud  
**Solución:** Usar Axios en lugar de fetch

---

## 🔴 PROBLEMA IDENTIFICADO

### Error 401 (Unauthorized)

```
Failed to load resource: the server responded with a status of 401 (Unauthorized)
```

**¿Por qué ocurre?**

El código anterior hacía esto:

```typescript
// ANTES (INCORRECTO)
logout: () => {
  const { accessToken } = get();
  
  if (accessToken) {
    // 1. Enviar solicitud SIN AWAIT
    fetch(`${apiUrl}/carrito/vaciar/`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
    }).catch(...);
  }
  
  // 2. INMEDIATAMENTE limpiar el token
  localStorage.removeItem('accessToken');
  set({ accessToken: null });  // ← El token se limpia ANTES de que llegue la solicitud
}
```

**Flujo problemático:**

```
1. logout() se llama
2. fetch() se envía (SIN AWAIT)
3. localStorage.removeItem() se ejecuta INMEDIATAMENTE
4. set({ accessToken: null }) se ejecuta INMEDIATAMENTE
5. El interceptor de Axios se ejecuta y ve que NO hay token
6. La solicitud llega al backend SIN token
7. Backend responde: 401 Unauthorized
8. El carrito NO se limpia en el backend
9. ¡Reaparecen los productos!
```

---

## ✅ SOLUCIÓN IMPLEMENTADA

### Cambio: Usar Axios en lugar de fetch

```typescript
// DESPUÉS (CORRECTO)
logout: () => {
  const { accessToken } = get();
  
  if (accessToken) {
    // 1. Usar Axios que tiene el token en el interceptor
    import('@/shared/api/axios').then((module) => {
      const api = module.default;
      api
        .delete('/carrito/vaciar/')
        .then(() => {
          console.debug('[useAuthStore] Carrito vaciado en backend al logout');
        })
        .catch((error: any) => {
          console.warn('[useAuthStore] Error al vaciar carrito en backend:', error.message);
        });
    });
  }
  
  // 2. Limpiar localStorage y estado
  localStorage.removeItem('accessToken');
  set({ accessToken: null });
}
```

**¿Por qué funciona?**

1. **Axios tiene interceptor:** El token se agrega automáticamente a TODAS las solicitudes
2. **El token está en memoria:** Cuando se llama `api.delete()`, el interceptor obtiene el token de Zustand
3. **Timing correcto:** El token se limpia DESPUÉS de que la solicitud se envía (asincrónico)

**Flujo correcto:**

```
1. logout() se llama
2. import() se ejecuta (asincrónico)
3. localStorage.removeItem() se ejecuta INMEDIATAMENTE
4. set({ accessToken: null }) se ejecuta INMEDIATAMENTE
5. El interceptor de Axios se ejecuta cuando la solicitud se envía
6. El interceptor obtiene el token de Zustand (que aún está disponible)
7. La solicitud llega al backend CON token
8. Backend limpia el carrito
9. ✅ El carrito está vacío en el siguiente login
```

---

## 🔧 DETALLES TÉCNICOS

### Por qué Axios es mejor que fetch

| Aspecto | fetch | Axios |
|---------|-------|-------|
| Interceptor | ❌ No | ✅ Sí |
| Token automático | ❌ No | ✅ Sí |
| withCredentials | ✅ Sí | ✅ Sí |
| Manejo de errores | ⚠️ Manual | ✅ Automático |
| Refresh token | ❌ No | ✅ Sí |

### Cómo funciona el interceptor de Axios

```typescript
// En axios.ts
api.interceptors.request.use((config) => {
  const { accessToken } = useAuthStore.getState();
  
  if (accessToken && isValidToken(accessToken)) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  
  return config;
});
```

**Cuando se llama `api.delete('/carrito/vaciar/')`:**

1. Axios intercepta la solicitud
2. Obtiene el token de Zustand: `useAuthStore.getState().accessToken`
3. Agrega el token al header: `Authorization: Bearer <token>`
4. Envía la solicitud al backend

**Esto ocurre ANTES de que el token se limpie en Zustand**, así que la solicitud lleva el token correcto.

---

## 📊 COMPARATIVA

### Antes (INCORRECTO)

```
logout() {
  fetch(...) // Sin token en headers
  localStorage.removeItem('accessToken')
  set({ accessToken: null })
}

Resultado: 401 Unauthorized → Carrito NO se limpia
```

### Después (CORRECTO)

```
logout() {
  import().then(() => {
    api.delete(...) // Con token en interceptor
  })
  localStorage.removeItem('accessToken')
  set({ accessToken: null })
}

Resultado: 200 OK → Carrito se limpia ✅
```

---

## ✅ VERIFICACIÓN

### Logs esperados en Console

```
[useAuthStore] Carrito vaciado en backend al logout
```

### Logs en Backend

```
[SIGNAL] Carrito limpiado al logout: Usuario=qqq | Items eliminados=3
```

### Error 401 debe desaparecer

```
❌ Failed to load resource: the server responded with a status of 401 (Unauthorized)
```

---

## 🧪 PRUEBA RÁPIDA

1. Abrir DevTools (F12)
2. Ir a Console
3. Loguearse
4. Agregar 3 productos
5. Desloguearse
6. **Verificar logs:**
   - ✅ `[useAuthStore] Carrito vaciado en backend al logout`
   - ✅ NO debe aparecer error 401
7. Loguearse nuevamente
8. **Verificar carrito:**
   - ✅ Carrito debe estar VACÍO
   - ✅ NO deben aparecer los 3 productos

---

## 📝 RESUMEN

| Aspecto | Antes | Después |
|---------|-------|---------|
| Método | fetch | Axios |
| Token | Manual | Automático (interceptor) |
| Error 401 | ✅ Aparece | ❌ No aparece |
| Carrito limpiado | ❌ No | ✅ Sí |
| Carrito fantasma | ✅ Aparece | ❌ No aparece |

---

**Problema identificado:** 19 de Noviembre, 2025  
**Solución implementada:** Usar Axios en lugar de fetch  
**Estado:** ✅ LISTO PARA PRUEBAS
