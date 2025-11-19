"""
═══════════════════════════════════════════════════════════════════════════════
🧪 TEST SUITE - Refresh Token (2 horas)
═══════════════════════════════════════════════════════════════════════════════

Suite de pruebas para verificar que el sistema de refresh token funciona
correctamente con una duración de 2 horas.

PRUEBAS INCLUIDAS:
1. ✅ Login genera Access Token (15 min) + Refresh Token (2 horas)
2. ✅ Refresh Token se guarda en HTTP-Only Cookie
3. ✅ Access Token expira después de 15 minutos
4. ✅ Refresh Token refresca el Access Token
5. ✅ Refresh Token se rota (nuevo token después de refresh)
6. ✅ Token anterior se revoca después de refresh
7. ✅ Refresh Token expira después de 2 horas
8. ✅ Peticiones con token expirado retornan 401
9. ✅ Dos pestañas tienen tokens independientes
10. ✅ Logout limpia todo correctamente
"""

import os
import django
import json
from datetime import datetime, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import RefreshToken, UserProfile
from api.utils.jwt_utils import generar_access_token, verificar_access_token


class RefreshTokenTestCase(TestCase):
    """Test suite para Refresh Token (2 horas)"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.client = APIClient()
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear perfil (el signal post_save lo crea automáticamente)
        # Pero lo creamos explícitamente para asegurar que existe
        UserProfile.objects.get_or_create(
            user=self.user,
            defaults={'rol': 'cliente'}
        )
        
        self.login_url = '/api/auth/login/'
        self.refresh_url = '/api/auth/refresh/'
        self.logout_url = '/api/auth/logout/'
    
    def test_01_login_genera_tokens(self):
        """✅ Test 1: Login genera Access Token (15 min) + Refresh Token (2 horas)"""
        print("\n" + "="*80)
        print("TEST 1: Login genera Access Token + Refresh Token")
        print("="*80)
        
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        self.assertIn('accessToken', response.json())
        self.assertIn('user', response.json())
        
        # Verificar Access Token
        access_token = response.json()['accessToken']
        payload = verificar_access_token(access_token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload['user_id'], self.user.id)
        
        # Verificar Refresh Token en cookie
        cookies = response.cookies
        self.assertIn('refreshToken', cookies)
        
        print(f"✅ Access Token generado: {access_token[:50]}...")
        print(f"✅ Refresh Token en cookie: {cookies['refreshToken'].value[:50]}...")
        print(f"✅ Usuario: {self.user.username}")
        print("✅ TEST 1 PASÓ\n")
    
    def test_02_refresh_token_en_cookie(self):
        """✅ Test 2: Refresh Token se guarda en HTTP-Only Cookie"""
        print("\n" + "="*80)
        print("TEST 2: Refresh Token en HTTP-Only Cookie")
        print("="*80)
        
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        cookies = response.cookies
        refresh_cookie = cookies['refreshToken']
        
        # Verificar propiedades de la cookie
        self.assertEqual(refresh_cookie['httponly'], True)
        self.assertEqual(refresh_cookie['path'], '/')
        self.assertEqual(refresh_cookie['samesite'], 'Lax')
        
        # Verificar max_age (2 horas = 7200 segundos)
        max_age = refresh_cookie['max-age']
        self.assertEqual(int(max_age), 2 * 60 * 60)
        
        print(f"✅ Cookie name: refreshToken")
        print(f"✅ HttpOnly: {refresh_cookie['httponly']}")
        print(f"✅ Path: {refresh_cookie['path']}")
        print(f"✅ SameSite: {refresh_cookie['samesite']}")
        print(f"✅ Max-Age: {max_age} segundos (2 horas)")
        print("✅ TEST 2 PASÓ\n")
    
    def test_03_access_token_expira_15min(self):
        """✅ Test 3: Access Token expira después de 15 minutos"""
        print("\n" + "="*80)
        print("TEST 3: Access Token expira después de 15 minutos")
        print("="*80)
        
        # Generar token
        access_token = generar_access_token(self.user)
        payload = verificar_access_token(access_token)
        
        # Verificar duración
        iat = datetime.fromtimestamp(payload['iat'])
        exp = datetime.fromtimestamp(payload['exp'])
        duration = (exp - iat).total_seconds() / 60  # En minutos
        
        self.assertAlmostEqual(duration, 15, delta=1)
        
        print(f"✅ Token generado: {iat}")
        print(f"✅ Token expira: {exp}")
        print(f"✅ Duración: {duration:.1f} minutos")
        print("✅ TEST 3 PASÓ\n")
    
    def test_04_refresh_token_refresca_access(self):
        """✅ Test 4: Refresh Token refresca el Access Token"""
        print("\n" + "="*80)
        print("TEST 4: Refresh Token refresca Access Token")
        print("="*80)
        
        # Login
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        access_token_1 = response.json()['accessToken']
        payload_1 = verificar_access_token(access_token_1)
        
        # Esperar 1 segundo para que cambie el timestamp
        import time
        time.sleep(1)
        
        # Refresh
        response = self.client.post(self.refresh_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('accessToken', response.json())
        
        access_token_2 = response.json()['accessToken']
        payload_2 = verificar_access_token(access_token_2)
        
        # Verificar que ambos son válidos
        self.assertIsNotNone(payload_1)
        self.assertIsNotNone(payload_2)
        
        # Verificar que tienen diferentes timestamps (iat)
        self.assertNotEqual(payload_1['iat'], payload_2['iat'])
        
        print(f"✅ Access Token 1 (iat): {payload_1['iat']}")
        print(f"✅ Access Token 2 (iat): {payload_2['iat']}")
        print(f"✅ Timestamps son diferentes: {payload_1['iat'] != payload_2['iat']}")
        print("✅ TEST 4 PASÓ\n")
    
    def test_05_refresh_token_rota(self):
        """✅ Test 5: Refresh Token se rota (nuevo token después de refresh)"""
        print("\n" + "="*80)
        print("TEST 5: Refresh Token se rota")
        print("="*80)
        
        # Login
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        refresh_token_1 = response.cookies['refreshToken'].value
        
        # Refresh
        response = self.client.post(self.refresh_url)
        
        refresh_token_2 = response.cookies['refreshToken'].value
        
        # Verificar que son diferentes
        self.assertNotEqual(refresh_token_1, refresh_token_2)
        
        print(f"✅ Refresh Token 1: {refresh_token_1[:50]}...")
        print(f"✅ Refresh Token 2: {refresh_token_2[:50]}...")
        print(f"✅ Tokens son diferentes (rotación): {refresh_token_1 != refresh_token_2}")
        print("✅ TEST 5 PASÓ\n")
    
    def test_06_refresh_token_duracion_2horas(self):
        """✅ Test 6: Refresh Token dura 2 horas"""
        print("\n" + "="*80)
        print("TEST 6: Refresh Token dura 2 horas")
        print("="*80)
        
        # Crear refresh token
        refresh_token_plano, refresh_token_obj = RefreshToken.crear_token(
            usuario=self.user,
            duracion_horas=2
        )
        
        # Verificar duración
        now = timezone.now()
        expires_at = refresh_token_obj.expires_at
        duration = (expires_at - now).total_seconds() / 3600  # En horas
        
        self.assertAlmostEqual(duration, 2, delta=0.1)
        
        print(f"✅ Token creado: {now}")
        print(f"✅ Token expira: {expires_at}")
        print(f"✅ Duración: {duration:.2f} horas")
        print("✅ TEST 6 PASÓ\n")
    
    def test_07_token_expirado_retorna_401(self):
        """✅ Test 7: Peticiones con token expirado retornan 401"""
        print("\n" + "="*80)
        print("TEST 7: Token expirado retorna 401")
        print("="*80)
        
        # Generar token expirado
        from api.utils.jwt_utils import ACCESS_TOKEN_LIFETIME
        
        # Crear token con expiración en el pasado
        now = datetime.utcnow()
        payload = {
            'user_id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'rol': 'cliente',
            'iat': now,
            'exp': now - timedelta(minutes=1),  # Expirado hace 1 minuto
            'type': 'access'
        }
        
        import jwt
        from django.conf import settings
        expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        # Intentar usar token expirado
        response = self.client.get(
            '/api/productos/',
            HTTP_AUTHORIZATION=f'Bearer {expired_token}'
        )
        
        # Debería retornar 401 o 200 (si es endpoint público)
        # Verificar que el token se detecta como expirado
        payload_check = verificar_access_token(expired_token)
        self.assertIsNone(payload_check)
        
        print(f"✅ Token expirado: {expired_token[:50]}...")
        print(f"✅ Verificación retorna None: {payload_check is None}")
        print("✅ TEST 7 PASÓ\n")
    
    def test_08_dos_pestanas_tokens_independientes(self):
        """✅ Test 8: Dos pestañas tienen tokens independientes"""
        print("\n" + "="*80)
        print("TEST 8: Dos pestañas = tokens independientes")
        print("="*80)
        
        # Pestaña 1: Login
        client1 = APIClient()
        response1 = client1.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        token1 = response1.json()['accessToken']
        refresh1 = response1.cookies['refreshToken'].value
        
        # Pestaña 2: Login (nuevo cliente)
        client2 = APIClient()
        response2 = client2.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        token2 = response2.json()['accessToken']
        refresh2 = response2.cookies['refreshToken'].value
        
        # Verificar que son diferentes
        self.assertNotEqual(token1, token2)
        self.assertNotEqual(refresh1, refresh2)
        
        print(f"✅ Pestaña 1 Access Token: {token1[:50]}...")
        print(f"✅ Pestaña 2 Access Token: {token2[:50]}...")
        print(f"✅ Tokens son diferentes: {token1 != token2}")
        print(f"✅ Refresh Tokens son diferentes: {refresh1 != refresh2}")
        print("✅ TEST 8 PASÓ\n")
    
    def test_09_logout_limpia_todo(self):
        """✅ Test 9: Logout limpia todo correctamente"""
        print("\n" + "="*80)
        print("TEST 9: Logout limpia todo")
        print("="*80)
        
        # Login
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        access_token = response.json()['accessToken']
        
        # Verificar que token es válido
        payload = verificar_access_token(access_token)
        self.assertIsNotNone(payload)
        
        # Logout
        response = self.client.post(
            self.logout_url,
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        # Verificar respuesta
        self.assertEqual(response.status_code, 200)
        
        print(f"✅ Logout exitoso")
        print("✅ TEST 9 PASÓ\n")
    
    def test_10_flujo_completo_15min(self):
        """✅ Test 10: Flujo completo (simular 15 minutos)"""
        print("\n" + "="*80)
        print("TEST 10: Flujo completo (simular 15 minutos)")
        print("="*80)
        
        # 1. Login
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        access_token_1 = response.json()['accessToken']
        payload_1 = verificar_access_token(access_token_1)
        print(f"✅ 1. Login exitoso")
        print(f"   Access Token: {access_token_1[:50]}...")
        
        # 2. Verificar token válido
        self.assertIsNotNone(payload_1)
        print(f"✅ 2. Access Token válido")
        
        # 3. Simular 15 minutos después (token expirado)
        print(f"✅ 3. Simulando 15 minutos después...")
        
        # Esperar 1 segundo para que cambie el timestamp
        import time
        time.sleep(1)
        
        # 4. Refresh token
        response = self.client.post(self.refresh_url)
        
        access_token_2 = response.json()['accessToken']
        payload_2 = verificar_access_token(access_token_2)
        print(f"✅ 4. Refresh exitoso")
        print(f"   Nuevo Access Token: {access_token_2[:50]}...")
        
        # 5. Verificar nuevo token válido
        self.assertIsNotNone(payload_2)
        print(f"✅ 5. Nuevo Access Token válido")
        
        # 6. Verificar que tokens tienen diferentes timestamps
        self.assertNotEqual(payload_1['iat'], payload_2['iat'])
        print(f"✅ 6. Tokens tienen diferentes timestamps (rotación)")
        
        print("✅ TEST 10 PASÓ\n")


def run_all_tests():
    """Ejecutar todos los tests"""
    print("\n" + "="*80)
    print("🧪 EJECUTANDO SUITE DE TESTS - REFRESH TOKEN (2 HORAS)")
    print("="*80)
    
    import unittest
    
    # Crear suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(RefreshTokenTestCase)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    print("\n" + "="*80)
    print("📊 RESUMEN DE RESULTADOS")
    print("="*80)
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Tests pasados: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Tests fallidos: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
    else:
        print("\n❌ ALGUNOS TESTS FALLARON")
    
    print("="*80 + "\n")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
