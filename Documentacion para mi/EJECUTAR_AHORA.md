# ⚡ EJECUTAR AHORA - Comandos Inmediatos

## 🎯 Sigue estos pasos EN ORDEN

---

## 📍 PASO 1: Abrir PowerShell en Backend

```powershell
cd "C:\Users\Alejandro\Desktop\Electro-Isla\backend"
```

---

## 📍 PASO 2: Crear y Aplicar Migraciones

```powershell
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate
```

**✅ Deberías ver:**
```
Migrations for 'api':
  api\migrations\0XXX_refreshtoken_loginattempt.py
    - Create model RefreshToken
    - Create model LoginAttempt
Running migrations:
  Applying api.0XXX_refreshtoken_loginattempt... OK
```

---

## 📍 PASO 3: Probar Comando de Limpieza

```powershell
python manage.py limpiar_tokens
```

**✅ Deberías ver:**
```
🧹 Iniciando limpieza...
  → Limpiando tokens expirados...
    ✓ No hay tokens expirados para eliminar
  → Limpiando intentos de login antiguos...
    ✓ No hay intentos de login antiguos para eliminar

✅ Limpieza completada exitosamente
```

---

## 📍 PASO 4: Configurar Tarea Programada (OPCIONAL)

### Opción A: Automática (Recomendada)

1. **Cierra PowerShell actual**
2. **Abre PowerShell como Administrador** (clic derecho → "Ejecutar como administrador")
3. Ejecuta:

```powershell
cd "C:\Users\Alejandro\Desktop\Electro-Isla\backend"
.\configurar_tarea_programada.ps1
```

**✅ Deberías ver:**
```
✅ ¡Tarea programada configurada exitosamente!

📋 Detalles de la tarea:
   • Nombre: ElectroIsla_LimpiarTokens
   • Frecuencia: Diariamente a las 3:00 AM
   ...
```

### Opción B: Manual (Si no quieres tarea automática)

Simplemente ejecuta el comando de limpieza manualmente cuando lo necesites:

```powershell
python manage.py limpiar_tokens
```

---

## 📍 PASO 5: Iniciar Servidor Backend

```powershell
python manage.py runserver
```

**✅ Deberías ver:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

**🔴 NO CIERRES ESTA VENTANA - Déjala corriendo**

---

## 📍 PASO 6: Iniciar Frontend

1. **Abre OTRA ventana de PowerShell**
2. Navega al frontend:

```powershell
cd "C:\Users\Alejandro\Desktop\Electro-Isla\frontend\electro_isla"
```

3. Inicia el servidor de desarrollo:

```powershell
npm run dev
```

**✅ Deberías ver:**
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**🔴 NO CIERRES ESTA VENTANA - Déjala corriendo**

---

## 📍 PASO 7: Probar el Sistema

### 🧪 Test 1: Login Normal

1. Abre tu navegador en `http://localhost:5173/login`
2. Ingresa credenciales válidas
3. Haz login

**✅ Deberías:**
- Ver que te redirige correctamente
- En DevTools (F12) → Application → Local Storage → ver `accessToken`
- En DevTools → Application → Cookies → ver `refreshToken` (HTTP-Only)

---

### 🧪 Test 2: Rate Limiting

1. Ve a `http://localhost:5173/login`
2. Intenta hacer login **5 veces** con credenciales incorrectas
3. En el 5to intento:

**✅ Deberías ver:**
- El formulario de login desaparece
- Aparece un componente de bloqueo con:
  - Mensaje "Cuenta Temporalmente Bloqueada"
  - Contador regresivo (01:00, 00:59, 00:58...)
  - Información clara del bloqueo
- Después de 60 segundos, el formulario vuelve a aparecer

---

### 🧪 Test 3: Refresh Automático (Opcional - Requiere esperar)

**Para probar más rápido, modifica temporalmente:**

En `backend/api/utils/jwt_utils.py`, línea 22:
```python
# Cambiar de 15 minutos a 1 minuto para probar
ACCESS_TOKEN_LIFETIME = timedelta(minutes=1)  # Era: minutes=15
```

Luego:
1. Reinicia el servidor backend (Ctrl+C y `python manage.py runserver`)
2. Haz login
3. Espera 1 minuto
4. Haz cualquier acción (ej: navegar a productos)

**✅ Deberías:**
- Ver que la petición se completa sin errores
- NO ser redirigido a login
- En la consola del navegador (F12), ver que se hizo una petición a `/auth/refresh/`

**🔴 IMPORTANTE:** Después de probar, vuelve a cambiar a `minutes=15`

---

## 📍 PASO 8: Verificar Base de Datos (Opcional)

Si tienes acceso a tu base de datos, ejecuta:

```sql
-- Ver tokens de refresco
SELECT * FROM refresh_tokens ORDER BY created_at DESC LIMIT 10;

-- Ver intentos de login
SELECT * FROM login_attempts ORDER BY timestamp DESC LIMIT 20;
```

---

## 🎉 ¡LISTO!

Si todos los tests pasaron, tu sistema está **100% funcional** con:

- ✅ JWT Authentication
- ✅ Refresh Token automático
- ✅ Rate Limiting
- ✅ Componente de bloqueo visual
- ✅ Limpieza automática (si configuraste la tarea)

---

## ⚠️ Si algo falla...

### Error: "No module named 'jwt'"
```powershell
pip install PyJWT==2.8.0
```

### Error: "Table doesn't exist"
```powershell
python manage.py migrate
```

### Error: "CORS policy"
Verifica que el frontend esté en `http://localhost:5173` (o actualiza `CORS_ALLOWED_ORIGINS` en `settings.py`)

### Error: "Cookie not being sent"
Verifica que en `axios.ts` tengas `withCredentials: true`

### Componente de bloqueo no aparece
1. Verifica que hayas hecho 5 intentos fallidos
2. Abre DevTools (F12) → Network → ve la respuesta del servidor
3. Debería ser status 429 con `bloqueado: true`

---

## 📚 Documentación Completa

- 📖 `SISTEMA_JWT_TOKENS.md` - Todo sobre JWT
- 📖 `RATE_LIMITING.md` - Todo sobre rate limiting
- 📖 `COMANDOS_FINALES.md` - Guía completa
- 📖 `RESUMEN_IMPLEMENTACION.md` - Resumen ejecutivo

---

## 🚀 Siguiente Paso

Una vez que todo funcione correctamente:

1. ✅ Marca como completado en tu checklist
2. ✅ Haz commit de los cambios
3. ✅ Considera configurar la tarea programada si no lo hiciste
4. ✅ En producción, cambia `secure=False` a `secure=True` en las cookies

---

**¡Éxito! 🎉**
