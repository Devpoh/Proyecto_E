"""
Script para debuggear qué valor está causando el error
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.utils import obtener_info_request
from api.models import RefreshToken
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
import secrets

# Simular un request
class FakeRequest:
    def __init__(self):
        self.META = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'REMOTE_ADDR': '127.0.0.1'
        }

request = FakeRequest()
info = obtener_info_request(request)

print("=" * 80)
print("INFORMACION DEL REQUEST")
print("=" * 80)
print(f"IP Address: {info['ip_address']}")
print(f"Longitud IP: {len(info['ip_address'])} caracteres")
print(f"User Agent: {info['user_agent']}")
print(f"Longitud User Agent: {len(info['user_agent'])} caracteres")
print()

# Generar un JTI y ver su longitud
jti = secrets.token_urlsafe(32)
print("=" * 80)
print("JTI GENERADO")
print("=" * 80)
print(f"JTI: {jti}")
print(f"Longitud JTI: {len(jti)} caracteres")
print()

# Generar token y ver su longitud
token = secrets.token_hex(64)
print("=" * 80)
print("TOKEN GENERADO")
print("=" * 80)
print(f"Token (primeros 50 chars): {token[:50]}...")
print(f"Longitud Token: {len(token)} caracteres")
print()

# Hash del token
import hashlib
token_hash = hashlib.sha256(token.encode()).hexdigest()
print("=" * 80)
print("TOKEN HASH")
print("=" * 80)
print(f"Token Hash: {token_hash}")
print(f"Longitud Token Hash: {len(token_hash)} caracteres")
print()

print("=" * 80)
print("ANALISIS")
print("=" * 80)
print("Campos en RefreshToken y sus límites:")
print(f"  - token_hash: max_length=64, valor actual={len(token_hash)}")
print(f"  - jti: max_length=36, valor actual={len(jti)}")
print(f"  - user_agent: max_length=500, valor actual={len(info['user_agent'])}")
print(f"  - ip_address: GenericIPAddressField, valor actual={len(info['ip_address'])}")
print()

if len(jti) > 36:
    print("⚠️  PROBLEMA ENCONTRADO: JTI es demasiado largo!")
    print(f"   JTI tiene {len(jti)} caracteres pero el campo solo permite 36")
    print()
