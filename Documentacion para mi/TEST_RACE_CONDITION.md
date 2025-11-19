# 🧪 TEST: VERIFICAR RACE CONDITION SOLUCIONADA

## Instrucciones de Prueba

### Prerequisitos
- ✅ Backend corriendo: `python manage.py runserver`
- ✅ Frontend corriendo: `npm run dev`
- ✅ Cambios aplicados en ambos lados

---

## TEST 1: Clicks Normales (Baseline)

### Pasos
1. Abre http://localhost:5173
2. Login con tu usuario
3. Agrega 3 productos al carrito
4. Espera 1 segundo entre cada click de eliminar
5. Elimina los 3 productos uno por uno

### Resultado Esperado
- ✅ Sin errores 404
- ✅ Sin errores 500
- ✅ Carrito se actualiza correctamente
- ✅ Logs en consola del servidor muestran eliminaciones exitosas

### Logs Esperados
```
[Cart DELETE] Intentando eliminar item_id=109...
[Cart DELETE] Item encontrado: id=109, producto=...
[Cart DELETE] Item eliminado exitosamente: id=109
```

---

## TEST 2: Clicks Rápidos (CRÍTICO - RACE CONDITION)

### Pasos
1. Abre http://localhost:5173
2. Login con tu usuario
3. Agrega 3 productos al carrito
4. **Haz click rápidamente en los 3 botones de eliminar (casi simultáneamente)**
5. Observa la consola del navegador y del servidor

### Resultado Esperado
- ✅ Sin errores 404 en frontend
- ✅ Sin errores 500 en backend
- ✅ Carrito se actualiza correctamente
- ✅ Debounce evita múltiples eliminaciones simultáneas

### Logs Esperados
```
[useSyncCart] Producto ya está siendo eliminado: 109
[useSyncCart] Producto ya está siendo eliminado: 108
[Cart DELETE] Intentando eliminar item_id=109...
[Cart DELETE] Item encontrado: id=109...
[Cart DELETE] Item eliminado exitosamente: id=109
```

### Qué NO Deberías Ver
- ❌ Error 404 en frontend
- ❌ Error 500 en backend
- ❌ `[Cart DELETE] Item NO encontrado`

---

## TEST 3: Eliminación Simultánea (STRESS TEST)

### Pasos
1. Abre http://localhost:5173
2. Login con tu usuario
3. Agrega 5 productos al carrito
4. **Haz click en todos los botones de eliminar casi simultáneamente**
5. Observa que el carrito se actualiza correctamente

### Resultado Esperado
- ✅ Sin errores
- ✅ Carrito vacío al final
- ✅ Todos los items eliminados correctamente
- ✅ Debounce previene race conditions

### Verificación
En la consola del servidor:
```
[Cart DELETE] Intentando eliminar item_id=...
[Cart DELETE] Item encontrado: id=...
[Cart DELETE] Item eliminado exitosamente: id=...
(repetido 5 veces, sin errores 404)
```

---

## TEST 4: Manejo de 404 (Edge Case)

### Pasos
1. Abre DevTools (F12)
2. Abre Network tab
3. Agrega 2 productos al carrito
4. Haz click en eliminar el primero
5. Mientras se procesa, haz click en eliminar el segundo
6. Observa las requests en Network tab

### Resultado Esperado
- ✅ Primer DELETE: 200 OK
- ✅ Segundo DELETE: Puede ser 404 (item ya eliminado)
- ✅ Frontend maneja 404 correctamente
- ✅ Carrito se sincroniza desde backend

### Verificación
En Network tab:
```
DELETE /api/carrito/items/109/ → 200 OK
DELETE /api/carrito/items/108/ → 200 OK (o 404 si ya fue eliminado)
```

En consola del navegador:
```
[useSyncCart] Item no encontrado (404), sincronizando carrito...
```

---

## TEST 5: Verificar Transacción Atómica (Backend)

### Pasos
1. Abre terminal en backend
2. Agrega logging temporal en `delete_item`:
   ```python
   logger.info(f"[TRANSACTION] Iniciando transacción para item {item_id}")
   ```
3. Agrega 3 productos
4. Haz click rápidamente en eliminar
5. Observa logs

### Resultado Esperado
- ✅ Logs muestran transacciones atómicas
- ✅ Sin errores de concurrencia
- ✅ Datos consistentes en BD

---

## CHECKLIST DE VERIFICACIÓN

### Frontend
- [ ] Sin errores 404 en clicks normales
- [ ] Sin errores 404 en clicks rápidos
- [ ] Debounce evita múltiples eliminaciones
- [ ] Carrito se actualiza correctamente
- [ ] Logs en consola son claros

### Backend
- [ ] Sin errores 500
- [ ] Logs muestran eliminaciones exitosas
- [ ] Transacción atómica funciona
- [ ] Select for update previene race conditions
- [ ] Datos en BD son consistentes

### UX
- [ ] Eliminación es fluida
- [ ] Sin mensajes de error confusos
- [ ] Carrito siempre está sincronizado
- [ ] Feedback visual es claro

---

## PROBLEMAS COMUNES

### Problema: Aún veo errores 404
**Solución:**
1. Verificar que cambios en `useSyncCart.ts` están aplicados
2. Verificar que `deleteQueue` está definido
3. Limpiar cache del navegador (Ctrl+Shift+Del)
4. Reiniciar servidor

### Problema: Debounce no funciona
**Solución:**
1. Verificar que `deleteQueue.has()` está en el código
2. Verificar que `deleteQueue.add()` se ejecuta
3. Revisar logs en consola del navegador
4. Verificar que finalmente se ejecuta `deleteQueue.delete()`

### Problema: Carrito no se sincroniza
**Solución:**
1. Verificar que `fetchCartFromBackend()` se llama en 404
2. Verificar que backend devuelve carrito actualizado
3. Revisar logs en consola del servidor
4. Verificar que `setItems()` se ejecuta

---

## MÉTRICAS DE ÉXITO

✅ **Test 1 (Normal):** 100% exitoso
✅ **Test 2 (Rápido):** 0 errores 404
✅ **Test 3 (Stress):** Todos los items eliminados
✅ **Test 4 (404):** Manejo correcto
✅ **Test 5 (Transacción):** Atómica

---

## PRÓXIMOS PASOS

Si todos los tests pasan:
1. ✅ Cambios listos para producción
2. ✅ Documentar en release notes
3. ✅ Monitorear en producción
4. ✅ Recopilar feedback de usuarios

Si algún test falla:
1. ⚠️ Revisar logs detallados
2. ⚠️ Verificar que cambios están aplicados
3. ⚠️ Limpiar cache y reiniciar
4. ⚠️ Contactar soporte si persiste

---

*Test creado por: Cascade AI Assistant*
*Fecha: 10 de Noviembre 2025*
