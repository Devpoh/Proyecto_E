# 🔒 Guía de Seguridad - Electro Isla Backend

## 📧 Configuración de Email (Gmail)

### ⚠️ IMPORTANTE: Nunca expongas tus credenciales

El archivo `.env` contiene información sensible y **NUNCA** debe ser subido a Git o compartido públicamente.

### ✅ Archivos de Seguridad Implementados

1. **`.env`** - Contiene las credenciales reales (NUNCA subir a Git)
2. **`.env.example`** - Plantilla sin credenciales (SÍ subir a Git)
3. **`.gitignore`** - Protege archivos sensibles

---

## 🔐 Contraseña de Aplicación de Gmail

### Cómo obtener una contraseña de aplicación:

1. **Ir a tu cuenta de Google:**
   - https://myaccount.google.com/security

2. **Activar verificación en 2 pasos:**
   - Seguridad → Verificación en 2 pasos → Activar

3. **Generar contraseña de aplicación:**
   - Seguridad → Contraseñas de aplicaciones
   - Seleccionar app: "Correo"
   - Seleccionar dispositivo: "Otro (nombre personalizado)"
   - Escribir: "Django Electro Isla"
   - Copiar la contraseña de 16 caracteres

4. **Guardar en .env (SIN ESPACIOS):**
   ```env
   EMAIL_HOST_PASSWORD=abcdabcdabcdabcd
   ```

---

## 🛡️ Mejores Prácticas de Seguridad

### ✅ DO (Hacer):

- ✅ Usar contraseñas de aplicación, NO tu contraseña de Gmail
- ✅ Mantener `.env` en `.gitignore`
- ✅ Usar `.env.example` para documentar variables necesarias
- ✅ Rotar contraseñas de aplicación periódicamente
- ✅ Usar variables de entorno en producción
- ✅ Mantener `DEBUG=False` en producción

### ❌ DON'T (No hacer):

- ❌ Subir `.env` a Git
- ❌ Compartir credenciales en chat/email
- ❌ Usar tu contraseña personal de Gmail
- ❌ Hardcodear credenciales en el código
- ❌ Dejar `DEBUG=True` en producción
- ❌ Compartir el `SECRET_KEY`

---

## 🔄 Rotar Credenciales

Si crees que tus credenciales fueron expuestas:

1. **Revocar contraseña de aplicación:**
   - https://myaccount.google.com/apppasswords
   - Eliminar la contraseña comprometida

2. **Generar nueva contraseña:**
   - Seguir los pasos anteriores
   - Actualizar `.env` con la nueva contraseña

3. **Reiniciar servidor Django:**
   ```bash
   python manage.py runserver
   ```

---

## 📋 Checklist de Seguridad

Antes de hacer commit:

- [ ] `.env` está en `.gitignore`
- [ ] `.env.example` está actualizado (sin credenciales reales)
- [ ] No hay credenciales hardcodeadas en el código
- [ ] `SECRET_KEY` es único y seguro
- [ ] Contraseñas de aplicación (no contraseñas personales)

---

## 🚀 Configuración en Producción

En producción, usa variables de entorno del sistema:

```bash
# Linux/Mac
export EMAIL_HOST_USER="isla.verificacion@gmail.com"
export EMAIL_HOST_PASSWORD="your-app-password"

# Windows PowerShell
$env:EMAIL_HOST_USER="isla.verificacion@gmail.com"
$env:EMAIL_HOST_PASSWORD="your-app-password"
```

O usa servicios como:
- **Heroku:** Config Vars
- **AWS:** Parameter Store / Secrets Manager
- **Azure:** Key Vault
- **Google Cloud:** Secret Manager

---

## 📞 Contacto de Seguridad

Si encuentras una vulnerabilidad de seguridad, por favor:
1. NO la publiques públicamente
2. Contacta al equipo de desarrollo directamente
3. Proporciona detalles para reproducir el problema

---

**Última actualización:** 25 de Noviembre, 2025
