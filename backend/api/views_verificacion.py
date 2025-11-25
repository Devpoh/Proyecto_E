"""
═══════════════════════════════════════════════════════════════════════════════
📧 VIEWS - Verificación de Email
═══════════════════════════════════════════════════════════════════════════════

Endpoints para verificación de email con código de 6 dígitos.

Endpoints:
1. POST /api/auth/register-with-verification/ - Registro con verificación
2. POST /api/auth/verify-email/ - Verificar código de email
3. POST /api/auth/resend-verification/ - Reenviar código
"""

from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import logging

from .models import EmailVerification, LoginAttempt, RefreshToken
from .tasks import enviar_email_verificacion
from .throttles import AnonLoginRateThrottle
from .utils.jwt_utils import generar_access_token, obtener_info_request

logger = logging.getLogger('auth')


def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def verificar_intentos_login(username, ip_address):
    """
    Verifica si hay demasiados intentos fallidos.
    Usa el patrón LoginAttempt existente.
    
    Returns:
        tuple: (bloqueado, tiempo_restante_segundos)
    """
    from datetime import timedelta
    
    # Buscar intentos recientes (últimos 15 minutos)
    hace_15_min = timezone.now() - timedelta(minutes=15)
    
    intentos = LoginAttempt.objects.filter(
        username=username,
        ip_address=ip_address,
        timestamp__gte=hace_15_min,
        success=False
    ).count()
    
    # Bloquear después de 5 intentos fallidos
    if intentos >= 5:
        # Calcular tiempo restante hasta que expire el bloqueo
        ultimo_intento = LoginAttempt.objects.filter(
            username=username,
            ip_address=ip_address
        ).order_by('-timestamp').first()
        
        if ultimo_intento:
            tiempo_transcurrido = (timezone.now() - ultimo_intento.timestamp).total_seconds()
            tiempo_restante = max(0, 900 - tiempo_transcurrido)  # 15 minutos = 900 segundos
            return True, int(tiempo_restante)
    
    return False, 0


