"""
═══════════════════════════════════════════════════════════════════════════════
🎯 CELERY TASKS - Tareas Asincrónicas
═══════════════════════════════════════════════════════════════════════════════

Tareas que se ejecutan en segundo plano sin bloquear el servidor.

Tareas:
1. liberar_reservas_expiradas() - Libera stock de reservas vencidas
2. limpiar_tokens_expirados() - Limpia tokens JWT expirados
3. enviar_email_verificacion() - Envía email de verificación con código
4. limpiar_codigos_verificacion() - Limpia códigos de verificación expirados
"""

from celery import shared_task
from django.utils import timezone
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def liberar_reservas_expiradas(self):
    """
    🔄 TAREA: Liberar reservas de stock expiradas
    
    Ejecuta cada minuto (configurado en celery.py)
    
    Flujo:
    1. Busca todas las reservas con status='pending' y expires_at < ahora
    2. Para cada reserva expirada:
       - Libera el stock_reservado del producto
       - Marca la reserva como 'expired'
    3. Retorna cantidad de reservas liberadas
    
    Seguridad:
    - @transaction.atomic: Si falla, todo se revierte
    - Manejo de excepciones con reintentos
    - Logging detallado para auditoría
    """
    from .models import StockReservation, Producto
    
    try:
        ahora = timezone.now()
        
        # Buscar reservas expiradas
        reservas_expiradas = StockReservation.objects.filter(
            status='pending',
            expires_at__lt=ahora
        ).select_related('producto', 'usuario')
        
        count = 0
        
        with transaction.atomic():
            for reserva in reservas_expiradas:
                try:
                    # Liberar stock_reservado
                    producto = reserva.producto
                    producto.stock_reservado -= reserva.cantidad
                    
                    # Validar que no quede negativo
                    if producto.stock_reservado < 0:
                        logger.warning(
                            f'[RESERVA_EXPIRADA] Stock negativo detectado para '
                            f'producto {producto.id}. Corrigiendo a 0.'
                        )
                        producto.stock_reservado = 0
                    
                    producto.save()
                    
                    # Marcar reserva como expirada
                    reserva.status = 'expired'
                    reserva.cancelled_at = ahora
                    reserva.save()
                    
                    count += 1
                    
                    logger.info(
                        f'[RESERVA_EXPIRADA] Liberada reserva {reserva.id} '
                        f'del usuario {reserva.usuario.username} '
                        f'(Producto: {producto.nombre}, Cantidad: {reserva.cantidad})'
                    )
                
                except Exception as e:
                    logger.error(
                        f'[RESERVA_EXPIRADA_ERROR] Error liberando reserva {reserva.id}: {str(e)}'
                    )
                    continue
        
        logger.info(f'[RESERVAS_EXPIRADAS] Total liberadas: {count}')
        return {
            'status': 'success',
            'reservas_liberadas': count,
            'timestamp': ahora.isoformat()
        }
    
    except Exception as exc:
        logger.error(f'[LIBERAR_RESERVAS_ERROR] {str(exc)}')
        # Reintentar con backoff exponencial
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def limpiar_tokens_expirados(self):
    """
    🔄 TAREA: Limpiar tokens JWT expirados
    
    Ejecuta cada hora (configurado en celery.py)
    
    Flujo:
    1. Busca todos los tokens en blacklist con expiration < ahora
    2. Los elimina de la base de datos
    3. Retorna cantidad de tokens eliminados
    
    Nota: Los tokens JWT expiran automáticamente, pero mantener la blacklist
    limpia evita que crezca indefinidamente.
    """
    from .models import TokenBlacklist
    
    try:
        ahora = timezone.now()
        
        # Buscar tokens en blacklist que fueron añadidos hace más de 24 horas
        # (los tokens JWT expiran en 24h, así que podemos limpiar después)
        hace_24_horas = ahora - timezone.timedelta(hours=24)
        tokens_expirados = TokenBlacklist.objects.filter(
            blacklisted_at__lt=hace_24_horas
        )
        
        count = tokens_expirados.count()
        tokens_expirados.delete()
        
        logger.info(f'[TOKENS_LIMPIOS] Total eliminados: {count}')
        return {
            'status': 'success',
            'tokens_eliminados': count,
            'timestamp': ahora.isoformat()
        }
    
    except Exception as exc:
        logger.error(f'[LIMPIAR_TOKENS_ERROR] {str(exc)}')
        # Reintentar con backoff exponencial
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def enviar_email_verificacion(self, email=None, codigo=None, nombre=None, usuario_id=None):
    """
    📧 TAREA: Enviar email de verificación
    
    Envía un email con el código de verificación de 6 dígitos.
    Usa plantilla HTML profesional para mejor presentación.
    
    ✅ OPCIÓN 1: Soporta dos modos:
    - Modo nuevo: email, codigo, nombre (sin usuario creado aún)
    - Modo antiguo: usuario_id, codigo (usuario ya existe)
    
    Args:
        email: Email del usuario (OPCIÓN 1)
        codigo: Código de verificación de 6 dígitos
        nombre: Nombre del usuario (OPCIÓN 1)
        usuario_id: ID del usuario (modo antiguo)
    
    Flujo:
    1. Obtiene datos del usuario (temporal o existente)
    2. Renderiza plantilla HTML con contexto
    3. Envía el email usando Gmail SMTP (HTML + texto plano)
    4. Registra el resultado en logs
    
    Seguridad:
    - Reintentos automáticos (max 3)
    - Logging detallado
    - Manejo de excepciones
    """
    from django.core.mail import EmailMultiAlternatives
    from django.contrib.auth.models import User
    from django.conf import settings
    from django.template.loader import render_to_string
    
    try:
        # Modo OPCIÓN 1: Datos temporales (sin usuario aún)
        if email and codigo and nombre:
            email_destino = email
            nombre_usuario = nombre
            
            logger.info(f'[EMAIL_VERIFICACION] Enviando a {email_destino} (modo temporal)')
        
        # Modo antiguo: Usuario ya existe
        elif usuario_id and codigo:
            usuario = User.objects.get(id=usuario_id)
            email_destino = usuario.email
            nombre_usuario = usuario.first_name or usuario.username
            
            logger.info(f'[EMAIL_VERIFICACION] Enviando a {email_destino} (modo usuario existente)')
        
        else:
            raise ValueError('Parámetros inválidos: proporciona (email, codigo, nombre) o (usuario_id, codigo)')
        
        # Contexto para la plantilla
        context = {
            'nombre': nombre_usuario,
            'codigo': codigo,
            'username': nombre_usuario,
        }
        
        # Renderizar plantilla HTML
        html_content = render_to_string('emails/verificacion_email.html', context)
        
        # Mensaje de texto plano (fallback)
        text_content = f'''
Hola {nombre_usuario},

Tu código de verificación es: {codigo}

Este código expira en 5 minutos.

Si no solicitaste este código, ignora este email.

Saludos,
Equipo Electronica Isla
        '''
        
        # Crear email con HTML y texto plano
        subject = 'Verifica tu cuenta - Electronica Isla'
        email_msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_destino]
        )
        email_msg.attach_alternative(html_content, "text/html")
        
        # Enviar email
        email_msg.send(fail_silently=False)
        
        logger.info(f'[EMAIL_VERIFICACION] Enviado a {email_destino} (HTML)')
        return {
            'status': 'success',
            'email': email_destino,
            'usuario_id': usuario_id,
            'format': 'html'
        }
    
    except User.DoesNotExist:
        logger.error(f'[EMAIL_ERROR] Usuario {usuario_id} no encontrado')
        return {
            'status': 'error',
            'message': 'Usuario no encontrado'
        }
    
    except Exception as exc:
        logger.error(f'[EMAIL_ERROR] {str(exc)}')
        # Reintentar con backoff exponencial (60 segundos)
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def limpiar_codigos_verificacion(self):
    """
    🔄 TAREA: Limpiar códigos de verificación expirados
    
    Ejecuta cada 6 horas (configurado en celery.py)
    
    Flujo:
    1. Busca todos los códigos con expires_at < ahora y verificado=False
    2. Los elimina de la base de datos
    3. Retorna cantidad de códigos eliminados
    
    Nota: Los códigos de verificación expiran en 15 minutos, pero mantener
    la base de datos limpia evita que crezca indefinidamente.
    """
    from .models import EmailVerification
    
    try:
        ahora = timezone.now()
        
        # Buscar códigos expirados y no verificados
        codigos_expirados = EmailVerification.objects.filter(
            expires_at__lt=ahora,
            verificado=False
        )
        
        count = codigos_expirados.count()
        codigos_expirados.delete()
        
        logger.info(f'[CODIGOS_LIMPIOS] Total eliminados: {count}')
        return {
            'status': 'success',
            'codigos_eliminados': count,
            'timestamp': ahora.isoformat()
        }
    
    except Exception as exc:
        logger.error(f'[LIMPIAR_CODIGOS_ERROR] {str(exc)}')
        # Reintentar con backoff exponencial
        raise self.retry(exc=exc, countdown=60)
