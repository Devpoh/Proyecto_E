from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductoViewSet, 
    register, 
    login, 
    logout, 
    refresh_token, 
    productos_carrusel, 
    get_csrf_token, 
    check_email,
    agregar_favorito,
    remover_favorito,
    es_favorito,
    verificar_favoritos_batch,
    validar_stock_producto,
    mis_pedidos,
    mis_favoritos
)
from .views_admin import (
    UserManagementViewSet,
    ProductoManagementViewSet,
    dashboard_stats,
    AuditLogViewSet
)
from .views_pedidos import PedidoViewSet, NotificacionViewSet
from .views_estadisticas import (
    estadisticas_ventas,
    estadisticas_usuarios,
    estadisticas_productos,
    reporte_completo
)
from . import urls_catalogo  # Corregir import de urls_catalogo

# Router principal
router = DefaultRouter()
router.register(r'productos', ProductoViewSet, basename='producto')

# Router para admin
admin_router = DefaultRouter()
admin_router.register(r'users', UserManagementViewSet, basename='admin-users')
admin_router.register(r'productos', ProductoManagementViewSet, basename='admin-productos')
admin_router.register(r'pedidos', PedidoViewSet, basename='admin-pedidos')
admin_router.register(r'historial', AuditLogViewSet, basename='admin-historial')

# Router para notificaciones
notif_router = DefaultRouter()
notif_router.register(r'notificaciones', NotificacionViewSet, basename='notificaciones')

urlpatterns = [
    # Rutas públicas
    path('', include(router.urls)),
    path('carrusel/', productos_carrusel, name='productos-carrusel'),
    path('catalogo/', include(urls_catalogo)),  # Agregar ruta catalogo
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/logout/', logout, name='logout'),
    path('auth/refresh/', refresh_token, name='refresh-token'),
    path('auth/csrf-token/', get_csrf_token, name='csrf-token'),
    path('auth/check-email/', check_email, name='check-email'),
    
    # Rutas de verificación de email
    path('auth/', include('api.urls_verificacion')),
    
    # Rutas de favoritos
    path('favoritos/agregar/<int:producto_id>/', agregar_favorito, name='agregar-favorito'),
    path('favoritos/remover/<int:producto_id>/', remover_favorito, name='remover-favorito'),
    path('favoritos/es-favorito/<int:producto_id>/', es_favorito, name='es-favorito'),
    path('favoritos/verificar-batch/', verificar_favoritos_batch, name='verificar-favoritos-batch'),
    
    # Rutas de usuario
    path('productos/<int:producto_id>/validar-stock/', validar_stock_producto, name='validar-stock'),
    path('mis-pedidos/', mis_pedidos, name='mis-pedidos'),
    path('mis-favoritos/', mis_favoritos, name='mis-favoritos'),
    
    # Rutas del carrito (manual)
    path('carrito/', include('api.urls_carrito')),
    
    # Notificaciones (usuario autenticado)
    path('', include(notif_router.urls)),
    
    # Rutas de admin
    path('admin/', include(admin_router.urls)),
    path('admin/dashboard/stats/', dashboard_stats, name='admin-dashboard-stats'),
    
    # Estadísticas avanzadas
    path('admin/estadisticas/ventas/', estadisticas_ventas, name='estadisticas-ventas'),
    path('admin/estadisticas/usuarios/', estadisticas_usuarios, name='estadisticas-usuarios'),
    path('admin/estadisticas/productos/', estadisticas_productos, name='estadisticas-productos'),
    path('admin/estadisticas/reporte/', reporte_completo, name='reporte-completo'),
]
