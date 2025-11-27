# 🔐 AUDITORÍA DE SEGURIDAD - FLUJO DE RECUPERACIÓN DE CONTRASEÑA

## 📋 RESUMEN EJECUTIVO

Se realizó un análisis exhaustivo de seguridad del flujo de recuperación de contraseña (backend, frontend, emails y almacenamiento). Se identificaron **8 vulnerabilidades críticas y medianas** con sus respectivas soluciones.

---

## 🚨 VULNERABILIDADES ENCONTRADAS

### 1. ⚠️ **CRÍTICA: Contraseña en Logs de Error**

**Ubicación:** `views_recuperacion.py` línea 124, 275

**Problema:**
```python
logger_security.error(f'[FORGOT_PASSWORD_ERROR] {str(e)}')
logger_security.error(f'[RESET_PASSWORD_ERROR] {str(e)}')
```

Si ocurre una excepción durante el cambio de contraseña, la contraseña podría quedar en el stack trace y ser registrada en logs.

**Riesgo:** 
- Exposición de contraseñas en archivos de log
- Acceso a logs por atacantes
- Violación de GDPR/privacidad

**Solución:**
```python
# ✅ CORRECTO - No incluir detalles de la excepción
logger_security.error(f'[FORGOT_PASSWORD_ERROR] Error procesando solicitud')
logger_security.error(f'[RESET_PASSWORD_ERROR] Error al cambiar contraseña')

# Si necesitas logs detallados:
logger_security.debug(f'[FORGOT_PASSWORD_ERROR_DETAIL] {str(e)}')  # Solo en desarrollo
```

---

### 2. ⚠️ **CRÍTICA: Email del Usuario en Logs**

**Ubicación:** `views_recuperacion.py` línea 101, 115, 189, 269

**Problema:**
```python
logger_auth.info(f'[FORGOT_PASSWORD_SOLICITADO] Usuario: {usuario.username} | Email: {usuario.email}')
logger_security.info(f'[FORGOT_PASSWORD_EMAIL_NO_EXISTE] Email: {email} | IP: {ip_address}')
```

Los emails se registran en logs, permitiendo:
- Enumeración de usuarios
- Exposición de información personal
- Violación de privacidad

**Riesgo:**
- GDPR/CCPA: Datos personales en logs
- Enumeración de usuarios (aunque el endpoint retorna 200 siempre)
- Acceso a información sensible

**Solución:**
```python
# ✅ CORRECTO - Usar hash del email en lugar del email completo
import hashlib

email_hash = hashlib.sha256(email.encode()).hexdigest()[:8]
logger_auth.info(f'[FORGOT_PASSWORD_SOLICITADO] Usuario: {usuario.username} | Email_Hash: {email_hash}')

# O simplemente no loguear el email:
logger_auth.info(f'[FORGOT_PASSWORD_SOLICITADO] Usuario: {usuario.username}')
```

---

### 3. ⚠️ **ALTA: Código en Logs**

**Ubicación:** `tasks.py` línea 373

**Problema:**
```python
logger.info(f'[EMAIL_RECUPERACION] Enviado a {email} (usuario_id: {usuario_id})')
```

Aunque no incluye el código, el email sí se registra.

**Riesgo:**
- Exposición de información personal
- Enumeración de usuarios

**Solución:**
```python
# ✅ CORRECTO - Usar hash del email
email_hash = hashlib.sha256(email.encode()).hexdigest()[:8]
logger.info(f'[EMAIL_RECUPERACION] Enviado a {email_hash} (usuario_id: {usuario_id})')
```

---

### 4. ⚠️ **ALTA: Código de Recuperación en Texto Plano en Email**

**Ubicación:** `tasks.py` línea 348, `recuperacion_contraseña.html` línea 228

**Problema:**
```python
Tu código de recuperación de contraseña es: {codigo}
```

El código se envía en texto plano en el email. Si el email es interceptado, el atacante puede cambiar la contraseña.

