# 🔐 Sistema de Autenticación JWT + Refresh Token

## ✅ Implementación Completada

Se ha implementado un sistema de autenticación seguro usando **JWT (JSON Web Tokens)** con **Refresh Tokens** almacenados en **HTTP-Only Cookies**.

---

## 📋 Características Implementadas

### 1. **Access Token (JWT)**
- ⏱️ **Duración**: 15 minutos
- 🔒 **Almacenamiento**: Memoria del frontend (variable)
- 📦 **Contenido**: user_id, username, email, rol
- 🔐 **Algoritmo**: HS256 (HMAC con SHA-256)

### 2. **Refresh Token**
- ⏱️ **Duración**: 30 días
- 🔒 **Almacenamiento**: HTTP-Only Cookie (seguro contra XSS)
- 💾 **Base de datos**: Hasheado con SHA-256
- 🔄 **Rotación**: Se genera uno nuevo en cada refresh
- ❌ **Revocación**: Soporte para logout global

### 3. **Seguridad**
- ✅ Tokens hasheados en base de datos (SHA-256)
- ✅ HTTP-Only Cookies (no accesibles desde JavaScript)
- ✅ SameSite=Lax (protección CSRF)
- ✅ Rotación de Refresh Tokens
- ✅ Revocación de tokens
- ✅ Auditoría de dispositivos (IP, User-Agent)
- ✅ Limpieza automática de tokens expirados

---

## 🔌 Endpoints de Autenticación

### 1. **Registro** - `POST /api/auth/register/`
```json
// Request
{
  "username": "usuario",
  "email": "usuario@example.com",
  "password": "contraseña123",
  "first_name": "Nombre",
  "last_name": "Apellido"
}

// Response
{
  "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "nombre": "Nombre Apellido",
    "rol": "cliente"
  },
  "message": "Usuario registrado exitosamente"
}
// + Cookie HTTP-Only: refreshToken
```

### 2. **Login** - `POST /api/auth/login/`
```json
// Request
{
  "username": "usuario",  // o email
  "password": "contraseña123"
}

// Response (igual que registro)
{
  "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": { ... },
  "message": "Login exitoso"
}
// + Cookie HTTP-Only: refreshToken
```

### 3. **Refresh Token** - `POST /api/auth/refresh/`
```json
// Request: Vacío (el refresh token viene en la cookie)
{}

// Response
{
  "accessToken": "eyJ0eXAiOiJKV1QiLCJhbGc...",  // Nuevo token
  "user": { ... },
  "message": "Token refrescado exitosamente"
}
// + Cookie HTTP-Only: refreshToken (nuevo token rotado)
```

### 4. **Logout** - `POST /api/auth/logout/`
```json
// Request: Vacío
{}

// Response
{
  "message": "Logout exitoso"
}
// + Cookie eliminada + Todos los tokens del usuario revocados
```

---

## 🔧 Uso en el Frontend

### Configuración de Axios

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  withCredentials: true,  // ¡IMPORTANTE! Para enviar cookies
});

// Interceptor para agregar Access Token
api.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para refrescar token automáticamente
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si el token expiró (401) y no hemos intentado refrescar
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Refrescar token
        const { data } = await axios.post(
          'http://localhost:8000/api/auth/refresh/',
          {},
          { withCredentials: true }
        );

        // Guardar nuevo access token
        localStorage.setItem('accessToken', data.accessToken);

        // Reintentar petición original
        originalRequest.headers.Authorization = `Bearer ${data.accessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Si falla el refresh, redirigir a login
        localStorage.removeItem('accessToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

### Login

```javascript
const login = async (username, password) => {
  try {
    const { data } = await api.post('/auth/login/', {
      username,
      password
    });

    // Guardar access token
    localStorage.setItem('accessToken', data.accessToken);
    
    // Guardar info del usuario
    localStorage.setItem('user', JSON.stringify(data.user));

    return data;
  } catch (error) {
    console.error('Error en login:', error);
    throw error;
  }
};
```

### Logout

```javascript
const logout = async () => {
  try {
    await api.post('/auth/logout/');
    
    // Limpiar storage
    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
    
    // Redirigir a login
    window.location.href = '/login';
  } catch (error) {
    console.error('Error en logout:', error);
  }
};
```

---

## 🗄️ Modelo de Base de Datos

### Tabla: `refresh_tokens`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | Integer | ID único |
| `usuario_id` | ForeignKey | Usuario propietario |
| `token_hash` | CharField(64) | Token hasheado (SHA-256) |
| `jti` | CharField(36) | JWT ID único |
| `user_agent` | CharField(500) | Navegador/dispositivo |
| `ip_address` | GenericIPAddress | IP del cliente |
| `created_at` | DateTime | Fecha de creación |
| `expires_at` | DateTime | Fecha de expiración |
| `revocado` | Boolean | Si fue revocado |
| `revocado_at` | DateTime | Cuándo fue revocado |
| `last_used_at` | DateTime | Última vez usado |

---

## 🛠️ Comandos de Administración

### Limpiar tokens expirados
```bash
python manage.py limpiar_tokens
```

Este comando elimina todos los refresh tokens que ya expiraron de la base de datos.

**Recomendación**: Ejecutar este comando periódicamente (ej: cron job diario).

---

## 🔍 Auditoría

El sistema registra:
- ✅ IP del cliente
- ✅ User-Agent (navegador/dispositivo)
- ✅ Fecha de creación del token
- ✅ Última vez que se usó
- ✅ Fecha de revocación (si aplica)

Esto permite:
- Ver todos los dispositivos donde el usuario tiene sesión activa
- Revocar sesiones específicas
- Detectar accesos sospechosos

---

## 🚀 Flujo Completo

```
1. Usuario hace LOGIN
   ↓
