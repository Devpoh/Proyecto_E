# 🚀 COMANDOS FINALES - Sistema JWT + Rate Limiting

## ✅ Todo lo que necesitas ejecutar para completar la implementación

---

## 📋 PASO 1: Crear Migraciones (Backend)

Abre PowerShell en la carpeta `backend` y ejecuta:

```powershell
# Crear migraciones para los nuevos modelos
python manage.py makemigrations

# Aplicar migraciones a la base de datos
python manage.py migrate
```

**Esto creará las tablas:**
- ✅ `refresh_tokens` - Para almacenar tokens de refresco
- ✅ `login_attempts` - Para rate limiting

---

## 📋 PASO 2: Probar el Sistema Manualmente

### Probar limpieza de tokens

```powershell
python manage.py limpiar_tokens
```

**Salida esperada:**
```
🧹 Iniciando limpieza...
  → Limpiando tokens expirados...
    ✓ No hay tokens expirados para eliminar
  → Limpiando intentos de login antiguos...
    ✓ No hay intentos de login antiguos para eliminar

✅ Limpieza completada exitosamente
```

---

## 📋 PASO 3: Configurar Tarea Programada (OPCIONAL pero RECOMENDADO)

### Para Windows:

1. **Abre PowerShell como Administrador** (clic derecho → "Ejecutar como administrador")

2. Navega a la carpeta del backend:
```powershell
cd "C:\Users\Alejandro\Desktop\Electro-Isla\backend"
```

3. Ejecuta el script de configuración:
```powershell
.\configurar_tarea_programada.ps1
```

4. Verifica que la tarea se creó correctamente:
```powershell
Get-ScheduledTask -TaskName "ElectroIsla_LimpiarTokens"
```

**Esto configurará una tarea que se ejecuta automáticamente cada día a las 3:00 AM para limpiar tokens expirados.**

---

## 📋 PASO 4: Iniciar el Servidor Backend

```powershell
python manage.py runserver
```

**El servidor debería iniciar en:** `http://localhost:8000`

---

## 📋 PASO 5: Iniciar el Frontend

Abre otra terminal PowerShell en la carpeta `frontend/electro_isla` y ejecuta:

```powershell
npm run dev
```

**El frontend debería iniciar en:** `http://localhost:5173` (o el puerto que Vite asigne)

---

## 🧪 PASO 6: Probar el Sistema Completo

### Probar Login Normal

1. Ve a `http://localhost:5173/login`
2. Intenta hacer login con credenciales válidas
3. Verifica que:
   - ✅ Se guarda `accessToken` en localStorage
   - ✅ Se crea una cookie `refreshToken` (HTTP-Only)
   - ✅ Rediriges según el rol del usuario

### Probar Rate Limiting

1. Ve a `http://localhost:5173/login`
2. Intenta hacer login **5 veces** con credenciales incorrectas
3. Verifica que:
   - ✅ Aparece el componente de bloqueo
   - ✅ Muestra un contador regresivo de 60 segundos
   - ✅ El formulario está oculto
   - ✅ Después de 60 segundos, se desbloquea automáticamente

### Probar Refresh Token Automático

1. Inicia sesión normalmente
2. Espera 15 minutos (o modifica el tiempo de expiración en `jwt_utils.py` para probar más rápido)
3. Haz una petición a la API (ej: ver productos)
4. Verifica que:
   - ✅ El token se refresca automáticamente
   - ✅ La petición se completa sin errores
   - ✅ No te redirige a login

### Probar Logout

1. Estando logueado, haz logout
2. Verifica que:
   - ✅ Se elimina `accessToken` de localStorage
   - ✅ Se elimina la cookie `refreshToken`
   - ✅ Todos los tokens del usuario se revocan en la BD
   - ✅ Rediriges a login

---

## 🔍 PASO 7: Verificar en la Base de Datos

### Ver tokens de refresco

```sql
SELECT * FROM refresh_tokens ORDER BY created_at DESC LIMIT 10;
```

### Ver intentos de login

```sql
SELECT * FROM login_attempts ORDER BY timestamp DESC LIMIT 20;
```

---

## 📊 PASO 8: Monitoreo (OPCIONAL)

### Ver logs de limpieza automática

```powershell
# Ver últimas 50 líneas del log
Get-Content backend\logs\limpieza_tokens.log -Tail 50
```

### Ver tarea programada en ejecución

```powershell
# Ver última ejecución
Get-ScheduledTask -TaskName "ElectroIsla_LimpiarTokens" | Get-ScheduledTaskInfo
```

### Ejecutar tarea manualmente (para probar)

