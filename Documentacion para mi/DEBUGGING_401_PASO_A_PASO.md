# 🔍 DEBUGGING 401 - Paso a Paso Clínico

## Contexto
```
POST http://localhost:8000/api/auth/refresh/ 401 (Unauthorized)
```

El backend está rechazando la solicitud de refresh token.

---

## ⚠️ IMPORTANTE: NO CAMBIAR NADA AÚN

Solo vamos a **OBSERVAR** y **RECOPILAR INFORMACIÓN** para entender qué está pasando.

---

## Paso 1: Verificar si el refresh token se guarda en la cookie

### Instrucciones:
1. Abre DevTools (F12)
2. Ve a **Application → Cookies**
3. Selecciona `http://localhost:5173`
4. **Busca `refreshToken`**

### Preguntas:
- ¿Está presente después del login?
- ¿Tiene el flag `HttpOnly`?
- ¿Tiene el flag `Secure`?
- ¿Cuál es su valor?

### Captura de pantalla esperada:
```
Name: refreshToken
Value: eyJhbGciOiJIUzI1NiIs... (token largo)
Domain: localhost
Path: /
Expires/Max-Age: [fecha futura]
HttpOnly: ✓
Secure: ✗ (en desarrollo)
SameSite: Lax
```

---

## Paso 2: Verificar si el refresh token se envía con la solicitud

### Instrucciones:
1. Abre DevTools (F12)
2. Ve a **Network**
3. Recarga la página (sin estar logueado)
4. Busca la solicitud `refresh/` (POST)
5. Haz click en ella
6. Ve a **Headers**
7. Busca la sección **Request Headers**

### Preguntas:
- ¿Está presente el header `Cookie`?
- ¿Contiene `refreshToken=...`?

### Captura de pantalla esperada:
```
Request Headers:
  Cookie: refreshToken=eyJhbGciOiJIUzI1NiIs...
  Content-Type: application/json
```

---

## Paso 3: Verificar la respuesta del login

### Instrucciones:
1. Abre DevTools (F12)
2. Ve a **Network**
3. Haz login
4. Busca la solicitud `login/` (POST)
5. Haz click en ella
6. Ve a **Response Headers**
7. Busca `Set-Cookie`

### Preguntas:
- ¿Está presente `Set-Cookie: refreshToken=...`?
- ¿Tiene `HttpOnly`?
- ¿Tiene `Path=/`?

### Captura de pantalla esperada:
```
Response Headers:
  Set-Cookie: refreshToken=eyJhbGciOiJIUzI1NiIs...; HttpOnly; Path=/; SameSite=Lax; Max-Age=7200
```

---

## Paso 4: Verificar los logs del backend

### Instrucciones:
1. Mira la consola del backend
2. Busca líneas que digan `[REFRESH_FAILED]` o `[TOKEN_REFRESH]`

### Preguntas:
- ¿Qué dice el log?
- ¿Dice "Refresh token no encontrado"?
- ¿Dice "Refresh token inválido o expirado"?

### Ejemplos de logs:
```
[REFRESH_FAILED] Refresh token no encontrado en cookie
[REFRESH_FAILED] Refresh token inválido o expirado
[TOKEN_REFRESH] Usuario: qqq | IP: 127.0.0.1
```

---

## Paso 5: Verificar la consola del navegador

### Instrucciones:
1. Abre DevTools (F12)
2. Ve a **Console**
3. Busca mensajes de `[useAuthStore]`

### Preguntas:
- ¿Qué dice?
- ¿Dice "Sesión restaurada"?
- ¿Dice "Refresh token inválido o expirado"?

### Ejemplos:
```
[useAuthStore] Intentando restaurar sesión desde refresh token...
[useAuthStore] ⚠️ Refresh token inválido o expirado: {status: 401, error: "Refresh token no encontrado"}
```

---

## Resumen de información a recopilar

Completa este checklist:

- [ ] ¿Está `refreshToken` en cookies después del login?
- [ ] ¿Tiene el flag `HttpOnly`?
- [ ] ¿Se envía `Cookie: refreshToken=...` con la solicitud de refresh?
- [ ] ¿Tiene `Set-Cookie: refreshToken=...` la respuesta del login?
- [ ] ¿Qué dice el log del backend? (`[REFRESH_FAILED]` o `[TOKEN_REFRESH]`)
- [ ] ¿Qué dice la consola del navegador? (`[useAuthStore]`)

---

## Próximos pasos

Una vez que recopiles esta información, podremos:

1. **Si el refresh token NO se guarda en la cookie:**
   - Problema: CORS o backend no está configurado correctamente
   - Solución: Revisar `Set-Cookie` en la respuesta del login

2. **Si el refresh token se guarda pero NO se envía:**
   - Problema: Frontend no está enviando `credentials: 'include'`
   - Solución: Revisar Axios o fetch

3. **Si el refresh token se envía pero backend rechaza:**
   - Problema: Token inválido, expirado o backend no lo está buscando correctamente
   - Solución: Revisar lógica de validación en backend

4. **Si todo se ve bien pero sigue fallando:**
   - Problema: Algo más complejo (middleware, CORS, etc.)
   - Solución: Revisar logs más detallados

---

## ⚠️ IMPORTANTE

**NO CAMBIES NADA HASTA QUE RECOPILES ESTA INFORMACIÓN.**

Solo estamos observando para entender qué está pasando.

Una vez que tengas los datos, compartelos y haremos los cambios de manera segura.
