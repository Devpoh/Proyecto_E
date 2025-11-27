# 🔐 SOLUCIONES DE SEGURIDAD - IMPLEMENTACIÓN

## Cambios Requeridos en views_recuperacion.py

### 1. Agregar Imports

```python
from .validators import validar_contraseña_fuerte, validar_email, hash_email_para_logs
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
import hashlib
```

---

## 2. Actualizar forgot_password_request

### ANTES (Vulnerable):
```python
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_request(request):
    try:
        email = request.data.get('email', '').strip().lower()
        
        # ... código ...
        
        logger_auth.info(
            f'[FORGOT_PASSWORD_SOLICITADO] Usuario: {usuario.username} | Email: {usuario.email}'
        )
        
    except Exception as e:
        logger_security.error(f'[FORGOT_PASSWORD_ERROR] {str(e)}')
```

### DESPUÉS (Seguro):
```python
@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_request(request):
    """
    📧 ENDPOINT - Solicitar Código de Recuperación
    
    Seguridad mejorada:
    - ✅ Validación de email
    - ✅ Emails NO en logs (usar hash)
    - ✅ Contraseñas NO en logs
    - ✅ Rate limiting
    """
    try:
        email = request.data.get('email', '').strip().lower()
        
        if not email:
            return Response({
                'message': 'Si el email existe en nuestro sistema, recibirás un código de recuperación'
            }, status=status.HTTP_200_OK)
        
        # ✅ NUEVO: Validar formato de email
        try:
            email = validar_email(email)
        except ValidationError as e:
            logger_security.warning(f'[FORGOT_PASSWORD_EMAIL_INVALIDO] Email_Hash: {hash_email_para_logs(email)}')
            return Response({
                'message': 'Si el email existe en nuestro sistema, recibirás un código de recuperación'
            }, status=status.HTTP_200_OK)
        
        # Obtener información del request
        info_request = obtener_info_request(request)
        ip_address = info_request['ip_address']
        
        # Verificar rate limiting (5 intentos en 15 minutos)
        if LoginAttempt.esta_bloqueado(ip_address, attempt_type='forgot_password', max_intentos=5, minutos=15):
            tiempo_restante = LoginAttempt.tiempo_restante_bloqueo(ip_address, attempt_type='forgot_password', minutos=15)
            logger_security.warning(
                f'[FORGOT_PASSWORD_BLOQUEADO] IP: {ip_address} | Tiempo restante: {tiempo_restante}s'
            )
            return Response({
                'message': 'Si el email existe en nuestro sistema, recibirás un código de recuperación'
            }, status=status.HTTP_200_OK)
        
        # Buscar usuario por email
        try:
            usuario = User.objects.get(email__iexact=email)
            
            # Generar código de recuperación
            recovery_code = PasswordRecoveryCode.crear_codigo(
                usuario=usuario,
                duracion_minutos=15,
                user_agent=info_request['user_agent'],
                ip_address=ip_address
            )
            
            # Enviar email con código de forma asíncrona
            enviar_email_recuperacion.delay(
                email=usuario.email,
                nombre=usuario.first_name or usuario.username,
                codigo=recovery_code.codigo,
                usuario_id=usuario.id
            )
            
            # Registrar intento exitoso
            LoginAttempt.registrar_intento(
                ip_address=ip_address,
                username=usuario.username,
                attempt_type='forgot_password',
                success=True,
                user_agent=info_request['user_agent']
            )
            
            # ✅ MEJORADO: NO loguear email completo, usar hash
            email_hash = hash_email_para_logs(usuario.email)
            logger_auth.info(
                f'[FORGOT_PASSWORD_SOLICITADO] Usuario: {usuario.username} | Email_Hash: {email_hash}'
            )
        
        except User.DoesNotExist:
            # Registrar intento fallido (usuario no existe)
            LoginAttempt.registrar_intento(
                ip_address=ip_address,
                username=email,
                attempt_type='forgot_password',
                success=False,
                user_agent=info_request['user_agent']
            )
            
            # ✅ MEJORADO: NO loguear email completo, usar hash
            email_hash = hash_email_para_logs(email)
            logger_security.info(
                f'[FORGOT_PASSWORD_EMAIL_NO_EXISTE] Email_Hash: {email_hash} | IP: {ip_address}'
            )
        
        # Devolver siempre success (seguridad)
        return Response({
            'message': 'Si el email existe en nuestro sistema, recibirás un código de recuperación'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        # ✅ MEJORADO: NO loguear detalles de la excepción (podría contener datos sensibles)
        logger_security.error(f'[FORGOT_PASSWORD_ERROR] Error procesando solicitud')
        # Solo en desarrollo:
        logger_security.debug(f'[FORGOT_PASSWORD_ERROR_DETAIL] {str(e)}')
        
        return Response({
            'message': 'Si el email existe en nuestro sistema, recibirás un código de recuperación'
        }, status=status.HTTP_200_OK)
```