**Riesgo:**
- Email no es seguro (SMTP sin TLS)
- Código en texto plano
- Acceso a cuenta si el email es interceptado

**Solución:**
```python
# ✅ CORRECTO - Enviar código con instrucciones claras de seguridad
text_content = f'''
Hola {nombre},

Se solicitó recuperación de contraseña para tu cuenta.

Tu código de recuperación es: {codigo}

INSTRUCCIONES IMPORTANTES:
1. Este código expira en 15 minutos
2. No compartas este código con nadie
3. Electronica Isla NUNCA te pedirá tu código por email
4. Si no solicitaste esto, ignora este email

Ingresa el código en la aplicación para cambiar tu contraseña.

Saludos,
Equipo Electronica Isla
'''
```

**Medidas adicionales:**
- Usar SMTP con TLS/SSL
- Configurar SPF, DKIM, DMARC
- Considerar usar tokens con hash en lugar de códigos simples

---

### 5. ⚠️ **MEDIA: Falta de Validación de Contraseña Fuerte**

**Ubicación:** `views_recuperacion.py` línea 180

**Problema:**
```python
if len(password) < 8:
    return Response({'error': 'La contraseña debe tener al menos 8 caracteres'})
```

Solo valida longitud, no complejidad. Permite contraseñas débiles como "12345678".

**Riesgo:**
- Contraseñas débiles
- Fácil de crackear
- Violación de estándares de seguridad

**Solución:**
```python
# ✅ CORRECTO - Validación de contraseña fuerte
import re

def validar_contraseña_fuerte(password):
    """
    Valida que la contraseña cumpla con requisitos de seguridad:
    - Mínimo 8 caracteres
    - Al menos 1 mayúscula
    - Al menos 1 minúscula
    - Al menos 1 número
    - Al menos 1 carácter especial
    """
    if len(password) < 8:
        return False, "Mínimo 8 caracteres"
    
    if not re.search(r'[A-Z]', password):
        return False, "Debe contener al menos 1 mayúscula"
    
    if not re.search(r'[a-z]', password):
        return False, "Debe contener al menos 1 minúscula"
    
    if not re.search(r'[0-9]', password):
        return False, "Debe contener al menos 1 número"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Debe contener al menos 1 carácter especial"
    
    return True, "Contraseña válida"

# En el endpoint:
is_valid, message = validar_contraseña_fuerte(password)
if not is_valid:
    return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
```

---

### 6. ⚠️ **MEDIA: Falta de Rate Limiting en reset_password_confirm**

**Ubicación:** `views_recuperacion.py` línea 132

**Problema:**
El endpoint `reset_password_confirm` NO tiene rate limiting. Un atacante puede hacer fuerza bruta de códigos (1,000,000 combinaciones).

**Riesgo:**
- Fuerza bruta de códigos
- Acceso no autorizado a cuentas
- Denegación de servicio

