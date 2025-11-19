"""
═══════════════════════════════════════════════════════════════════════════════
🔍 UTILIDAD - Sistema de Auditoría
═══════════════════════════════════════════════════════════════════════════════
Registra automáticamente todas las acciones realizadas en el panel de admin.
"""

import json
from decimal import Decimal
from api.models import AuditLog


def get_client_ip(request):
    """Obtener IP del cliente desde el request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def serializar_objeto(obj):
    """
    Serializar un objeto a un diccionario JSON-compatible.
    Maneja Decimals, fechas, y campos técnicos de Django.
    NUNCA incluye imagen_url en los detalles.
    """
    if not hasattr(obj, '__dict__'):
        return str(obj)
    
    datos = {}
    for key, value in obj.__dict__.items():
        # Filtrar campos técnicos de Django
        if key.startswith('_') or key in ['creado_por_id', 'actualizado_por_id']:
            continue
        
        # ✅ EXCLUIR COMPLETAMENTE imagen_url - nunca mostrar en historial
        if key == 'imagen_url':
            continue
            
        # Convertir Decimal a string
        if isinstance(value, Decimal):
            datos[key] = str(value)
        # Otros valores
        elif value is not None:
            try:
                json.dumps(value)  # Verificar si es serializable
                datos[key] = value
            except (TypeError, ValueError):
                datos[key] = str(value)
    
    return datos


def registrar_accion(request, accion, modulo, objeto_id, objeto_repr, detalles=None):
    """
    Registrar una acción en el log de auditoría.
    
    Args:
        request: HttpRequest object
        accion: str - Tipo de acción ('crear', 'editar', 'eliminar', etc.)
        modulo: str - Módulo afectado ('producto', 'usuario', 'pedido', etc.)
        objeto_id: int - ID del objeto afectado
        objeto_repr: str - Representación legible del objeto
        detalles: dict - Información adicional sobre el cambio
    
    Returns:
        AuditLog instance
    """
    if detalles is None:
        detalles = {}
    
    # Obtener información del request
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
    
    # Crear registro de auditoría
    audit_log = AuditLog.objects.create(
        usuario=request.user if request.user.is_authenticated else None,
        accion=accion,
        modulo=modulo,
        objeto_id=objeto_id,
        objeto_repr=objeto_repr,
        detalles=detalles,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return audit_log


def registrar_creacion(request, modulo, objeto):
    """
    Registrar creación de un objeto.
    Muestra todos los datos del objeto creado (excepto imagen_url).
    """
    datos_serializados = serializar_objeto(objeto)
    
    # Convertir Decimals a strings
    datos_formateados = {}
    for key, value in datos_serializados.items():
        if isinstance(value, Decimal):
            datos_formateados[key] = str(value)
        else:
            datos_formateados[key] = value
    
    detalles = {
        'datos_creados': datos_formateados
    }
    
    return registrar_accion(
        request=request,
        accion='crear',
        modulo=modulo,
        objeto_id=objeto.id,
        objeto_repr=str(objeto),
        detalles=detalles
    )


def registrar_edicion(request, modulo, objeto, cambios=None):
    """
    Registrar edición de un objeto.
    Captura SOLO los cambios realizados (antes → después).
    """
    if cambios is None:
        cambios = {}
    
    # Filtrar cambios: excluir imagen_url y campos vacíos
    cambios_filtrados = {}
    for key, valor_nuevo in cambios.items():
        # Excluir imagen_url
        if key == 'imagen_url':
            continue
        # Excluir valores vacíos
        if valor_nuevo is None or valor_nuevo == '':
            continue
        
        # Obtener valor anterior del objeto
        valor_anterior = getattr(objeto, key, None)
        
        # Solo incluir si hubo cambio
        if valor_anterior != valor_nuevo:
            # Convertir Decimal a string
            if isinstance(valor_anterior, Decimal):
                valor_anterior = str(valor_anterior)
            if isinstance(valor_nuevo, Decimal):
                valor_nuevo = str(valor_nuevo)
            
            # Convertir objetos a string para serialización JSON
            if valor_anterior is not None and not isinstance(valor_anterior, (str, int, float, bool)):
                valor_anterior = str(valor_anterior)
            if valor_nuevo is not None and not isinstance(valor_nuevo, (str, int, float, bool)):
                valor_nuevo = str(valor_nuevo)
            
            cambios_filtrados[key] = {
                'anterior': valor_anterior,
                'nuevo': valor_nuevo
            }
    
    detalles = {
        'cambios_realizados': cambios_filtrados
    }
    
    return registrar_accion(
        request=request,
        accion='editar',
        modulo=modulo,
        objeto_id=objeto.id,
        objeto_repr=str(objeto),
        detalles=detalles
    )


def registrar_eliminacion(request, modulo, objeto_id, objeto_repr, datos_eliminados=None):
    """
    Registrar eliminación de un objeto.
    Captura todos los datos del objeto eliminado (excepto imagen_url).
    """
    # Si no se proporcionan datos, usar diccionario vacío
    if datos_eliminados is None:
        datos_eliminados = {}
    
    # Convertir Decimals a strings
    datos_formateados = {}
    for key, value in datos_eliminados.items():
        if isinstance(value, Decimal):
            datos_formateados[key] = str(value)
        else:
            datos_formateados[key] = value
    
    detalles = {
        'datos_eliminados': datos_formateados
    }
    
    return registrar_accion(
        request=request,
        accion='eliminar',
        modulo=modulo,
        objeto_id=objeto_id,
        objeto_repr=objeto_repr,
        detalles=detalles
    )


def registrar_cambio_estado(request, modulo, objeto, nuevo_estado):
    """Registrar cambio de estado (activar/desactivar)"""
    accion = 'activar' if nuevo_estado else 'desactivar'
    detalles = {
        'accion': f'Objeto {"activado" if nuevo_estado else "desactivado"}',
        'estado_anterior': not nuevo_estado,
        'estado_nuevo': nuevo_estado
    }
    
    return registrar_accion(
        request=request,
        accion=accion,
        modulo=modulo,
        objeto_id=objeto.id,
        objeto_repr=str(objeto),
        detalles=detalles
    )


def registrar_cambio_rol(request, usuario, rol_anterior, rol_nuevo):
    """Registrar cambio de rol de usuario"""
    detalles = {
        'accion': 'Cambio de rol',
        'rol_anterior': rol_anterior,
        'rol_nuevo': rol_nuevo,
        'usuario_afectado': usuario.username
    }
    
    return registrar_accion(
        request=request,
        accion='cambiar_rol',
        modulo='usuario',
        objeto_id=usuario.id,
        objeto_repr=f'{usuario.username} ({usuario.get_full_name() or "Sin nombre"})',
        detalles=detalles
    )
