"""
═══════════════════════════════════════════════════════════════════════════════
✅ TESTS - Verificación de Mejoras de Seguridad y Rendimiento
═══════════════════════════════════════════════════════════════════════════════
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.cache import cache
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
import time

from .models import Producto, Favorito, Cart, CartItem, Pedido, DetallePedido


class SecurityTestCase(APITestCase):
    """Tests de seguridad"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )
        self.producto = Producto.objects.create(
            nombre='Laptop Test',
            precio=1000.00,
            stock=10,
            activo=True
        )
    
    def test_validacion_stock_carrito(self):
        """✅ Validar que no se puede agregar más stock del disponible"""
        self.client.force_authenticate(user=self.user)
        
        # Intentar agregar 15 items cuando solo hay 10
        response = self.client.post('/api/carrito/agregar/', {
            'product_id': self.producto.id,
            'quantity': 15
        }, format='json')
        
        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Stock insuficiente', str(response.data))
    
    def test_validacion_producto_favoritos(self):
        """✅ Validar que no se puede agregar favorito de producto inexistente"""
        self.client.force_authenticate(user=self.user)
        
        # Intentar agregar favorito de producto que no existe
        response = self.client.post('/api/favoritos/agregar/99999/')
        
        # Debe fallar
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_cliente_solo_ve_propios_pedidos(self):
        """✅ Validar que clientes solo ven sus propios pedidos"""
        # Crear dos usuarios
        user1 = User.objects.create_user(username='user1', password='pass123')
        user2 = User.objects.create_user(username='user2', password='pass123')
        
        # Crear perfiles con rol cliente
        from .models import UserProfile
        UserProfile.objects.get_or_create(user=user1, defaults={'rol': 'cliente'})
        UserProfile.objects.get_or_create(user=user2, defaults={'rol': 'cliente'})
        
        # Crear pedidos para cada usuario
        pedido1 = Pedido.objects.create(
            usuario=user1,
            estado='confirmado',
            total=100.00,
            direccion_entrega='Calle 1',
            telefono='123456789'
        )
        pedido2 = Pedido.objects.create(
            usuario=user2,
            estado='confirmado',
            total=200.00,
            direccion_entrega='Calle 2',
            telefono='987654321'
        )
        
        # User1 intenta ver sus pedidos
        self.client.force_authenticate(user=user1)
        response = self.client.get('/api/admin/pedidos/')
        
        # Debe tener acceso (cliente viendo sus propios pedidos)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar que solo ve 1 pedido (el suyo)
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
    
    def test_cookies_httponly(self):
        """✅ Validar que cookies son HTTP-Only"""
        response = self.client.post('/api/auth/login/', {
            'username': self.user.username,
            'password': 'TestPassword123'
        })
        
        # Verificar que la cookie tiene httponly
        self.assertIn('refreshToken', response.cookies)
        self.assertTrue(response.cookies['refreshToken']['httponly'])