---

## 3. Actualizar reset_password_confirm

### ANTES (Vulnerable):
```python
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm(request):
    try:
        # ... código ...
        
        # Validar longitud mínima de contraseña
        if len(password) < 8:
            return Response({
                'error': 'La contraseña debe tener al menos 8 caracteres'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # ... código ...
        
    except Exception as e:
        logger_security.error(f'[RESET_PASSWORD_ERROR] {str(e)}')
```

### DESPUÉS (Seguro):
```python
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm(request):
    """
    🔑 ENDPOINT - Confirmar Recuperación de Contraseña con Código
    
    Seguridad mejorada:
    - ✅ Validación de contraseña fuerte
    - ✅ Rate limiting por IP y email
    - ✅ Emails NO en logs (usar hash)
    - ✅ Contraseñas NO en logs
    """
    try:
        email = request.data.get('email', '').strip().lower()
        codigo = request.data.get('codigo', '').strip()
        password = request.data.get('password', '')
        password_confirm = request.data.get('password_confirm', '')
        
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
        if email:
            if LoginAttempt.usuario_esta_bloqueado(email, attempt_type='reset_password', max_intentos=5, minutos=15):
                tiempo_restante = LoginAttempt.tiempo_restante_bloqueo_usuario(email, attempt_type='reset_password', minutos=15)
                email_hash = hash_email_para_logs(email)
                logger_security.warning(
                    f'[RESET_PASSWORD_BLOQUEADO_EMAIL] Email_Hash: {email_hash} | Tiempo restante: {tiempo_restante}s'
                )
                return Response({
                    'error': f'Demasiados intentos. Intenta de nuevo en {tiempo_restante} segundos.'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Validar que el código esté presente
        if not codigo:
            logger_security.warning('[RESET_PASSWORD_SIN_CODIGO]')
            return Response({
                'error': 'Código es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar que las contraseñas coincidan
        if password != password_confirm:
            logger_security.warning('[RESET_PASSWORD_CONTRASEÑAS_NO_COINCIDEN]')
            return Response({
                'error': 'Las contraseñas no coinciden'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # ✅ MEJORADO: Validación de contraseña fuerte
        try:
            validar_contraseña_fuerte(password)
        except ValidationError as e:
            logger_security.warning(f'[RESET_PASSWORD_CONTRASEÑA_DEBIL] {str(e)}')
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar usuario
        try:
            usuario = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # ✅ MEJORADO: NO loguear email completo
            email_hash = hash_email_para_logs(email)
            logger_security.warning(f'[RESET_PASSWORD_USUARIO_NO_EXISTE] Email_Hash: {email_hash}')
            
            # ✅ NUEVO: Registrar intento fallido
            LoginAttempt.registrar_intento(
                ip_address=ip_address,
                username=email,
                attempt_type='reset_password',
                success=False,
                user_agent=info_request['user_agent']
            )
            
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verificar código
        recovery_code = PasswordRecoveryCode.verificar_codigo(usuario, codigo)
        
        if not recovery_code:
            # Incrementar intentos fallidos si el código existe pero es inválido
            try:
                invalid_code = PasswordRecoveryCode.objects.get(usuario=usuario, codigo=codigo)
                invalid_code.incrementar_intentos()
                
                if invalid_code.intentos_fallidos >= 5:
                    logger_security.warning(f'[RESET_PASSWORD_LIMITE_INTENTOS] Usuario: {usuario.username}')
                    return Response({
                        'error': 'Demasiados intentos fallidos. Solicita un nuevo código.'
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            except PasswordRecoveryCode.DoesNotExist:
                pass
            
            logger_security.warning(f'[RESET_PASSWORD_CODIGO_INVALIDO] Usuario: {usuario.username}')
            
            # ✅ NUEVO: Registrar intento fallido
            LoginAttempt.registrar_intento(
                ip_address=ip_address,
                username=email,
                attempt_type='reset_password',
                success=False,
                user_agent=info_request['user_agent']
            )
            
            return Response({
                'error': 'Código inválido o expirado'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Actualizar contraseña
        usuario.set_password(password)
        usuario.save()
        
        # Marcar código como verificado
        recovery_code.marcar_verificado()
        
        # Revocar todos los refresh tokens del usuario
        RefreshToken.revocar_todos_usuario(usuario)
        
        # Generar nuevos tokens
        access_token = generar_access_token(usuario)
        
        refresh_token_plano, refresh_token_obj = RefreshToken.crear_token(
            usuario=usuario,
            duracion_dias=30,
            user_agent=info_request['user_agent'],
            ip_address=info_request['ip_address']
        )
        
        # Construir nombre completo
        nombre = f"{usuario.first_name} {usuario.last_name}".strip() or usuario.username
        
        # Obtener rol del perfil
        rol = usuario.profile.rol if hasattr(usuario, 'profile') else 'cliente'
        
        # Crear respuesta
        response = Response({
            'accessToken': access_token,
            'user': {
                'id': usuario.id,
                'email': usuario.email,
                'nombre': nombre,
                'rol': rol
            },
            'message': 'Contraseña actualizada exitosamente'
        }, status=status.HTTP_200_OK)
        
        # Configurar Refresh Token como HTTP-Only Cookie
        response.set_cookie(
            key='refreshToken',
            value=refresh_token_plano,
            max_age=30 * 24 * 60 * 60,  # 30 días en segundos
            httponly=True,
            secure=False,  # True en producción (HTTPS)
            samesite='Lax',
            path='/'
        )
        
        # ✅ MEJORADO: NO loguear email completo
        email_hash = hash_email_para_logs(usuario.email)
        logger_auth.info(
            f'[RESET_PASSWORD_EXITOSO] Usuario: {usuario.username} | Email_Hash: {email_hash}'
        )
        
        # ✅ NUEVO: Registrar intento exitoso
        LoginAttempt.registrar_intento(
            ip_address=ip_address,
            username=email,
            attempt_type='reset_password',
            success=True,
            user_agent=info_request['user_agent']
        )
        
        return response
    
    except Exception as e:
        # ✅ MEJORADO: NO loguear detalles de la excepción
        logger_security.error(f'[RESET_PASSWORD_ERROR] Error al cambiar contraseña')
        # Solo en desarrollo:
        logger_security.debug(f'[RESET_PASSWORD_ERROR_DETAIL] {str(e)}')
        
        return Response({
            'error': 'Error al actualizar contraseña'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

---

## 4. Actualizar LoginAttempt Model

Agregar tipo 'reset_password' a las opciones:

```python
attempt_type = models.CharField(
    max_length=20,
    choices=[
        ('login', 'Login'),
        ('register', 'Register'),
        ('forgot_password', 'Forgot Password'),  # ✅ NUEVO
        ('reset_password', 'Reset Password'),     # ✅ NUEVO
    ],
    default='login'
)
```

---

## 5. Actualizar tasks.py

```python
@shared_task(bind=True, max_retries=3)
def enviar_email_recuperacion(self, email=None, nombre=None, codigo=None, usuario_id=None):
    """
    📧 TAREA: Enviar email de recuperación de contraseña con código
    
    Seguridad mejorada:
    - ✅ Emails NO en logs (usar hash)
    - ✅ Códigos NO en logs
    """
    from django.core.mail import EmailMultiAlternatives
    from django.conf import settings
    from django.template.loader import render_to_string
    
    try:
        if not email or not codigo or not nombre:
            raise ValueError('Parámetros inválidos: email, codigo y nombre son requeridos')
        
        # Contexto para la plantilla
        context = {
            'nombre': nombre,
            'codigo': codigo,
            'expiracion_minutos': 15,
        }
        
        # Renderizar plantilla HTML
        html_content = render_to_string('emails/recuperacion_contraseña.html', context)
        
        # Mensaje de texto plano (fallback)
        text_content = f'''
Hola {nombre},

Se solicitó recuperación de contraseña para tu cuenta en Electronica Isla.

Tu código de recuperación es: {codigo}

INSTRUCCIONES IMPORTANTES:
1. Este código expira en 15 minutos
2. No compartas este código con nadie
3. Electronica Isla NUNCA te pedirá tu código por email
4. Si no solicitaste esto, ignora este email de forma segura

Ingresa el código en la aplicación para cambiar tu contraseña.

Saludos,
Equipo Electronica Isla
        '''
        
        # Crear email con HTML y texto plano
        subject = 'Código de recuperación de contraseña - Electronica Isla'
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email]
        )
        email_msg.attach_alternative(html_content, "text/html")
        
        # Enviar email
        email_msg.send(fail_silently=False)
        
        # ✅ MEJORADO: NO loguear email completo, usar hash
        email_hash = hash_email_para_logs(email)
        logger.info(f'[EMAIL_RECUPERACION] Enviado a {email_hash} (usuario_id: {usuario_id})')
        
        return {
            'status': 'success',
            'email_hash': email_hash,
            'usuario_id': usuario_id,
            'format': 'html'
        }
    
    except Exception as exc:
        logger.error(f'[EMAIL_RECUPERACION_ERROR] Error enviando email (usuario_id: {usuario_id})')
        # Reintentar con backoff exponencial (60 segundos)
        raise self.retry(exc=exc, countdown=60)
