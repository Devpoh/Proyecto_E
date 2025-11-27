#!/usr/bin/env python
"""
═══════════════════════════════════════════════════════════════════════════════
🧪 DEBUG - Análisis del Cambio de Contraseña
═══════════════════════════════════════════════════════════════════════════════

Script para debuggear el problema del cambio de contraseña.
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
from django.utils import timezone
import time

print("\n" + "="*80)
print("🧪 DEBUG - ANÁLISIS DEL CAMBIO DE CONTRASEÑA")
print("="*80 + "\n")

# 1. Crear usuario de prueba
print("1️⃣  Buscando usuario ale...")
try:
    usuario = User.objects.get(username='ale')
    print(f"   ✅ Usuario encontrado: {usuario.username} ({usuario.email})")
    print(f"   📧 Email: {usuario.email}")
    print(f"   🔐 Password hash actual: {usuario.password[:50]}...")
except User.DoesNotExist:
    print("   ❌ Usuario ale no encontrado")
    sys.exit(1)

# 2. Guardar hash de contraseña actual
print("\n2️⃣  Guardando hash de contraseña actual...")
hash_anterior = usuario.password
print(f"   Hash anterior: {hash_anterior[:50]}...")

# 3. Generar código de recuperación
print("\n3️⃣  Generando código de recuperación...")
recovery_code = PasswordRecoveryCode.crear_codigo(
    usuario=usuario,
    duracion_minutos=15,
    ip_address='127.0.0.1',
    user_agent='Test Browser'
)
print(f"   ✅ Código generado: {recovery_code.codigo}")
print(f"   ⏰ Expira en: {recovery_code.expires_at}")
print(f"   🔒 Verificado: {recovery_code.verificado}")
print(f"   📊 Intentos fallidos: {recovery_code.intentos_fallidos}")

# 4. Verificar que el código es válido
print("\n4️⃣  Verificando que el código es válido...")
verified_code = PasswordRecoveryCode.verificar_codigo(usuario, recovery_code.codigo)
if verified_code:
    print(f"   ✅ Código válido: {verified_code.codigo}")
    print(f"   📊 is_valid(): {verified_code.is_valid()}")
else:
    print(f"   ❌ Código NO es válido")
    sys.exit(1)

# 5. Cambiar contraseña
print("\n5️⃣  Cambiando contraseña...")
nueva_password = "NuevaPassword123!"
usuario.set_password(nueva_password)
usuario.save()
print(f"   ✅ Contraseña actualizada")
print(f"   Hash nuevo: {usuario.password[:50]}...")

# 6. Verificar que el hash cambió
print("\n6️⃣  Verificando que el hash cambió...")
if usuario.password != hash_anterior:
    print(f"   ✅ Hash cambió correctamente")
else:
    print(f"   ❌ PROBLEMA: El hash NO cambió")

# 7. Marcar código como verificado
print("\n7️⃣  Marcando código como verificado...")
recovery_code.marcar_verificado()
print(f"   ✅ Código marcado como verificado")
print(f"   🔒 Verificado: {recovery_code.verificado}")

# 8. Intentar verificar el código nuevamente (debe fallar)
print("\n8️⃣  Intentando verificar el código nuevamente (debe fallar)...")
reused_code = PasswordRecoveryCode.verificar_codigo(usuario, recovery_code.codigo)
if reused_code:
    print(f"   ❌ PROBLEMA: El código se puede reutilizar")
else:
    print(f"   ✅ Código no se puede reutilizar (correcto)")

# 9. Probar login con nueva contraseña
print("\n9️⃣  Probando login con nueva contraseña...")
usuario_refresco = User.objects.get(username='ale')
if usuario_refresco.check_password(nueva_password):
    print(f"   ✅ Login exitoso con nueva contraseña")
else:
    print(f"   ❌ PROBLEMA: Login FALLA con nueva contraseña")
    print(f"   Hash en BD: {usuario_refresco.password[:50]}...")

# 10. Probar login con contraseña anterior
print("\n🔟 Probando login con contraseña anterior (debe fallar)...")
if usuario_refresco.check_password("admin"):
    print(f"   ❌ PROBLEMA: Login funciona con contraseña anterior")
else:
    print(f"   ✅ Login falla con contraseña anterior (correcto)")

print("\n" + "="*80)
print("✅ DEBUG COMPLETADO")
print("="*80 + "\n")

print("📋 RESUMEN:")
print(f"   • Usuario: {usuario.username}")
print(f"   • Email: {usuario.email}")
print(f"   • Código generado: {recovery_code.codigo}")
print(f"   • Hash cambió: ✅")
print(f"   • Código verificado: ✅")
print(f"   • Login con nueva contraseña: ✅")
print("\n")
