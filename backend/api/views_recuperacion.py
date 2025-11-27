"""
═══════════════════════════════════════════════════════════════════════════════
🔐 VISTAS - Recuperación de Contraseña con Códigos
═══════════════════════════════════════════════════════════════════════════════

Endpoints para solicitar y confirmar recuperación de contraseña usando códigos de 6 dígitos.
Similar al sistema de verificación de email.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import PasswordRecoveryCode, LoginAttempt, RefreshToken
from .utils import generar_access_token, obtener_info_request
from .tasks import enviar_email_recuperacion
from .validators import validar_email, hash_email_para_logs, validar_contraseña_fuerte
import logging

logger_security = logging.getLogger('security')
logger_auth = logging.getLogger('auth')


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_request(request):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    📧 ENDPOINT - Solicitar Código de Recuperación
    ═══════════════════════════════════════════════════════════════════════════════
    
    Solicita un código de 6 dígitos para recuperar la contraseña.
    
    Request:
    {
        "email": "usuario@example.com"
    }
    
    Retorna:
    - 200: { "message": "Si el email existe, recibirás un código de recuperación" }
    
    Notas de seguridad:
    - Siempre devuelve 200 aunque el email no exista (previene enumeración de usuarios)
    - Implementa rate limiting para prevenir abuso
    - Genera código de 6 dígitos con expiración de 15 minutos
    """
    try:
        email = request.data.get('email', '').strip().lower()
        
        if not email:
            # Devolver success aunque no haya email (seguridad)
            return Response({
                'message': 'Si el email existe en nuestro sistema, recibirás un código de recuperación'
            }, status=status.HTTP_200_OK)
        
        # ✅ NUEVO: Validar formato de email
        try:
            email = validar_email(email)
        except ValidationError as e:
            email_hash = hash_email_para_logs(email)
            logger_security.warning(f'[FORGOT_PASSWORD_EMAIL_INVALIDO] Email_Hash: {email_hash}')
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
                'message': 'Si el email existe en nuestro sistema, recibirás un enlace de recuperación'
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
            'message': 'Si el email existe en nuestro sistema, recibirás un enlace de recuperación'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        # ✅ MEJORADO: NO loguear detalles de la excepción (podría contener datos sensibles)
        logger_security.error(f'[FORGOT_PASSWORD_ERROR] Error procesando solicitud')
        logger_security.debug(f'[FORGOT_PASSWORD_ERROR_DETAIL] {str(e)}')
        return Response({
            'message': 'Si el email existe en nuestro sistema, recibirás un código de recuperación'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm(request):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    🔑 ENDPOINT - Confirmar Recuperación de Contraseña con Código
    ═══════════════════════════════════════════════════════════════════════════════
    
    Confirma el código y actualiza la contraseña.
    
    Request:
    {
        "email": "usuario@example.com",
        "codigo": "123456",
        "password": "nueva_contraseña",
        "password_confirm": "nueva_contraseña"
    }
    
    Retorna:
    - 200: { "message": "Contraseña actualizada", "accessToken": "...", "user": {...} }
    - 400: Código inválido, expirado o contraseñas no coinciden
    - 401: Código no encontrado
    
    Notas de seguridad:
    - Valida que el código sea válido y no esté expirado
    - Marca el código como verificado (uso único)
    - Revoca todos los refresh tokens del usuario
    - Genera nuevos tokens y autentica al usuario
    """
    try:
        email = request.data.get('email', '').strip().lower()
        codigo = request.data.get('codigo', '').strip()
        password = request.data.get('password', '')
        password_confirm = request.data.get('password_confirm', '')
        
        # ✅ NUEVO: Obtener información del request para rate limiting
        info_request = obtener_info_request(request)
        ip_address = info_request['ip_address']
        
        # ✅ NUEVO: Rate limiting por IP (10 intentos en 15 minutos)
        if LoginAttempt.esta_bloqueado(ip_address, attempt_type='reset_password', max_intentos=10, minutos=15):
            tiempo_restante = LoginAttempt.tiempo_restante_bloqueo(ip_address, attempt_type='reset_password', minutos=15)
            logger_security.warning(
                f'[RESET_PASSWORD_BLOQUEADO_IP] IP: {ip_address} | Tiempo restante: {tiempo_restante}s'
            )
            return Response({
                'error': 'Demasiados intentos. Intenta más tarde.',
                'retry_after': tiempo_restante
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # ✅ NUEVO: Rate limiting por Email (5 intentos en 15 minutos)
        if email:
            if LoginAttempt.usuario_esta_bloqueado(email, attempt_type='reset_password', max_intentos=5, minutos=15):
                tiempo_restante = LoginAttempt.tiempo_restante_bloqueo_usuario(email, attempt_type='reset_password', minutos=15)
                email_hash = hash_email_para_logs(email)
                logger_security.warning(
                    f'[RESET_PASSWORD_BLOQUEADO_EMAIL] Email_Hash: {email_hash} | Tiempo restante: {tiempo_restante}s'
                )
                return Response({
                    'error': 'Demasiados intentos. Intenta más tarde.',
                    'retry_after': tiempo_restante
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
            # ✅ MEJORADO: NO loguear email completo, usar hash
            email_hash = hash_email_para_logs(email)
            logger_security.warning(f'[RESET_PASSWORD_USUARIO_NO_EXISTE] Email_Hash: {email_hash}')
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verificar código
        recovery_code = PasswordRecoveryCode.verificar_codigo(usuario, codigo)
        
        if not recovery_code:
            # ✅ NUEVO: Registrar intento fallido en rate limiting
            LoginAttempt.registrar_intento(ip_address, attempt_type='reset_password', success=False)
            
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
        
        # ✅ NUEVO: Registrar intento exitoso en rate limiting
        LoginAttempt.registrar_intento(ip_address, attempt_type='reset_password', success=True)
        
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
        
        # ✅ MEJORADO: NO loguear email completo, usar hash
        email_hash = hash_email_para_logs(usuario.email)
        logger_auth.info(
            f'[RESET_PASSWORD_EXITOSO] Usuario: {usuario.username} | Email_Hash: {email_hash}'
        )
        
        return response
    
    except Exception as e:
        # ✅ MEJORADO: NO loguear detalles de la excepción
        import traceback
        logger_security.error(f'[RESET_PASSWORD_ERROR] Error al cambiar contraseña')
        logger_security.error(f'[RESET_PASSWORD_ERROR_DETAIL] {str(e)}')
        logger_security.error(f'[RESET_PASSWORD_ERROR_TRACEBACK] {traceback.format_exc()}')
        return Response({
            'error': 'Error al actualizar contraseña'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
