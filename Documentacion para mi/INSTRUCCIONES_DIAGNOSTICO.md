# 🔧 INSTRUCCIONES - Cómo Diagnosticar el Problema de Login

## 🎯 Objetivo

Identificar exactamente por qué el usuario no puede loguear después de cambiar la contraseña.

---

## 📋 PASO 1: Preparar el Navegador

1. **Abrir el navegador** (Chrome, Firefox, Edge)
2. **Presionar F12** para abrir DevTools
3. **Ir a la pestaña "Console"**
4. **Ir a la pestaña "Network"** (mantenerla abierta)

---

## 📋 PASO 2: Simular el Flujo de Recuperación

1. **Ir a la aplicación** en `http://localhost:3000`
2. **Hacer clic en "¿Recuerdas tu contraseña?"**
3. **Ingresar tu email** (ej: `ale@example.com`)
4. **Hacer clic en "Recuperar Contraseña"**
5. **Esperar a recibir el código** (revisa tu email o logs)

---

## 📋 PASO 3: Ingresar el Código y Nueva Contraseña

1. **Ingresar el código** que recibiste
2. **Ingresar nueva contraseña** (ej: `NuevaPassword123!`)
3. **Confirmar contraseña**
4. **Hacer clic en "Cambiar Contraseña"**

---

## 📋 PASO 4: Revisar la Consola

**En la pestaña "Console", busca los siguientes logs:**

### Log 1: Response Recibida
```
[ResetPasswordForm] Response recibida: {
  hasAccessToken: true,
  hasUser: true,
  user: { id: 1, email: 'ale@example.com', ... }
}
```

**Esperado:** `hasAccessToken: true` y `hasUser: true`

**Si ves:** `hasAccessToken: false` o `hasUser: false` → El backend no está retornando los datos correctamente

---

### Log 2: Guardando Autenticación
```
[ResetPasswordForm] Guardando autenticación en Zustand: {
  userId: 1,
  userEmail: 'ale@example.com',
  userRol: 'cliente',
  tokenLength: 250
}
```

**Esperado:** Todos los campos presentes

**Si no ves este log:** El response estaba incompleto

---

### Log 3: Estado Después de Guardar
```
[ResetPasswordForm] Estado después de guardar: {
  isAuthenticated: true,
  userEmail: 'ale@example.com',
  hasToken: true
}
```

**Esperado:** `isAuthenticated: true` y `hasToken: true`

**Si ves:** `isAuthenticated: false` → El token no se guardó correctamente

---

### Log 4: Redirigiendo
```
[ResetPasswordForm] Redirigiendo: {
  userRol: 'cliente',
  destination: '/'
}
```

**Esperado:** `destination: '/'` (o `/admin` si es admin)

**Si no ves este log:** Hubo un error antes de la redirección

---

## 📋 PASO 5: Revisar la Pestaña Network

1. **En la pestaña "Network"**, busca la solicitud a `/api/auth/reset-password/`
2. **Haz clic en ella**
3. **Ir a la pestaña "Response"**
4. **Verificar que retorna:**

```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "ale@example.com",
    "nombre": "Alejandro",
    "rol": "cliente"
  },
  "message": "Contraseña actualizada exitosamente"
}
```

**Esperado:** Status `200 OK` y los campos anteriores

**Si ves:** Status `400` o `401` → El backend rechazó la solicitud

---

## 📋 PASO 6: Verificar el Dashboard

1. **Después de la redirección**, deberías estar en el dashboard (`/`)
2. **Abre la consola nuevamente** (F12)
3. **Busca logs de autenticación**

**Esperado:** Deberías ver logs indicando que estás autenticado

**Si ves:** Redirección a `/auth/login` → El usuario no está autenticado

---

## 🐛 Posibles Problemas y Soluciones

### Problema 1: "Response incompleta"

**Síntoma:** Ves el log `[ResetPasswordForm] Response incompleta`

**Causa:** El backend no está retornando `accessToken` o `user`

**Solución:**
1. Revisar logs del backend
2. Ejecutar test E2E: `python test_e2e_reset_password.py`
3. Verificar que el endpoint retorna los datos correctamente

---

### Problema 2: "isAuthenticated: false"

**Síntoma:** El estado muestra `isAuthenticated: false` después de guardar

**Causa:** `setAuthState` no está funcionando correctamente

**Solución:**
1. Verificar que `useAuthStore` está importado correctamente
2. Revisar que `setAuthState` es la función `login` del store
3. Ejecutar test de Zustand

---

### Problema 3: No se ve ningún log

**Síntoma:** No aparecen los logs `[ResetPasswordForm]`

**Causa:** El código no está siendo ejecutado o hay un error antes

**Solución:**
1. Verificar que no hay errores en la consola
2. Revisar que el archivo `ResetPasswordForm.tsx` fue actualizado
3. Hacer refresh de la página (Ctrl+Shift+R)

---

### Problema 4: Error 400 o 401 en la solicitud

**Síntoma:** La solicitud a `/api/auth/reset-password/` retorna error

**Causa:** El backend rechazó la solicitud

**Solución:**
1. Revisar el mensaje de error en la Response
2. Verificar que el código es válido
3. Verificar que la contraseña cumple requisitos
4. Revisar logs del backend

---

## 📊 Información para Reportar

Cuando reportes el problema, incluye:

1. **Captura de pantalla de la consola** (todos los logs `[ResetPasswordForm]`)
2. **Captura de pantalla de Network** (la solicitud a `/api/auth/reset-password/`)
3. **Logs del backend** (si hay errores)
4. **Pasos exactos** que hiciste para reproducir el problema

---

## ✅ Checklist de Verificación

- [ ] Consola muestra `[ResetPasswordForm] Response recibida`
- [ ] `hasAccessToken: true` en la response
- [ ] `hasUser: true` en la response
- [ ] Consola muestra `[ResetPasswordForm] Guardando autenticación en Zustand`
- [ ] `isAuthenticated: true` después de guardar
- [ ] `hasToken: true` después de guardar
- [ ] Consola muestra `[ResetPasswordForm] Redirigiendo`
- [ ] Eres redirigido al dashboard (`/`)
- [ ] Estás autenticado en el dashboard
- [ ] Puedes acceder a funciones protegidas

---

## 🚀 Si Todo Funciona

¡Excelente! El problema está resuelto. Puedes:

1. **Remover los console.log** del código (opcional)
2. **Hacer commit** de los cambios
3. **Desplegar** a producción

---

## 🆘 Si Aún Hay Problemas

1. **Recopila toda la información** del checklist anterior
2. **Crea un issue** con los detalles
3. **Incluye capturas de pantalla** de la consola y Network
4. **Describe exactamente** qué es lo que ves vs. lo que esperas

---

**Última actualización:** 25 de Noviembre de 2025
