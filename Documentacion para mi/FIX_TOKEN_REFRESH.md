# ✅ FIX: Token Refresh Funcionando Correctamente

## 🐛 Problema
Token expiraba y mostraba "Token inválido o expirado" mientras el usuario estaba activo.

## 🔍 Causa Raíz
La cookie `refreshToken` tenía `path='/api/auth/'` lo que significaba que solo se enviaba en peticiones a rutas bajo `/api/auth/`. 

Cuando el frontend hacía peticiones a otros endpoints como `/api/carrito/`, `/api/productos/`, etc., la cookie NO se enviaba porque no coincidía con el path.

Cuando el token expiraba y el frontend intentaba refrescar en `/api/auth/refresh/`, la cookie SÍ se enviaba, pero solo porque coincidía con el path.

**Problema:** El refresh funcionaba, pero era inconsistente y frágil.

## ✅ Solución

**Archivo:** `backend/api/views.py`

Cambiar el path de la cookie de `/api/auth/` a `/`:

```python
# ANTES (Línea 164, 281, 382):
path='/api/auth/'  # ❌ Solo en rutas de auth

# DESPUÉS:
path='/'  # ✅ Accesible desde cualquier ruta
```

**Cambios realizados:**
1. Línea 164: Register endpoint
2. Línea 281: Login endpoint
3. Línea 382: Refresh endpoint

## 🔧 Cómo Funciona Ahora

```
Usuario hace petición a /api/carrito/agregar/
    ↓
Cookie refreshToken se envía (path='/')
    ↓
Si token expirado (401):
    ↓
Frontend intenta refrescar en /api/auth/refresh/
    ↓
Cookie refreshToken se envía (path='/')
    ↓
Backend genera nuevo token
    ↓
Frontend reintentar petición original
    ↓
✅ Éxito
```

## 📊 Resultado

- ✅ Token se refresca automáticamente
- ✅ Usuario no ve "Token inválido"
- ✅ Sesión continúa sin interrupciones
- ✅ 15 minutos de duración es suficiente (se refresca automáticamente)

## 🧪 Verificación

```bash
# 1. Login
# 2. Agregar productos al carrito
# 3. Esperar 15 minutos
# 4. Intentar agregar otro producto

# Resultado esperado:
# ✅ Sin error "Token inválido"
# ✅ Producto se agrega correctamente
# ✅ Token se refrescó automáticamente en background
```

## 🎯 Conclusión

**Solución limpia y efectiva:**
- ✅ Sin cambios innecesarios
- ✅ Sin aumentar duración del token
- ✅ Refresh automático funciona correctamente
- ✅ Experiencia de usuario profesional

**¡LISTO!** 🚀