**Solución:**
```python
# ✅ CORRECTO - Agregar rate limiting por IP
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm(request):
    """
    Confirma el código y actualiza la contraseña.
    
    Rate limiting:
    - Máximo 10 intentos por IP en 15 minutos
    - Máximo 5 intentos por email en 15 minutos
    """
    try:
        email = request.data.get('email', '').strip().lower()
        codigo = request.data.get('codigo', '').strip()
        
        # Obtener información del request
        info_request = obtener_info_request(request)
        ip_address = info_request['ip_address']
        
        # ✅ NUEVO: Rate limiting por IP
        if LoginAttempt.esta_bloqueado(ip_address, attempt_type='reset_password', max_intentos=10, minutos=15):
            tiempo_restante = LoginAttempt.tiempo_restante_bloqueo(ip_address, attempt_type='reset_password', minutos=15)
            logger_security.warning(
                f'[RESET_PASSWORD_BLOQUEADO_IP] IP: {ip_address} | Tiempo restante: {tiempo_restante}s'
            )
            return Response({
                'error': f'Demasiados intentos. Intenta de nuevo en {tiempo_restante} segundos.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # ✅ NUEVO: Rate limiting por email
        if email and LoginAttempt.usuario_esta_bloqueado(email, attempt_type='reset_password', max_intentos=5, minutos=15):
            tiempo_restante = LoginAttempt.tiempo_restante_bloqueo_usuario(email, attempt_type='reset_password', minutos=15)
            logger_security.warning(
                f'[RESET_PASSWORD_BLOQUEADO_EMAIL] Email_Hash: {hashlib.sha256(email.encode()).hexdigest()[:8]} | Tiempo restante: {tiempo_restante}s'
            )
            return Response({
                'error': f'Demasiados intentos. Intenta de nuevo en {tiempo_restante} segundos.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # ... resto del código ...
        
        # ✅ NUEVO: Registrar intento fallido
        if not recovery_code:
            LoginAttempt.registrar_intento(
                ip_address=ip_address,
                username=email,
                attempt_type='reset_password',
                success=False,
                user_agent=info_request['user_agent']
            )
        
        # ✅ NUEVO: Registrar intento exitoso
        if recovery_code:
            LoginAttempt.registrar_intento(
                ip_address=ip_address,
                username=email,
                attempt_type='reset_password',
                success=True,
                user_agent=info_request['user_agent']
            )
```

---

### 7. ⚠️ **MEDIA: Falta de Validación de CSRF**

**Ubicación:** Frontend `ResetPasswordForm.tsx`

**Problema:**
Las solicitudes POST no incluyen validación CSRF. Un sitio malicioso podría hacer que el usuario cambie su contraseña sin saberlo.

**Riesgo:**
- CSRF (Cross-Site Request Forgery)
- Cambio no autorizado de contraseña
- Acceso a cuenta

**Solución:**
```python
# ✅ CORRECTO - Backend: Usar CSRF middleware de Django
# En settings.py:
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',  # ✅ Debe estar habilitado
    ...
]

# En views_recuperacion.py:
from django.views.decorators.csrf import csrf_protect

@csrf_protect  # ✅ Proteger contra CSRF
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm(request):
    ...
```

```typescript
// ✅ CORRECTO - Frontend: Incluir CSRF token
// En ResetPasswordForm.tsx:
const getCsrfToken = () => {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

// En la solicitud:
const response = await axios.post(
  `${API_BASE_URL}/auth/reset-password/`,
  {
    email,
    codigo,
    password,
    password_confirm: passwordConfirm,
  },
  {
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),  // ✅ Incluir CSRF token
    },
  }
);
```

---

### 8. ⚠️ **MEDIA: Falta de Validación de Email**

**Ubicación:** `views_recuperacion.py` línea 49

**Problema:**
```python
email = request.data.get('email', '').strip().lower()
```

No valida que el email sea válido. Permite emails malformados.

**Riesgo:**
- Emails inválidos en la BD
- Errores en envío de emails
- Inyección de datos

**Solución:**
```python
# ✅ CORRECTO - Validar email
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

email = request.data.get('email', '').strip().lower()

# Validar formato de email
try:
    validate_email(email)
except ValidationError:
    logger_security.warning(f'[FORGOT_PASSWORD_EMAIL_INVALIDO] Email: {email}')
    return Response({
        'message': 'Si el email existe en nuestro sistema, recibirás un código de recuperación'
    }, status=status.HTTP_200_OK)
```

---

## 🔒 MEDIDAS DE SEGURIDAD IMPLEMENTADAS (BIEN)

### ✅ Fortalezas Actuales

1. **Códigos Criptográficamente Seguros**
   - Usa `secrets.randbelow()` para generar códigos
   - 6 dígitos = 1,000,000 combinaciones
   - Expiración de 15 minutos

2. **Rate Limiting en forgot_password_request**
   - 5 intentos en 15 minutos por IP
   - Previene abuso

