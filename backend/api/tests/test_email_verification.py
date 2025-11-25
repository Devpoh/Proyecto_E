"""
═══════════════════════════════════════════════════════════════════════════════
🧪 TESTS - Verificación de Email
═══════════════════════════════════════════════════════════════════════════════

Tests para el sistema de verificación de email con código de 6 dígitos.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from api.models import EmailVerification, LoginAttempt
from unittest.mock import patch
import json


class EmailVerificationModelTest(TestCase):
    """Tests para el modelo EmailVerification"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            is_active=False
        )
    
    def test_generar_codigo(self):
        """Test: Generar código de 6 dígitos"""
        codigo = EmailVerification.generar_codigo()
        
        self.assertEqual(len(codigo), 6)
        self.assertTrue(codigo.isdigit())
    
    def test_crear_codigo(self):
        """Test: Crear código de verificación"""
        verificacion = EmailVerification.crear_codigo(
            usuario=self.user,
            duracion_minutos=15,
            ip_address='127.0.0.1'
        )
        
        self.assertIsNotNone(verificacion)
        self.assertEqual(verificacion.usuario, self.user)
        self.assertEqual(len(verificacion.codigo), 6)
        self.assertFalse(verificacion.verificado)
        self.assertEqual(verificacion.intentos_fallidos, 0)
        self.assertEqual(verificacion.ip_address, '127.0.0.1')
    
    def test_is_valid_codigo_valido(self):
        """Test: Código válido no expirado"""
        verificacion = EmailVerification.crear_codigo(
            usuario=self.user,
            duracion_minutos=15
        )
        
        self.assertTrue(verificacion.is_valid())
    
    def test_is_valid_codigo_expirado(self):
        """Test: Código expirado"""
        verificacion = EmailVerification.crear_codigo(
            usuario=self.user,
            duracion_minutos=15
        )
        
        # Simular expiración
        verificacion.expires_at = timezone.now() - timedelta(minutes=1)
        verificacion.save()
        
        self.assertFalse(verificacion.is_valid())
    
    def test_is_valid_codigo_verificado(self):
        """Test: Código ya verificado"""
        verificacion = EmailVerification.crear_codigo(
            usuario=self.user,
            duracion_minutos=15
        )
        verificacion.marcar_verificado()
        
        self.assertFalse(verificacion.is_valid())
    
    def test_marcar_verificado(self):
        """Test: Marcar código como verificado"""
        verificacion = EmailVerification.crear_codigo(
            usuario=self.user,
            duracion_minutos=15
        )
        
        verificacion.marcar_verificado()
        
        self.assertTrue(verificacion.verificado)
        self.assertIsNotNone(verificacion.verificado_at)
    
    def test_incrementar_intentos(self):
        """Test: Incrementar intentos fallidos"""
        verificacion = EmailVerification.crear_codigo(
            usuario=self.user,
            duracion_minutos=15
        )
        
        self.assertEqual(verificacion.intentos_fallidos, 0)
        
        verificacion.incrementar_intentos()
        self.assertEqual(verificacion.intentos_fallidos, 1)
        
        verificacion.incrementar_intentos()
        self.assertEqual(verificacion.intentos_fallidos, 2)
    
    def test_puede_reenviar_sin_reenvios_previos(self):
        """Test: Puede reenviar sin reenvíos previos"""
        verificacion = EmailVerification.crear_codigo(
            usuario=self.user,
            duracion_minutos=15
        )
        
        self.assertTrue(verificacion.puede_reenviar(minutos_espera=1))
    
    def test_puede_reenviar_antes_del_cooldown(self):
        """Test: No puede reenviar antes del cooldown"""
        verificacion = EmailVerification.crear_codigo(
            usuario=self.user,
            duracion_minutos=15
        )
        verificacion.marcar_reenvio()
        
        self.assertFalse(verificacion.puede_reenviar(minutos_espera=1))
    
    def test_verificar_codigo_valido(self):
        """Test: Verificar código válido"""
        verificacion = EmailVerification.crear_codigo(
            usuario=self.user,
            duracion_minutos=15
        )
        codigo = verificacion.codigo
        
        resultado = EmailVerification.verificar_codigo(self.user, codigo)
        
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado.codigo, codigo)
    
    def test_verificar_codigo_invalido(self):
        """Test: Verificar código inválido"""
        EmailVerification.crear_codigo(
            usuario=self.user,
            duracion_minutos=15
        )
        
        resultado = EmailVerification.verificar_codigo(self.user, '000000')
        
        self.assertIsNone(resultado)
    
    def test_limpiar_codigos_expirados(self):
        """Test: Limpiar códigos expirados"""
        # Crear código expirado
        verificacion = EmailVerification.crear_codigo(
            usuario=self.user,
            duracion_minutos=15
        )
        verificacion.expires_at = timezone.now() - timedelta(minutes=1)
        verificacion.save()
        
        # Limpiar
        count = EmailVerification.limpiar_codigos_expirados()
        
        self.assertEqual(count, 1)
        self.assertEqual(EmailVerification.objects.count(), 0)
    
    def test_invalidar_codigos_usuario(self):
        """Test: Invalidar códigos de un usuario"""
        # Crear múltiples códigos
        for _ in range(3):
            EmailVerification.crear_codigo(
                usuario=self.user,
                duracion_minutos=15
            )
        
        # Invalidar todos
        count = EmailVerification.invalidar_codigos_usuario(self.user)
        
        self.assertEqual(count, 3)
        
        # Verificar que todos están marcados como verificados
        codigos = EmailVerification.objects.filter(usuario=self.user)
        for codigo in codigos:
            self.assertTrue(codigo.verificado)


