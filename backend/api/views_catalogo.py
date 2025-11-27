"""
═══════════════════════════════════════════════════════════════════════════════
📦 VIEWS - Catálogo de Productos
═══════════════════════════════════════════════════════════════════════════════

Endpoints para obtener productos del catálogo completo y tarjetas inferiores.
Separado de views.py para mantener código limpio y organizado.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from django.db.models import Q
from .models import Producto
from .serializers import ProductoSerializer
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def productos_catalogo_completo(request):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    📦 ENDPOINT - Catálogo Completo de Productos
    ═══════════════════════════════════════════════════════════════════════════════
    
    Obtiene TODOS los productos marcados para mostrar en el catálogo completo, INCLUYENDO el carrusel principal.
    SIN LÍMITE de productos.
    
    GET /api/catalogo/productos/
    
    Query Parameters:
    - categoria: str (opcional) - Filtrar por categoría
    - search: str (opcional) - Buscar por nombre o descripción
    
    Retorna:
    - count: int - Número total de productos
    - data: array - Lista de productos con información completa
    """
    try:
        # ✅ CORREGIDO: Obtener TODOS los productos con en_all_products=true (incluyendo carrusel)
        queryset = Producto.objects.filter(
            en_all_products=True,
            activo=True
        ).select_related(
            'creado_por'
        ).only(
            'id', 'nombre', 'descripcion', 'precio', 'descuento', 'categoria',
            'imagen', 'imagen_url', 'stock_total', 'stock_reservado', 'stock_vendido',
            'activo', 'en_all_products', 'en_carousel_card', 'en_carrusel',
            'creado_por', 'created_at', 'updated_at'
        ).order_by('-created_at')
        
        # Filtros opcionales
        categoria = request.query_params.get('categoria', None)
        search = request.query_params.get('search', None)
        
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search)
            )
        
        # Serializar
        serializer = ProductoSerializer(
            queryset,
            many=True,
            context={'is_list': True, 'request': request}
        )
        
        response_data = {
            'count': len(serializer.data),
            'data': serializer.data
        }
        
        logger.info(f'[CATALOGO_COMPLETO] {len(serializer.data)} productos cargados')
        
        return Response(response_data)
    
    except Exception as e:
        logger.error(f'Error al obtener catálogo completo: {str(e)}')
        return Response(
            {'error': 'Error al obtener productos'},
            status=500
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def productos_tarjetas_inferiores(request):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    🎠 ENDPOINT - Tarjetas Inferiores
    ═══════════════════════════════════════════════════════════════════════════════
    
    Obtiene TODOS los productos marcados para mostrar en tarjetas inferiores.
    SIN LÍMITE de productos.
    
    GET /api/catalogo/tarjetas-inferiores/
    
    Retorna:
    - count: int - Número total de productos
    - data: array - Lista de productos
    """
    try:
        # Obtener TODOS los productos con en_carousel_card=true
        queryset = Producto.objects.filter(
            en_carousel_card=True,
            activo=True
        ).select_related(
            'creado_por'
        ).only(
            'id', 'nombre', 'descripcion', 'precio', 'descuento', 'categoria',
            'imagen', 'imagen_url', 'stock_total', 'stock_reservado', 'stock_vendido',
            'activo', 'en_all_products', 'en_carousel_card', 'en_carrusel',
            'creado_por', 'created_at', 'updated_at'
        ).order_by('-created_at')
        
        # Serializar
        serializer = ProductoSerializer(
            queryset,
            many=True,
            context={'is_list': True, 'request': request}
        )
        
        response_data = {
            'count': len(serializer.data),
            'data': serializer.data
        }
        
        logger.info(f'[TARJETAS_INFERIORES] {len(serializer.data)} productos cargados')
        
        return Response(response_data)
    
    except Exception as e:
        logger.error(f'Error al obtener tarjetas inferiores: {str(e)}')
        return Response(
            {'error': 'Error al obtener productos'},
            status=500
        )
