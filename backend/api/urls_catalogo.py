"""
═══════════════════════════════════════════════════════════════════════════════
🔗 URLS - Catálogo de Productos
═══════════════════════════════════════════════════════════════════════════════

Rutas para endpoints de catálogo.
Separado de urls.py para mantener código limpio y organizado.
"""

from django.urls import path
from .views_catalogo import (
    productos_catalogo_completo,
    productos_tarjetas_inferiores,
)

urlpatterns = [
    path('productos/', productos_catalogo_completo, name='catalogo-productos'),
    path('tarjetas-inferiores/', productos_tarjetas_inferiores, name='tarjetas-inferiores'),
]
