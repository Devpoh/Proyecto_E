"""
🛒 TESTS DEL CARRITO - Flujo completo de sincronización
═══════════════════════════════════════════════════════════════════════════════

Tests para verificar:
✅ Agregar productos al carrito
✅ Actualizar cantidades
✅ Eliminar items
✅ Bulk-update (múltiples cambios en 1 request)
✅ Vaciar carrito
✅ Validación de stock
✅ Checkout con reserva de stock
"""

import json
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from api.models import Producto, Cart, CartItem


@pytest.fixture
def api_client():
    """Cliente API para tests"""
    return APIClient()


@pytest.fixture
def test_user(django_user_model):
    """Crear usuario de prueba"""
    return django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def test_products():
    """Crear productos de prueba con stock"""
    productos = []
    for i in range(1, 4):
        p = Producto.objects.create(
            nombre=f'Producto {i}',
            descripcion=f'Descripción del producto {i}',
            precio=100.00 + (i * 10),
            stock_total=100,
            stock_reservado=0,
            stock_vendido=0,
            activo=True,
            categoria='Electrónica'
        )
        productos.append(p)
    return productos


@pytest.mark.django_db
class TestCartFlow:
    """Suite de tests para el flujo completo del carrito"""

    def test_obtener_carrito_vacio(self, api_client, test_user):
        """✅ Obtener carrito vacío del usuario"""
        api_client.force_authenticate(user=test_user)
        
        response = api_client.get(reverse('carrito-list'))
        
        assert response.status_code == 200
        data = response.json()
        assert data['items'] == []
        assert float(data['total']) == 0.0  # Total es float, no string
        assert data['total_items'] == 0

    def test_agregar_producto_al_carrito(self, api_client, test_user, test_products):
        """✅ Agregar un producto al carrito"""
        api_client.force_authenticate(user=test_user)
        producto = test_products[0]
        
        response = api_client.post(
            reverse('carrito-agregar'),
            data=json.dumps({
                'product_id': producto.id,
                'quantity': 2
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data['items']) == 1
        assert data['items'][0]['quantity'] == 2
        assert data['items'][0]['product']['id'] == producto.id
        assert data['total_items'] == 2

    def test_agregar_producto_sin_stock(self, api_client, test_user, test_products):
        """❌ Intentar agregar más cantidad que stock disponible"""
        api_client.force_authenticate(user=test_user)
        producto = test_products[0]
        
        response = api_client.post(
            reverse('carrito-agregar'),
            data=json.dumps({
                'product_id': producto.id,
                'quantity': 150  # Más que stock_total (100)
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
        assert 'Stock insuficiente' in data['error']

    def test_actualizar_cantidad_item(self, api_client, test_user, test_products):
        """✅ Actualizar cantidad de un item existente"""
        api_client.force_authenticate(user=test_user)
        producto = test_products[0]
        
        # Agregar producto
        response = api_client.post(
            reverse('carrito-agregar'),
            data=json.dumps({
                'product_id': producto.id,
                'quantity': 2
            }),
            content_type='application/json'
        )
        item_id = response.json()['items'][0]['id']
        
        # Actualizar cantidad
        response = api_client.put(
            reverse('carrito-item-detail', kwargs={'item_id': item_id}),
            data=json.dumps({'quantity': 5}),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['items'][0]['quantity'] == 5
        assert data['total_items'] == 5

    def test_eliminar_item_del_carrito(self, api_client, test_user, test_products):
        """✅ Eliminar un item del carrito"""
        api_client.force_authenticate(user=test_user)
        producto = test_products[0]
        
        # Agregar producto
        response = api_client.post(
            reverse('carrito-agregar'),
            data=json.dumps({
                'product_id': producto.id,
                'quantity': 2
            }),
            content_type='application/json'
        )
        item_id = response.json()['items'][0]['id']
        
        # Eliminar item
        response = api_client.delete(
            reverse('carrito-item-detail', kwargs={'item_id': item_id})
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) == 0
        assert data['total_items'] == 0

    def test_bulk_update_carrito(self, api_client, test_user, test_products):
        """✅ Actualizar múltiples items en 1 request (bulk-update)"""
        api_client.force_authenticate(user=test_user)
        
        # Agregar varios productos
        for i, producto in enumerate(test_products[:2], 1):
            api_client.post(
                reverse('carrito-agregar'),
                data=json.dumps({
                    'product_id': producto.id,
                    'quantity': i
                }),
                content_type='application/json'
            )
        
        # Bulk update: cambiar cantidades de múltiples productos
        response = api_client.post(
            reverse('carrito-bulk-update'),
            data=json.dumps({
                'updates': {
                    str(test_products[0].id): 10,
                    str(test_products[1].id): 20
                }
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['cart']['items']) == 2
        # Verificar que las cantidades se actualizaron
        quantities = {item['product']['id']: item['quantity'] for item in data['cart']['items']}
        assert quantities[test_products[0].id] == 10
        assert quantities[test_products[1].id] == 20

    def test_vaciar_carrito(self, api_client, test_user, test_products):
        """✅ Vaciar todos los items del carrito"""
        api_client.force_authenticate(user=test_user)
        
        # Agregar productos
        for producto in test_products[:2]:
            api_client.post(
                reverse('carrito-agregar'),
                data=json.dumps({
                    'product_id': producto.id,
                    'quantity': 1
                }),
                content_type='application/json'
            )
        
        # Vaciar carrito
        response = api_client.delete(reverse('carrito-vaciar'))
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) == 0
        assert data['total_items'] == 0

    def test_carrito_persiste_entre_requests(self, api_client, test_user, test_products):
        """✅ El carrito persiste entre múltiples requests"""
        api_client.force_authenticate(user=test_user)
        producto = test_products[0]
        
        # Agregar producto
        api_client.post(
            reverse('carrito-agregar'),
            data=json.dumps({
                'product_id': producto.id,
                'quantity': 3
            }),
            content_type='application/json'
        )
        
        # Obtener carrito en otro request
        response = api_client.get(reverse('carrito-list'))
        
        assert response.status_code == 200
        data = response.json()
        assert len(data['items']) == 1
        assert data['items'][0]['quantity'] == 3

    def test_checkout_reserva_stock(self, api_client, test_user, test_products):
        """✅ Checkout reserva stock correctamente"""
        api_client.force_authenticate(user=test_user)
        
        # Agregar productos
        for i, producto in enumerate(test_products[:2], 1):
            api_client.post(
                reverse('carrito-agregar'),
                data=json.dumps({
                    'product_id': producto.id,
                    'quantity': i
                }),
                content_type='application/json'
            )
        
        # Hacer checkout
        response = api_client.post(reverse('carrito-checkout'))
        
        # Verificar que la respuesta sea exitosa
        if response.status_code != 200:
            print(f"Checkout error: {response.status_code}")
            print(f"Response: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert 'reservas' in data
        assert len(data['reservas']) == 2
        assert data['ttl_minutos'] == 15

    def test_checkout_sin_stock_suficiente(self, api_client, test_user, test_products):
        """❌ Checkout falla si no hay stock suficiente"""
        api_client.force_authenticate(user=test_user)
        producto = test_products[0]
        
        # Agregar más cantidad que stock disponible
        api_client.post(
            reverse('carrito-agregar'),
            data=json.dumps({
                'product_id': producto.id,
                'quantity': 50
            }),
            content_type='application/json'
        )
        
        # Cambiar stock a 30 (menos que lo que agregamos)
        producto.stock_total = 30
        producto.save()
        
        # Intentar checkout
        response = api_client.post(reverse('carrito-checkout'))
        
        assert response.status_code == 409
        data = response.json()
        assert 'error' in data
        assert 'Stock insuficiente' in data['error']

    def test_no_autenticado_no_puede_acceder(self, api_client):
        """❌ Usuario no autenticado no puede acceder al carrito"""
        response = api_client.get(reverse('carrito-list'))
        
        assert response.status_code == 401

    def test_incrementar_cantidad_existente(self, api_client, test_user, test_products):
        """✅ Agregar el mismo producto incrementa cantidad"""
        api_client.force_authenticate(user=test_user)
        producto = test_products[0]
        
        # Agregar producto primera vez
        api_client.post(
            reverse('carrito-agregar'),
            data=json.dumps({
                'product_id': producto.id,
                'quantity': 2
            }),
            content_type='application/json'
        )
        
        # Agregar el mismo producto segunda vez
        response = api_client.post(
            reverse('carrito-agregar'),
            data=json.dumps({
                'product_id': producto.id,
                'quantity': 3
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.json()
        assert len(data['items']) == 1
        assert data['items'][0]['quantity'] == 5  # 2 + 3