3. **Uso Único de Códigos**
   - Códigos marcados como verificados después de usar
   - No se pueden reutilizar

4. **Revocación de Tokens**
   - Se revocan todos los refresh tokens del usuario
   - Cierra todas las sesiones existentes

5. **HTTP-Only Cookies**
   - Refresh token en HTTP-Only Cookie
   - Protegido contra XSS

6. **Enumeración de Usuarios Prevenida**
   - Siempre retorna 200 aunque el email no exista
   - No revela si el usuario existe

---

## 📋 PLAN DE ACCIÓN

### Prioridad 1 (CRÍTICA) - Implementar Inmediatamente
- [ ] Remover emails de logs
- [ ] Remover contraseñas de logs
- [ ] Agregar validación de contraseña fuerte
- [ ] Agregar rate limiting en reset_password_confirm

### Prioridad 2 (ALTA) - Implementar en Próxima Versión
- [ ] Agregar CSRF protection
- [ ] Agregar validación de email
- [ ] Configurar SMTP con TLS/SSL
- [ ] Implementar SPF, DKIM, DMARC

### Prioridad 3 (MEDIA) - Considerar
- [ ] Usar tokens con hash en lugar de códigos simples
- [ ] Agregar 2FA (autenticación de dos factores)
- [ ] Agregar notificaciones de cambio de contraseña
- [ ] Agregar auditoría detallada de cambios de contraseña

---

## 🛠️ IMPLEMENTACIÓN DE SOLUCIONES

### Paso 1: Crear archivo de validación de contraseña

**Archivo:** `backend/api/validators.py`

```python
import re
import hashlib
from django.core.exceptions import ValidationError

def validar_contraseña_fuerte(password):
    """
    Valida que la contraseña cumpla con requisitos de seguridad.
    
    Requisitos:
    - Mínimo 8 caracteres
    - Al menos 1 mayúscula
    - Al menos 1 minúscula
    - Al menos 1 número
    - Al menos 1 carácter especial
    """
    if len(password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres")
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError("La contraseña debe contener al menos 1 mayúscula")
    
    if not re.search(r'[a-z]', password):
        raise ValidationError("La contraseña debe contener al menos 1 minúscula")
    
    if not re.search(r'[0-9]', password):
        raise ValidationError("La contraseña debe contener al menos 1 número")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("La contraseña debe contener al menos 1 carácter especial")

def hash_email_para_logs(email):
    """Retorna un hash del email para logs (no expone el email completo)"""
    return hashlib.sha256(email.encode()).hexdigest()[:8]
```

### Paso 2: Actualizar views_recuperacion.py

Ver archivo de soluciones adjunto.

### Paso 3: Actualizar tasks.py

Ver archivo de soluciones adjunto.

---

## 📊 CHECKLIST DE SEGURIDAD

- [ ] Contraseñas NO en logs
- [ ] Emails NO en logs (usar hash)
- [ ] Códigos NO en logs
- [ ] Validación de contraseña fuerte
- [ ] Rate limiting en ambos endpoints
- [ ] CSRF protection habilitada
- [ ] Validación de email
- [ ] SMTP con TLS/SSL
- [ ] SPF, DKIM, DMARC configurados
- [ ] Auditoría de cambios de contraseña
- [ ] Notificaciones de cambio de contraseña
- [ ] 2FA (opcional pero recomendado)

---

## 🔍 REFERENCIAS DE SEGURIDAD

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- NIST Password Guidelines: https://pages.nist.gov/800-63-3/
- CWE-256: Plaintext Storage of Password: https://cwe.mitre.org/data/definitions/256.html
- CWE-640: Weak Password Recovery Mechanism: https://cwe.mitre.org/data/definitions/640.html

---

**Auditoría realizada:** 25 de Noviembre de 2025
**Versión:** 1.0
**Estado:** Pendiente de implementación
