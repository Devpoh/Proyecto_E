from django.contrib import admin
from .models import Producto, UserProfile, Pedido, DetallePedido, Notificacion, AuditLog, TokenBlacklist, Cart, CartItem


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'rol', 'telefono', 'created_at']
    list_filter = ['rol', 'created_at']
    search_fields = ['user__username', 'user__email', 'telefono']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'categoria', 'precio', 'stock', 'activo', 'creado_por', 'created_at']
    search_fields = ['nombre', 'descripcion']
    list_filter = ['categoria', 'activo', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'estado', 'total', 'metodo_pago', 'mensajero', 'created_at']
    list_filter = ['estado', 'metodo_pago', 'created_at']
    search_fields = ['usuario__username', 'telefono', 'direccion_entrega']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [DetallePedidoInline]


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'usuario', 'tipo', 'leida', 'created_at']
    list_filter = ['tipo', 'leida', 'created_at']
    search_fields = ['titulo', 'mensaje', 'usuario__username']
    readonly_fields = ['created_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'usuario', 'accion', 'modulo', 'objeto_repr', 'ip_address']
    list_filter = ['accion', 'modulo', 'timestamp']
    search_fields = ['objeto_repr', 'usuario__username', 'ip_address']
    readonly_fields = ['usuario', 'accion', 'modulo', 'objeto_id', 'objeto_repr', 'detalles', 'ip_address', 'user_agent', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        """No permitir agregar registros manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar registros"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar"""
        return request.user.is_superuser


@admin.register(TokenBlacklist)
class TokenBlacklistAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'razon', 'blacklisted_at']
    list_filter = ['razon', 'blacklisted_at']
    search_fields = ['usuario__username', 'usuario__email', 'token']
    readonly_fields = ['token', 'usuario', 'blacklisted_at', 'razon']
    date_hierarchy = 'blacklisted_at'
    
    def has_add_permission(self, request):
        """No permitir agregar registros manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar registros"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar"""
        return request.user.is_superuser


# ═══════════════════════════════════════════════════════════════════════════════
# 🛒 CARRITO DE COMPRAS - ADMIN
# ═══════════════════════════════════════════════════════════════════════════════

class CartItemInline(admin.TabularInline):
    """Inline para items del carrito"""
    model = CartItem
    extra = 0
    readonly_fields = ['created_at', 'updated_at', 'price_at_addition']
    fields = ['product', 'quantity', 'price_at_addition']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin para carritos de compras"""
    list_display = ('user', 'get_total_items', 'get_total', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]
    
    def get_total_items(self, obj):
        """Muestra la cantidad total de items"""
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'
    
    def get_total(self, obj):
        """Muestra el total del carrito"""
        return f'${obj.get_total():.2f}'
    get_total.short_description = 'Total'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin para items del carrito"""
    list_display = ('product', 'cart', 'quantity', 'price_at_addition', 'get_subtotal', 'created_at')
    list_filter = ('created_at', 'product__categoria')
    search_fields = ('product__nombre', 'cart__user__email')
    readonly_fields = ('created_at', 'updated_at', 'price_at_addition')
    
    def get_subtotal(self, obj):
        """Muestra el subtotal del item"""
        return f'${obj.get_subtotal():.2f}'
    get_subtotal.short_description = 'Subtotal'