```powershell
Start-ScheduledTask -TaskName "ElectroIsla_LimpiarTokens"
```

---

## ⚠️ TROUBLESHOOTING

### Error: "No module named 'jwt'"

```powershell
pip install PyJWT==2.8.0
```

### Error: "Table doesn't exist"

```powershell
python manage.py migrate
```

### Error: "CORS policy"

Verifica que en `settings.py` tengas:

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

CORS_ALLOW_CREDENTIALS = True
```

### Error: "Cookie not being sent"

Verifica que en Axios tengas:

```typescript
withCredentials: true
```

### Frontend no muestra el componente de bloqueo

Verifica que:
1. El backend retorne status 429
2. El hook `useLogin` o `useRegister` esté capturando el error
3. El componente `RateLimitBlock` esté importado correctamente

---

## 📝 RESUMEN DE ARCHIVOS MODIFICADOS/CREADOS

### Backend

**Modificados:**
- ✅ `requirements.txt` - PyJWT agregado
- ✅ `api/models.py` - RefreshToken y LoginAttempt agregados
- ✅ `api/views.py` - Login/Register/Logout/Refresh actualizados con rate limiting
- ✅ `api/urls.py` - Endpoint /auth/refresh/ agregado
- ✅ `api/middleware.py` - JWT Authentication Middleware
- ✅ `api/serializers_admin.py` - Sanitización de imágenes base64
- ✅ `config/settings.py` - Middleware actualizado

**Creados:**
- ✅ `api/utils/jwt_utils.py` - Utilidades JWT
- ✅ `api/management/commands/limpiar_tokens.py` - Comando de limpieza
- ✅ `limpiar_tokens_auto.bat` - Script batch para tarea programada
- ✅ `configurar_tarea_programada.ps1` - Script PowerShell
- ✅ `SISTEMA_JWT_TOKENS.md` - Documentación JWT
- ✅ `RATE_LIMITING.md` - Documentación Rate Limiting

### Frontend

**Modificados:**
- ✅ `src/shared/api/axios.ts` - withCredentials + interceptor refresh
- ✅ `src/app/store/useAuthStore.ts` - accessToken en lugar de token
- ✅ `src/contexts/AuthContext.tsx` - accessToken en lugar de token
- ✅ `src/features/auth/login/types.ts` - accessToken en tipos
- ✅ `src/features/auth/register/types.ts` - accessToken en tipos
- ✅ `src/features/auth/login/hooks/useLogin.ts` - Rate limiting
- ✅ `src/features/auth/register/hooks/useRegister.ts` - Rate limiting
- ✅ `src/features/auth/login/ui/LoginForm.tsx` - Componente bloqueo
- ✅ `src/features/auth/register/ui/RegisterForm.tsx` - Componente bloqueo

**Creados:**
- ✅ `src/features/auth/components/RateLimitBlock.tsx` - Componente de bloqueo

---

## 🎯 CHECKLIST FINAL

Antes de considerar completo, verifica:

### Backend
- [ ] Migraciones aplicadas correctamente
- [ ] PyJWT instalado
- [ ] Servidor Django corriendo sin errores
- [ ] Endpoints de auth funcionando
- [ ] Rate limiting activado
- [ ] Comando limpiar_tokens funciona
- [ ] Tarea programada configurada (opcional)

### Frontend
- [ ] Axios configurado con withCredentials
- [ ] Interceptor de refresh funcionando
- [ ] Login guarda accessToken (no token)
- [ ] Register guarda accessToken (no token)
- [ ] Componente RateLimitBlock se muestra al bloquear
- [ ] Contador regresivo funciona
- [ ] Auto-desbloqueo funciona

### Pruebas
- [ ] Login exitoso funciona
- [ ] Logout funciona y revoca tokens
- [ ] Refresh automático funciona
- [ ] Rate limiting bloquea después de 5 intentos
- [ ] Componente de bloqueo se muestra correctamente
- [ ] Desbloqueo automático después de 60 segundos

---

## 🎉 ¡LISTO!

Si todos los pasos anteriores funcionan correctamente, tu sistema está completamente implementado con:

- ✅ **JWT Authentication** con Access Token (15 min) y Refresh Token (30 días)
- ✅ **HTTP-Only Cookies** para máxima seguridad
- ✅ **Refresh automático** transparente para el usuario
- ✅ **Rate Limiting** contra ataques de fuerza bruta
- ✅ **Componente visual** de bloqueo temporal
- ✅ **Limpieza automática** de tokens expirados
- ✅ **Auditoría completa** de intentos de login
- ✅ **Sanitización** de imágenes base64 en historial

**¡Tu aplicación ahora es mucho más segura! 🔐**
