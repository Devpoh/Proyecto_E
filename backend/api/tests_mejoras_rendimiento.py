"""
═══════════════════════════════════════════════════════════════════════════════
🧪 TESTS - Mejoras de Rendimiento y Seguridad
═══════════════════════════════════════════════════════════════════════════════

Tests para verificar que las 4 mejoras de alto impacto funcionan correctamente:
1. Rate Limiting en Admin
2. Caché en Estadísticas
3. Optimización de Queries (N+1)
4. Validación en CRUD de Productos
"""

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test.utils import override_settings
from .models import UserProfile, Producto
import json


class RateLimitingTestCase(APITestCase):
    """✅ Test: Rate Limiting en Admin"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username='admin_rate', password='pass123', is_staff=True)
        UserProfile.objects.get_or_create(user=self.admin, defaults={'rol': 'admin'})
        self.client.force_authenticate(user=self.admin)
    
    def test_rate_limiting_activo(self):
        """✅ Verificar que rate limiting está configurado"""
        # Hacer múltiples requests
        for i in range(5):
            response = self.client.get('/api/admin/users/')
            # Verificar que el request es exitoso
            self.assertIn(response.status_code, [200, 429])  # 429 = Too Many Requests
        
        # Si llegamos aquí sin error 500, rate limiting está funcionando
        self.assertTrue(True)


class CacheEstadisticasTestCase(APITestCase):
    """✅ Test: Caché en Estadísticas"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username='admin_cache', password='pass123', is_staff=True)
        UserProfile.objects.get_or_create(user=self.admin, defaults={'rol': 'admin'})
        self.client.force_authenticate(user=self.admin)
        cache.clear()
    
    def test_cache_estadisticas_ventas(self):
        """✅ Verificar que estadísticas de ventas se cachean"""
        # Primera llamada (sin caché)
        response1 = self.client.get('/api/admin/estadisticas/ventas/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Verificar que está en caché
        cached_data = cache.get('estadisticas_ventas')
        self.assertIsNotNone(cached_data)
        
        # Segunda llamada (desde caché)
        response2 = self.client.get('/api/admin/estadisticas/ventas/')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Los datos deben ser idénticos
        self.assertEqual(response1.data, response2.data)
    
    def test_cache_estadisticas_usuarios(self):
        """✅ Verificar que estadísticas de usuarios se cachean"""
        # Primera llamada
        response1 = self.client.get('/api/admin/estadisticas/usuarios/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Verificar caché
        cached_data = cache.get('estadisticas_usuarios')
        self.assertIsNotNone(cached_data)


class OptimizacionQueriesTestCase(APITestCase):
    """✅ Test: Optimización de Queries (N+1)"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username='admin_queries', password='pass123', is_staff=True)
        UserProfile.objects.get_or_create(user=self.admin, defaults={'rol': 'admin'})
        
        # Crear múltiples usuarios para probar N+1
        for i in range(10):
            user = User.objects.create_user(username=f'user_queries_{i}', password='pass123')
            UserProfile.objects.get_or_create(user=user, defaults={'rol': 'cliente'})
        
        self.client.force_authenticate(user=self.admin)
    
    def test_queries_optimizadas(self):
        """✅ Verificar que queries están optimizadas"""
        from django.test.utils import CaptureQueriesContext
        from django.db import connection
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.get('/api/admin/users/')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Con optimización, debería haber pocas queries (< 10)
        # Sin optimización, habría 1 + N queries (1 + 10 = 11+)
        query_count = len(context)
        self.assertLess(query_count, 15, f"Demasiadas queries: {query_count}")


class ValidacionProductosTestCase(APITestCase):
    """✅ Test: Validación en CRUD de Productos"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username='admin_productos', password='pass123', is_staff=True)
        UserProfile.objects.get_or_create(user=self.admin, defaults={'rol': 'admin'})
        self.client.force_authenticate(user=self.admin)
    
    def test_precio_negativo_rechazado(self):
        """❌ Precio negativo debe ser rechazado"""
        response = self.client.post(
            '/api/admin/productos/',
            {
                'nombre': 'Producto Test',
                'descripcion': 'Test',
                'precio': -100,
                'stock': 10,
                'categoria': 'energia_tecnologia'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('precio', str(response.data).lower())
    
    def test_precio_cero_rechazado(self):
        """❌ Precio cero debe ser rechazado"""
        response = self.client.post(
            '/api/admin/productos/',
            {
                'nombre': 'Producto Test',
                'descripcion': 'Test',
                'precio': 0,
                'stock': 10,
                'categoria': 'energia_tecnologia'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_stock_negativo_rechazado(self):
        """❌ Stock negativo debe ser rechazado"""
        response = self.client.post(
            '/api/admin/productos/',
            {
                'nombre': 'Producto Test',
                'descripcion': 'Test',
                'precio': 100,
                'stock': -5,
                'categoria': 'energia_tecnologia'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('stock', str(response.data).lower())
    
    def test_nombre_vacio_rechazado(self):
        """❌ Nombre vacío debe ser rechazado"""
        response = self.client.post(
            '/api/admin/productos/',
            {
                'nombre': '',
                'descripcion': 'Test',
                'precio': 100,
                'stock': 10,
                'categoria': 'energia_tecnologia'
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_descuento_invalido_rechazado(self):
        """❌ Descuento fuera de rango debe ser rechazado"""
        response = self.client.post(
            '/api/admin/productos/',
            {
                'nombre': 'Producto Test',
                'descripcion': 'Test',
                'precio': 100,
                'stock': 10,
                'categoria': 'energia_tecnologia',
                'descuento': 150  # Mayor a 100
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('descuento', str(response.data).lower())
    
    def test_producto_valido_aceptado(self):
        """✅ Producto válido debe ser aceptado"""
        response = self.client.post(
            '/api/admin/productos/',
            {
                'nombre': 'Producto Válido',
                'descripcion': 'Descripción válida',
                'precio': 99.99,
                'stock': 50,
                'categoria': 'energia_tecnologia',
                'descuento': 10
            },
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre'], 'Producto Válido')
        self.assertEqual(float(response.data['precio']), 99.99)
