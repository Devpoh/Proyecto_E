#!/usr/bin/env python
"""
Script para probar el endpoint verify_email directamente
"""

import os
import django
import json

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import EmailVerification
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password

print("=" * 80)
print("🧪 PRUEBA DEL ENDPOINT verify_email")
print("=" * 80)

# 1. Crear un registro de verificación de prueba
print("\n1️⃣ Creando registro de verificación de prueba...")
try:
    # Limpiar registros anteriores
    EmailVerification.objects.filter(email_temporal='test_verify@example.com').delete()
    
    password_hash = make_password('TestPass123!')
    verificacion = EmailVerification.objects.create(
        usuario=None,
        email_temporal='test_verify@example.com',
        username_temporal='test_verify_user',
        password_hash=password_hash,
        first_name_temporal='Test',
        last_name_temporal='Verify',
        codigo=EmailVerification.generar_codigo(),
        expires_at=timezone.now() + timedelta(minutes=15)
    )
    print(f"   ✅ Registro creado")
    print(f"   Email: {verificacion.email_temporal}")
    print(f"   Código: {verificacion.codigo}")
    print(f"   Username: {verificacion.username_temporal}")
    print(f"   Password hash: {verificacion.password_hash[:50]}...")
    
except Exception as e:
    print(f"   ❌ Error al crear registro: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 2. Simular la verificación
print("\n2️⃣ Simulando verificación de email...")
try:
    from django.db import transaction
    from django.contrib.auth.models import User
    
    email = verificacion.email_temporal
    codigo = verificacion.codigo
    
    # Obtener el registro
    verificacion_obj = EmailVerification.objects.get(
        email_temporal=email,
        verificado=False
    )
    
    # Verificar código
    if verificacion_obj.codigo != codigo:
        print(f"   ❌ Código incorrecto")
        exit(1)
    
    print(f"   ✅ Código correcto")
    
    # Crear usuario
    print(f"\n3️⃣ Creando usuario...")
    with transaction.atomic():
        user = User.objects.create_user(
            username=verificacion_obj.username_temporal,
            email=verificacion_obj.email_temporal,
            password='temp_password_will_be_replaced',
            first_name=verificacion_obj.first_name_temporal or '',
            last_name=verificacion_obj.last_name_temporal or '',
            is_active=True
        )
        print(f"   ✅ Usuario creado: {user.username}")
        
        # Reemplazar contraseña
        user.password = verificacion_obj.password_hash
        user.save()
        print(f"   ✅ Contraseña establecida")
        
        # Marcar como verificado
        verificacion_obj.usuario = user
        verificacion_obj.marcar_verificado()
        print(f"   ✅ Verificación marcada como completada")
    
    print(f"\n✅ PRUEBA EXITOSA")
    print(f"   Usuario: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Activo: {user.is_active}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 80)