```

---

## 6. Configuración de Django (settings.py)

```python
# ✅ Seguridad: CSRF Protection
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',  # ✅ Debe estar habilitado
    # ... otros middlewares ...
]

# ✅ Seguridad: SMTP con TLS
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True  # ✅ IMPORTANTE: Usar TLS
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@electronicaisla.com')

# ✅ Seguridad: Cookies
SESSION_COOKIE_SECURE = True  # Solo en HTTPS
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True  # Solo en HTTPS
CSRF_COOKIE_HTTPONLY = True
```

---

## 7. Configuración de Frontend (CSRF Token)

```typescript
// En forgotPasswordApi.ts
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

export const confirmPasswordReset = async (
  email: string,
  codigo: string,
  password: string,
  passwordConfirm: string
) => {
  try {
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
    return response.data;
  } catch (error: any) {
    throw error.response?.data || { error: 'Error al actualizar contraseña' };
  }
};
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [ ] Crear `backend/api/validators.py`
- [ ] Actualizar `backend/api/views_recuperacion.py`
- [ ] Actualizar `backend/api/tasks.py`
- [ ] Actualizar `backend/api/models.py` (LoginAttempt)
- [ ] Actualizar `backend/config/settings.py`
- [ ] Actualizar `frontend/api/forgotPasswordApi.ts`
- [ ] Probar flujo completo
- [ ] Revisar logs para asegurar que no contienen datos sensibles
- [ ] Configurar SMTP con TLS
- [ ] Configurar SPF, DKIM, DMARC (en producción)

---

**Implementación completada:** 25 de Noviembre de 2025