2. Backend genera:
   - Access Token (JWT, 15 min) → Frontend (memoria)
   - Refresh Token (30 días) → Cookie HTTP-Only
   ↓
3. Frontend usa Access Token en cada petición
   ↓
4. Después de 15 minutos, Access Token expira
   ↓
5. Frontend detecta error 401
   ↓
6. Frontend llama a /auth/refresh/ automáticamente
   ↓
7. Backend verifica Refresh Token (desde cookie)
   ↓
8. Backend genera nuevos tokens:
   - Nuevo Access Token → Frontend
   - Nuevo Refresh Token → Cookie (rotación)
   - Revoca el Refresh Token anterior
   ↓
9. Frontend reintenta la petición original con el nuevo token
   ↓
10. Usuario sigue navegando sin interrupciones
```

---

## ⚠️ Importante para Producción

### En `settings.py`, cambiar:

```python
# DESARROLLO (HTTP)
response.set_cookie(
    key='refreshToken',
    value=refresh_token_plano,
    max_age=30 * 24 * 60 * 60,
    httponly=True,
    secure=False,  # ← Cambiar a True en producción
    samesite='Lax',
    path='/api/auth/'
)

# PRODUCCIÓN (HTTPS)
response.set_cookie(
    key='refreshToken',
    value=refresh_token_plano,
    max_age=30 * 24 * 60 * 60,
    httponly=True,
    secure=True,  # ← HTTPS obligatorio
    samesite='Strict',  # ← Más restrictivo
    path='/api/auth/'
)
```

---

## 📝 Historial de Auditoría

### Problema Solucionado: Imágenes Base64

Antes, el historial mostraba imágenes base64 completas (miles de caracteres).

**Solución implementada**: El serializer `AuditLogSerializer` ahora detecta y reemplaza imágenes base64 con indicadores:

```json
// Antes
{
  "imagen_url": "data:image/jpeg;base64,/9j/4AAQSkZJRg..." // 50,000 caracteres
}

// Ahora
{
  "imagen_url": "[IMAGEN_JPEG]"
}
```

---

## ✅ Checklist de Seguridad

- [x] Access Token con expiración corta (15 min)
- [x] Refresh Token con expiración larga (30 días)
- [x] Refresh Token en HTTP-Only Cookie
- [x] Tokens hasheados en base de datos (SHA-256)
- [x] Rotación de Refresh Tokens
- [x] Revocación de tokens (logout global)
- [x] Auditoría de dispositivos
- [x] Limpieza de tokens expirados
- [x] Protección CSRF (SameSite)
- [x] Middleware de autenticación JWT
- [x] Sanitización de datos sensibles en logs

---

## 🎯 Próximos Pasos

1. ✅ Ejecutar migraciones
2. ✅ Actualizar frontend para usar el nuevo sistema
3. ⏳ Configurar cron job para limpiar tokens
4. ⏳ Configurar `secure=True` en producción
5. ⏳ Implementar rate limiting en endpoints de auth

---

## 📚 Referencias

- [JWT.io](https://jwt.io/)
- [OWASP - JWT Security](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [RFC 7519 - JWT](https://tools.ietf.org/html/rfc7519)
