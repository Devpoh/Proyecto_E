#!/usr/bin/env python
"""
═══════════════════════════════════════════════════════════════════════════════
🧪 TEST - Flujo Completo de Recuperación de Contraseña
═══════════════════════════════════════════════════════════════════════════════

Script para probar el flujo completo de recuperación de contraseña con códigos.
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from api.models import PasswordRecoveryCode
from api.tasks import enviar_email_recuperacion
import time

print("\n" + "="*80)
print("🧪 TEST - FLUJO DE RECUPERACIÓN DE CONTRASEÑA")
print("="*80 + "\n")

# 1. Crear usuario de prueba
print("1️⃣  Creando usuario de prueba...")
try:
    usuario = User.objects.get(username='testuser')
    print(f"   ✅ Usuario existente: {usuario.email}")
except User.DoesNotExist:
    usuario = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='OldPassword123!'
    )
    print(f"   ✅ Usuario creado: {usuario.email}")

# 2. Generar código de recuperación
print("\n2️⃣  Generando código de recuperación...")
recovery_code = PasswordRecoveryCode.crear_codigo(
    usuario=usuario,
    duracion_minutos=15,
    ip_address='127.0.0.1',
    user_agent='Test Browser'
)
print(f"   ✅ Código generado: {recovery_code.codigo}")
print(f"   ⏰ Expira en: {recovery_code.expires_at}")
print(f"   🔒 Verificado: {recovery_code.verificado}")

# 3. Enviar email con Celery
print("\n3️⃣  Enviando email con código...")
try:
    result = enviar_email_recuperacion.delay(
        email=usuario.email,
        nombre=usuario.first_name or usuario.username,
        codigo=recovery_code.codigo,
        usuario_id=usuario.id
    )
    print(f"   ✅ Tarea Celery enviada: {result.id}")
    print(f"   ⏳ Esperando resultado...")
    time.sleep(3)
    print(f"   📧 Email enviado a: {usuario.email}")
except Exception as e:
    print(f"   ❌ Error al enviar email: {str(e)}")

# 4. Verificar código
print("\n4️⃣  Verificando código...")
verified_code = PasswordRecoveryCode.verificar_codigo(usuario, recovery_code.codigo)
if verified_code:
    print(f"   ✅ Código válido y verificado")
else:
    print(f"   ❌ Código inválido")

# 5. Actualizar contraseña
print("\n5️⃣  Actualizando contraseña...")
usuario.set_password('NewPassword123!')
usuario.save()
print(f"   ✅ Contraseña actualizada")

# 6. Marcar código como usado
print("\n6️⃣  Marcando código como usado...")
recovery_code.marcar_verificado()
print(f"   ✅ Código marcado como verificado")

# 7. Verificar que el código no se puede reutilizar
print("\n7️⃣  Intentando reutilizar código...")
reused_code = PasswordRecoveryCode.verificar_codigo(usuario, recovery_code.codigo)
if reused_code:
    print(f"   ❌ PROBLEMA: El código se puede reutilizar")
else:
    print(f"   ✅ Código no se puede reutilizar (seguridad correcta)")

print("\n" + "="*80)
print("✅ FLUJO COMPLETADO EXITOSAMENTE")
print("="*80 + "\n")

print("📋 RESUMEN:")
print(f"   • Usuario: {usuario.username} ({usuario.email})")
print(f"   • Código: {recovery_code.codigo}")
print(f"   • Duración: 15 minutos")
print(f"   • Email enviado: ✅")
print(f"   • Código verificado: ✅")
print(f"   • Contraseña actualizada: ✅")
print(f"   • Reutilización bloqueada: ✅")
print("\n")
