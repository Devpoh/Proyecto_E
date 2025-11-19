"""
═══════════════════════════════════════════════════════════════════════════════
📊 VIEWS - Estadísticas Avanzadas
═══════════════════════════════════════════════════════════════════════════════
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Sum, Avg, Q, F
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
from .models import Pedido, Producto, UserProfile, DetallePedido
from .views_admin import IsAdminOrStaff
from .utils.cache_manager import CacheManager


class EstadisticasPagination(PageNumberPagination):
    """Paginación para endpoints de estadísticas"""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


@api_view(['GET'])
@permission_classes([IsAdminOrStaff])
def estadisticas_ventas(request):
    """
    Estadísticas detalladas de ventas
    
    Retorna:
    - Ventas por mes (últimos 12 meses)
    - Productos más vendidos
    - Métodos de pago más usados
    - Ticket promedio
    
    Caché: 5 minutos (datos volátiles)
    Invalidación: Automática cuando se crea/actualiza un Pedido
    """
    
    def fetch_estadisticas_ventas():
        """Función que obtiene datos de la fuente original"""
        # Ventas por mes (últimos 12 meses)
        ventas_por_mes = []
        for i in range(12):
            mes_inicio = (timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) 
                         - timedelta(days=30 * i))
            mes_fin = mes_inicio + timedelta(days=30)
            
            ventas = Pedido.objects.filter(
                created_at__gte=mes_inicio,
                created_at__lt=mes_fin,
                estado__in=['confirmado', 'en_preparacion', 'en_camino', 'entregado']
            ).aggregate(
                total=Sum('total'),
                count=Count('id')
            )
            
            ventas_por_mes.insert(0, {
                'mes': mes_inicio.strftime('%Y-%m'),
                'total': float(ventas['total'] or 0),
                'pedidos': ventas['count']
            })
        
        # Productos más vendidos
        productos_vendidos = DetallePedido.objects.filter(
            pedido__estado__in=['confirmado', 'en_preparacion', 'en_camino', 'entregado']
        ).values(
            'producto__nombre',
            'producto__categoria'
        ).annotate(
            cantidad_vendida=Sum('cantidad'),
            ingresos=Sum('subtotal')
        ).order_by('-cantidad_vendida')[:10]
        
        # Métodos de pago (limitado a 10 métodos)
        metodos_pago = Pedido.objects.filter(
            estado__in=['confirmado', 'en_preparacion', 'en_camino', 'entregado']
        ).values('metodo_pago').annotate(
            count=Count('id'),
            total=Sum('total')
        )[:10]
        
        # Ticket promedio
        ticket_promedio = Pedido.objects.filter(
            estado__in=['confirmado', 'en_preparacion', 'en_camino', 'entregado']
        ).aggregate(promedio=Avg('total'))['promedio'] or 0
        
        return {
            'ventas_por_mes': ventas_por_mes,
            'productos_mas_vendidos': list(productos_vendidos),
            'metodos_pago': list(metodos_pago),
            'ticket_promedio': float(ticket_promedio),
        }
    
    # Usar CacheManager con invalidación automática
    data = CacheManager.get(
        cache_key='estadisticas_ventas',
        fetch_func=fetch_estadisticas_ventas,
        ttl=300  # 5 minutos
    )
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAdminOrStaff])
def estadisticas_usuarios(request):
    """
    Estadísticas de usuarios
    
    Retorna:
    - Crecimiento de usuarios por mes
    - Usuarios por rol
    - Usuarios más activos
    - Tasa de retención
    
    Caché: 10 minutos (datos menos volátiles)
    Invalidación: Automática cuando se crea/actualiza un UserProfile
    """
    
    def fetch_estadisticas_usuarios():
        """Función que obtiene datos de la fuente original"""
        # Crecimiento por mes (últimos 12 meses)
        usuarios_por_mes = []
        for i in range(12):
            mes_inicio = (timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) 
                         - timedelta(days=30 * i))
            mes_fin = mes_inicio + timedelta(days=30)
            
            nuevos = User.objects.filter(
                date_joined__gte=mes_inicio,
                date_joined__lt=mes_fin
            ).count()
            
            usuarios_por_mes.insert(0, {
                'mes': mes_inicio.strftime('%Y-%m'),
                'nuevos': nuevos
            })
        
        # Usuarios por rol
        usuarios_por_rol = UserProfile.objects.values('rol').annotate(
            count=Count('id')
        )
        
        # Usuarios más activos (por pedidos)
        usuarios_activos = User.objects.annotate(
            pedidos_count=Count('pedidos')
        ).filter(pedidos_count__gt=0).order_by('-pedidos_count')[:10].values(
            'username',
            'first_name',
            'last_name',
            'pedidos_count'
        )
        
        # Tasa de retención (usuarios con más de 1 pedido)
        total_usuarios = User.objects.filter(pedidos__isnull=False).distinct().count()
        usuarios_recurrentes = User.objects.annotate(
            pedidos_count=Count('pedidos')
        ).filter(pedidos_count__gt=1).count()
        
        tasa_retencion = (usuarios_recurrentes / total_usuarios * 100) if total_usuarios > 0 else 0
        
        return {
            'usuarios_por_mes': usuarios_por_mes,
            'usuarios_por_rol': list(usuarios_por_rol),
            'usuarios_mas_activos': list(usuarios_activos),
            'tasa_retencion': round(tasa_retencion, 2),
            'total_usuarios': total_usuarios,
            'usuarios_recurrentes': usuarios_recurrentes,
        }
    
    # Usar CacheManager con invalidación automática
    data = CacheManager.get(
        cache_key='estadisticas_usuarios',
        fetch_func=fetch_estadisticas_usuarios,
        ttl=600  # 10 minutos
    )
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAdminOrStaff])
def estadisticas_productos(request):
    """
    Estadísticas de productos
    
    Retorna:
    - Productos por categoría
    - Stock bajo
    - Productos sin stock
    - Valor del inventario
    """
    
    # Productos por categoría
    productos_por_categoria = Producto.objects.values('categoria').annotate(
        count=Count('id'),
        stock_total=Sum('stock')
    )
    
    # Productos con stock bajo (menos de 10)
    stock_bajo = Producto.objects.filter(
        stock__lt=10,
        stock__gt=0,
        activo=True
    ).values('id', 'nombre', 'stock', 'categoria')
    
    # Productos sin stock
    sin_stock = Producto.objects.filter(
        stock=0,
        activo=True
    ).count()
    
    # Valor del inventario
    valor_inventario = Producto.objects.filter(activo=True).aggregate(
        total=Sum('precio')
    )['total'] or 0
    
    # Productos más rentables (precio * stock)
    from django.db.models import F
    productos_rentables = Producto.objects.filter(
        activo=True,
        stock__gt=0
    ).annotate(
        valor_total=F('precio') * F('stock')
    ).order_by('-valor_total')[:10].values(
        'nombre',
        'precio',
        'stock',
        'valor_total'
    )
    
    return Response({
        'productos_por_categoria': list(productos_por_categoria),
        'stock_bajo': list(stock_bajo),
        'productos_sin_stock': sin_stock,
        'valor_inventario': float(valor_inventario),
        'productos_mas_rentables': list(productos_rentables),
    })


@api_view(['GET'])
@permission_classes([IsAdminOrStaff])
def reporte_completo(request):
    """
    Reporte completo para exportación
    
    Combina todas las estadísticas en un solo endpoint
    """
    
    # Resumen general
    total_usuarios = User.objects.count()
    total_productos = Producto.objects.filter(activo=True).count()
    total_pedidos = Pedido.objects.count()
    
    # Ingresos
    ingresos_totales = Pedido.objects.filter(
        estado__in=['confirmado', 'en_preparacion', 'en_camino', 'entregado']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Pedidos del mes
    inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    pedidos_mes = Pedido.objects.filter(created_at__gte=inicio_mes).count()
    ingresos_mes = Pedido.objects.filter(
        created_at__gte=inicio_mes,
        estado__in=['confirmado', 'en_preparacion', 'en_camino', 'entregado']
    ).aggregate(total=Sum('total'))['total'] or 0
    
    # Pedidos pendientes
    pedidos_pendientes = Pedido.objects.filter(estado='pendiente').count()
    pedidos_en_proceso = Pedido.objects.filter(
        estado__in=['confirmado', 'en_preparacion', 'en_camino']
    ).count()
    
    return Response({
        'resumen': {
            'total_usuarios': total_usuarios,
            'total_productos': total_productos,
            'total_pedidos': total_pedidos,
            'ingresos_totales': float(ingresos_totales),
            'pedidos_mes': pedidos_mes,
            'ingresos_mes': float(ingresos_mes),
            'pedidos_pendientes': pedidos_pendientes,
            'pedidos_en_proceso': pedidos_en_proceso,
        },
        'fecha_generacion': timezone.now().isoformat(),
    })
