"""
═══════════════════════════════════════════════════════════════════════════════
🚦 THROTTLES - Rate Limiting Centralizado (Producción Realista)
═══════════════════════════════════════════════════════════════════════════════

Clases de throttle personalizadas para diferentes tipos de endpoints.
Cada scope está configurado en settings.py con tasas específicas.

Scopes disponibles:
- 'anon_auth': Autenticación (login, register) - 5/minuto (anónimos)
- 'cart_write': Escritura en carrito (bulk-update) - 30/minuto (logueados)
- 'checkout': Proceso de checkout - 5/hora (logueados)
- 'admin': Panel administrativo - 2000/hora (admin)
- 'user': Endpoints logueados - 5000/hora
- 'anon': Endpoints públicos - 1000/hora

SINCRONIZACIÓN:
- LoginAttempt bloquea por IP/usuario (5 intentos/1 minuto)
- Throttles DRF se aplican ADEMÁS para máxima seguridad
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
import logging

logger = logging.getLogger(__name__)


# ==========================================
# 🔐 LOGIN (Anónimos)
# ==========================================
class AnonLoginRateThrottle(AnonRateThrottle):
    """
    Throttle para endpoints de autenticación (anónimos).
    Previene ataques de fuerza bruta en login/register.
    Scope: 'anon_auth' → 5 requests/minuto
    
    NOTA: Trabaja en conjunto con LoginAttempt (5 intentos/1 minuto)
    """
    scope = "anon_auth"


# ==========================================
# 🛒 CARRITO (Usuarios logueados)
# ==========================================
class CartWriteRateThrottle(UserRateThrottle):
    """
    Throttle para escritura masiva en carrito.
    Protege el endpoint bulk-update que sincroniza múltiples items.
    Scope: 'cart_write' → 30 requests/minuto
    """
    scope = "cart_write"


# ==========================================
# 💳 CHECKOUT (Usuarios logueados)
# ==========================================
class CheckoutRateThrottle(UserRateThrottle):
    """
    Throttle para proceso de checkout.
    Protege el endpoint crítico de checkout.
    Previene múltiples intentos de compra simultáneos.
    Scope: 'checkout' → 5 requests/hora
    """
    scope = "checkout"


# ==========================================
# 🧑‍💼 ADMIN
# ==========================================
class AdminRateThrottle(UserRateThrottle):
    """
    Throttle para panel administrativo.
    Protege endpoints CRUD del panel admin.
    Scope: 'admin' → 2000 requests/hora
    """
    scope = "admin"


# ==========================================
# 👥 USUARIOS LOGUEADOS (Límites generales)
# ==========================================
class UserGlobalRateThrottle(UserRateThrottle):
    """
    Throttle general para usuarios logueados.
    Aplica a endpoints públicos que requieren autenticación.
    Scope: 'user' → 5000 requests/hora
    """
    scope = "user"


# ==========================================
# 🌍 ANÓNIMOS (Consultas públicas)
# ==========================================
class AnonGlobalRateThrottle(AnonRateThrottle):
    """
    Throttle general para usuarios anónimos.
    Aplica a endpoints públicos sin autenticación.
    Scope: 'anon' → 1000 requests/hora
    """
    scope = "anon"
