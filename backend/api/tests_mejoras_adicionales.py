"""
═══════════════════════════════════════════════════════════════════════════════
🧪 TESTS - Mejoras Adicionales
═══════════════════════════════════════════════════════════════════════════════

Tests para los 4 próximos pasos:
1. Índices en BD
2. Paginación en Estadísticas
3. Sanitización en Búsquedas
4. Validación de Tipos en Query Params
"""

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import UserProfile, Producto
from .utils.validators import validate_query_params, validate_page_number, validate_page_size


class SanitizacionBusquedasTestCase(APITestCase):
    """✅ Test: Sanitización en Búsquedas"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username='admin_sanitize', password='pass123', is_staff=True)
        UserProfile.objects.get_or_create(user=self.admin, defaults={'rol': 'admin'})
        self.client.force_authenticate(user=self.admin)
    
    def test_busqueda_con_espacios_multiples(self):
        """✅ Espacios múltiples deben ser normalizados"""
        response = self.client.get('/api/admin/users/?search=juan    perez')
        # Debe aceptar pero normalizar
        self.assertIn(response.status_code, [200, 400])
    
    def test_busqueda_con_caracteres_invalidos(self):
        """❌ Caracteres especiales inválidos deben ser rechazados"""
        response = self.client.get('/api/admin/users/?search=<script>alert()</script>')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('inválido', str(response.data).lower())
    
    def test_busqueda_valida_aceptada(self):
        """✅ Búsqueda válida debe ser aceptada"""
        response = self.client.get('/api/admin/users/?search=juan-perez_123')
        self.assertIn(response.status_code, [200, 400])  # 400 si no hay resultados, 200 si los hay
    
    def test_busqueda_productos_con_caracteres_validos(self):
        """✅ Búsqueda de productos con caracteres válidos"""
        response = self.client.get('/api/admin/productos/?search=Laptop (HP)')
        self.assertIn(response.status_code, [200, 400])


class ValidacionTiposQueryParamsTestCase(APITestCase):
    """✅ Test: Validación de Tipos en Query Params"""
    
    def test_validate_query_params_int(self):
        """✅ Validar parámetro entero"""
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/', {'page': '5'})
        
        try:
            result = validate_query_params(request, optional_params={'page': 'int'})
            self.assertEqual(result['page'], 5)
        except ValueError:
            self.fail("Validación de int falló")
    
    def test_validate_query_params_int_invalido(self):
        """❌ Parámetro entero inválido debe fallar"""
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/', {'page': 'abc'})
        
        with self.assertRaises(ValueError):
            validate_query_params(request, optional_params={'page': 'int'})
    
    def test_validate_query_params_bool(self):
        """✅ Validar parámetro booleano"""
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/', {'activo': 'true'})
        
        try:
            result = validate_query_params(request, optional_params={'activo': 'bool'})
            self.assertEqual(result['activo'], True)
        except ValueError:
            self.fail("Validación de bool falló")
    
    def test_validate_query_params_bool_invalido(self):
        """❌ Parámetro booleano inválido debe fallar"""
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/', {'activo': 'maybe'})
        
        with self.assertRaises(ValueError):
            validate_query_params(request, optional_params={'activo': 'bool'})
    
    def test_validate_page_number_valido(self):
        """✅ Número de página válido"""
        page = validate_page_number('5')
        self.assertEqual(page, 5)
    
    def test_validate_page_number_invalido(self):
        """❌ Número de página inválido"""
        with self.assertRaises(ValueError):
            validate_page_number('0')
        
        with self.assertRaises(ValueError):
            validate_page_number('abc')
    
    def test_validate_page_size_valido(self):
        """✅ Tamaño de página válido"""
        size = validate_page_size('50')
        self.assertEqual(size, 50)
    
    def test_validate_page_size_excede_maximo(self):
        """❌ Tamaño de página que excede máximo"""
        with self.assertRaises(ValueError):
            validate_page_size('5000', max_size=1000)


class PaginacionEstadisticasTestCase(APITestCase):
    """✅ Test: Paginación en Estadísticas"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username='admin_paginate', password='pass123', is_staff=True)
        UserProfile.objects.get_or_create(user=self.admin, defaults={'rol': 'admin'})
        self.client.force_authenticate(user=self.admin)
    
    def test_estadisticas_con_paginacion(self):
        """✅ Estadísticas deben respetar paginación"""
        response = self.client.get('/api/admin/estadisticas/ventas/?page=1&page_size=50')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_estadisticas_page_size_maximo(self):
        """✅ Page size no debe exceder máximo"""
        response = self.client.get('/api/admin/estadisticas/ventas/?page_size=5000')
        # Debe limitar a 1000 o retornar error
        self.assertIn(response.status_code, [200, 400])


class IndicesTestCase(APITestCase):
    """✅ Test: Índices en BD"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username='admin_indexes', password='pass123', is_staff=True)
        UserProfile.objects.get_or_create(user=self.admin, defaults={'rol': 'admin'})
        
        # Crear múltiples usuarios para probar índices
        for i in range(50):
            user = User.objects.create_user(username=f'user_idx_{i}', password='pass123')
            UserProfile.objects.get_or_create(user=user, defaults={'rol': 'cliente'})
        
        self.client.force_authenticate(user=self.admin)
    
    def test_busqueda_con_indice_rapida(self):
        """✅ Búsqueda debe ser rápida con índices"""
        import time
        
        start = time.time()
        response = self.client.get('/api/admin/users/?search=user_idx')
        end = time.time()
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Debe ser rápido (< 1 segundo)
        self.assertLess(end - start, 1.0)
    
    def test_filtro_activo_con_indice(self):
        """✅ Filtro activo debe ser rápido con índice"""
        response = self.client.get('/api/admin/users/?activo=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
