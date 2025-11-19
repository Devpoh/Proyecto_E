# 🧪 PRUEBAS FINALES - Carrito Fantasma

**Objetivo:** Verificar que el carrito fantasma está completamente resuelto  
**Fecha:** 19 de Noviembre, 2025  
**Estado:** ✅ LISTO PARA PRUEBAS

---

## 📋 CHECKLIST DE PRUEBAS

### ✅ Prueba 1: Logout y Login Básico

**Objetivo:** Verificar que el carrito se vacía al logout y permanece vacío al login

```
1. Abre la aplicación
2. Logúeate con tu usuario
3. Agrega 3-4 productos al carrito
4. Verifica que el carrito muestra los productos
5. Deslogúeate
   ├─ Verifica backend logs: [LOGOUT_CART_CLEARED] Usuario=qqq | Items eliminados=X
   ├─ Verifica que NO hay error 401 en DELETE /api/carrito/vaciar/
   └─ Verifica que localStorage está limpio (F12 → Application → localStorage)
6. Logúeate nuevamente
7. ✅ RESULTADO ESPERADO: Carrito está VACÍO
```

---

### ✅ Prueba 2: Agregar Después de Logout

**Objetivo:** Verificar que no hay productos fantasma después de logout

```
1. Logúeate
2. Agrega 5 productos
3. Deslogúeate
4. Logúeate nuevamente
5. Agrega 1 producto NUEVO
6. ✅ RESULTADO ESPERADO: Carrito tiene SOLO 1 producto (no 6)
```

---

### ✅ Prueba 3: Recargar Página Después de Logout

**Objetivo:** Verificar que recargar no trae productos fantasma

```
1. Logúeate
2. Agrega 3 productos
3. Deslogúeate
4. Recarga la página (F5)
5. Logúeate nuevamente
6. ✅ RESULTADO ESPERADO: Carrito está VACÍO
```

---

### ✅ Prueba 4: Múltiples Logout/Login

**Objetivo:** Verificar que funciona correctamente en múltiples ciclos

```
1. Logúeate
2. Agrega 2 productos
3. Deslogúeate
4. Logúeate
5. Verifica carrito vacío ✅
6. Agrega 3 productos
7. Deslogúeate
8. Logúeate
9. ✅ RESULTADO ESPERADO: Carrito está VACÍO (no tiene los 3 productos)
```

---

### ✅ Prueba 5: Verificar Logs del Backend

**Objetivo:** Verificar que el backend está limpiando correctamente

```
1. Abre la consola del backend
2. Logúeate
3. Agrega 4 productos
4. Deslogúeate
5. Busca en los logs:
   ├─ [LOGOUT_CART_CLEARED] Usuario: qqq | Items eliminados: 4 ✅
   ├─ [LOGOUT_SUCCESS] Usuario: qqq | IP: 127.0.0.1 ✅
   ├─ [REFRESH_TOKENS_REVOKED] Usuario: qqq | IP: 127.0.0.1 ✅
   ├─ POST /api/auth/logout/ HTTP/1.1" 200 28 ✅
   └─ NO debe haber: DELETE /api/carrito/vaciar/ HTTP/1.1" 401 ✅
```

---

### ✅ Prueba 6: Verificar localStorage

**Objetivo:** Verificar que localStorage se limpia correctamente

```
1. Abre DevTools (F12)
2. Logúeate
3. Agrega 3 productos
4. Verifica en Application → localStorage:
   ├─ cart-storage: { items: [...], pending: {} } ✅
   └─ auth-storage: { isAuthenticated: true, ... } ✅
5. Deslogúeate
6. Verifica que localStorage está limpio:
   ├─ cart-storage: NO EXISTE ✅
   ├─ auth-storage: NO EXISTE ✅
   └─ accessToken: NO EXISTE ✅
7. Logúeate nuevamente
8. Verifica que localStorage está vacío:
   ├─ cart-storage: { items: [], pending: {} } ✅
```

---

### ✅ Prueba 7: Verificar Zustand State

**Objetivo:** Verificar que el estado de Zustand se limpia correctamente

```
1. Abre DevTools (F12)
2. Abre Console
3. Logúeate
4. Agrega 3 productos
5. Ejecuta en Console:
   > import { useCartStore } from '@/app/store/useCartStore'
   > useCartStore.getState().items
   ✅ Debe mostrar los 3 productos
6. Deslogúeate
7. Ejecuta en Console:
   > useCartStore.getState().items
   ✅ Debe mostrar: []
8. Logúeate nuevamente
9. Ejecuta en Console:
   > useCartStore.getState().items
   ✅ Debe mostrar: []
```

---

### ✅ Prueba 8: Verificar BD (SQL)

**Objetivo:** Verificar que la BD se limpia correctamente

```sql
-- Después del logout
SELECT * FROM cart_items WHERE cart_id = (SELECT id FROM carts WHERE user_id = 1);
-- ✅ RESULTADO ESPERADO: 0 filas (vacío)

-- Después del login y agregar 1 producto
SELECT * FROM cart_items WHERE cart_id = (SELECT id FROM carts WHERE user_id = 1);
-- ✅ RESULTADO ESPERADO: 1 fila (solo el nuevo producto)
```

---

## 📊 TABLA DE RESULTADOS

| Prueba | Descripción | Resultado |
|--------|-------------|-----------|
| 1 | Logout y Login Básico | ✅ |
| 2 | Agregar Después de Logout | ✅ |
| 3 | Recargar Página | ✅ |
| 4 | Múltiples Logout/Login | ✅ |
| 5 | Logs del Backend | ✅ |
| 6 | localStorage | ✅ |
| 7 | Zustand State | ✅ |
| 8 | Base de Datos | ✅ |

---

## 🔍 ERRORES A EVITAR

### ❌ NO debe ocurrir:

```
1. DELETE /api/carrito/vaciar/ HTTP/1.1" 401
   └─ Si ves esto, significa que el frontend intenta vaciar después del logout
   
2. Carrito con productos después de logout/login
   └─ Si ves esto, el carrito fantasma sigue existiendo
   
3. ReferenceError: Cannot access 'useAuthStore' before initialization
   └─ Si ves esto, hay un problema de circular dependency
   
4. localStorage['cart-storage'] con datos después del logout
   └─ Si ves esto, localStorage no se limpió correctamente
```

---

## ✅ CRITERIOS DE ÉXITO

- ✅ Carrito se vacía al logout
- ✅ Carrito permanece vacío al login
- ✅ NO hay productos fantasma
- ✅ NO hay errores 401 en DELETE /api/carrito/vaciar/
- ✅ Backend logs muestran [LOGOUT_CART_CLEARED]
- ✅ localStorage se limpia correctamente
- ✅ Zustand state se limpia correctamente
- ✅ BD se limpia correctamente

---

## 🚀 PRÓXIMOS PASOS

1. **Ejecutar todas las pruebas**
2. **Verificar que todos los criterios se cumplen**
3. **Desplegar a producción**
4. **Monitorear en producción**

---

**Pruebas finales:** 19 de Noviembre, 2025  
**Estado:** ✅ LISTO PARA EJECUTAR  
**Confianza:** MUY ALTA
