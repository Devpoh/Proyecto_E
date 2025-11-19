# 🧪 INSTRUCCIONES DE PRUEBA: Carrito Fantasma - Opción C

**Objetivo:** Verificar que el carrito fantasma ha sido eliminado  
**Duración:** ~15 minutos  
**Requisitos:** Aplicación en desarrollo funcionando

---

## ✅ ANTES DE EMPEZAR

- [x] Backend corriendo en `http://localhost:8000`
- [x] Frontend corriendo en `http://localhost:5173`
- [x] Base de datos PostgreSQL disponible
- [x] Redis disponible (para caché)
- [x] Cambios implementados (Frontend + Backend)

---

## 🧪 PRUEBA 1: Logout y Login Básico

### Pasos

1. **Abrir aplicación**
   - Ir a `http://localhost:5173`
   - Abrir DevTools (F12)
   - Ir a Console

2. **Loguearse**
   - Hacer click en "Iniciar Sesión"
   - Ingresar credenciales (usuario: `qqq`, contraseña: `123456`)
   - Verificar que se loguea correctamente

3. **Agregar productos al carrito**
   - Agregar 3 productos diferentes
   - Verificar que aparecen en el carrito
   - Anotar los nombres: `[p1, p2, p3]`

4. **Verificar en DevTools**
   - Console: Buscar `[useAuthStore]` o `[useSyncCart]`
   - Application → Cookies: Verificar `refreshToken`
   - Application → LocalStorage: Verificar `cart-storage`

5. **Desloguearse**
   - Click en el menú de usuario
   - Click en "Cerrar Sesión"
   - Verificar que se desloguea

6. **Verificar logs en Console**
   - Buscar: `[useAuthStore] Error al vaciar carrito en backend`
   - O: `[useSyncCart] Carrito limpiado al cerrar sesión`
   - Verificar que NO hay errores

7. **Verificar en DevTools**
   - Application → LocalStorage: `cart-storage` debe estar vacío o no existir
   - Application → Cookies: `refreshToken` debe estar vacío

8. **Loguearse nuevamente**
   - Hacer click en "Iniciar Sesión"
   - Ingresar las mismas credenciales
   - Verificar que se loguea correctamente

9. **Verificar carrito**
   - ✅ El carrito debe estar VACÍO
   - ❌ NO deben aparecer los 3 productos anteriores
   - Si aparecen: **FALLO - Carrito fantasma**

### Resultado Esperado

```
✅ Carrito vacío después de logout y login
✅ Sin productos fantasma
✅ Sin errores en console
```

---

## 🧪 PRUEBA 2: Agregar Después de Logout

### Pasos

1. **Loguearse**
   - Ingresar credenciales

2. **Agregar 3 productos**
   - Anotar los nombres: `[p1, p2, p3]`

3. **Desloguearse**
   - Verificar que se desloguea

4. **Loguearse nuevamente**
   - Ingresar credenciales

5. **Agregar 1 producto nuevo**
   - Anotar el nombre: `[p4]`

6. **Verificar carrito**
   - ✅ El carrito debe tener SOLO 1 producto (p4)
   - ❌ NO deben aparecer p1, p2, p3
   - Si aparecen: **FALLO - Carrito fantasma**

### Resultado Esperado

```
✅ Carrito tiene solo el nuevo producto
✅ Sin productos fantasma
✅ Sin errores en console
```

---

## 🧪 PRUEBA 3: Recargar Página Después de Logout

### Pasos

1. **Loguearse**
   - Ingresar credenciales

2. **Agregar 3 productos**
   - Anotar los nombres: `[p1, p2, p3]`

3. **Desloguearse**
   - Verificar que se desloguea

4. **Recargar página**
   - Presionar F5 o Ctrl+R
   - Esperar a que cargue

5. **Loguearse nuevamente**
   - Ingresar credenciales

6. **Verificar carrito**
   - ✅ El carrito debe estar VACÍO
   - ❌ NO deben aparecer los 3 productos
   - Si aparecen: **FALLO - Carrito fantasma**

### Resultado Esperado

```
✅ Carrito vacío después de recargar
✅ Sin productos fantasma
✅ Sin errores en console
```

---

## 🧪 PRUEBA 4: Logout desde Diferentes Lugares

### Pasos

