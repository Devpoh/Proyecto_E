"""
═══════════════════════════════════════════════════════════════════════════════
🔐 VALIDADORES - Seguridad y Validación de Datos
═══════════════════════════════════════════════════════════════════════════════

Funciones de validación para seguridad de contraseñas, emails y datos sensibles.
"""

import re
import hashlib
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as django_validate_email


def validar_contraseña_fuerte(password):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    🔐 Valida que la contraseña cumpla con requisitos de seguridad
    ═══════════════════════════════════════════════════════════════════════════════
    
    Requisitos:
    - Mínimo 8 caracteres
    - Al menos 1 mayúscula (A-Z)
    - Al menos 1 minúscula (a-z)
    - Al menos 1 número (0-9)
    - Al menos 1 carácter especial (!@#$%^&*...)
    
    Args:
        password (str): Contraseña a validar
    
    Raises:
        ValidationError: Si la contraseña no cumple con los requisitos
    
    Ejemplo:
        >>> validar_contraseña_fuerte("MiPassword123!")
        # Sin excepción - válida
        
        >>> validar_contraseña_fuerte("123456")
        # Lanza ValidationError
    """
    if not password:
        raise ValidationError("La contraseña es requerida")
    
    if len(password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres")
    
    if len(password) > 256:
        raise ValidationError("La contraseña no puede exceder 256 caracteres")
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError("La contraseña debe contener al menos 1 mayúscula (A-Z)")
    
    if not re.search(r'[a-z]', password):
        raise ValidationError("La contraseña debe contener al menos 1 minúscula (a-z)")
    
    if not re.search(r'[0-9]', password):
        raise ValidationError("La contraseña debe contener al menos 1 número (0-9)")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("La contraseña debe contener al menos 1 carácter especial (!@#$%^&*...)")
    
    # Verificar que no sea una contraseña común (solo si es exactamente igual)
    contraseñas_comunes = [
        'password1!', 'qwerty123!', 'admin123!', 'welcome1!',
        'letmein1!', 'monkey1!', 'dragon1!', 'master1!'
    ]
    if password.lower() in contraseñas_comunes:
        raise ValidationError("Esta contraseña es demasiado común. Elige una más única.")


def validar_email(email):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    📧 Valida que el email sea válido
    ═══════════════════════════════════════════════════════════════════════════════
    
    Args:
        email (str): Email a validar
    
    Raises:
        ValidationError: Si el email no es válido
    
    Ejemplo:
        >>> validar_email("usuario@example.com")
        # Sin excepción - válida
    """
    email = email.strip().lower()
    
    if not email:
        raise ValidationError("El email es requerido")
    
    if len(email) > 254:
        raise ValidationError("El email es demasiado largo")
    
    try:
        django_validate_email(email)
    except ValidationError:
        raise ValidationError("El email no es válido")
    
    return email


def hash_email_para_logs(email):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    🔒 Retorna un hash del email para logs (no expone el email completo)
    ═══════════════════════════════════════════════════════════════════════════════
    
    Propósito: Permitir auditoría sin exponer información personal
    
    Args:
        email (str): Email a hashear
    
    Returns:
        str: Primeros 8 caracteres del hash SHA256
    
    Ejemplo:
        >>> hash_email_para_logs("usuario@example.com")
        "a1b2c3d4"
    """
    return hashlib.sha256(email.encode()).hexdigest()[:8]


def sanitizar_para_logs(valor):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    🧹 Sanitiza valores para logs (remueve datos sensibles)
    ═══════════════════════════════════════════════════════════════════════════════
    
    Propósito: Prevenir que datos sensibles terminen en logs
    
    Args:
        valor (str): Valor a sanitizar
    
    Returns:
        str: Valor sanitizado
    
    Ejemplo:
        >>> sanitizar_para_logs("password123")
        "[REDACTED]"
    """
    if not valor:
        return "[EMPTY]"
    
    valor_str = str(valor).lower()
    
    # Palabras clave que indican datos sensibles
    palabras_sensibles = [
        'password', 'contraseña', 'pwd', 'secret', 'token', 'key',
        'api_key', 'access_token', 'refresh_token', 'codigo'
    ]
    
    for palabra in palabras_sensibles:
        if palabra in valor_str:
            return "[REDACTED]"
    
    return valor
