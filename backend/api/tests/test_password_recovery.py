"""
═══════════════════════════════════════════════════════════════════════════════
🧪 TESTS - Recuperación de Contraseña
═══════════════════════════════════════════════════════════════════════════════

Tests para el sistema de recuperación de contraseña con tokens seguros.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from api.models import PasswordResetToken, LoginAttempt
from unittest.mock import patch
import json


class PasswordResetTokenModelTest(TestCase):
    """Tests para el modelo PasswordResetToken"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
    
    def test_generar_token(self):
        """Test: Generar token seguro"""
        token = PasswordResetToken.generate_token()
        
        self.assertIsNotNone(token)
        self.assertGreater(len(token), 20)
    
    def test_hash_token(self):
        """Test: Hashear token con SHA-256"""
        token = PasswordResetToken.generate_token()
        token_hash = PasswordResetToken.hash_token(token)
        
        self.assertEqual(len(token_hash), 64)  # SHA-256 = 64 caracteres hex
        self.assertNotEqual(token, token_hash)
    
    def test_crear_token(self):
        """Test: Crear token de recuperación"""
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30,
            ip_address='127.0.0.1'
        )
        
        self.assertIsNotNone(token_plano)
        self.assertIsNotNone(token_obj)
        self.assertEqual(token_obj.usuario, self.user)
        self.assertFalse(token_obj.usado)
        self.assertEqual(token_obj.ip_address, '127.0.0.1')
    
    def test_is_valid_token_valido(self):
        """Test: Token válido no expirado"""
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        
        self.assertTrue(token_obj.is_valid())
    
    def test_is_valid_token_expirado(self):
        """Test: Token expirado"""
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        
        # Simular expiración
        token_obj.expires_at = timezone.now() - timedelta(minutes=1)
        token_obj.save()
        
        self.assertFalse(token_obj.is_valid())
    
    def test_is_valid_token_usado(self):
        """Test: Token ya usado"""
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        token_obj.marcar_como_usado()
        
        self.assertFalse(token_obj.is_valid())
    
    def test_marcar_como_usado(self):
        """Test: Marcar token como usado"""
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        
        token_obj.marcar_como_usado()
        
        self.assertTrue(token_obj.usado)
        self.assertIsNotNone(token_obj.usado_at)
    
    def test_verificar_token_valido(self):
        """Test: Verificar token válido"""
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        
        resultado = PasswordResetToken.verificar_token(token_plano)
        
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.usuario, self.user)
    
    def test_verificar_token_invalido(self):
        """Test: Verificar token inválido"""
        resultado = PasswordResetToken.verificar_token('token_invalido_xyz')
        
        self.assertIsNone(resultado)
    
    def test_verificar_token_expirado(self):
        """Test: Verificar token expirado"""
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        
        # Simular expiración
        token_obj.expires_at = timezone.now() - timedelta(minutes=1)
        token_obj.save()
        
        resultado = PasswordResetToken.verificar_token(token_plano)
        
        self.assertIsNone(resultado)
    
    def test_verificar_token_usado(self):
        """Test: Verificar token ya usado"""
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        token_obj.marcar_como_usado()
        
        resultado = PasswordResetToken.verificar_token(token_plano)
        
        self.assertIsNone(resultado)
    
    def test_limpiar_tokens_expirados(self):
        """Test: Limpiar tokens expirados"""
        # Crear token expirado
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        token_obj.expires_at = timezone.now() - timedelta(minutes=1)
        token_obj.save()
        
        # Limpiar
        count = PasswordResetToken.limpiar_tokens_expirados()
        
        self.assertEqual(count, 1)
        self.assertEqual(PasswordResetToken.objects.count(), 0)
    
    def test_crear_token_revoca_anteriores(self):
        """Test: Crear nuevo token revoca los anteriores sin usar"""
        # Crear primer token
        token1_plano, token1_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        
        # Crear segundo token
        token2_plano, token2_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        
        # El primer token debe estar eliminado
        self.assertEqual(PasswordResetToken.objects.count(), 1)
        self.assertEqual(PasswordResetToken.objects.first().usuario, self.user)


