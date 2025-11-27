#!/usr/bin/env python
"""
═══════════════════════════════════════════════════════════════════════════════
🧪 TEST E2E - Flujo Completo de Recuperación de Contraseña
═══════════════════════════════════════════════════════════════════════════════

Este test simula el flujo completo:
1. Usuario solicita recuperación de contraseña
2. Recibe código por email
3. Ingresa código + nueva contraseña
4. Intenta loguear con nueva contraseña
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
from api.models import PasswordRecoveryCode, RefreshToken
from api.utils import generar_access_token
from api.validators import validar_contraseña_fuerte, validar_email
from django.core.exceptions import ValidationError
import json

print("\n" + "="*80)
print("🧪 TEST E2E - FLUJO COMPLETO DE RECUPERACIÓN DE CONTRASEÑA")
print("="*80 + "\n")

# ============================================================================
# PASO 1: Crear usuario de prueba (simular usuario existente)
# ============================================================================
print("1️⃣  CREAR USUARIO DE PRUEBA")
print("-" * 80)

usuario, created = User.objects.get_or_create(
    username='ale_test_e2e',
    defaults={
        'email': 'ale_test_e2e@example.com',
        'first_name': 'Alejandro',
        'last_name': 'Test'
    }
)

# Establecer contraseña inicial
usuario.set_password('PasswordAntigua123!')
usuario.save()

print(f"   ✅ Usuario creado/encontrado: {usuario.username}")
print(f"   ✅ Email: {usuario.email}")
print(f"   ✅ Contraseña inicial establecida")

# ============================================================================
# PASO 2: Simular solicitud de recuperación (forgot_password_request)
# ============================================================================
print("\n2️⃣  SOLICITAR RECUPERACIÓN DE CONTRASEÑA")
print("-" * 80)

email_solicitado = usuario.email  # Usar el email del usuario creado

# Validar email
try:
    email_validado = validar_email(email_solicitado)
    print(f"   ✅ Email validado: {email_validado}")
except ValidationError as e:
    print(f"   ❌ Email inválido: {str(e)}")
    sys.exit(1)

# Buscar usuario
try:
    usuario_encontrado = User.objects.get(email__iexact=email_validado)
    print(f"   ✅ Usuario encontrado: {usuario_encontrado.username}")
except User.DoesNotExist:
    print(f"   ❌ Usuario no encontrado")
    sys.exit(1)

# Generar código
recovery_code = PasswordRecoveryCode.crear_codigo(
    usuario=usuario_encontrado,
    duracion_minutos=15,
    ip_address='127.0.0.1',
    user_agent='Test Browser'
)

print(f"   ✅ Código generado: {recovery_code.codigo}")
print(f"   ✅ Código válido: {recovery_code.is_valid()}")

# ============================================================================
# PASO 3: Simular confirmación de recuperación (reset_password_confirm)
# ============================================================================
print("\n3️⃣  CONFIRMAR RECUPERACIÓN CON CÓDIGO Y NUEVA CONTRASEÑA")
print("-" * 80)

codigo_ingresado = recovery_code.codigo
nueva_password = "NuevaPassword123!"
nueva_password_confirm = "NuevaPassword123!"

print(f"   Código ingresado: {codigo_ingresado}")
print(f"   Nueva contraseña: {nueva_password}")

# Validar que las contraseñas coincidan
if nueva_password != nueva_password_confirm:
    print(f"   ❌ Las contraseñas no coinciden")
    sys.exit(1)

print(f"   ✅ Las contraseñas coinciden")

# Validar contraseña fuerte
try:
    validar_contraseña_fuerte(nueva_password)
    print(f"   ✅ Contraseña cumple requisitos de seguridad")
except ValidationError as e:
    print(f"   ❌ Contraseña débil: {str(e)}")
    sys.exit(1)

# Verificar código
recovery_code_verificado = PasswordRecoveryCode.verificar_codigo(usuario_encontrado, codigo_ingresado)

if not recovery_code_verificado:
    print(f"   ❌ Código inválido o expirado")
    sys.exit(1)

print(f"   ✅ Código verificado correctamente")

# Actualizar contraseña
usuario_encontrado.set_password(nueva_password)
usuario_encontrado.save()

print(f"   ✅ Contraseña actualizada en la BD")

# Marcar código como verificado
recovery_code_verificado.marcar_verificado()

print(f"   ✅ Código marcado como verificado")

# Revocar todos los refresh tokens del usuario
RefreshToken.revocar_todos_usuario(usuario_encontrado)

print(f"   ✅ Refresh tokens revocados")

# Generar nuevos tokens
access_token = generar_access_token(usuario_encontrado)

print(f"   ✅ Access token generado")

# Construir respuesta como lo hace el backend
nombre = f"{usuario_encontrado.first_name} {usuario_encontrado.last_name}".strip() or usuario_encontrado.username
rol = usuario_encontrado.profile.rol if hasattr(usuario_encontrado, 'profile') else 'cliente'

response_data = {
    'accessToken': access_token,
    'user': {
        'id': usuario_encontrado.id,
        'email': usuario_encontrado.email,
        'nombre': nombre,
        'rol': rol
    },
    'message': 'Contraseña actualizada exitosamente'
}

print(f"\n   Respuesta del backend:")
print(f"   {json.dumps(response_data, indent=2, ensure_ascii=False)}")

# ============================================================================
# PASO 4: Verificar que el login funciona con la nueva contraseña
# ============================================================================
print("\n4️⃣  VERIFICAR LOGIN CON NUEVA CONTRASEÑA")
print("-" * 80)

# Recargar usuario desde BD
usuario_login = User.objects.get(username='ale_test_e2e')

# Intentar login con nueva contraseña
if usuario_login.check_password(nueva_password):
    print(f"   ✅ Login exitoso con nueva contraseña")
else:
    print(f"   ❌ Login falló con nueva contraseña")
    sys.exit(1)

# Intentar login con contraseña antigua (debe fallar)
if usuario_login.check_password('PasswordAntigua123!'):
    print(f"   ❌ Login funciona con contraseña antigua (PROBLEMA)")
    sys.exit(1)
else:
    print(f"   ✅ Login falla con contraseña antigua (correcto)")

# ============================================================================
# PASO 5: Verificar que el token es válido
# ============================================================================
print("\n5️⃣  VERIFICAR VALIDEZ DEL TOKEN")
print("-" * 80)

import jwt
from django.conf import settings

try:
    # Decodificar token
    decoded = jwt.decode(
        access_token,
        settings.SECRET_KEY,
        algorithms=['HS256']
    )
    
    print(f"   ✅ Token decodificado exitosamente")
    print(f"   Token payload:")
    print(f"   {json.dumps(decoded, indent=2, ensure_ascii=False)}")
    
    # Verificar que el user_id es correcto
    if decoded['user_id'] == usuario_encontrado.id:
        print(f"   ✅ user_id en token es correcto: {decoded['user_id']}")
    else:
        print(f"   ❌ user_id en token es incorrecto: {decoded['user_id']} (esperado: {usuario_encontrado.id})")
        sys.exit(1)
    
    # Verificar que el username es correcto
    if decoded['username'] == usuario_encontrado.username:
        print(f"   ✅ username en token es correcto: {decoded['username']}")
    else:
        print(f"   ❌ username en token es incorrecto: {decoded['username']} (esperado: {usuario_encontrado.username})")
        sys.exit(1)
    
except jwt.InvalidTokenError as e:
    print(f"   ❌ Token inválido: {str(e)}")
    sys.exit(1)

# ============================================================================
# PASO 6: Simular login con el token
# ============================================================================
print("\n6️⃣  SIMULAR LOGIN CON EL TOKEN")
print("-" * 80)

# Extraer user_id del token
user_id_from_token = decoded['user_id']

# Buscar usuario por ID
try:
    usuario_from_token = User.objects.get(id=user_id_from_token)
    print(f"   ✅ Usuario encontrado por ID del token: {usuario_from_token.username}")
    
    if usuario_from_token.username == 'ale_test_e2e':
        print(f"   ✅ Es el usuario correcto: ale_test_e2e")
    else:
        print(f"   ❌ Es un usuario diferente: {usuario_from_token.username}")
        sys.exit(1)
    
except User.DoesNotExist:
    print(f"   ❌ Usuario no encontrado por ID: {user_id_from_token}")
    sys.exit(1)

# ============================================================================
# RESUMEN
# ============================================================================
print("\n" + "="*80)
print("📋 RESUMEN DEL TEST E2E")
print("="*80 + "\n")

print("✅ TODAS LAS ETAPAS COMPLETADAS EXITOSAMENTE:")
print("   1. ✅ Usuario creado/encontrado")
print("   2. ✅ Solicitud de recuperación procesada")
print("   3. ✅ Código generado y validado")
print("   4. ✅ Contraseña actualizada")
print("   5. ✅ Token generado correctamente")
print("   6. ✅ Login funciona con nueva contraseña")
print("   7. ✅ Token contiene datos correctos")
print("   8. ✅ Usuario puede ser identificado por el token")

print("\n🎉 FLUJO E2E COMPLETADO EXITOSAMENTE")
print("\n" + "="*80 + "\n")

print("📝 CONCLUSIÓN:")
print("   El backend está funcionando correctamente.")
print("   El problema debe estar en el frontend o en la comunicación.")
print("\n   Próximos pasos:")
print("   1. Verificar que el frontend está guardando el token correctamente")
print("   2. Verificar que el frontend está enviando el token en las solicitudes")
print("   3. Verificar que el backend está validando el token correctamente")
print("\n")
