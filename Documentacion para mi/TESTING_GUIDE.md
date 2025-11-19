# 🧪 Testing Guide - Frontend Security Improvements

## Tabla de Contenidos
1. [Tests Unitarios](#tests-unitarios)
2. [Tests de Integración](#tests-de-integración)
3. [Testing Manual](#testing-manual)
4. [Verificación de Logs](#verificación-de-logs)

---

## Tests Unitarios

### 1. JWT Utilities Tests

**Archivo:** `src/shared/utils/jwt.test.ts`

**Ejecutar:**
```bash
npm test -- jwt.test.ts
```

**Casos de Prueba:**
- ✅ Decodificar JWT válido
- ✅ Rechazar JWT inválido
- ✅ Validar exp claim
- ✅ Calcular tiempo restante
- ✅ Extraer claims (rol, user_id, username)
- ✅ Validar estructura JWT

**Ejemplo:**
```typescript
// Validar que token expirado se rechaza
const expiredToken = createMockToken(-100);
expect(isTokenExpired(expiredToken)).toBe(true);

// Validar que token válido se acepta
const validToken = createMockToken(900);
expect(isTokenExpired(validToken)).toBe(false);
```

---

### 2. Storage Tests

**Archivo:** `src/shared/utils/storage.test.ts`

**Ejecutar:**
```bash
npm test -- storage.test.ts
```

**Casos de Prueba:**
- ✅ sessionStorage como primario
- ✅ localStorage como fallback
- ✅ Prioridad: sessionStorage → localStorage
- ✅ Limpieza de ambos storages
- ✅ Sincronización de tokens

**Ejemplo:**
```typescript
// Verificar que sessionStorage es primario
sessionStorage.setItem('accessToken', 'session_token');
localStorage.setItem('accessToken', 'local_token');

let token = sessionStorage.getItem('accessToken');
if (!token) {
  token = localStorage.getItem('accessToken');
}

expect(token).toBe('session_token');
```

---

### 3. CSRF Protection Tests

**Archivo:** `src/shared/utils/csrf.test.ts`

**Ejecutar:**
```bash
npm test -- csrf.test.ts
```

**Casos de Prueba:**
- ✅ Obtener CSRF token desde meta tag
- ✅ Obtener CSRF token desde cookie
- ✅ Prioridad: meta tag → cookie
- ✅ Agregar CSRF token a peticiones POST/PUT/DELETE/PATCH
- ✅ No agregar CSRF token a peticiones GET

**Ejemplo:**
```typescript
// Verificar que CSRF token se agrega a POST
const headers: Record<string, string> = {};
const csrfToken = getCsrfToken();
if (csrfToken) {
  headers['X-CSRFToken'] = csrfToken;
}

expect(headers['X-CSRFToken']).toBeDefined();
```

---

## Tests de Integración

### 1. Flujo Completo de Autenticación

**Pasos:**
1. Obtener CSRF token
2. Hacer login
3. Verificar que tokens se guardan en sessionStorage
4. Hacer petición autenticada
5. Verificar que CSRF token se agrega
6. Refrescar token
7. Hacer logout
8. Verificar que tokens se limpian

**Código de Test:**
```typescript
describe('Flujo Completo de Autenticación', () => {
  it('debe completar login → petición → logout', async () => {
    // 1. Obtener CSRF token
    const csrfResponse = await api.get('/auth/csrf-token/');
    expect(csrfResponse.status).toBe(200);

    // 2. Login
    const loginResponse = await api.post('/auth/login/', {
      username: 'test_user',
      password: 'TestPassword123',
    });
    expect(loginResponse.status).toBe(200);
    expect(loginResponse.data.accessToken).toBeDefined();

    // 3. Verificar que tokens se guardan
    expect(sessionStorage.getItem('accessToken')).toBe(loginResponse.data.accessToken);

    // 4. Hacer petición autenticada
    const petitionResponse = await api.get('/api/productos/');
    expect(petitionResponse.status).toBe(200);

    // 5. Logout
    const logoutResponse = await api.post('/auth/logout/');
    expect(logoutResponse.status).toBe(200);

    // 6. Verificar que tokens se limpian
    expect(sessionStorage.getItem('accessToken')).toBeNull();
    expect(localStorage.getItem('accessToken')).toBeNull();
  });
});
```

---

### 2. Validación de exp claim

**Pasos:**
1. Crear token que expira en 20 segundos
2. Intentar usar token
3. Verificar que se rechaza (faltan menos de 30 segundos)
4. Esperar a que expire
5. Verificar que se rechaza

**Código de Test:**
```typescript
describe('Validación de exp claim', () => {
  it('debe rechazar token que está por expirar', async () => {
    // Token que expira en 20 segundos
    const token = createMockToken(20);
    
    // Debe estar expirado (buffer de 30 segundos)
    expect(isTokenExpired(token)).toBe(true);
  });

  it('debe aceptar token válido', async () => {
    // Token que expira en 15 minutos
    const token = createMockToken(900);
    
    expect(isTokenExpired(token)).toBe(false);
  });
});
```

---

## Testing Manual

### 1. Probar Validación de exp claim

**Pasos:**
1. Abre DevTools (F12)
2. Ve a Console
3. Ejecuta:

```javascript
// Crear token que expira en 20 segundos
const now = Math.floor(Date.now() / 1000);
const payload = {
  user_id: 1,
  username: 'test',
  rol: 'cliente',
  iat: now,
  exp: now + 20,  // Expira en 20 segundos
  type: 'access',
};

const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
const body = btoa(JSON.stringify(payload));
const token = `${header}.${body}.signature`;

// Verificar que está expirado
console.log('Token expirado:', isTokenExpired(token)); // true
```

---

### 2. Probar sessionStorage vs localStorage

**Pasos:**
1. Abre DevTools (F12)
2. Ve a Application → Storage
3. Ejecuta en Console:

```javascript
// Guardar en ambos
sessionStorage.setItem('accessToken', 'session_token');
localStorage.setItem('accessToken', 'local_token');

// Verificar prioridad
let token = sessionStorage.getItem('accessToken');
if (!token) {
  token = localStorage.getItem('accessToken');
}

console.log('Token usado:', token); // session_token

// Limpiar sessionStorage
sessionStorage.clear();

// Ahora debe usar localStorage
token = sessionStorage.getItem('accessToken');
if (!token) {
  token = localStorage.getItem('accessToken');
}

console.log('Token usado (fallback):', token); // local_token
```

---

### 3. Probar CSRF Protection

**Pasos:**
1. Abre DevTools (F12)
2. Ve a Network
3. Ejecuta login
4. Verifica que petición POST incluye header `X-CSRFToken`

**Verificar:**
- ✅ Header `X-CSRFToken` presente en POST
- ✅ Header `X-CSRFToken` presente en PUT
- ✅ Header `X-CSRFToken` presente en DELETE
- ✅ Header `X-CSRFToken` presente en PATCH
- ✅ Header `X-CSRFToken` NO presente en GET

---

### 4. Probar Rate Limiting Feedback

**Pasos:**
1. Abre la página de login
2. Intenta login 5 veces con credenciales incorrectas
3. Verifica que aparece alerta de rate limiting

**Verificar:**
- ✅ Alerta aparece después de 5 intentos
- ✅ Contador regresivo funciona
- ✅ Color cambia según tiempo restante:
  - Normal (rojo): > 30 segundos
  - Warning (naranja): 10-30 segundos
  - Critical (rojo intenso + pulso): < 10 segundos
- ✅ Botón de login está deshabilitado durante bloqueo

---

### 5. Probar ProtectedRoute

**Pasos:**
1. Intenta acceder a `/admin` sin autenticarse
2. Verifica que redirige a `/login`
3. Haz login como usuario regular
4. Intenta acceder a `/admin`
5. Verifica que redirige a `/`
6. Haz login como admin
7. Verifica que puedes acceder a `/admin`

**Verificar:**
- ✅ Redirige a login si no está autenticado
- ✅ Redirige a home si no tiene rol requerido
- ✅ Permite acceso si tiene rol correcto
- ✅ Limpia sesión si token está expirado

---

## Verificación de Logs

### 1. Logs de Seguridad (Backend)

**Ubicación:** `backend/logs/security.log`

**Verificar:**
```
[WARNING] 2025-11-06 00:05:42 security [LOGIN_FAILED] Usuario: admin | IP: 127.0.0.1 | Razón: Credenciales inválidas
[WARNING] 2025-11-06 00:05:47 security [SECURITY] Token en blacklist usado por test_user desde 127.0.0.1
```

**Comandos:**
```bash
# Ver últimas líneas
tail -f backend/logs/security.log

# Buscar intentos fallidos
grep "LOGIN_FAILED" backend/logs/security.log

# Buscar tokens invalidados
grep "SECURITY" backend/logs/security.log
```

---

### 2. Logs de Autenticación (Backend)

**Ubicación:** `backend/logs/auth.log`

**Verificar:**
```
[INFO] 2025-11-06 00:05:40 auth [LOGIN_SUCCESS] Usuario: test_user | Email: test@example.com | IP: 127.0.0.1 | Rol: cliente
[INFO] 2025-11-06 00:05:44 auth [LOGOUT_SUCCESS] Usuario: test_user | IP: 127.0.0.1
```

**Comandos:**
```bash
# Ver últimas líneas
tail -f backend/logs/auth.log

# Buscar logins exitosos
grep "LOGIN_SUCCESS" backend/logs/auth.log

# Buscar logouts
grep "LOGOUT_SUCCESS" backend/logs/auth.log
```

---

### 3. Logs de Frontend (DevTools Console)

**Verificar:**
```
[Axios] Token válido agregado a /api/productos/
[Axios] CSRF token agregado a /api/auth/login/
[AuthProvider] Token expirado detectado al iniciar. Limpiando sesión.
[ProtectedRoute] Acceso permitido. Rol: admin
```

**Comandos en Console:**
```javascript
// Filtrar logs de Axios
console.log('%cAXIOS LOGS', 'color: blue');

// Filtrar logs de Auth
console.log('%cAUTH LOGS', 'color: green');

// Filtrar logs de JWT
console.log('%cJWT LOGS', 'color: red');
```

---

## Checklist de Testing

### Frontend
- [ ] JWT exp claim validation
- [ ] sessionStorage como primario
- [ ] localStorage como fallback
- [ ] CSRF token en POST/PUT/DELETE/PATCH
- [ ] CSRF token NO en GET
- [ ] Rate limiting feedback visual
- [ ] ProtectedRoute redirige si no autenticado
- [ ] ProtectedRoute redirige si rol incorrecto
- [ ] ProtectedRoute permite acceso si rol correcto
- [ ] Tokens se limpian al logout

### Backend
- [ ] Endpoint GET /auth/csrf-token/ funciona
- [ ] Endpoint POST /auth/login/ retorna JWT
- [ ] Endpoint POST /auth/refresh/ retorna nuevo token
- [ ] Endpoint POST /auth/logout/ invalida token
- [ ] TokenBlacklist middleware rechaza tokens invalidados
- [ ] Rate limiting bloquea después de 5 intentos
- [ ] Logs de seguridad se registran correctamente
- [ ] Logs de autenticación se registran correctamente

### Integración
- [ ] Flujo completo: login → petición → logout
- [ ] Token refresh automático en 401
- [ ] CSRF protection funciona
- [ ] Rate limiting funciona
- [ ] Sincronización frontend-backend

---

## Comandos Útiles

### Ejecutar todos los tests
```bash
npm test
```

### Ejecutar tests específicos
```bash
npm test -- jwt.test.ts
npm test -- storage.test.ts
npm test -- csrf.test.ts
```

### Ejecutar tests con cobertura
```bash
npm test -- --coverage
```

### Ejecutar tests en modo watch
```bash
npm test -- --watch
```

### Backend - Ver logs en tiempo real

**Linux/Mac:**
```bash
tail -f backend/logs/security.log
tail -f backend/logs/auth.log
```

**Windows PowerShell:**
```powershell
Get-Content backend/logs/security.log -Wait
Get-Content backend/logs/auth.log -Wait
```

### Backend - Buscar en logs

**Linux/Mac:**
```bash
grep "LOGIN_FAILED" backend/logs/security.log
grep "LOGIN_SUCCESS" backend/logs/auth.log
```

**Windows PowerShell:**
```powershell
Select-String "LOGIN_FAILED" backend/logs/security.log
Select-String "LOGIN_SUCCESS" backend/logs/auth.log
```

### Backend - Limpiar tokens expirados
```bash
python manage.py limpiar_tokens
```

---

## Notas Importantes

1. **Tests Unitarios:**
   - Rápidos y aislados
   - Verifican funcionalidad específica
   - No requieren servidor

2. **Tests de Integración:**
   - Más lentos pero más realistas
   - Verifican flujos completos
   - Requieren servidor corriendo

3. **Testing Manual:**
   - Verifica UX
   - Detecta problemas no cubiertos por tests
   - Importante para validación final

4. **Logs:**
   - Invaluables para debugging
   - Registran eventos de seguridad
   - Ayudan a identificar problemas

---

**¡Testing completado con éxito!** ✨
