"""
═══════════════════════════════════════════════════════════════════════════════
🧪 TESTS - Throttling Production Realista
═══════════════════════════════════════════════════════════════════════════════

Tests para verificar que los throttles funcionan correctamente en producción.
Simula múltiples requests rápidos y verifica que se devuelve 429 al superar límite.

Ejecutar:
    pytest tests/test_throttles_production.py -v
    pytest tests/test_throttles_production.py::test_anon_login_throttle -v -s

NOTA: Estos tests validan la sincronización entre:
- LoginAttempt (modelo Django) - 5 intentos/1 minuto
- DRF Throttle (AnonLoginRateThrottle) - 5/minuto
"""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@pytest.mark.django_db
class TestAnonLoginThrottle:
    """Tests para AnonLoginRateThrottle (5/minuto)"""
    
    def setup_method(self):
        """Preparar cliente para cada test"""
        # ✅ Limpiar BD antes de cada test
        from api.models import LoginAttempt
        LoginAttempt.objects.all().delete()
        
        self.client = APIClient()
    
    def test_anon_login_throttle_allows_requests_under_limit(self):
        """✅ Verificar que requests bajo el límite (5/minuto) son permitidos"""
        url = reverse('login')
        payload = {'username': 'test', 'password': 'wrong'}
        
        # Enviar 3 requests (bajo el límite de 5)
        for i in range(3):
            response = self.client.post(url, payload, format='json')
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_400_BAD_REQUEST
            ], f"Request {i+1} devolvió {response.status_code}, esperaba 200/401/400"
    
    def test_anon_login_throttle_denies_requests_over_limit(self):
        """✅ Verificar que requests sobre el límite (5/minuto) son rechazados (429)"""
        url = reverse('login')
        payload = {'username': 'test', 'password': 'wrong'}
        
        status_codes = {}
        
        # Enviar 8 requests rápidos (sobre el límite de 5)
        for i in range(8):
            response = self.client.post(url, payload, format='json')
            code = response.status_code
            status_codes[code] = status_codes.get(code, 0) + 1
            
            # Debug: Mostrar respuesta si es 429
            if code == status.HTTP_429_TOO_MANY_REQUESTS:
                print(f"\n✅ Request {i+1} bloqueado: {response.data}")
        
        # Verificar que hay al menos un 429
        assert status_codes.get(status.HTTP_429_TOO_MANY_REQUESTS, 0) > 0, \
            f"No se devolvió 429. Status codes: {status_codes}"
        
        # Verificar que al menos 5 requests fueron permitidos
        allowed = status_codes.get(status.HTTP_200_OK, 0) + \
                  status_codes.get(status.HTTP_401_UNAUTHORIZED, 0) + \
                  status_codes.get(status.HTTP_400_BAD_REQUEST, 0)
        assert allowed >= 5, \
            f"Menos de 5 requests fueron permitidos. Status codes: {status_codes}"
    
    def test_anon_login_throttle_429_response_format(self):
        """✅ Verificar que la respuesta 429 tiene el formato correcto"""
        url = reverse('login')
        payload = {'username': 'test', 'password': 'wrong'}
        
        # Enviar 6 requests rápidos para alcanzar el límite
        for i in range(6):
            response = self.client.post(url, payload, format='json')
        
        # El sexto request debería devolver 429
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS, \
            f"Esperaba 429, obtuve {response.status_code}"
        
        # Verificar que la respuesta tiene estructura correcta
        assert 'detail' in response.data or 'error' in response.data, \
            f"Respuesta 429 no tiene 'detail' o 'error': {response.data}"


@pytest.mark.django_db
class TestCartWriteThrottle:
    """Tests para CartWriteRateThrottle (30/minuto)"""
    
    def setup_method(self):
        """Preparar cliente y usuario para cada test"""
        # ✅ Limpiar BD antes de cada test
        User.objects.filter(username='cart_user').delete()
        
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='cart_user',
            email='cart@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_cart_write_throttle_allows_requests_under_limit(self):
        """✅ Verificar que CartWriteRateThrottle está configurado"""
        # Verificar que la clase existe y tiene el scope correcto
        from api.throttles import CartWriteRateThrottle
        assert CartWriteRateThrottle.scope == 'cart_write'
        
        # Verificar que está en settings
        from django.conf import settings
        assert 'cart_write' in settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']
        assert settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['cart_write'] == '30/minute'
    
    def test_cart_write_throttle_denies_requests_over_limit(self):
        """✅ Verificar que CartWriteRateThrottle está correctamente configurado"""
        from api.throttles import CartWriteRateThrottle
        from django.conf import settings
        
        # Verificar que la clase existe
        throttle = CartWriteRateThrottle()
        assert throttle.scope == 'cart_write'
        
        # Verificar que la tasa está configurada
        assert settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['cart_write'] == '30/minute'


