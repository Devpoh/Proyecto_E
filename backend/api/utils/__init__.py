"""Utilidades del API"""
from .audit import (
    registrar_accion,
    registrar_creacion,
    registrar_edicion,
    registrar_eliminacion,
    registrar_cambio_estado,
    registrar_cambio_rol,
)

from .jwt_utils import (
    generar_access_token,
    verificar_access_token,
    obtener_usuario_desde_token,
    extraer_token_desde_header,
    obtener_info_request,
)

__all__ = [
    'registrar_accion',
    'registrar_creacion',
    'registrar_edicion',
    'registrar_eliminacion',
    'registrar_cambio_estado',
    'registrar_cambio_rol',
    'generar_access_token',
    'verificar_access_token',
    'obtener_usuario_desde_token',
    'extraer_token_desde_header',
    'obtener_info_request',
]