class EmailVerificationEndpointsTest(TestCase):
    """Tests para los endpoints de verificación"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.register_url = '/api/auth/register-with-verification/'
        self.verify_url = '/api/auth/verify-email/'
        self.resend_url = '/api/auth/resend-verification/'
        self.status_url = '/api/auth/verification-status/'
    
    @patch('api.tasks.enviar_email_verificacion.delay')
    def test_register_with_verification(self, mock_email):
        """Test: Registro con verificación"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(
            self.register_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        # Verificar que el usuario fue creado
        user = User.objects.get(username='newuser')
        self.assertFalse(user.is_active)
        
        # Verificar que se creó el código
        verificacion = EmailVerification.objects.filter(usuario=user).first()
        self.assertIsNotNone(verificacion)
        
        # Verificar que se llamó a la tarea de email
        mock_email.assert_called_once()
    
    def test_verify_email_codigo_valido(self):
        """Test: Verificar email con código válido"""
        # Crear usuario y código
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            is_active=False
        )
        verificacion = EmailVerification.crear_codigo(
            usuario=user,
            duracion_minutos=15
        )
        
        data = {
            'email': 'test@example.com',
            'codigo': verificacion.codigo
        }
        
        response = self.client.post(
            self.verify_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que el usuario fue activado
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        
        # Verificar que el código fue marcado como verificado
        verificacion.refresh_from_db()
        self.assertTrue(verificacion.verificado)
    
    def test_verify_email_codigo_invalido(self):
        """Test: Verificar email con código inválido"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            is_active=False
        )
        EmailVerification.crear_codigo(
            usuario=user,
            duracion_minutos=15
        )
        
        data = {
            'email': 'test@example.com',
            'codigo': '000000'
        }
        
        response = self.client.post(
            self.verify_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        
        # Verificar que el usuario sigue inactivo
        user.refresh_from_db()
        self.assertFalse(user.is_active)
    
    @patch('api.tasks.enviar_email_verificacion.delay')
    def test_resend_verification(self, mock_email):
        """Test: Reenviar código de verificación"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            is_active=False
        )
        
        # Crear código inicial
        verificacion = EmailVerification.crear_codigo(
            usuario=user,
            duracion_minutos=15
        )
        
        # Simular que pasó el tiempo de cooldown
        verificacion.ultimo_reenvio = timezone.now() - timedelta(minutes=2)
        verificacion.save()
        
        data = {'email': 'test@example.com'}
        
        response = self.client.post(
            self.resend_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        mock_email.assert_called_once()
    
    def test_check_verification_status(self):
        """Test: Verificar estado de verificación"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            is_active=False
        )
        EmailVerification.crear_codigo(
            usuario=user,
            duracion_minutos=15
        )
        
        response = self.client.get(
            f'{self.status_url}?email=test@example.com'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['email'], 'test@example.com')
        self.assertFalse(data['is_verified'])
        self.assertTrue(data['has_pending_verification'])


class EmailVerificationSecurityTest(TestCase):
    """Tests de seguridad para verificación de email"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            is_active=False
        )
        self.verificacion = EmailVerification.crear_codigo(
            usuario=self.user,
            duracion_minutos=15,
            ip_address='127.0.0.1'
        )
    
    def test_limite_intentos_fallidos(self):
        """Test: Límite de 5 intentos fallidos por código"""
        # Hacer 5 intentos fallidos
        for i in range(5):
            self.verificacion.incrementar_intentos()
        
        self.assertEqual(self.verificacion.intentos_fallidos, 5)
        
        # El código debería estar bloqueado
        data = {
            'email': 'test@example.com',
            'codigo': '000000'
        }
        
        response = self.client.post(
            '/api/auth/verify-email/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 429)
    
    def test_limite_reenvios(self):
        """Test: Límite de 3 reenvíos"""
        # Hacer 3 reenvíos
        for _ in range(3):
            self.verificacion.marcar_reenvio()
        
        self.assertEqual(self.verificacion.contador_reenvios, 3)
        
        # Intentar reenviar de nuevo
        data = {'email': 'test@example.com'}
        
        response = self.client.post(
            '/api/auth/resend-verification/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 429)
    
    def test_codigo_expira_en_15_minutos(self):
        """Test: Código expira en 15 minutos"""
        # Verificar que el código expira en aproximadamente 15 minutos
        tiempo_expiracion = (self.verificacion.expires_at - self.verificacion.created_at).total_seconds()
        
        # Permitir 1 segundo de margen
        self.assertAlmostEqual(tiempo_expiracion, 15 * 60, delta=1)
