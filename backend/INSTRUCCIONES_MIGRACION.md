# 🔄 Instrucciones de Migración - Sistema de Verificación de Email

## ✅ ERROR CORREGIDO

**Problema:** `ImportError: cannot import name 'AnonAuthThrottle'`

**Solución:** ✅ Corregido - Se cambió `AnonAuthThrottle` por `AnonLoginRateThrottle`

---

## 📋 PASOS PARA EJECUTAR LA MIGRACIÓN

### **Opción 1: PowerShell (Recomendado para Windows)**

```powershell
# Navegar al directorio backend
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend

# Ejecutar script de PowerShell
.\migrate.ps1
```

---

### **Opción 2: Comandos Manuales en PowerShell**

```powershell
# 1. Navegar al directorio backend
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend

# 2. Activar entorno virtual
.\venv\Scripts\Activate.ps1

# 3. Crear migraciones
python manage.py makemigrations

# 4. Aplicar migraciones
python manage.py migrate
```

---

### **Opción 3: CMD (Command Prompt)**

```cmd
REM 1. Navegar al directorio backend
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend

REM 2. Activar entorno virtual
venv\Scripts\activate.bat

REM 3. Crear migraciones
python manage.py makemigrations

REM 4. Aplicar migraciones
python manage.py migrate
```

---

### **Opción 4: Usar el archivo .bat**

```powershell
# En PowerShell, usar .\ para ejecutar scripts locales
.\migrate_email_verification.bat
```

---

## 🔍 VERIFICAR QUE LA MIGRACIÓN FUE EXITOSA

Después de ejecutar la migración, deberías ver:

```
Migrations for 'api':
  api\migrations\0XXX_emailverification.py
    - Create model EmailVerification

Operations to perform:
  Apply all migrations: admin, api, auth, contenttypes, sessions
Running migrations:
  Applying api.0XXX_emailverification... OK
```

---

## 🚀 SIGUIENTE PASO: INICIAR CELERY

Una vez completada la migración, inicia Celery:

### **Terminal 1: Celery Worker**

```powershell
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
.\venv\Scripts\Activate.ps1
celery -A config worker -l info --pool=solo
```

### **Terminal 2: Celery Beat (Scheduler)**

```powershell
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
.\venv\Scripts\Activate.ps1
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### **Terminal 3: Django Server**

```powershell
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

---

## 🧪 EJECUTAR TESTS

```powershell
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
.\venv\Scripts\Activate.ps1
python manage.py test api.tests.test_email_verification -v 2
```

---

## ❓ SOLUCIÓN DE PROBLEMAS

### **Error: "No se encontró el comando migrate_email_verification.bat"**

**Causa:** PowerShell no ejecuta scripts del directorio actual por seguridad.

**Solución:** Usar `.\` antes del nombre del script:
```powershell
.\migrate_email_verification.bat
```

---

### **Error: "cannot import name 'AnonAuthThrottle'"**

**Causa:** Nombre incorrecto del throttle.

**Solución:** ✅ Ya corregido en el código. El throttle correcto es `AnonLoginRateThrottle`.

---

### **Error: "No module named 'api.views_verificacion'"**

**Causa:** Archivo no encontrado o error de sintaxis.

**Solución:** Verificar que existe `backend/api/views_verificacion.py`

---

### **Error al enviar emails**

**Causa:** Credenciales de Gmail incorrectas o contraseña de aplicación mal configurada.

**Solución:**
1. Verificar `backend/.env`:
   ```
   EMAIL_HOST_USER=isla.verificacion@gmail.com
   EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion_sin_espacios
   ```

2. Generar nueva contraseña de aplicación:
   - Ir a: https://myaccount.google.com/apppasswords
   - Crear nueva contraseña de aplicación
   - Copiar sin espacios en `.env`

---

## ✅ CHECKLIST POST-MIGRACIÓN

```
✅ Migración ejecutada sin errores
✅ Modelo EmailVerification creado en BD
✅ Celery Worker iniciado
✅ Celery Beat iniciado
✅ Django server corriendo
✅ Tests pasando
✅ Email de prueba enviado correctamente
```

---

## 📞 SOPORTE

Si encuentras algún error, revisa:

1. **Logs de Django:** `backend/logs/`
2. **Logs de Celery:** En la terminal donde corre Celery
3. **Documentación:** `backend/VERIFICACION_EMAIL_RESUMEN.md`
4. **Notas:** `backend/NOTAS_IMPLEMENTACION.md`

---

**Sistema listo para usar después de completar estos pasos** 🚀✅