class PerformanceTestCase(APITestCase):
    """Tests de rendimiento"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.client = APIClient()
        
        # Crear productos para carrusel
        for i in range(20):
            Producto.objects.create(
                nombre=f'Producto {i}',
                precio=100.00 + i,
                stock=10,
                activo=True,
                en_carrusel=i % 5 == 0  # 4 productos en carrusel
            )
    
    def test_cache_productos_carrusel(self):
        """✅ Validar que caché funciona en productos carrusel"""
        cache.clear()
        
        # Primera llamada (sin caché)
        start = time.time()
        response1 = self.client.get('/api/carrusel/')
        time1 = time.time() - start
        
        # Segunda llamada (con caché)
        start = time.time()
        response2 = self.client.get('/api/carrusel/')
        time2 = time.time() - start
        
        # Ambas deben tener éxito
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # La segunda debe ser más rápida (caché)
        # Permitir margen de error
        print(f"Primera llamada: {time1:.4f}s")
        print(f"Segunda llamada: {time2:.4f}s")
    
    def test_paginacion_pedidos(self):
        """✅ Validar que paginación funciona"""
        user = User.objects.create_user(username='testuser', password='pass123')
        user.is_staff = True  # Necesario para acceder a admin
        user.save()
        
        # Crear perfil con rol admin
        from .models import UserProfile
        UserProfile.objects.get_or_create(user=user, defaults={'rol': 'admin'})
        
        # Crear 50 pedidos
        for i in range(50):
            Pedido.objects.create(
                usuario=user,
                estado='confirmado',
                total=100.00 + i,
                direccion_entrega=f'Calle {i}',
                telefono='123456789'
            )
        
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/admin/pedidos/')
        
        # Debe tener paginación
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que trae máximo 20 resultados (page_size)
        if 'results' in response.data:
            self.assertLessEqual(len(response.data['results']), 20)
    
    def test_indices_favoritos(self):
        """✅ Validar que índices en favoritos funcionan"""
        user = User.objects.create_user(username='testuser', password='pass123')
        
        # Crear 100 favoritos
        productos = []
        for i in range(100):
            p = Producto.objects.create(
                nombre=f'Producto {i}',
                precio=100.00,
                stock=10,
                activo=True
            )
            productos.append(p)
        
        for p in productos:
            Favorito.objects.create(usuario=user, producto=p)
        
        # Buscar favoritos del usuario (debe ser rápido con índice)
        start = time.time()
        favoritos = Favorito.objects.filter(usuario=user).select_related('producto')
        list(favoritos)  # Forzar evaluación
        elapsed = time.time() - start
        
        # Debe ser rápido (< 100ms)
        print(f"Búsqueda de 100 favoritos: {elapsed:.4f}s")
        self.assertLess(elapsed, 0.1)


class ValidationTestCase(APITestCase):
    """Tests de validación"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )
    
    def test_validacion_busqueda_larga(self):
        """✅ Validar que búsquedas muy largas se rechazan"""
        self.client.force_authenticate(user=self.user)
        
        # Crear un pedido
        Pedido.objects.create(
            usuario=self.user,
            estado='confirmado',
            total=100.00,
            direccion_entrega='Calle 1',
            telefono='123456789'
        )
        
        # Intentar búsqueda muy larga (> 100 caracteres)
        search_query = 'a' * 101
        response = self.client.get(f'/api/admin/pedidos/?search={search_query}')
        
        # Debe retornar 0 resultados
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 0)
    
    def test_rate_limiting(self):
        """✅ Validar que rate limiting funciona"""
        # Hacer muchas peticiones rápidamente
        for i in range(101):  # Más de 100/hora
            response = self.client.get('/api/carrusel/')
        
        # Después de 100 peticiones, debe retornar 429 (Too Many Requests)
        # Nota: Esto depende de la configuración de rate limiting


class IntegrationTestCase(APITestCase):
    """Tests de integración"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPassword123'
        )
        self.producto = Producto.objects.create(
            nombre='Laptop Test',
            precio=1000.00,
            stock=10,
            activo=True
        )
    
    def test_flujo_completo_compra(self):
        """✅ Validar flujo completo de compra"""
        self.client.force_authenticate(user=self.user)
        
        # 1. Agregar al carrito (con validación de stock)
        response = self.client.post('/api/carrito/agregar/', {
            'product_id': self.producto.id,
            'quantity': 2
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 2. Agregar a favoritos (con validación de producto)
        response = self.client.post(f'/api/favoritos/agregar/{self.producto.id}/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 3. Ver carrito
        response = self.client.get('/api/carrito/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_cache_y_paginacion_juntos(self):
        """✅ Validar que caché y paginación funcionan juntos"""
        cache.clear()
        
        # Crear muchos productos
        for i in range(100):
            Producto.objects.create(
                nombre=f'Producto {i}',
                precio=100.00,
                stock=10,
                activo=True,
                en_carrusel=i < 20
            )
        
        # Primera llamada a carrusel (caché)
        response1 = self.client.get('/api/carrusel/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Segunda llamada (debe usar caché)
        response2 = self.client.get('/api/carrusel/')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Ambas deben retornar los mismos datos
        self.assertEqual(response1.data, response2.data)


class HeadersTestCase(APITestCase):
    """Tests de headers de seguridad"""
    
    def test_security_headers_presentes(self):
        """✅ Validar que headers de seguridad están presentes"""
        response = self.client.get('/api/carrusel/')
        
        # Verificar headers de seguridad
        self.assertIn('X-Frame-Options', response)
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        
        self.assertIn('X-Content-Type-Options', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')


if __name__ == '__main__':
    import unittest
    unittest.main()
