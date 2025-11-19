# 🚀 GUÍA PASO A PASO - IMPLEMENTACIÓN BACKEND

**Fecha:** 7 de Noviembre, 2025  
**Objetivo:** Implementar carrito por usuario de manera profesional

---

## ✅ PASO 1: CREAR LA APP

```bash
cd backend
python manage.py startapp carrito
```

---

## ✅ PASO 2: CREAR MODELOS

**Archivo:** `apps/carrito/models.py`

```python
from django.db import models
from django.contrib.auth.models import User
from apps.productos.models import Producto

class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
    
    def __str__(self):
        return f'Carrito de {self.user.email}'
    
    def get_total(self):
        return sum(item.price_at_addition * item.quantity for item in self.items.all())
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Producto, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        unique_together = ('cart', 'product')
    
    def __str__(self):
        return f'{self.product.nombre} x {self.quantity}'
    
    def get_subtotal(self):
        return self.price_at_addition * self.quantity
```

---

## ✅ PASO 3: CREAR SERIALIZERS

**Archivo:** `apps/carrito/serializers.py`

```python
from rest_framework import serializers
from apps.carrito.models import Cart, CartItem
from apps.productos.models import Producto

class ProductoSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'imagen_url', 'categoria']

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductoSimpleSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price_at_addition', 'subtotal', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'price_at_addition']
    
    def get_subtotal(self, obj):
        return float(obj.get_subtotal())

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total', 'total_items', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total(self, obj):
        return float(obj.get_total())
    
    def get_total_items(self, obj):
        return obj.get_total_items()
```

---

## ✅ PASO 4: CREAR VIEWS

**Archivo:** `apps/carrito/views.py`

```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound

from apps.carrito.models import Cart, CartItem
from apps.carrito.serializers import CartSerializer, CartItemSerializer
from apps.productos.models import Producto

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    
    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    @action(detail=False, methods=['get'])
    def list(self, request, *args, **kwargs):
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def agregar(self, request):
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        if not product_id:
            raise ValidationError({'product_id': 'Este campo es requerido'})
        
        if quantity < 1:
            raise ValidationError({'quantity': 'La cantidad debe ser mayor a 0'})
        
        try:
            product = Producto.objects.get(id=product_id)
        except Producto.DoesNotExist:
            raise NotFound('Producto no encontrado')
        
        if product.stock < quantity:
            raise ValidationError({'quantity': f'Stock insuficiente. Disponible: {product.stock}'})
        
        cart = self.get_object()
        
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity, 'price_at_addition': product.precio}
        )
        
        if not created:
            new_quantity = item.quantity + quantity
            if product.stock < new_quantity:
                raise ValidationError({'quantity': f'Stock insuficiente. Disponible: {product.stock}'})
            item.quantity = new_quantity
            item.save()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['put'], url_path='items/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        quantity = request.data.get('quantity')
        
        if quantity is None:
            raise ValidationError({'quantity': 'Este campo es requerido'})
        
        if quantity < 1:
            raise ValidationError({'quantity': 'La cantidad debe ser mayor a 0'})
        
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            raise NotFound('Item no encontrado')
        
        if item.product.stock < quantity:
            raise ValidationError({'quantity': f'Stock insuficiente. Disponible: {item.product.stock}'})
        
        item.quantity = quantity
        item.save()
        
        cart = item.cart
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'], url_path='items/(?P<item_id>[^/.]+)')
    def delete_item(self, request, item_id=None):
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            raise NotFound('Item no encontrado')
        
        cart = item.cart
        item.delete()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'])
    def vaciar(self, request):
        cart = self.get_object()
        cart.items.all().delete()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
```

---

## ✅ PASO 5: CREAR URLS

**Archivo:** `apps/carrito/urls.py`

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.carrito.views import CartViewSet

router = DefaultRouter()
router.register(r'carrito', CartViewSet, basename='carrito')

urlpatterns = [
    path('', include(router.urls)),
]
```

**Archivo:** `config/urls.py` (Agregar a urlpatterns)

```python
urlpatterns = [
    # ... otros urls ...
    path('api/', include('apps.carrito.urls')),
]
```

---

## ✅ PASO 6: REGISTRAR EN INSTALLED_APPS

**Archivo:** `config/settings.py`

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    'rest_framework',
    'corsheaders',
    
    'apps.usuarios',
    'apps.productos',
    'apps.carrito',  # ← AGREGAR AQUÍ
]
```

---

## ✅ PASO 7: CREAR MIGRACIONES

```bash
python manage.py makemigrations carrito
python manage.py migrate carrito
```

---

## ✅ PASO 8: CREAR ADMIN (OPCIONAL)

**Archivo:** `apps/carrito/admin.py`

```python
from django.contrib import admin
from apps.carrito.models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_total_items', 'get_total', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'
    
    def get_total(self, obj):
        return f'${obj.get_total():.2f}'
    get_total.short_description = 'Total'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'price_at_addition', 'get_subtotal')
    list_filter = ('created_at', 'product__categoria')
    search_fields = ('product__nombre', 'cart__user__email')
    readonly_fields = ('created_at', 'updated_at', 'price_at_addition')
    
    def get_subtotal(self, obj):
        return f'${obj.get_subtotal():.2f}'
    get_subtotal.short_description = 'Subtotal'
```

---

## ✅ PASO 9: CREAR TESTS

**Archivo:** `apps/carrito/tests.py`

```python
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from apps.carrito.models import Cart, CartItem
from apps.productos.models import Producto

class CartAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.product = Producto.objects.create(
            nombre='Producto Test',
            descripcion='Descripción test',
            precio=100.00,
            stock=10,
            categoria='Test'
        )
    
    def test_get_cart_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/carrito/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_add_to_cart(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/carrito/agregar/', {
            'product_id': self.product.id,
            'quantity': 2
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['total_items'], 2)
    
    def test_add_to_cart_insufficient_stock(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/carrito/agregar/', {
            'product_id': self.product.id,
            'quantity': 20
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
```

---

## ✅ PASO 10: EJECUTAR TESTS

```bash
python manage.py test apps.carrito
```

---

## ✅ PASO 11: EJECUTAR SERVIDOR

```bash
python manage.py runserver
```

---

## 🧪 PROBAR ENDPOINTS CON CURL

### 1. Obtener Token (si usas JWT)
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

### 2. Obtener Carrito
```bash
curl -X GET http://localhost:8000/api/carrito/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Agregar Producto
```bash
curl -X POST http://localhost:8000/api/carrito/agregar/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":2}'
```

### 4. Actualizar Cantidad
```bash
curl -X PUT http://localhost:8000/api/carrito/items/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity":5}'
```

### 5. Eliminar Item
```bash
curl -X DELETE http://localhost:8000/api/carrito/items/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 6. Vaciar Carrito
```bash
curl -X DELETE http://localhost:8000/api/carrito/vaciar/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 ENDPOINTS FINALES

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/carrito/` | Obtener carrito |
| POST | `/api/carrito/agregar/` | Agregar producto |
| PUT | `/api/carrito/items/{id}/` | Actualizar cantidad |
| DELETE | `/api/carrito/items/{id}/` | Eliminar item |
| DELETE | `/api/carrito/vaciar/` | Vaciar carrito |

---

## ✨ ¡LISTO!

Backend completamente implementado y funcional.

Todos los endpoints están listos para conectar con el frontend.

¡Vamos a sincronizar! 🚀