def registrar_intento_verificacion(username, ip_address, exitoso):
    """
    Registra un intento de verificación usando el modelo LoginAttempt.
    """
    LoginAttempt.objects.create(
        username=username,
        ip_address=ip_address,
        attempt_type='verification',
        success=exitoso,
        user_agent=''
    )


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonLoginRateThrottle])
def register_with_verification(request):
    """
    📧 ENDPOINT: Registro con verificación de email
    
    Crea un usuario inactivo y envía código de verificación por email.
    
    Body:
        - username: Nombre de usuario (único)
        - email: Email (único)
        - password: Contraseña
        - first_name: Nombre (opcional)
        - last_name: Apellido (opcional)
    
    Returns:
        - 201: Usuario creado, email enviado
        - 400: Datos inválidos
        - 429: Demasiados intentos
    
    Flujo:
    1. Validar datos de entrada
    2. Crear usuario con is_active=False
    3. Generar código de verificación
    4. Enviar email asincrónicamente
    5. Retornar mensaje de éxito
    """
    try:
        # Obtener datos
        username = request.data.get('username', '').strip()
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        first_name = request.data.get('first_name', '').strip()
        last_name = request.data.get('last_name', '').strip()
        
        # Validaciones básicas
        if not username or not email or not password:
            return Response({
                'error': 'Username, email y password son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar formato de email
        if '@' not in email or '.' not in email:
            return Response({
                'error': 'Email inválido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si el usuario ya existe (solo en Users creados)
        if User.objects.filter(username=username).exists():
            return Response({
                'error': 'El nombre de usuario ya está en uso'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'El email ya está registrado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar contraseña
        try:
            validate_password(password)
        except ValidationError as e:
            return Response({
                'error': 'Contraseña inválida',
                'detalles': list(e.messages)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # ✅ OPCIÓN 1: NO crear usuario aún, solo guardar datos temporales
        with transaction.atomic():
            # Obtener IP del usuario
            ip_address = request.META.get('REMOTE_ADDR')
            
            # Crear registro de verificación CON DATOS TEMPORALES (sin User)
            # Esto permite que el usuario no sea creado hasta verificar
            from django.contrib.auth.hashers import make_password
            password_hash = make_password(password)
            
            verificacion = EmailVerification.objects.create(
                usuario=None,  # ✅ No crear User aún
                email_temporal=email,
                username_temporal=username,
                password_hash=password_hash,
                first_name_temporal=first_name,
                last_name_temporal=last_name,
                codigo=EmailVerification.generar_codigo(),
                expires_at=timezone.now() + timedelta(minutes=5),
                ip_address=ip_address
            )
            
            # Enviar email de forma asíncrona
            # Nota: Pasamos email_temporal en lugar de usuario_id
            enviar_email_verificacion.delay(
                email=email,
                codigo=verificacion.codigo,
                nombre=first_name or username
            )
            
            logger.info(
                f'[REGISTRO_VERIFICACION] Registro iniciado. '
                f'Email: {email}. Código enviado. Usuario será creado tras verificación.'
            )
        
        return Response({
            'message': 'Código de verificación enviado exitosamente',
            'detail': 'Revisa tu email para obtener el código',
            'email': email,
            'username': username,
            'expires_in_minutes': 5
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f'[REGISTRO_ERROR] {str(e)}')
        return Response({
            'error': 'Error al registrar usuario',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonLoginRateThrottle])
def verify_email(request):
    """
    ✅ ENDPOINT: Verificar código de email
    
    Verifica el código de 6 dígitos y activa la cuenta.
    
    Body:
        - email: Email del usuario
        - codigo: Código de 6 dígitos
    
    Returns:
        - 200: Email verificado, tokens JWT generados
        - 400: Código inválido o expirado
        - 429: Demasiados intentos
    
    Flujo:
    1. Validar email y código
    2. Buscar usuario y verificación
    3. Verificar código (validez, expiración)
    4. Activar usuario (is_active=True)
    5. Generar tokens JWT
    6. Retornar tokens y datos de usuario
    """
    try:
        # Obtener datos
        email = request.data.get('email', '').strip().lower()
        codigo = request.data.get('codigo', '').strip()
        ip_address = get_client_ip(request)
        
        # Validaciones básicas
        if not email or not codigo:
            return Response({
                'error': 'Email y código son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(codigo) != 6 or not codigo.isdigit():
            return Response({
                'error': 'El código debe ser de 6 dígitos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # ✅ OPCIÓN 1: Buscar registro de verificación por email (no User aún)
        # Usar filter().first() en lugar de get() para evitar MultipleObjectsReturned
        # Obtener el más reciente si hay múltiples
        verificacion = EmailVerification.objects.filter(
            email_temporal=email,
            verificado=False
        ).order_by('-created_at').first()
        
        if not verificacion:
            return Response({
                'error': 'No hay registro de verificación para este email'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si el código ha expirado
        if not verificacion.is_valid():
            return Response({
                'error': 'El código ha expirado',
                'detail': 'Solicita un nuevo código de verificación'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar intentos fallidos en este código ANTES de validar el código
        if verificacion.intentos_fallidos >= 5:
            logger.warning(
                f'[CODIGO_BLOQUEADO] Código para {email} bloqueado por intentos fallidos'
            )
            return Response({
                'error': 'Código bloqueado por intentos fallidos',
                'detail': 'Solicita un nuevo código de verificación'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Verificar si el código es correcto
        if verificacion.codigo != codigo:
            # Incrementar intentos fallidos
            verificacion.incrementar_intentos()
            
            # Si ya llegó a 5 intentos, bloquear
            if verificacion.intentos_fallidos >= 5:
                logger.warning(
                    f'[CODIGO_BLOQUEADO] Código para {email} bloqueado por intentos fallidos'
                )
                return Response({
                    'error': 'Código bloqueado por intentos fallidos',
                    'detail': 'Solicita un nuevo código de verificación'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            return Response({
                'error': 'Código inválido',
                'detail': f'Intentos restantes: {5 - verificacion.intentos_fallidos}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # ✅ CREAR USUARIO AHORA (después de verificar el código)
        with transaction.atomic():
            # Crear usuario con los datos temporales
            user = User.objects.create_user(
                username=verificacion.username_temporal,
                email=verificacion.email_temporal,
                password='temp_password_will_be_replaced',  # Temporal, será reemplazado
                first_name=verificacion.first_name_temporal or '',
                last_name=verificacion.last_name_temporal or '',
                is_active=True  # ✅ Usuario activo desde el inicio
            )
            
            # Reemplazar la contraseña con la hasheada guardada
            user.password = verificacion.password_hash
            user.save()
            
            # Crear perfil (se crea automáticamente por señal)
            if hasattr(user, 'profile'):
                user.profile.rol = 'cliente'
                user.profile.save()
            
            # Marcar verificación como completada
            verificacion.usuario = user  # Asociar el usuario creado
            verificacion.marcar_verificado()
            
            # Registrar intento exitoso
            registrar_intento_verificacion(user.username, ip_address, True)
            
            logger.info(
                f'[EMAIL_VERIFICADO] Usuario {user.username} creado y verificado exitosamente. IP: {ip_address}'
            )
        
        # ✅ NO generar tokens aquí - el usuario debe hacer login manualmente
        # Esto asegura que el usuario verifique su email y luego inicie sesión
        
        return Response({
            'message': 'Email verificado exitosamente',
            'detail': 'Tu cuenta ha sido activada. Por favor inicia sesión.',
            'email': user.email,
            'username': user.username
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f'[VERIFICACION_ERROR] {str(e)}\n{error_trace}')
        print(f'[VERIFICACION_ERROR] {str(e)}\n{error_trace}')  # También en consola
        return Response({
            'error': 'Error al verificar email',
            'detail': str(e),
            'trace': error_trace if True else None  # Para debugging
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonLoginRateThrottle])
def resend_verification(request):
    """
    🔄 ENDPOINT: Reenviar código de verificación
    
    Genera un nuevo código y lo envía por email.
    
    ✅ OPCIÓN 1: Busca datos temporales en EmailVerification
    
    Límites:
    - Máximo 3 reenvíos por usuario
    - 1 minuto entre cada reenvío
    
    Body:
        - email: Email del usuario
    
    Returns:
        - 200: Código reenviado
        - 400: Email inválido o ya verificado
        - 429: Demasiados intentos o tiempo de espera
    
    Flujo:
    1. Validar email
    2. Buscar registro de verificación con datos temporales
    3. Verificar límites de reenvío (tiempo y cantidad)
    4. Generar nuevo código
    5. Enviar email
    """
    try:
        # Obtener email
        email = request.data.get('email', '').strip().lower()
        
        if not email:
            return Response({
                'error': 'Email es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # ✅ OPCIÓN 1: Buscar registro de verificación con datos temporales
        try:
            ultima_verificacion = EmailVerification.objects.filter(
                email_temporal=email,
                verificado=False
            ).order_by('-created_at').first()
            
            if not ultima_verificacion:
                return Response({
                    'error': 'No hay registro de verificación para este email'
                }, status=status.HTTP_404_NOT_FOUND)
        except EmailVerification.DoesNotExist:
            return Response({
                'error': 'No hay registro de verificación para este email'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 🛡️ PROTECCIÓN: Verificar límite de reenvíos
        # 🛡️ LÍMITE DE TIEMPO: 1 minuto entre reenvíos
        if not ultima_verificacion.puede_reenviar(minutos_espera=1):
            tiempo_restante = 1 - (
                (timezone.now() - ultima_verificacion.ultimo_reenvio).total_seconds() / 60
            )
            logger.warning(
                f'[REENVIO_BLOQUEADO] Email {email} intentó reenviar '
                f'antes del tiempo de espera. Tiempo restante: {int(tiempo_restante * 60)}s'
            )
            return Response({
                'error': 'Debes esperar antes de reenviar',
                'detail': f'Espera {int(tiempo_restante * 60)} segundos',
                'tiempo_restante_segundos': int(tiempo_restante * 60)
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # 🛡️ LÍMITE DE CANTIDAD: Máximo 3 reenvíos por usuario
        if ultima_verificacion.contador_reenvios >= 3:
            logger.warning(
                f'[REENVIO_LIMITE] Email {email} alcanzó el límite de reenvíos'
            )
            return Response({
                'error': 'Límite de reenvíos alcanzado',
                'detail': 'Máximo 3 reenvíos permitidos. Contacta con soporte si necesitas ayuda.'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # ✅ Actualizar el registro existente en lugar de crear uno nuevo
        ultima_verificacion.marcar_reenvio()
        ultima_verificacion.codigo = EmailVerification.generar_codigo()
        ultima_verificacion.expires_at = timezone.now() + timedelta(minutes=5)
        ultima_verificacion.save()
        
        # Enviar email de forma asíncrona con el nuevo código
        enviar_email_verificacion.delay(
            email=email,
            codigo=ultima_verificacion.codigo,
            nombre=ultima_verificacion.first_name_temporal or ultima_verificacion.username_temporal
        )
        
        logger.info(
            f'[CODIGO_REENVIADO] Email {email}. '
            f'Reenvío #{ultima_verificacion.contador_reenvios}'
        )
        
        return Response({
            'message': 'Código de verificación reenviado',
            'email': email,
            'expires_in_minutes': 5
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f'[REENVIO_ERROR] {str(e)}')
        return Response({
            'error': 'Error al reenviar código',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_verification_status(request):
    """
    📊 ENDPOINT: Estado de verificación de email
    
    ✅ OPCIÓN 1: Verifica estado de verificación usando datos temporales
    
    Verifica si un email está verificado.
    Útil para la página de verificación.
    
    Query Params:
        - email: Email del usuario
    
    Returns:
        - 200: Estado de verificación
        - 400: Email no proporcionado
        - 404: Usuario no encontrado
    
    Response:
        {
            "email": "user@example.com",
            "is_verified": true/false,
            "username": "usuario123",
            "has_pending_verification": true/false,
            "verification_expires_at": "2024-11-25T12:00:00Z",
            "can_resend": true/false,
            "resend_count": 2,
            "max_resends": 3
        }
    """
    try:
        # Obtener email del query param
        email = request.query_params.get('email', '').strip().lower()
        
        if not email:
            return Response({
                'error': 'Email es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # ✅ OPCIÓN 1: Buscar en EmailVerification con datos temporales
        verificacion_pendiente = EmailVerification.objects.filter(
            email_temporal=email,
            verificado=False
        ).order_by('-created_at').first()
        
        if not verificacion_pendiente:
            return Response({
                'error': 'No hay registro de verificación para este email'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Preparar respuesta
        response_data = {
            'email': email,
            'is_verified': False,  # Aún no verificado
            'username': verificacion_pendiente.username_temporal,
            'has_pending_verification': True
        }
        
        # Agregar detalles de verificación
        response_data.update({
            'verification_expires_at': verificacion_pendiente.expires_at.isoformat(),
            'is_expired': not verificacion_pendiente.is_valid(),
            'can_resend': verificacion_pendiente.puede_reenviar(minutos_espera=1),
            'resend_count': verificacion_pendiente.contador_reenvios,
            'max_resends': 3,
            'failed_attempts': verificacion_pendiente.intentos_fallidos,
            'max_attempts': 5
        })
        
        # Calcular tiempo restante para reenviar
        if verificacion_pendiente.ultimo_reenvio:
            tiempo_transcurrido = (timezone.now() - verificacion_pendiente.ultimo_reenvio).total_seconds()
            tiempo_restante = max(0, 60 - tiempo_transcurrido)  # 1 minuto = 60 segundos
            response_data['resend_available_in_seconds'] = int(tiempo_restante)
        
        logger.info(f'[ESTADO_VERIFICACION] Email {email}. Verificado: False')
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f'[ESTADO_ERROR] {str(e)}')
        return Response({
            'error': 'Error al verificar estado',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
