# 🔐 Autenticación - Documentación Completa de Endpoints

## Tabla de Contenidos
1. [Endpoints](#endpoints)
2. [Flujo de Autenticación](#flujo-de-autenticación)
3. [Seguridad](#seguridad)
4. [Errores Comunes](#errores-comunes)
5. [Ejemplos de Uso](#ejemplos-de-uso)

---

## Endpoints

### 1. POST `/api/auth/register/`

**Descripción:** Registra un nuevo usuario en el sistema.

**Request:**
```json
{
  "username": "juan_perez",
  "email": "juan@example.com",
  "password": "MiPassword123",
  "first_name": "Juan",
  "last_name": "Pérez"
}
```

**Response (201 Created):**
```json
{
  "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "juan@example.com",
    "nombre": "Juan Pérez",
    "rol": "cliente"
  },
  "message": "Usuario registrado exitosamente"
}
```

**Cookies:**
- `refreshToken`: HttpOnly cookie con refresh token (30 días)

**Rate Limiting:**
- 5 intentos por minuto por IP
- 5 intentos por minuto por usuario

**Validaciones:**
- Username: 3-150 caracteres, solo alfanuméricos, guiones, guiones bajos
- Email: Debe ser único y válido
- Password: 8-128 caracteres, debe contener números y letras
- First/Last Name: Solo letras, espacios, guiones, apóstrofes

**Errores:**
- `400 Bad Request`: Validación fallida
- `429 Too Many Requests`: Demasiados intentos

---

### 2. POST `/api/auth/login/`

**Descripción:** Inicia sesión con credenciales (username o email).

**Request:**
```json
{
  "username": "juan_perez",
  "password": "MiPassword123"
}
```

O con email:
```json
{
  "username": "juan@example.com",
  "password": "MiPassword123"
}
```

**Response (200 OK):**
```json
{
  "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "juan@example.com",
    "nombre": "Juan Pérez",
    "rol": "cliente"
  },
  "message": "Login exitoso"
}
```

**Cookies:**
- `refreshToken`: HttpOnly cookie con refresh token (30 días)

**Rate Limiting:**
- 5 intentos por minuto por IP
- 5 intentos por minuto por usuario

**Response (429 Too Many Requests):**
```json
{
  "error": "Demasiados intentos de inicio de sesión",
  "bloqueado": true,
  "tiempo_restante": 45,
  "mensaje": "Has excedido el límite de intentos. Intenta de nuevo en 45 segundos."
}
```

**Errores:**
- `400 Bad Request`: Username/email o contraseña no proporcionados
- `401 Unauthorized`: Credenciales inválidas
- `429 Too Many Requests`: Demasiados intentos

---

### 3. POST `/api/auth/refresh/`

**Descripción:** Refresca el Access Token usando el Refresh Token de la cookie.

**Request:**
- No requiere body
- Envía automáticamente `refreshToken` desde la cookie

**Response (200 OK):**
```json
{
  "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "juan@example.com",
    "nombre": "Juan Pérez",
    "rol": "cliente"
  },
  "message": "Token refrescado exitosamente"
}
```

**Cookies:**
- `refreshToken`: Nuevo refresh token (rotación automática)

**Características:**
- Genera nuevo Access Token (15 minutos)
- Genera nuevo Refresh Token (30 días) - **ROTACIÓN**
- Invalida el Refresh Token anterior
- Automático en interceptor de axios

**Errores:**
- `401 Unauthorized`: Refresh token no encontrado o inválido/expirado

---

### 4. POST `/api/auth/logout/`

**Descripción:** Cierra sesión e invalida todos los tokens del usuario.

**Request:**
- Header: `Authorization: Bearer <accessToken>`
- Cookie: `refreshToken` (automático)

```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Cookie: refreshToken=..."
```

**Response (200 OK):**
```json
{
  "message": "Logout exitoso"
}
```

**Acciones:**
- Invalida Access Token en blacklist
- Revoca todos los Refresh Tokens del usuario
- Elimina cookie `refreshToken`
- Registra logout en logs de seguridad

**Errores:**
- `401 Unauthorized`: Token no válido o usuario no autenticado

---

### 5. GET `/api/auth/csrf-token/`

**Descripción:** Obtiene el CSRF token para proteger peticiones mutables.

**Request:**
```bash
curl -X GET http://localhost:8000/api/auth/csrf-token/
```

**Response (200 OK):**
```json
{
  "csrfToken": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
  "message": "CSRF token obtenido exitosamente"
}
```

**Cookies:**
- `csrftoken`: Cookie con CSRF token (1 año)

**Uso:**
El token debe incluirse en el header `X-CSRFToken` para peticiones POST/PUT/DELETE/PATCH:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "X-CSRFToken: abc123def456ghi789jkl012mno345pqr678stu901vwx234yz" \
  -H "Content-Type: application/json" \
  -d '{"username":"juan_perez","password":"MiPassword123"}'
```

**Errores:**
- Ninguno (siempre retorna 200)

---

## Flujo de Autenticación

### 1. Registro
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Frontend envía credenciales a POST /auth/register/       │
├─────────────────────────────────────────────────────────────┤
│ 2. Backend valida y sanitiza entrada                        │
│ 3. Backend crea usuario con contraseña hasheada             │
│ 4. Backend genera Access Token (JWT - 15 min)               │
│ 5. Backend genera Refresh Token (30 días)                   │
├─────────────────────────────────────────────────────────────┤
│ 6. Backend retorna:                                         │
│    - accessToken en body (JSON)                             │
│    - refreshToken en HttpOnly cookie                        │
│    - user data (id, email, nombre, rol)                     │
├─────────────────────────────────────────────────────────────┤
│ 7. Frontend almacena:                                       │
│    - accessToken en sessionStorage                          │
│    - user data en Zustand store                             │
│    - refreshToken en cookie (automático)                    │
└─────────────────────────────────────────────────────────────┘
```

### 2. Login
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Frontend envía credenciales a POST /auth/login/          │
├─────────────────────────────────────────────────────────────┤
│ 2. Backend valida rate limiting (5 intentos/min)            │
│ 3. Backend autentica usuario                                │
│ 4. Backend genera Access Token + Refresh Token              │
├─────────────────────────────────────────────────────────────┤
│ 5. Backend retorna tokens (igual que registro)              │
├─────────────────────────────────────────────────────────────┤
│ 6. Frontend almacena tokens (igual que registro)            │
└─────────────────────────────────────────────────────────────┘
```

### 3. Petición Autenticada
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Frontend obtiene accessToken de sessionStorage            │
│ 2. Frontend obtiene CSRF token de cookie                    │
│ 3. Frontend envía petición con headers:                     │
│    - Authorization: Bearer <accessToken>                    │
│    - X-CSRFToken: <csrfToken>                               │
├─────────────────────────────────────────────────────────────┤
│ 4. Backend valida:                                          │
│    - JWT signature y exp claim                              │
│    - Token no está en blacklist                             │
│    - CSRF token es válido                                   │
│    - Usuario está activo                                    │
├─────────────────────────────────────────────────────────────┤
│ 5. Backend procesa petición                                 │
│ 6. Backend retorna respuesta                                │
└─────────────────────────────────────────────────────────────┘
```

### 4. Token Expira
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Frontend envía petición con accessToken expirado         │
├─────────────────────────────────────────────────────────────┤
│ 2. Backend retorna 401 Unauthorized                         │
├─────────────────────────────────────────────────────────────┤
│ 3. Frontend interceptor detecta 401                         │
│ 4. Frontend envía POST /auth/refresh/ automáticamente       │
│ 5. Backend genera nuevo accessToken                         │
│ 6. Backend genera nuevo refreshToken (rotación)             │
│ 7. Backend invalida refreshToken anterior                   │
├─────────────────────────────────────────────────────────────┤
│ 8. Frontend actualiza accessToken en sessionStorage         │
│ 9. Frontend reintenta petición original                     │
│ 10. Petición se completa exitosamente                       │
└─────────────────────────────────────────────────────────────┘
```

### 5. Logout
```
┌─────────────────────────────────────────────────────────────┐
│ 1. Frontend envía POST /auth/logout/                        │
│    - Header: Authorization: Bearer <accessToken>           │
│    - Cookie: refreshToken (automático)                      │
├─────────────────────────────────────────────────────────────┤
│ 2. Backend invalida accessToken en blacklist                │
│ 3. Backend revoca todos los refreshTokens del usuario       │
│ 4. Backend elimina cookie refreshToken                      │
├─────────────────────────────────────────────────────────────┤
│ 5. Frontend limpia:                                         │
│    - accessToken de sessionStorage                          │
│    - user data de Zustand store                             │
│    - refreshToken de cookie (automático)                    │
│ 6. Frontend redirige a login                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Seguridad

### Access Token
- **Duración:** 15 minutos
- **Almacenamiento:** sessionStorage (frontend)
- **Validación:** 
  - Firma JWT (HS256)
  - Exp claim (expiración)
  - Claims requeridos: user_id, username, email, rol, iat, exp
  - Tipos de datos validados
  - No está en blacklist
- **Invalidación:** Al logout, se agrega a blacklist

### Refresh Token
- **Duración:** 30 días
- **Almacenamiento:** HttpOnly cookie (no accesible desde JS)
- **Rotación:** Cada refresh genera nuevo token
- **Revocación:** Al logout, todos se revocan
- **Seguridad:** 
  - Secure flag (HTTPS en producción)
  - HttpOnly flag
  - SameSite=Lax

### CSRF Protection
- **Token:** Obtenido de GET /auth/csrf-token/
- **Almacenamiento:** Cookie `csrftoken`
- **Validación:** Header `X-CSRFToken` en POST/PUT/DELETE/PATCH
- **SameSite:** Lax (protección contra CSRF)

### Rate Limiting
- **Login:** 5 intentos por minuto por IP
- **Register:** 5 intentos por minuto por IP
- **Bloqueo:** Automático después de 5 intentos fallidos
- **Tiempo restante:** Retornado en respuesta 429

### Validación de Entrada
- **Username:** 3-150 chars, solo alfanuméricos, guiones, guiones bajos
- **Email:** Único, válido, lowercase
- **Password:** 8-128 chars, números y letras, no solo números/letras
- **Nombres:** Solo letras, espacios, guiones, apóstrofes
- **Sanitización:** Trim, lowercase, validación de caracteres

### Logging de Seguridad
- **Login exitoso:** Usuario, email, IP, rol
- **Login fallido:** Usuario, IP, razón
- **Refresh exitoso:** Usuario, IP
- **Refresh fallido:** Razón del error
- **Logout:** Usuario, IP
- **Tokens revocados:** Usuario, IP
- **Validaciones fallidas:** Detalles del error

---

## Errores Comunes

### 401 Unauthorized
**Causas posibles:**
- Token expirado
- Token inválido o corrupto
- Token en blacklist (logout)
- Usuario inactivo
- Usuario no encontrado
- Claims inválidos en token

**Solución:**
- Frontend detecta 401 automáticamente
- Intenta refrescar token con POST /auth/refresh/
- Si refresh falla, redirige a login

### 429 Too Many Requests
**Causas posibles:**
- Más de 5 intentos de login en 1 minuto (por IP)
- Más de 5 intentos de registro en 1 minuto (por IP)

**Solución:**
- Esperar `tiempo_restante` segundos
- Frontend muestra contador regresivo
- Después del tiempo, se pueden reintentar

### 400 Bad Request
**Causas posibles:**
- Username/email o contraseña no proporcionados
- Validación fallida (username, email, password, etc.)
- Caracteres inválidos en entrada

**Solución:**
- Verificar que todos los campos requeridos estén presentes
- Verificar formato de entrada
- Revisar mensaje de error en respuesta

### 403 Forbidden
**Causas posibles:**
- CSRF token inválido o no proporcionado
- Token CSRF no coincide con cookie

**Solución:**
- Obtener nuevo CSRF token de GET /auth/csrf-token/
- Incluir token en header X-CSRFToken
- Verificar que cookies estén habilitadas

---

## Ejemplos de Uso

### JavaScript/TypeScript (Axios)

**Registro:**
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  withCredentials: true, // Enviar cookies
});

async function register() {
  try {
    const response = await api.post('/auth/register/', {
      username: 'juan_perez',
      email: 'juan@example.com',
      password: 'MiPassword123',
      first_name: 'Juan',
      last_name: 'Pérez'
    });
    
    // Guardar accessToken
    sessionStorage.setItem('accessToken', response.data.accessToken);
    
    // refreshToken está en cookie automáticamente
    console.log('Registro exitoso:', response.data.user);
  } catch (error) {
    console.error('Error en registro:', error.response.data);
  }
}
```

**Login:**
```typescript
async function login() {
  try {
    const response = await api.post('/auth/login/', {
      username: 'juan_perez',
      password: 'MiPassword123'
    });
    
    sessionStorage.setItem('accessToken', response.data.accessToken);
    console.log('Login exitoso:', response.data.user);
  } catch (error) {
    if (error.response.status === 429) {
      console.error('Demasiados intentos. Espera:', error.response.data.tiempo_restante, 'segundos');
    } else {
      console.error('Error en login:', error.response.data);
    }
  }
}
```

**Petición Autenticada:**
```typescript
async function obtenerPerfil() {
  try {
    const accessToken = sessionStorage.getItem('accessToken');
    
    const response = await api.get('/usuarios/perfil/', {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    console.log('Perfil:', response.data);
  } catch (error) {
    if (error.response.status === 401) {
      // Token expirado, interceptor refrescará automáticamente
      console.log('Token expirado, refrescando...');
    }
  }
}
```

**Logout:**
```typescript
async function logout() {
  try {
    const accessToken = sessionStorage.getItem('accessToken');
    
    await api.post('/auth/logout/', {}, {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    // Limpiar tokens
    sessionStorage.removeItem('accessToken');
    
    console.log('Logout exitoso');
  } catch (error) {
    console.error('Error en logout:', error.response.data);
  }
}
```

### cURL

**Obtener CSRF Token:**
```bash
curl -X GET http://localhost:8000/api/auth/csrf-token/ \
  -H "Content-Type: application/json" \
  -c cookies.txt
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <csrf_token>" \
  -b cookies.txt \
  -c cookies.txt \
  -d '{
    "username": "juan_perez",
    "password": "MiPassword123"
  }'
```

**Petición Autenticada:**
```bash
curl -X GET http://localhost:8000/api/usuarios/perfil/ \
  -H "Authorization: Bearer <access_token>" \
  -H "X-CSRFToken: <csrf_token>" \
  -b cookies.txt
```

**Logout:**
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "X-CSRFToken: <csrf_token>" \
  -b cookies.txt
```

---

## Configuración de Producción

### HTTPS Obligatorio
```python
# settings.py
CSRF_COOKIE_SECURE = True  # Solo HTTPS
SESSION_COOKIE_SECURE = True  # Solo HTTPS
SECURE_SSL_REDIRECT = True  # Redirigir HTTP a HTTPS
```

### CORS Restringido
```python
CORS_ALLOWED_ORIGINS = [
    'https://electro-isla.com',
    'https://www.electro-isla.com',
]
```

### Dominios de Confianza CSRF
```python
CSRF_TRUSTED_ORIGINS = [
    'https://electro-isla.com',
    'https://www.electro-isla.com',
]
```

---

## Monitoreo y Logs

### Archivos de Log
- **Security Log:** `backend/logs/security.log`
- **Auth Log:** `backend/logs/auth.log`

### Eventos Registrados
- Intentos de login (éxito/fallo)
- Intentos de registro (éxito/fallo)
- Refresh de tokens
- Logout
- Tokens invalidados
- Validaciones fallidas
- Errores de seguridad

### Acceso a Logs
```bash
# Ver últimas líneas
tail -f backend/logs/security.log

# Buscar intentos fallidos
grep "LOGIN_FAILED" backend/logs/security.log

# Buscar tokens invalidados
grep "LOGOUT_SUCCESS" backend/logs/auth.log
```

---

## Soporte

Para reportar problemas o sugerencias, contactar al equipo de desarrollo.
