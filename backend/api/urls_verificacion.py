"""
═══════════════════════════════════════════════════════════════════════════════
🔗 URLS - Verificación de Email
═══════════════════════════════════════════════════════════════════════════════

Rutas para verificación de email con código de 6 dígitos.
"""

from django.urls import path
from .views_verificacion import (
    register_with_verification,
    verify_email,
    resend_verification,
    check_verification_status
)

urlpatterns = [
    # Registro con verificación
    path('register-with-verification/', register_with_verification, name='register_with_verification'),
    
    # Verificar email
    path('verify-email/', verify_email, name='verify_email'),
    
    # Reenviar código
    path('resend-verification/', resend_verification, name='resend_verification'),
    
    # Estado de verificación
    path('verification-status/', check_verification_status, name='check_verification_status'),
]
