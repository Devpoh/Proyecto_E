# 🚀 INSTRUCCIONES DE EJECUCIÓN - PASO A PASO

## ⚠️ IMPORTANTE: LEE ESTO PRIMERO

Todos los cambios ya están implementados en los archivos. Solo necesitas:
1. Limpiar cache
2. Reiniciar servidor
3. Probar

---

## 📋 PASO 1: LIMPIAR CACHE

### En PowerShell
```powershell
cd c:\Users\Alejandro\Desktop\Electro-Isla\backend
python clear_cache.py
```

### Resultado esperado
```
Limpiando cache...
✅ Cache limpiado exitosamente
```

---

## 🔄 PASO 2: REINICIAR SERVIDOR DJANGO

### En PowerShell (misma ventana o nueva)
```powershell
cd c:\Users\Alejandro\Desktop\Electro-Isla\backend
python manage.py runserver
```

### Resultado esperado
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
November 10, 2025 - 13:XX:XX
Django version 4.2.7, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

---

## 🧪 PASO 3: PROBAR EN FRONTEND

### 3.1 Abrir Frontend
```
http://localhost:5173
```

### 3.2 Hacer Login
1. Click en "Inicia Sesión"
2. Email: `qqq@gmail.com` (o tu usuario)
3. Contraseña: (tu contraseña)
4. Click "Inicia Sesión"

### 3.3 Agregar Productos al Carrito
1. Esperar a que cargue el carrusel
2. Click "Agregar al Carrito" en un producto
3. Repetir con otro producto
4. **Verificar:** Carrito se actualiza, sin errores

### 3.4 Eliminar Productos del Carrito
1. Click en icono del carrito (arriba derecha)
2. Ver los productos agregados
3. Click en "X" o botón eliminar de un producto
4. **VERIFICAR:** 
   - ✅ Sin error 500
   - ✅ Producto se elimina del carrito
   - ✅ Carrito se actualiza

### 3.5 Verificar Logs en Consola
En la consola del servidor deberías ver:
```
[Cart DELETE] Intentando eliminar item_id=97 para usuario=qqq
[Cart DELETE] Item encontrado: id=97, producto=Producto X, usuario=qqq
```

---

## ✅ CHECKLIST DE VALIDACIÓN

### Carrusel
- [ ] Carga en < 0.5 segundos
- [ ] Imágenes se muestran (o placeholder gris)
- [ ] Sin warnings en consola del navegador
- [ ] Botones de navegación funcionan

### Carrito
- [ ] Agregar producto funciona
- [ ] Carrito se actualiza
- [ ] Eliminar producto funciona (SIN error 500)
- [ ] Carrito se actualiza después de eliminar

### Logs
- [ ] Logs aparecen en consola del servidor
- [ ] Logs muestran información útil
- [ ] Sin errores NameError

### Performance
- [ ] Respuestas rápidas (< 0.5 seg)
- [ ] Sin errores 429
- [ ] Sin warnings de React

---

## 🔍 SI ALGO NO FUNCIONA

### Error: `NameError: name 'logger' is not defined`
**Solución:**
1. Abrir `backend/api/views.py`
2. Ir a línea 24
3. Verificar que existe: `logger = logging.getLogger(__name__)`
4. Si no existe, agregarlo
5. Guardar archivo
6. Reiniciar servidor

### Error: `500 Internal Server Error` al eliminar
**Solución:**
1. Revisar logs en consola del servidor
2. Buscar el error específico
3. Verificar que `item_id` sea numérico
4. Verificar que el item pertenece al usuario

### Error: `404 Item no encontrado`
**Solución:**
1. Revisar logs en consola
2. Verificar que el item existe en BD
3. Verificar que pertenece al usuario actual
4. Intentar agregar nuevamente

### Imágenes no se muestran
**Solución:**
1. Verificar que hay placeholder gris
2. Esto es normal (optimización)
3. Ir a detalles del producto para ver imagen completa

### Errores 429 Too Many Requests
**Solución:**
1. Verificar que rate limiting está desactivado
2. Abrir `backend/config/settings.py`
3. Verificar que `DEFAULT_THROTTLE_CLASSES` está comentado
4. Reiniciar servidor

---

## 📊 MONITOREO

### Verificar Performance
En la consola del navegador (F12):
1. Network tab
2. Filtrar por `api/carrusel`
3. Ver tamaño de respuesta (debe ser ~50KB, no 4.6MB)
4. Ver tiempo de respuesta (debe ser < 0.5 seg)

### Verificar Logs
En la consola del servidor:
1. Buscar `[Cart DELETE]` cuando eliminas
2. Debe mostrar: `Intentando eliminar item_id=X`
3. Debe mostrar: `Item encontrado` o `Item NO encontrado`

---

## 🎯 RESULTADO ESPERADO

Después de completar todos los pasos:

✅ **Carrusel**
- Carga rápido (< 0.5 seg)
- Imágenes se ven (o placeholder)
- Sin warnings

✅ **Carrito**
- Agregar funciona
- Eliminar funciona (SIN error 500)
- Se actualiza correctamente

✅ **Logs**
- Aparecen en consola
- Muestran información útil
- Sin errores

✅ **Performance**
- Respuestas pequeñas (~50KB)
- Carga rápida
- Sin errores 429

---

## 🚨 EMERGENCIA

Si todo se rompe:
1. Ctrl+C en servidor Django
2. Ejecutar: `python clear_cache.py`
3. Ejecutar: `python manage.py runserver`
4. Revisar logs
5. Contactar soporte

---

## 📝 NOTAS

- Todos los cambios ya están implementados
- No necesitas modificar código
- Solo ejecuta los pasos anteriores
- Si hay problemas, revisar logs

---

## ✅ CONFIRMACIÓN

Cuando todo funcione correctamente, deberías ver:

**En el navegador:**
- Carrusel cargando rápido
- Imágenes visibles
- Carrito funcionando
- Sin errores

**En la consola del servidor:**
```
[10/Nov/2025 13:XX:XX] "GET /api/carrusel/ HTTP/1.1" 200 615
[10/Nov/2025 13:XX:XX] "POST /api/carrito/agregar/ HTTP/1.1" 201 ...
[Cart DELETE] Intentando eliminar item_id=97 para usuario=qqq
[Cart DELETE] Item encontrado: id=97, producto=..., usuario=qqq
[10/Nov/2025 13:XX:XX] "DELETE /api/carrito/items/97/ HTTP/1.1" 200 ...
```

---

**¡Listo! Sigue estos pasos y todo debería funcionar correctamente.**

*Instrucciones preparadas por: Cascade AI Assistant*
*Fecha: 10 de Noviembre 2025*
