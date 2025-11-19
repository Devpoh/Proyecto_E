"""
═══════════════════════════════════════════════════════════════════════════════
🔍 VALIDATORS - Validadores Personalizados
═══════════════════════════════════════════════════════════════════════════════

Validadores para query parameters y datos de entrada
"""

from rest_framework import serializers
from datetime import datetime


def validate_query_params(request, required_params=None, optional_params=None):
    """
    Validar query parameters de un request
    
    Args:
        request: HttpRequest object (DRF Request o Django WSGIRequest)
        required_params: dict con {nombre: tipo} de parámetros requeridos
        optional_params: dict con {nombre: tipo} de parámetros opcionales
    
    Returns:
        dict con parámetros validados o error
    
    Tipos soportados: 'int', 'str', 'bool', 'date', 'float'
    """
    
    if required_params is None:
        required_params = {}
    if optional_params is None:
        optional_params = {}
    
    validated = {}
    errors = {}
    
    # Obtener query params (soporta DRF Request y Django WSGIRequest)
    if hasattr(request, 'query_params'):
        query_dict = request.query_params
    else:
        query_dict = request.GET
    
    # Validar parámetros requeridos
    for param_name, param_type in required_params.items():
        value = query_dict.get(param_name)
        
        if value is None:
            errors[param_name] = f"Parámetro requerido: {param_name}"
            continue
        
        try:
            validated[param_name] = _convert_param(value, param_type, param_name)
        except ValueError as e:
            errors[param_name] = str(e)
    
    # Validar parámetros opcionales
    for param_name, param_type in optional_params.items():
        value = query_dict.get(param_name)
        
        if value is None:
            continue
        
        try:
            validated[param_name] = _convert_param(value, param_type, param_name)
        except ValueError as e:
            errors[param_name] = str(e)
    
    if errors:
        raise ValueError(f"Errores en query params: {errors}")
    
    return validated


def _convert_param(value, param_type, param_name):
    """Convertir valor a tipo especificado"""
    
    if param_type == 'int':
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"{param_name} debe ser un número entero")
    
    elif param_type == 'float':
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"{param_name} debe ser un número decimal")
    
    elif param_type == 'bool':
        if value.lower() in ['true', '1', 'yes']:
            return True
        elif value.lower() in ['false', '0', 'no']:
            return False
        else:
            raise ValueError(f"{param_name} debe ser 'true' o 'false'")
    
    elif param_type == 'date':
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            raise ValueError(f"{param_name} debe estar en formato ISO (YYYY-MM-DD)")
    
    elif param_type == 'str':
        if not isinstance(value, str):
            raise ValueError(f"{param_name} debe ser texto")
        return value.strip()
    
    else:
        raise ValueError(f"Tipo desconocido: {param_type}")


def validate_page_number(page_str, max_page=None):
    """Validar número de página"""
    try:
        page = int(page_str)
        if page < 1:
            raise ValueError("Página debe ser >= 1")
        if max_page and page > max_page:
            raise ValueError(f"Página no puede exceder {max_page}")
        return page
    except ValueError as e:
        raise ValueError(f"Página inválida: {str(e)}")


def validate_page_size(size_str, max_size=1000):
    """Validar tamaño de página"""
    try:
        size = int(size_str)
        if size < 1:
            raise ValueError("Tamaño de página debe ser >= 1")
        if size > max_size:
            raise ValueError(f"Tamaño de página no puede exceder {max_size}")
        return size
    except ValueError as e:
        raise ValueError(f"Tamaño de página inválido: {str(e)}")
