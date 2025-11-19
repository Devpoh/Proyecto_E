# 🔍 DEBUG: Error 401 en Refresh Token

## Problema
```
POST http://localhost:8000/api/auth/refresh/ 401 (Unauthorized)
```

## Posibles causas

### 1. Refresh token no se está guardando en la cookie
- Backend: `response.set_cookie()` en login (línea 282-290) ✅
- Frontend: `credentials: 'include'` en fetch (línea 124) ✅

### 2. Refresh token no se está enviando con la solicitud
- Frontend: `credentials: 'include'` en fetch (línea 124) ✅
- Backend: Buscando en `request.COOKIES.get('refreshToken')` (línea 319) ✅

### 3. Refresh token está expirado
- Backend: Verifica con `RefreshToken.verificar_token()` (línea 329)

### 4. CORS/CSRF bloqueando cookies
- Backend: `CORS_ALLOW_CREDENTIALS = True` ✅
- Backend: `CSRF_COOKIE_SECURE = False` (desarrollo) ✅
- Frontend: `credentials: 'include'` ✅

---

## Pasos de verificación

### Paso 1: Verificar en DevTools
1. Ir a Application → Cookies
2. Buscar `refreshToken` después de login
3. ¿Está presente? ¿Es HTTP-Only?

### Paso 2: Verificar en Network
1. Hacer login
2. Ver respuesta de login
3. ¿Tiene Set-Cookie: refreshToken?

### Paso 3: Verificar en Network (refresh)
1. Recargar página
2. Ver solicitud a `/auth/refresh/`
3. ¿Tiene Cookie: refreshToken en headers?

### Paso 4: Verificar en Backend
1. Ver logs del backend
2. ¿Dice "Refresh token no encontrado"?
3. ¿O "Refresh token inválido o expirado"?

---

## Hipótesis más probable

El refresh token NO se está guardando en la cookie después del login.

**Razón:** El frontend está usando `fetch()` con `credentials: 'include'`, pero el backend podría no estar configurado correctamente para CORS.

---

## Solución propuesta

1. Verificar que CORS está permitiendo cookies
2. Verificar que el frontend está enviando `credentials: 'include'`
3. Verificar que el refresh token se guarda en la cookie
4. Verificar que el refresh token se envía con la solicitud

---

## Código a revisar

### Frontend (useAuthStore.ts línea 122)
```typescript
const response = await fetch(`${apiUrl}/auth/refresh/`, {
  method: 'POST',
  credentials: 'include', // ✅ Enviar cookies
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Backend (views.py línea 282-290)
```python
response.set_cookie(
    key='refreshToken',
    value=refresh_token_plano,
    max_age=2 * 60 * 60,
    httponly=True,
    secure=False,  # Desarrollo
    samesite='Lax',
    path='/'
)
```

### Backend (settings.py)
```python
CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_SECURE = False  # Desarrollo
```

---

## Próximos pasos

1. Verificar en DevTools si la cookie se está guardando
2. Si no se guarda → Problema de CORS
3. Si se guarda pero no se envía → Problema de fetch
4. Si se envía pero backend rechaza → Problema de validación
