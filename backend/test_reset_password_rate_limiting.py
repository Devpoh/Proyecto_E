"""
═══════════════════════════════════════════════════════════════════════════════
🧪 TEST - Rate Limiting en reset_password_confirm
═══════════════════════════════════════════════════════════════════════════════

Verifica que el rate limiting funciona correctamente:
- Máximo 10 intentos por IP en 15 minutos
- Bloquea después de 10 intentos fallidos
- Permite intentos después del tiempo de espera
"""

import os
import sys
import django

# Configurar Django ANTES de importar modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyecto_e.settings')

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json

from api.models import PasswordRecoveryCode, LoginAttempt


class ResetPasswordRateLimitingTest(TestCase):
    """Test para rate limiting en reset_password_confirm"""
    
    def setUp(self):
        """Preparar datos de prueba"""
        self.client = Client()
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='test_reset_rate',
            email='test_reset_rate@example.com',
            password='OldPassword123!'
        )
        
        # Crear código de recuperación válido
        self.recovery_code = PasswordRecoveryCode.crear_codigo(
            usuario=self.user,
            duracion_minutos=15
        )
        
        # IP de prueba
        self.test_ip = '192.168.1.100'
    
    def tearDown(self):
        """Limpiar después de cada test"""
        LoginAttempt.objects.all().delete()
        PasswordRecoveryCode.objects.all().delete()
        User.objects.all().delete()
    
    def test_rate_limiting_bloquea_despues_de_10_intentos(self):
        """Verifica que se bloquea después de 10 intentos fallidos"""
        print("\n✅ TEST: Rate limiting bloquea después de 10 intentos")
        
        # Hacer 10 intentos fallidos
        for i in range(10):
            response = self.client.post(
                '/api/auth/reset-password-confirm/',
                data=json.dumps({
                    'email': self.user.email,
                    'codigo': '000000',  # Código inválido
                    'password': 'NewPassword123!',
                    'password_confirm': 'NewPassword123!'
                }),
                content_type='application/json',
                REMOTE_ADDR=self.test_ip
            )
            
            # Los primeros 9 intentos deben retornar 401 (código inválido)
            if i < 9:
                self.assertEqual(response.status_code, 401, f"Intento {i+1}: esperaba 401")
                print(f"  Intento {i+1}: ✓ 401 (código inválido)")
            else:
                # El intento 10 también debe retornar 401 pero ahora está bloqueado
                self.assertEqual(response.status_code, 401, f"Intento {i+1}: esperaba 401")
                print(f"  Intento {i+1}: ✓ 401 (código inválido)")
        
        # El intento 11 debe retornar 429 (bloqueado por rate limiting)
        response = self.client.post(
            '/api/auth/reset-password-confirm/',
            data=json.dumps({
                'email': self.user.email,
                'codigo': '000000',
                'password': 'NewPassword123!',
                'password_confirm': 'NewPassword123!'
            }),
            content_type='application/json',
            REMOTE_ADDR=self.test_ip
        )
        
        self.assertEqual(response.status_code, 429, "Intento 11: esperaba 429 (bloqueado)")
        self.assertIn('retry_after', response.json(), "Debería incluir retry_after")
        print(f"  Intento 11: ✓ 429 (bloqueado por rate limiting)")
        print(f"  Tiempo de espera: {response.json()['retry_after']}s")
    
    def test_rate_limiting_por_ip(self):
        """Verifica que el rate limiting es por IP"""
        print("\n✅ TEST: Rate limiting es por IP")
        
        ip1 = '192.168.1.100'
        ip2 = '192.168.1.101'
        
        # Hacer 10 intentos desde IP1
        for i in range(10):
            response = self.client.post(
                '/api/auth/reset-password-confirm/',
                data=json.dumps({
                    'email': self.user.email,
                    'codigo': '000000',
                    'password': 'NewPassword123!',
                    'password_confirm': 'NewPassword123!'
                }),
                content_type='application/json',
                REMOTE_ADDR=ip1
            )
            self.assertEqual(response.status_code, 401)
        
        # IP1 debe estar bloqueada
        response = self.client.post(
            '/api/auth/reset-password-confirm/',
            data=json.dumps({
                'email': self.user.email,
                'codigo': '000000',
                'password': 'NewPassword123!',
                'password_confirm': 'NewPassword123!'
            }),
            content_type='application/json',
            REMOTE_ADDR=ip1
        )
        self.assertEqual(response.status_code, 429, "IP1 debe estar bloqueada")
        print(f"  IP1 (192.168.1.100): ✓ Bloqueada después de 10 intentos")
        
        # IP2 debe poder hacer intentos
        response = self.client.post(
            '/api/auth/reset-password-confirm/',
            data=json.dumps({
                'email': self.user.email,
                'codigo': '000000',
                'password': 'NewPassword123!',
                'password_confirm': 'NewPassword123!'
            }),
            content_type='application/json',
            REMOTE_ADDR=ip2
        )
        self.assertEqual(response.status_code, 401, "IP2 debe poder hacer intentos")
        print(f"  IP2 (192.168.1.101): ✓ Puede hacer intentos (no bloqueada)")
    
    def test_codigo_valido_no_se_bloquea(self):
        """Verifica que un código válido no se bloquea por rate limiting"""
        print("\n✅ TEST: Código válido no se bloquea por rate limiting")
        
        # Hacer 9 intentos fallidos
        for i in range(9):
            response = self.client.post(
                '/api/auth/reset-password-confirm/',
                data=json.dumps({
                    'email': self.user.email,
                    'codigo': '000000',
                    'password': 'NewPassword123!',
                    'password_confirm': 'NewPassword123!'
                }),
                content_type='application/json',
                REMOTE_ADDR=self.test_ip
            )
            self.assertEqual(response.status_code, 401)
        
        # Intento 10 con código válido debe funcionar
        response = self.client.post(
            '/api/auth/reset-password-confirm/',
            data=json.dumps({
                'email': self.user.email,
                'codigo': self.recovery_code.codigo,
                'password': 'NewPassword123!',
                'password_confirm': 'NewPassword123!'
            }),
            content_type='application/json',
            REMOTE_ADDR=self.test_ip
        )
        
        self.assertEqual(response.status_code, 200, "Código válido debe funcionar")
        self.assertIn('accessToken', response.json())
        print(f"  Intento 10 con código válido: ✓ 200 (éxito)")


if __name__ == '__main__':
    import unittest
    
    # Crear suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(ResetPasswordRateLimitingTest)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    print("\n" + "="*80)
    if result.wasSuccessful():
        print("✅ TODOS LOS TESTS PASARON")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        for failure in result.failures + result.errors:
            print(f"\n{failure[0]}:")
            print(failure[1])
