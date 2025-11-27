#!/usr/bin/env python
"""
Script para debuggear el test de rate limiting
"""
import os
import sys
import django
import logging

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

# Habilitar logging detallado
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('django')

from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from api.models import PasswordRecoveryCode, LoginAttempt
import json

# Crear cliente de prueba
client = Client()

# Crear usuario con nombre único
import uuid
username = f'testuser_{uuid.uuid4().hex[:8]}'
email = f'test_{uuid.uuid4().hex[:8]}@example.com'

user = User.objects.create_user(
    username=username,
    email=email,
    password='TestPass123!'
)

print("✅ Usuario creado")

# Hacer una solicitud al endpoint
url = '/api/auth/reset-password/'
data = {
    'email': email,  # Usar el email del usuario creado
    'codigo': '000000',  # Código incorrecto
    'password': 'NewPassword123!',
    'password_confirm': 'NewPassword123!'
}

print(f"📤 Enviando POST a {url}")
print(f"📋 Datos: {data}")

try:
    response = client.post(
        url,
        data=json.dumps(data),
        content_type='application/json',
        REMOTE_ADDR='192.168.1.1'
    )
    
    print(f"📥 Status Code: {response.status_code}")
    print(f"📥 Response: {response.data if hasattr(response, 'data') else response.content}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()

# Limpiar
user.delete()
print("✅ Usuario eliminado")