1. **Loguearse**
   - Ingresar credenciales

2. **Agregar 2 productos**
   - Anotar los nombres: `[p1, p2]`

3. **Desloguearse desde UserMenu**
   - Click en el menú de usuario
   - Click en "Cerrar Sesión"

4. **Loguearse**
   - Ingresar credenciales

5. **Verificar carrito**
   - ✅ Carrito debe estar VACÍO

6. **Agregar 2 productos**
   - Anotar los nombres: `[p3, p4]`

7. **Desloguearse desde ProtectedRoute** (si aplica)
   - Navegar a una ruta protegida
   - Esperar a que se desloguee

8. **Loguearse**
   - Ingresar credenciales

9. **Verificar carrito**
   - ✅ Carrito debe estar VACÍO

### Resultado Esperado

```
✅ Carrito vacío desde todos los puntos de logout
✅ Sin productos fantasma
✅ Sin errores en console
```

---

## 📊 VERIFICACIÓN EN BACKEND

### Logs del Backend

**Buscar estos logs:**

```
[SIGNAL] Carrito limpiado al logout: Usuario=qqq | Items eliminados=3
```

**O en caso de error:**

```
[SIGNAL] Error limpiando carrito al logout: Usuario=qqq | Error=...
```

### Base de Datos

**Verificar en PostgreSQL:**

```sql
-- Verificar que el carrito está vacío
SELECT * FROM cart_items WHERE cart_id = (SELECT id FROM carts WHERE user_id = 1);
-- Resultado: 0 filas (vacío)

-- Verificar que el carrito existe pero sin items
SELECT * FROM carts WHERE user_id = 1;
-- Resultado: 1 fila (carrito existe pero sin items)
```

---

## 🔍 DEBUGGING

### Si el carrito fantasma persiste

**Paso 1: Verificar Frontend**
```javascript
// En Console
localStorage.getItem('cart-storage')
// Debe devolver: null o {items: []}
```

**Paso 2: Verificar Backend**
```python
# En shell de Django
from api.models import Cart, User
user = User.objects.get(username='qqq')
cart = Cart.objects.get(user=user)
cart.items.count()
# Debe devolver: 0
```

**Paso 3: Verificar Logs**
```
Backend logs:
- ¿Aparece [SIGNAL] Carrito limpiado?
- ¿Aparece error en [SIGNAL]?

Frontend logs:
- ¿Aparece [useAuthStore] Error al vaciar carrito?
- ¿Aparece [useSyncCart] Carrito limpiado?
```

### Si hay errores en Console

**Error: "Error al vaciar carrito en backend"**
- Verificar que el endpoint DELETE /api/carrito/vaciar/ existe
- Verificar que el token es válido
- Verificar que el usuario está autenticado

**Error: "Signal error"**
- Verificar que signals.py está importado en apps.py
- Verificar que el signal está registrado correctamente
- Revisar logs del backend

---

## ✅ CHECKLIST DE PRUEBA

- [ ] Prueba 1: Logout y Login Básico - PASÓ
- [ ] Prueba 2: Agregar Después de Logout - PASÓ
- [ ] Prueba 3: Recargar Página - PASÓ
- [ ] Prueba 4: Logout desde Diferentes Lugares - PASÓ
- [ ] Verificación Backend - OK
- [ ] Logs del Backend - OK
- [ ] Base de Datos - OK
- [ ] Sin errores en Console - OK

---

## 📝 REPORTE DE RESULTADOS

**Fecha:** _______________  
**Tester:** _______________  
**Resultado General:** ✅ PASÓ / ❌ FALLÓ

### Prueba 1
- Estado: ✅ PASÓ / ❌ FALLÓ
- Notas: _____________________________

### Prueba 2
- Estado: ✅ PASÓ / ❌ FALLÓ
- Notas: _____________________________

### Prueba 3
- Estado: ✅ PASÓ / ❌ FALLÓ
- Notas: _____________________________

### Prueba 4
- Estado: ✅ PASÓ / ❌ FALLÓ
- Notas: _____________________________

### Backend
- Estado: ✅ OK / ❌ ERROR
- Notas: _____________________________

### Conclusión
_________________________________________________________________

---

**Instrucciones completadas:** 19 de Noviembre, 2025  
**Duración estimada:** 15 minutos  
**Dificultad:** Fácil
