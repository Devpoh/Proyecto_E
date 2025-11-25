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

from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
import logging

from .models import UserProfile, EmailVerification, LoginAttempt
from .tasks import enviar_email_verificacion
from .throttles import AnonAuthThrottle
from .authentication import crear_tokens_jwt

logger = logging.getLogger('auth')


def get_client_ip(request):
    """Obtiene la IP del cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def verificar_intentos_login(email, ip_address):
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
        email=email,
        ip_address=ip_address,
        timestamp__gte=hace_15_min,
        successful=False
    ).count()
    
    # Bloquear después de 5 intentos fallidos
    if intentos >= 5:
        # Calcular tiempo restante hasta que expire el bloqueo
        ultimo_intento = LoginAttempt.objects.filter(
            email=email,
            ip_address=ip_address
        ).order_by('-timestamp').first()
        
        if ultimo_intento:
            tiempo_transcurrido = (timezone.now() - ultimo_intento.timestamp).total_seconds()
            tiempo_restante = max(0, 900 - tiempo_transcurrido)  # 15 minutos = 900 segundos
            return True, int(tiempo_restante)
    
    return False, 0


def registrar_intento_verificacion(email, ip_address, exitoso):
    """
    Registra un intento de verificación usando el modelo LoginAttempt.
    """
    LoginAttempt.objects.create(
        email=email,
        ip_address=ip_address,
        successful=exitoso,
        timestamp=timezone.now()
    )


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonAuthThrottle])
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
        
        # Verificar si el usuario ya existe
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
        
        # Crear usuario con transacción atómica
        with transaction.atomic():
            # Crear usuario inactivo
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=False  # Usuario inactivo hasta verificar email
            )
            
            # El perfil se crea automáticamente por la señal
            # Asegurar que el rol sea 'cliente'
            if hasattr(user, 'profile'):
                user.profile.rol = 'cliente'
                user.profile.save()
            
            # Obtener IP del usuario
            ip_address = request.META.get('REMOTE_ADDR')
            
            # Crear código de verificación
            verificacion = EmailVerification.crear_codigo(
                usuario=user,
                duracion_minutos=15,
                ip_address=ip_address
            )
            
            # Enviar email de forma asíncrona
            enviar_email_verificacion.delay(
                usuario_id=user.id,
                codigo=verificacion.codigo
            )
            
            logger.info(
                f'[REGISTRO_VERIFICACION] Usuario {username} registrado. '
                f'Email: {email}. Código enviado.'
            )
        
        return Response({
            'message': 'Usuario registrado exitosamente',
            'detail': 'Se ha enviado un código de verificación a tu email',
            'email': email,
            'username': username,
            'expires_in_minutes': 15
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        logger.error(f'[REGISTRO_ERROR] {str(e)}')
        return Response({
            'error': 'Error al registrar usuario',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonAuthThrottle])
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
        
        # 🛡️ PROTECCIÓN: Verificar intentos fallidos usando LoginAttempt
        bloqueado, tiempo_restante = verificar_intentos_login(email, ip_address)
        if bloqueado:
            logger.warning(
                f'[VERIFICACION_BLOQUEADA] Email {email} bloqueado por intentos fallidos. '
                f'IP: {ip_address}. Tiempo restante: {tiempo_restante}s'
            )
            return Response({
                'error': 'Demasiados intentos fallidos',
                'detail': f'Intenta nuevamente en {tiempo_restante // 60} minutos',
                'tiempo_restante_segundos': tiempo_restante
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Buscar usuario
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Registrar intento fallido
            registrar_intento_verificacion(email, ip_address, False)
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar si ya está activo
        if user.is_active:
            return Response({
                'error': 'El email ya está verificado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar código
        verificacion = EmailVerification.verificar_codigo(
            usuario=user,
            codigo=codigo
        )
        
        if verificacion is None:
            # 🛡️ PROTECCIÓN: Registrar intento fallido en LoginAttempt
            registrar_intento_verificacion(email, ip_address, False)
            
            # Incrementar intentos fallidos en EmailVerification
            ultima_verificacion = EmailVerification.objects.filter(
                usuario=user,
                verificado=False
            ).order_by('-created_at').first()
            
            if ultima_verificacion:
                ultima_verificacion.incrementar_intentos()
                
                # Bloquear después de 5 intentos fallidos en el código específico
                if ultima_verificacion.intentos_fallidos >= 5:
                    logger.warning(
                        f'[CODIGO_BLOQUEADO] Código del usuario {user.username} '
                        f'bloqueado por intentos fallidos'
                    )
                    return Response({
                        'error': 'Código bloqueado por intentos fallidos',
                        'detail': 'Solicita un nuevo código de verificación'
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            return Response({
                'error': 'Código inválido o expirado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Activar usuario y marcar verificación como completada
        with transaction.atomic():
            # Activar usuario
            user.is_active = True
            user.save()
            
            # Marcar verificación como completada
            verificacion.marcar_verificado()
            
            # Invalidar otros códigos pendientes
            EmailVerification.invalidar_codigos_usuario(user)
            
            # 🛡️ PROTECCIÓN: Registrar intento exitoso en LoginAttempt
            registrar_intento_verificacion(email, ip_address, True)
            
            logger.info(
                f'[EMAIL_VERIFICADO] Usuario {user.username} verificado exitosamente. IP: {ip_address}'
            )
        
        # Generar tokens JWT
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        access_token, refresh_token_obj = crear_tokens_jwt(
            user,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        # Preparar respuesta
        return Response({
            'message': 'Email verificado exitosamente',
            'access_token': access_token,
            'refresh_token': refresh_token_obj['token'],
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'nombre': user.first_name,
                'apellido': user.last_name,
                'rol': user.profile.rol if hasattr(user, 'profile') else 'cliente'
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f'[VERIFICACION_ERROR] {str(e)}')
        return Response({
            'error': 'Error al verificar email',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonAuthThrottle])
def resend_verification(request):
    """
    🔄 ENDPOINT: Reenviar código de verificación
    
    Genera un nuevo código y lo envía por email.
    
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
    2. Buscar usuario
    3. Verificar límites de reenvío (tiempo y cantidad)
    4. Invalidar códigos anteriores
    5. Generar nuevo código
    6. Enviar email
    """
    try:
        # Obtener email
        email = request.data.get('email', '').strip().lower()
        
        if not email:
            return Response({
                'error': 'Email es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar usuario
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar si ya está activo
        if user.is_active:
            return Response({
                'error': 'El email ya está verificado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 🛡️ PROTECCIÓN: Verificar límite de reenvíos
        ultima_verificacion = EmailVerification.objects.filter(
            usuario=user
        ).order_by('-created_at').first()
        
        if ultima_verificacion:
            # 🛡️ LÍMITE DE TIEMPO: 1 minuto entre reenvíos (patrón RefreshToken)
            if not ultima_verificacion.puede_reenviar(minutos_espera=1):
                tiempo_restante = 1 - (
                    (timezone.now() - ultima_verificacion.ultimo_reenvio).total_seconds() / 60
                )
                logger.warning(
                    f'[REENVIO_BLOQUEADO] Usuario {user.username} intentó reenviar '
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
                    f'[REENVIO_LIMITE] Usuario {user.username} alcanzó el límite de reenvíos'
                )
                return Response({
                    'error': 'Límite de reenvíos alcanzado',
                    'detail': 'Máximo 3 reenvíos permitidos. Contacta con soporte si necesitas ayuda.'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Marcar reenvío
            ultima_verificacion.marcar_reenvio()
        
        # Invalidar códigos anteriores
        EmailVerification.invalidar_codigos_usuario(user)
        
        # Crear nuevo código
        ip_address = request.META.get('REMOTE_ADDR')
        verificacion = EmailVerification.crear_codigo(
            usuario=user,
            duracion_minutos=15,
            ip_address=ip_address
        )
        
        # Enviar email de forma asíncrona
        enviar_email_verificacion.delay(
            usuario_id=user.id,
            codigo=verificacion.codigo
        )
        
        logger.info(
            f'[CODIGO_REENVIADO] Usuario {user.username}. '
            f'Reenvío #{ultima_verificacion.contador_reenvios if ultima_verificacion else 1}'
        )
        
        return Response({
            'message': 'Código de verificación reenviado',
            'email': email,
            'expires_in_minutes': 15
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
        
        # Buscar usuario
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar si ya está verificado
        is_verified = user.is_active
        
        # Buscar verificación pendiente
        verificacion_pendiente = EmailVerification.objects.filter(
            usuario=user,
            verificado=False
        ).order_by('-created_at').first()
        
        # Preparar respuesta
        response_data = {
            'email': email,
            'is_verified': is_verified,
            'username': user.username,
            'has_pending_verification': verificacion_pendiente is not None
        }
        
        # Si hay verificación pendiente, agregar detalles
        if verificacion_pendiente:
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
        
        logger.info(f'[ESTADO_VERIFICACION] Email {email}. Verificado: {is_verified}')
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f'[ESTADO_ERROR] {str(e)}')
        return Response({
            'error': 'Error al verificar estado',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
