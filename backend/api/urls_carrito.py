"""
URLs específicas para el carrito
"""
from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .views import CartViewSet

# Instancia del ViewSet
cart_viewset = CartViewSet()

# Wrappear los métodos con @api_view para que DRF los reconozca
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def carrito_list(request):
    return cart_viewset.list(request)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def carrito_agregar(request):
    return cart_viewset.agregar(request)

@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def carrito_item_detail(request, item_id):
    """Maneja PUT (actualizar) y DELETE (eliminar) para items"""
    if request.method == 'PUT':
        return cart_viewset.update_item(request, item_id=item_id)
    elif request.method == 'DELETE':
        return cart_viewset.delete_item(request, item_id=item_id)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def carrito_vaciar(request):
    return cart_viewset.vaciar(request)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def carrito_checkout(request):
    return cart_viewset.checkout(request)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def carrito_bulk_update(request):
    return cart_viewset.bulk_update(request)

urlpatterns = [
    # GET /api/carrito/ - Obtener carrito
    path('', carrito_list, name='carrito-list'),
    
    # POST /api/carrito/agregar/ - Agregar producto
    path('agregar/', carrito_agregar, name='carrito-agregar'),
    
    # POST /api/carrito/checkout/ - Reservar stock (FASE 2)
    path('checkout/', carrito_checkout, name='carrito-checkout'),
    
    # PUT/DELETE /api/carrito/items/<item_id>/ - Actualizar o eliminar
    path('items/<int:item_id>/', carrito_item_detail, name='carrito-item-detail'),
    
    # DELETE /api/carrito/vaciar/ - Vaciar carrito
    path('vaciar/', carrito_vaciar, name='carrito-vaciar'),
    
    # POST /api/carrito/bulk-update/ - Actualizar múltiples items
    path('bulk-update/', carrito_bulk_update, name='carrito-bulk-update'),
]
