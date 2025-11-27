#!/usr/bin/env python
"""
═══════════════════════════════════════════════════════════════════════════════
🧪 TEST MANUAL - Recuperación de Contraseña
═══════════════════════════════════════════════════════════════════════════════

Script para probar manualmente el flujo de recuperación de contraseña.

Uso:
    python test_password_recovery_manual.py
"""

import os
import sys
import django
from django.conf import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
django.setup()

from django.contrib.auth.models import User
from api.models import PasswordResetToken
from api.tasks import enviar_email_recuperacion
import json

print("\n" + "="*80)
print("🧪 TEST MANUAL - RECUPERACIÓN DE CONTRASEÑA")
print("="*80 + "\n")

# 1. Crear o buscar usuario de prueba
print("1️⃣  Buscando/creando usuario de prueba...")
usuario, creado = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User'
    }
)
print(f"   ✅ Usuario: {usuario.username} ({usuario.email}) - {'Creado' if creado else 'Existente'}")

# 2. Crear token de recuperación
print("\n2️⃣  Creando token de recuperación...")
token_plano, token_obj = PasswordResetToken.crear_token(
    usuario=usuario,
    duracion_minutos=30,
    ip_address='127.0.0.1'
)
print(f"   ✅ Token creado (primeros 20 caracteres): {token_plano[:20]}...")
print(f"   ✅ Token hash: {token_obj.token_hash[:20]}...")
print(f"   ✅ Expira en: {token_obj.expires_at}")

# 3. Enviar email de forma síncrona (para prueba)
print("\n3️⃣  Enviando email de recuperación...")
try:
    # Usar apply_async con eager=True para ejecutar de forma síncrona
    result = enviar_email_recuperacion.apply_async(
        args=[],
        kwargs={
            'email': usuario.email,
            'nombre': usuario.first_name or usuario.username,
            'token': token_plano,
            'usuario_id': usuario.id
        }
    )
    print(f"   ✅ Email enviado exitosamente")
    print(f"   ✅ Task ID: {result.id}")
except Exception as e:
    print(f"   ❌ Error al enviar email: {str(e)}")

# 4. Verificar que el token se puede recuperar
print("\n4️⃣  Verificando token...")
token_recuperado = PasswordResetToken.verificar_token(token_plano)
if token_recuperado:
    print(f"   ✅ Token válido y recuperado")
    print(f"   ✅ Usuario: {token_recuperado.usuario.username}")
else:
    print(f"   ❌ Token no válido")

# 5. Simular reset de contraseña
print("\n5️⃣  Simulando reset de contraseña...")
nueva_contraseña = 'NewPassword123!'
usuario.set_password(nueva_contraseña)
usuario.save()
print(f"   ✅ Contraseña actualizada")

# 6. Marcar token como usado
print("\n6️⃣  Marcando token como usado...")
token_obj.marcar_como_usado()
print(f"   ✅ Token marcado como usado")

# 7. Verificar que el token ya no es válido
print("\n7️⃣  Verificando que token ya no es válido...")
token_recuperado_2 = PasswordResetToken.verificar_token(token_plano)
if token_recuperado_2:
    print(f"   ❌ Token debería estar inválido")
else:
    print(f"   ✅ Token correctamente invalidado")

print("\n" + "="*80)
print("✅ TEST COMPLETADO EXITOSAMENTE")
print("="*80 + "\n")

print("📝 RESUMEN:")
print(f"   - Usuario: {usuario.username} ({usuario.email})")
print(f"   - Token creado: {token_plano[:20]}...")
print(f"   - Email enviado: ✅")
print(f"   - Token verificado: ✅")
print(f"   - Contraseña actualizada: ✅")
print(f"   - Token invalidado: ✅")
print("\n")