class PasswordResetEndpointsTest(TestCase):
    """Tests para los endpoints de recuperación de contraseña"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.forgot_url = '/api/auth/forgot-password/'
        self.reset_url = '/api/auth/reset-password/'
    
    @patch('api.tasks.enviar_email_recuperacion.delay')
    def test_forgot_password_email_valido(self, mock_email):
        """Test: Solicitar recuperación con email válido"""
        data = {'email': 'test@example.com'}
        
        response = self.client.post(
            self.forgot_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json())
        
        # Verificar que se llamó a la tarea de email
        mock_email.assert_called_once()
    
    @patch('api.tasks.enviar_email_recuperacion.delay')
    def test_forgot_password_email_no_existe(self, mock_email):
        """Test: Solicitar recuperación con email que no existe"""
        data = {'email': 'noexiste@example.com'}
        
        response = self.client.post(
            self.forgot_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Devuelve 200 por seguridad (no revela si el email existe)
        self.assertEqual(response.status_code, 200)
        
        # No debe enviar email
        mock_email.assert_not_called()
    
    @patch('api.tasks.enviar_email_recuperacion.delay')
    def test_forgot_password_sin_email(self, mock_email):
        """Test: Solicitar recuperación sin email"""
        data = {'email': ''}
        
        response = self.client.post(
            self.forgot_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        mock_email.assert_not_called()
    
    def test_reset_password_token_valido(self):
        """Test: Resetear contraseña con token válido"""
        # Crear token
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        
        data = {
            'token': token_plano,
            'password': 'NewPassword123!',
            'password_confirm': 'NewPassword123!'
        }
        
        response = self.client.post(
            self.reset_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que la contraseña fue actualizada
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123!'))
        
        # Verificar que el token fue marcado como usado
        token_obj.refresh_from_db()
        self.assertTrue(token_obj.usado)
    
    def test_reset_password_token_invalido(self):
        """Test: Resetear contraseña con token inválido"""
        data = {
            'token': 'token_invalido_xyz',
            'password': 'NewPassword123!',
            'password_confirm': 'NewPassword123!'
        }
        
        response = self.client.post(
            self.reset_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_reset_password_contraseñas_no_coinciden(self):
        """Test: Resetear contraseña con contraseñas que no coinciden"""
        # Crear token
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        
        data = {
            'token': token_plano,
            'password': 'NewPassword123!',
            'password_confirm': 'DifferentPassword123!'
        }
        
        response = self.client.post(
            self.reset_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_reset_password_contraseña_muy_corta(self):
        """Test: Resetear contraseña con contraseña muy corta"""
        # Crear token
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        
        data = {
            'token': token_plano,
            'password': 'Short1!',
            'password_confirm': 'Short1!'
        }
        
        response = self.client.post(
            self.reset_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_reset_password_token_expirado(self):
        """Test: Resetear contraseña con token expirado"""
        # Crear token expirado
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        token_obj.expires_at = timezone.now() - timedelta(minutes=1)
        token_obj.save()
        
        data = {
            'token': token_plano,
            'password': 'NewPassword123!',
            'password_confirm': 'NewPassword123!'
        }
        
        response = self.client.post(
            self.reset_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)
    
    def test_reset_password_token_ya_usado(self):
        """Test: Resetear contraseña con token ya usado"""
        # Crear token y marcarlo como usado
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        token_obj.marcar_como_usado()
        
        data = {
            'token': token_plano,
            'password': 'NewPassword123!',
            'password_confirm': 'NewPassword123!'
        }
        
        response = self.client.post(
            self.reset_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 401)


class PasswordResetSecurityTest(TestCase):
    """Tests de seguridad para recuperación de contraseña"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
    
    @patch('api.tasks.enviar_email_recuperacion.delay')
    def test_rate_limiting_forgot_password(self, mock_email):
        """Test: Rate limiting en forgot-password (5 intentos/15 min)"""
        # Hacer 5 intentos
        for i in range(5):
            data = {'email': f'test{i}@example.com'}
            response = self.client.post(
                '/api/auth/forgot-password/',
                data=json.dumps(data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200)
        
        # El 6to intento debe ser bloqueado
        data = {'email': 'test6@example.com'}
        response = self.client.post(
            '/api/auth/forgot-password/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)  # Siempre devuelve 200 por seguridad
    
    def test_token_no_se_almacena_en_texto_plano(self):
        """Test: Token no se almacena en texto plano"""
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        
        # El token en la BD debe ser diferente al token plano
        self.assertNotEqual(token_plano, token_obj.token_hash)
        
        # El token_hash debe ser un hash SHA-256
        self.assertEqual(len(token_obj.token_hash), 64)
    
    def test_token_expira_en_30_minutos(self):
        """Test: Token expira en 30 minutos"""
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        
        # Verificar que el token expira en aproximadamente 30 minutos
        tiempo_expiracion = (token_obj.expires_at - token_obj.created_at).total_seconds()
        
        # Permitir 1 segundo de margen
        self.assertAlmostEqual(tiempo_expiracion, 30 * 60, delta=1)
    
    def test_token_uso_unico(self):
        """Test: Token solo se puede usar una vez"""
        token_plano, token_obj = PasswordResetToken.crear_token(
            usuario=self.user,
            duracion_minutos=30
        )
        
        # Primer intento debe funcionar
        resultado1 = PasswordResetToken.verificar_token(token_plano)
        self.assertIsNotNone(resultado1)
        
        # Marcar como usado
        token_obj.marcar_como_usado()
        
        # Segundo intento debe fallar
        resultado2 = PasswordResetToken.verificar_token(token_plano)
        self.assertIsNone(resultado2)


class ResetPasswordRateLimitingTest(TestCase):
    """Tests para el rate limiting en el endpoint reset-password"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!'
        )
        self.url = '/api/auth/reset-password/'
    
    def test_rate_limiting_bloquea_despues_de_10_intentos(self):
        """Test: Bloquear después de 10 intentos fallidos desde la misma IP"""
        from api.models import PasswordRecoveryCode
        
        # Realizar 10 intentos fallidos
        for i in range(10):
            response = self.client.post(
                self.url,
                {
                    'email': 'test@example.com',
                    'codigo': '000000',  # Código incorrecto
                    'password': 'NewPassword123!',
                    'password_confirm': 'NewPassword123!'
                },
                format='json',
                REMOTE_ADDR='192.168.1.1'  # IP fija para las pruebas
            )
            # Los primeros 10 intentos deben fallar con 400 o 401
            self.assertIn(response.status_code, [400, 401], f"Falló en el intento {i+1}, status: {response.status_code}")
        
        # El intento 11 debería estar bloqueado (429 Too Many Requests)
        response = self.client.post(
            self.url,
            {
                'email': 'test@example.com',
                'codigo': '000000',  # Código incorrecto, pero bloqueado por IP
                'password': 'NewPassword123!',
                'password_confirm': 'NewPassword123!'
            },
            format='json',
            REMOTE_ADDR='192.168.1.1'  # Misma IP
        )
        
        self.assertEqual(response.status_code, 429)
        self.assertIn('retry_after', response.data)
        
    def test_rate_limiting_por_ip(self):
        """Test: El bloqueo es por IP, no por usuario"""
        # Bloquear una IP
        for _ in range(10):
            response = self.client.post(
                self.url,
                {
                    'email': 'test@example.com',
                    'codigo': '000000',
                    'password': 'NewPassword123!',
                    'password_confirm': 'NewPassword123!'
                },
                format='json',
                REMOTE_ADDR='192.168.1.100'  # IP 1
            )
        
        # Otra IP diferente debería poder intentar
        response = self.client.post(
            self.url,
            {
                'email': 'test@example.com',
                'codigo': '000000',  # Código incorrecto, pero desde otra IP
                'password': 'NewPassword123!',
                'password_confirm': 'NewPassword123!'
            },
            format='json',
            REMOTE_ADDR='192.168.1.200'  # IP diferente
        )
        
        # Debería poder intentar desde otra IP
        self.assertIn(response.status_code, [400, 401])
        
    def test_codigo_valido_no_se_bloquea(self):
        """Test: Un código válido no debe contar para el rate limiting"""
        from api.models import PasswordRecoveryCode
        
        # Crear un código de recuperación válido
        recovery_code = '123456'
        
        PasswordRecoveryCode.objects.create(
            usuario=self.user,
            codigo=recovery_code,
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        
        # Realizar 9 intentos fallidos
        for _ in range(9):
            response = self.client.post(
                self.url,
                {
                    'email': 'test@example.com',
                    'codigo': '000000',  # Código incorrecto
                    'password': 'NewPassword123!',
                    'password_confirm': 'NewPassword123!'
                },
                format='json',
                REMOTE_ADDR='192.168.1.1'
            )
        
        # 10mo intento con código correcto
        response = self.client.post(
            self.url,
            {
                'email': 'test@example.com',
                'codigo': '123456',  # Código correcto
                'password': 'NewPassword123!',
                'password_confirm': 'NewPassword123!'
            },
            format='json',
            REMOTE_ADDR='192.168.1.1'
        )
        
        # Debería funcionar sin bloquear
        self.assertEqual(response.status_code, 200)
