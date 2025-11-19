# 🔧 INSTRUCCIONES DE DEBUGGING: Carrito Fantasma

**Objetivo:** Verificar exactamente qué está pasando  
**Duración:** ~10 minutos  
**Requisitos:** DevTools abierto

---

## 🧪 PRUEBA PASO A PASO

### Paso 1: Preparar

1. Abre DevTools (F12)
2. Ve a la pestaña **Network**
3. Ve a la pestaña **Console**
4. Limpia los logs anteriores

### Paso 2: Loguearse

1. Haz click en "Iniciar Sesión"
2. Ingresa: usuario `qqq`, contraseña `123456`
3. Espera a que se loguee

**Verifica en Console:**
```
[useAuthStore] Login exitoso. Token guardado en memoria (Zustand).
```

### Paso 3: Agregar 3 productos

1. Agrega 3 productos diferentes al carrito
2. Verifica que aparecen en el carrito

**Verifica en Console:**
```
[useSyncCart] Producto agregado: ...
```

### Paso 4: Desloguearse

1. Click en el menú de usuario
2. Click en "Cerrar Sesión"
3. Espera a que se desloguee

**Verifica en Console:**
```
[useAuthStore] Carrito vaciado en backend al logout
```

**O si hay error:**
```
[useAuthStore] Error al vaciar carrito en backend: ...
```

### Paso 5: Verificar Network

En la pestaña **Network**, busca:

1. **DELETE /api/carrito/vaciar/**
   - ✅ Debe aparecer
   - ✅ Status debe ser 200 OK
   - ✅ Response debe ser `{items: [], total: 0}`

2. **POST /api/auth/refresh/**
   - ✅ Puede aparecer con 401 (NORMAL)
   - ✅ Esto es esperado cuando no hay sesión

### Paso 6: Loguearse nuevamente

1. Click en "Iniciar Sesión"
2. Ingresa: usuario `qqq`, contraseña `123456`
3. Espera a que se loguee

**Verifica en Console:**
```
[useSyncCart] Carrito cargado del backend: ...
```

### Paso 7: Verificar carrito

**¿Qué debe pasar?**
- ✅ El carrito debe estar VACÍO
- ❌ NO deben aparecer los 3 productos

**Si aparecen los 3 productos:**
- ❌ FALLO - Carrito fantasma

---

## 🔍 DEBUGGING DETALLADO

### Si NO aparece DELETE /api/carrito/vaciar/

**Significa:** El endpoint NO se está llamando

**Pasos:**

1. Abre Console
2. Busca: `[useAuthStore] Error al vaciar carrito`
3. Si aparece, anota el error exacto

**Posibles causas:**
- El import de Axios no funciona
- El token no está disponible
- La función logout() no se ejecuta

---

### Si aparece DELETE /api/carrito/vaciar/ con 401

**Significa:** El endpoint se llama pero el token NO se envía

**Pasos:**

1. Click en la solicitud DELETE en Network
2. Ve a la pestaña "Headers"
3. Busca: `Authorization: Bearer ...`

**Si NO aparece:**
- ❌ El token NO se envía
- ❌ El problema está en Axios

**Si aparece:**
- ✅ El token se envía
- ❌ El problema está en el backend

---

### Si aparece DELETE /api/carrito/vaciar/ con 200

**Significa:** El endpoint funciona

**Pasos:**

1. Click en la solicitud DELETE en Network
2. Ve a la pestaña "Response"
3. Verifica que sea: `{items: [], total: 0}`

**Si es correcto:**
- ✅ El backend está limpiando
- ❌ El problema está en el frontend (carrito se recarga)

---

## 📊 TABLA DE DIAGNÓSTICO

| Síntoma | Causa | Solución |
|---------|-------|----------|
| No aparece DELETE | Endpoint NO se llama | Verificar import de Axios |
| DELETE con 401 | Token NO se envía | Verificar interceptor de Axios |
| DELETE con 200 | Endpoint funciona | Verificar que carrito se recarga |
| Carrito vacío | ✅ TODO OK | Problema resuelto |
| Carrito con productos | ❌ Fantasma | Investigar más |

---

## 🐛 LOGS A BUSCAR

### En Console (Frontend)

```
✅ Buscar estos logs:
[useAuthStore] Carrito vaciado en backend al logout
[useSyncCart] Carrito limpiado al cerrar sesión
[useSyncCart] Carrito cargado del backend

❌ Evitar estos logs:
[useAuthStore] Error al vaciar carrito en backend
[useAuthStore] Error importando Axios
```

### En Backend Logs

```
✅ Buscar estos logs:
[SIGNAL] Carrito limpiado al logout: Usuario=qqq | Items eliminados=3

❌ Evitar estos logs:
[SIGNAL] Error limpiando carrito al logout
```

---

## 📝 REPORTE DE DEBUGGING

**Fecha:** _______________

### Paso 1: Loguearse
- ✅ Logueado correctamente

### Paso 2: Agregar 3 productos
- ✅ Agregados correctamente

### Paso 3: Desloguearse
- ¿Aparece log `[useAuthStore] Carrito vaciado`? **SÍ / NO**
- ¿Aparece error? **SÍ / NO**
- Si hay error, ¿cuál es? _____________________________

### Paso 4: Network
- ¿Aparece DELETE /api/carrito/vaciar/? **SÍ / NO**
- ¿Cuál es el status? **200 / 401 / 500 / OTRO**
- ¿Cuál es la response? _____________________________

### Paso 5: Loguearse nuevamente
- ✅ Logueado correctamente

### Paso 6: Carrito
- ¿El carrito está vacío? **SÍ / NO**
- ¿Aparecen los 3 productos? **SÍ / NO**

### Conclusión
- **PROBLEMA RESUELTO** ✅ / **PROBLEMA PERSISTE** ❌

---

## 🆘 SI NADA FUNCIONA

1. **Abre la Console**
2. **Ejecuta esto:**
   ```javascript
   // Ver si el token existe
   console.log('Token:', localStorage.getItem('accessToken'));
   
   // Ver si el carrito existe en localStorage
   console.log('Carrito:', localStorage.getItem('cart-storage'));
   
   // Ver si el carrito existe en Zustand
   console.log('Zustand:', useCartStore.getState());
   ```

3. **Anota los resultados**
4. **Comparte conmigo**

---

**Instrucciones completadas:** 19 de Noviembre, 2025  
**Próximo paso:** Ejecutar debugging y compartir resultados
