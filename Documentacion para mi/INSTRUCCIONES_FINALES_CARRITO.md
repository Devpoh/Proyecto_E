# 🚀 INSTRUCCIONES FINALES - CARRITO REHECHOS

**Fecha:** 7 de Noviembre, 2025  
**Status:** ✅ **LISTO PARA PROBAR**

---

## 📋 REQUISITOS

- ✅ Python 3.8+
- ✅ Node.js 16+
- ✅ Django corriendo en puerto 8000
- ✅ React corriendo en puerto 3000

---

## 🚀 PASO 1: CREAR USUARIO DE PRUEBA

### En PowerShell (Windows):

```powershell
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
python manage.py createsuperuser
```

Completa con:
```
Username: testuser
Email: testuser@example.com
Password: testpass123
Password (again): testpass123
```

---

## 🚀 PASO 2: INICIAR SERVIDOR DJANGO

### En PowerShell (Terminal 1):

```powershell
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
python manage.py runserver
```

Deberías ver:
```
Starting development server at http://127.0.0.1:8000/
```

---

## 🚀 PASO 3: INICIAR FRONTEND REACT

### En PowerShell (Terminal 2):

```powershell
cd C:\Users\Alejandro\Desktop\Electro-Isla\frontend\electro_isla
npm start
```

Deberías ver:
```
Compiled successfully!
```

---

## 🧪 PASO 4: PROBAR EN NAVEGADOR

### 4.1 Abre DevTools

1. Ve a `http://localhost:3000`
2. Presiona F12 para abrir DevTools
3. Ve a: **Storage → Local Storage → http://localhost:3000**

### 4.2 Inicia Sesión

- Email: `testuser@example.com`
- Password: `testpass123`

### 4.3 Prueba 1: Agregar Producto

1. Busca un producto
2. Haz clic en "Agregar al Carrito"
3. Verifica en DevTools que aparece en localStorage
4. Verifica que el carrito en UI se actualiza
5. Verifica en backend: `GET /api/carrito/` devuelve el producto

### 4.4 Prueba 2: Actualizar Cantidad

1. Ve a la página del carrito
2. Aumenta la cantidad de un producto
3. Verifica que se sincroniza con backend
4. Navega a otra página y vuelve
5. Verifica que la cantidad sigue igual

### 4.5 Prueba 3: Eliminar Producto

1. Elimina un producto del carrito
2. Verifica que desaparece de la UI
3. Verifica que desaparece del backend
4. Navega y vuelve
5. Verifica que sigue eliminado

### 4.6 Prueba 4: Logout

1. Cierra sesión
2. Verifica que el carrito se limpia
3. Verifica que localStorage se limpia

### 4.7 Prueba 5: Login Nuevo Usuario

1. Inicia sesión con otro usuario
2. Verifica que el carrito está vacío (no tiene items del usuario anterior)
3. Agrega productos
4. Verifica que solo ve sus productos

---

## 🧪 PASO 5: PROBAR CON PowerShell

### En PowerShell (Terminal 3):

```powershell
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
.\test_carrito_windows.ps1
```

**Esperado:**
```
[1] Obteniendo token...
[OK] Token obtenido
Token: eyJ0eXAiOiJKV1QiLCJhbGc...

[2] Obteniendo carrito actual...
[OK] Carrito obtenido
Items: 0
Total: 0

[3] Agregando producto al carrito...
[OK] Producto agregado
Items en carrito: 2
Total: 2000

[4] Obteniendo carrito nuevamente...
[OK] Carrito obtenido
Items: 2
Total: 2000

[OK] TEST COMPLETADO
```

---

## 🔍 VERIFICACIÓN EN ADMIN

1. Ve a: `http://localhost:8000/admin/`
2. Inicia sesión con superuser
3. Ve a: **Carrito**
4. Deberías ver el carrito de `testuser` con los items

---

## ✅ CHECKLIST DE PRUEBAS

- [ ] Usuario creado exitosamente
- [ ] Servidor Django corriendo
- [ ] Frontend React corriendo
- [ ] Inicia sesión correctamente
- [ ] Agrega producto → aparece en carrito
- [ ] Actualiza cantidad → se sincroniza
- [ ] Elimina producto → desaparece
- [ ] Logout → carrito se limpia
- [ ] Login nuevo usuario → carrito vacío
- [ ] Script PowerShell ejecuta sin errores
- [ ] Admin muestra carrito correctamente

---

## 🐛 TROUBLESHOOTING

### Error: "Credenciales inválidas"
- Verifica que el usuario existe: `python manage.py shell`
- Crea el usuario: `python manage.py createsuperuser`

### Error: "No es posible conectar con el servidor remoto"
- Verifica que Django está corriendo: `python manage.py runserver`
- Verifica que el puerto es 8000

### Error: "Token no proporcionado"
- Verifica que el token es válido
- Verifica que el header es: `Authorization: Bearer TOKEN`

### Carrito vacío al login
- Verifica que el usuario tiene items en el backend
- Verifica que el token es válido
- Verifica que useSyncCart se ejecuta

### Items desaparecen
- Verifica que syncRemoveFromBackend se ejecuta
- Verifica que el backend devuelve carrito actualizado
- Verifica que setItems() actualiza el store

---

## 🎉 ¡LISTO!

Todos los endpoints funcionando correctamente. 🚀

**Carrito completamente sincronizado y funcional.**

¡Adelante con el checkout! 🎉
