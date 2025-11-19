"""
═══════════════════════════════════════════════════════════════════════════════
🧪 TESTS - Throttling Verification
═══════════════════════════════════════════════════════════════════════════════

Tests para verificar que los throttles funcionan correctamente.
Simula múltiples requests rápidos y verifica que se devuelve 429 al superar límite.

Ejecutar:
    pytest tests/test_throttles.py -v
    pytest tests/test_throttles.py::test_cart_write_throttle -v
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestCartWriteThrottle:
    """Tests para CartWriteThrottle (100/hora)"""
    
    def setup_method(self):
        """Preparar cliente y usuario para cada test"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='cart_user',
            email='cart@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_cart_write_throttle_allows_requests_under_limit(self):
        """✅ Verificar que requests bajo el límite son permitidos"""
        url = reverse('carrito-bulk-update')
        payload = {'items': {'1': 1}}
        
        # Enviar 50 requests (bajo el límite de 100)
        for i in range(50):
            response = self.client.post(url, payload, format='json')
            assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST], \
                f"Request {i} devolvió {response.status_code}, esperaba 200/201/400"
    
    def test_cart_write_throttle_denies_requests_over_limit(self):
        """✅ Verificar que requests sobre el límite son rechazados (429)"""
        url = reverse('carrito-bulk-update')
        payload = {'items': {'1': 1}}
        
        status_codes = {}
        
        # Enviar 110 requests (sobre el límite de 100)
        for i in range(110):
            response = self.client.post(url, payload, format='json')
            code = response.status_code
            status_codes[code] = status_codes.get(code, 0) + 1
        
        # Verificar que hay al menos un 429
        assert status_codes.get(status.HTTP_429_TOO_MANY_REQUESTS, 0) > 0, \
            f"No se devolvió 429. Status codes: {status_codes}"
        
        # Verificar que la mayoría de requests iniciales fueron permitidos
        assert status_codes.get(status.HTTP_200_OK, 0) + \
               status_codes.get(status.HTTP_201_CREATED, 0) + \
               status_codes.get(status.HTTP_400_BAD_REQUEST, 0) >= 100, \
            f"Menos de 100 requests fueron permitidos. Status codes: {status_codes}"


@pytest.mark.django_db
class TestCheckoutThrottle:
    """Tests para CheckoutThrottle (50/hora)"""
    
    def setup_method(self):
        """Preparar cliente y usuario para cada test"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='checkout_user',
            email='checkout@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_checkout_throttle_allows_requests_under_limit(self):
        """✅ Verificar que requests bajo el límite son permitidos"""
        url = reverse('carrito-checkout')
        payload = {}
        
        # Enviar 25 requests (bajo el límite de 50)
        for i in range(25):
            response = self.client.post(url, payload, format='json')
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_201_CREATED,
                status.HTTP_400_BAD_REQUEST,
                status.HTTP_409_CONFLICT
            ], f"Request {i} devolvió {response.status_code}"
    
    def test_checkout_throttle_denies_requests_over_limit(self):
        """✅ Verificar que requests sobre el límite son rechazados (429)"""
        url = reverse('carrito-checkout')
        payload = {}
        
        status_codes = {}
        
        # Enviar 60 requests (sobre el límite de 50)
        for i in range(60):
            response = self.client.post(url, payload, format='json')
            code = response.status_code
            status_codes[code] = status_codes.get(code, 0) + 1
        
        # Verificar que hay al menos un 429
        assert status_codes.get(status.HTTP_429_TOO_MANY_REQUESTS, 0) > 0, \
            f"No se devolvió 429. Status codes: {status_codes}"


@pytest.mark.django_db
class TestAuthThrottle:
    """Tests para AuthThrottle (10/hora)"""
    
    def setup_method(self):
        """Preparar cliente para cada test"""
        self.client = APIClient()
    
    def test_auth_throttle_allows_requests_under_limit(self):
        """✅ Verificar que requests bajo el límite son permitidos"""
        url = reverse('login')  # Ajusta al nombre correcto de tu ruta
        payload = {'username': 'test', 'password': 'wrong'}
        
        # Enviar 5 requests (bajo el límite de 10)
        for i in range(5):
            response = self.client.post(url, payload, format='json')
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_400_BAD_REQUEST
            ], f"Request {i} devolvió {response.status_code}"
    
    def test_auth_throttle_denies_requests_over_limit(self):
        """✅ Verificar que requests sobre el límite son rechazados (429)"""
        url = reverse('login')  # Ajusta al nombre correcto de tu ruta
        payload = {'username': 'test', 'password': 'wrong'}
        
        status_codes = {}
        
        # Enviar 15 requests (sobre el límite de 10)
        for i in range(15):
            response = self.client.post(url, payload, format='json')
            code = response.status_code
            status_codes[code] = status_codes.get(code, 0) + 1
        
        # Verificar que hay al menos un 429
        assert status_codes.get(status.HTTP_429_TOO_MANY_REQUESTS, 0) > 0, \
            f"No se devolvió 429. Status codes: {status_codes}"


@pytest.mark.django_db
class TestAdminThrottle:
    """Tests para AdminThrottle (500/hora)"""
    
    def setup_method(self):
        """Preparar cliente y usuario admin para cada test"""
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin_user',
            email='admin@test.com',
            password='adminpass123'
        )
        self.client.force_authenticate(user=self.admin_user)
    
    def test_admin_throttle_allows_requests_under_limit(self):
        """✅ Verificar que requests bajo el límite son permitidos"""
        url = reverse('producto-list')  # Ajusta al nombre correcto
        
        # Enviar 100 requests (bajo el límite de 500)
        for i in range(100):
            response = self.client.get(url)
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_403_FORBIDDEN
            ], f"Request {i} devolvió {response.status_code}"
    
    def test_admin_throttle_denies_requests_over_limit(self):
        """✅ Verificar que requests sobre el límite son rechazados (429)"""
        url = reverse('producto-list')  # Ajusta al nombre correcto
        
        status_codes = {}
        
        # Enviar 510 requests (sobre el límite de 500)
        for i in range(510):
            response = self.client.get(url)
            code = response.status_code
            status_codes[code] = status_codes.get(code, 0) + 1
        
        # Verificar que hay al menos un 429
        assert status_codes.get(status.HTTP_429_TOO_MANY_REQUESTS, 0) > 0, \
            f"No se devolvió 429. Status codes: {status_codes}"


@pytest.mark.django_db
class TestPublicEndpointsNoThrottle:
    """Tests para verificar que endpoints públicos NO tienen throttle"""
    
    def setup_method(self):
        """Preparar cliente para cada test"""
        self.client = APIClient()
    
    def test_productos_endpoint_no_throttle(self):
        """✅ Verificar que /api/productos/ NO tiene throttle"""
        url = reverse('producto-list')
        
        # Enviar 200 requests rápidos (sin throttle, todos deberían pasar)
        for i in range(200):
            response = self.client.get(url)
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_403_FORBIDDEN
            ], f"Request {i} devolvió {response.status_code}"
    
    def test_carrusel_endpoint_no_throttle(self):
        """✅ Verificar que /api/carrusel/ NO tiene throttle"""
        url = reverse('productos-carrusel')  # Ajusta al nombre correcto
        
        # Enviar 200 requests rápidos (sin throttle, todos deberían pasar)
        for i in range(200):
            response = self.client.get(url)
            assert response.status_code == status.HTTP_200_OK, \
                f"Request {i} devolvió {response.status_code}"