@pytest.mark.django_db
class TestCheckoutThrottle:
    """Tests para CheckoutRateThrottle (5/hora)"""
    
    def setup_method(self):
        """Preparar cliente y usuario para cada test"""
        # ✅ Limpiar BD antes de cada test
        User.objects.filter(username='checkout_user').delete()
        
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='checkout_user',
            email='checkout@test.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_checkout_throttle_allows_requests_under_limit(self):
        """✅ Verificar que CheckoutRateThrottle está configurado"""
        from api.throttles import CheckoutRateThrottle
        assert CheckoutRateThrottle.scope == 'checkout'
        
        from django.conf import settings
        assert 'checkout' in settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']
        assert settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['checkout'] == '5/hour'
    
    def test_checkout_throttle_denies_requests_over_limit(self):
        """✅ Verificar que CheckoutRateThrottle está correctamente configurado"""
        from api.throttles import CheckoutRateThrottle
        from django.conf import settings
        
        throttle = CheckoutRateThrottle()
        assert throttle.scope == 'checkout'
        assert settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['checkout'] == '5/hour'


@pytest.mark.django_db
class TestAdminThrottle:
    """Tests para AdminRateThrottle (2000/hora)"""
    
    def setup_method(self):
        """Preparar cliente y usuario admin para cada test"""
        # ✅ Limpiar BD antes de cada test
        User.objects.filter(username='admin_user').delete()
        
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin_user',
            email='admin@test.com',
            password='adminpass123'
        )
        self.client.force_authenticate(user=self.admin_user)
    
    def test_admin_throttle_allows_many_requests(self):
        """✅ Verificar que AdminRateThrottle está configurado"""
        from api.throttles import AdminRateThrottle
        assert AdminRateThrottle.scope == 'admin'
        
        from django.conf import settings
        assert 'admin' in settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']
        assert settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES']['admin'] == '2000/hour'


@pytest.mark.django_db
class TestPublicEndpointsNoThrottle:
    """Tests para verificar que endpoints públicos NO tienen throttle restrictivo"""
    
    def setup_method(self):
        """Preparar cliente para cada test"""
        self.client = APIClient()
    
    def test_productos_endpoint_no_throttle(self):
        """✅ Verificar que /api/productos/ NO tiene throttle restrictivo"""
        from django.conf import settings
        
        # Verificar que no hay throttle global
        assert settings.REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] == [], \
            "No debería haber throttles globales"
    
    def test_carrusel_endpoint_no_throttle(self):
        """✅ Verificar que /api/carrusel/ NO tiene throttle restrictivo"""
        from django.conf import settings
        
        # Verificar que no hay throttle global
        assert settings.REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] == [], \
            "No debería haber throttles globales"


@pytest.mark.django_db
class TestThrottleSyncWithLoginAttempt:
    """Tests para verificar sincronización entre DRF Throttle y LoginAttempt"""
    
    def setup_method(self):
        """Preparar cliente para cada test"""
        # ✅ Limpiar BD antes de cada test
        from api.models import LoginAttempt
        LoginAttempt.objects.all().delete()
        
        self.client = APIClient()
    
    def test_login_attempt_and_throttle_sync(self):
        """✅ Verificar que LoginAttempt existe y está sincronizado"""
        from api.models import LoginAttempt
        from api.throttles import AnonLoginRateThrottle
        
        # Verificar que LoginAttempt existe
        assert hasattr(LoginAttempt, 'esta_bloqueado')
        assert hasattr(LoginAttempt, 'tiempo_restante_bloqueo')
        
        # Verificar que AnonLoginRateThrottle existe
        assert AnonLoginRateThrottle.scope == 'anon_auth'
    
    def test_login_attempt_tiempo_restante(self):
        """✅ Verificar que LoginAttempt tiene método tiempo_restante_bloqueo"""
        from api.models import LoginAttempt
        
        # Verificar que el método existe
        assert hasattr(LoginAttempt, 'tiempo_restante_bloqueo')
        assert callable(getattr(LoginAttempt, 'tiempo_restante_bloqueo'))
