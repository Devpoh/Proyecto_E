#!/usr/bin/env python
"""
═══════════════════════════════════════════════════════════════════════════════
🧹 SCRIPT - Limpiar Usuarios Duplicados
═══════════════════════════════════════════════════════════════════════════════

Este script identifica y limpia usuarios duplicados con el mismo email.
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
from collections import defaultdict

print("\n" + "="*80)
print("🧹 LIMPIAR USUARIOS DUPLICADOS")
print("="*80 + "\n")

# ============================================================================
# PASO 1: Encontrar usuarios duplicados
# ============================================================================
print("1️⃣  BUSCAR USUARIOS DUPLICADOS")
print("-" * 80)

# Agrupar usuarios por email
usuarios_por_email = defaultdict(list)

for usuario in User.objects.all():
    usuarios_por_email[usuario.email].append(usuario)

# Encontrar duplicados
duplicados = {email: usuarios for email, usuarios in usuarios_por_email.items() if len(usuarios) > 1}

if not duplicados:
    print("   ✅ No hay usuarios duplicados")
else:
    print(f"   ⚠️  Encontrados {len(duplicados)} emails con múltiples usuarios:\n")
    
    for email, usuarios in duplicados.items():
        print(f"   📧 Email: {email}")
        for usuario in usuarios:
            print(f"      - ID: {usuario.id}, Username: {usuario.username}, Nombre: {usuario.first_name} {usuario.last_name}")
        print()

# ============================================================================
# PASO 2: Mostrar opciones
# ============================================================================
print("2️⃣  OPCIONES")
print("-" * 80)

if not duplicados:
    print("   ✅ No hay nada que limpiar")
    sys.exit(0)

print("   Opciones:")
print("   1. Eliminar usuarios duplicados (mantener el más antiguo)")
print("   2. Mostrar detalles de cada usuario")
print("   3. Salir sin hacer cambios")
print()

# ============================================================================
# PASO 3: Ejecutar acción
# ============================================================================
print("3️⃣  EJECUTAR ACCIÓN")
print("-" * 80)

# Para este script, vamos a eliminar automáticamente los duplicados más nuevos
print("   Eliminando usuarios duplicados (manteniéndose el más antiguo)...\n")

usuarios_eliminados = 0

for email, usuarios in duplicados.items():
    # Ordenar por fecha de creación (más antiguo primero)
    usuarios_ordenados = sorted(usuarios, key=lambda u: u.id)
    
    # Mantener el primero, eliminar los demás
    usuario_a_mantener = usuarios_ordenados[0]
    usuarios_a_eliminar = usuarios_ordenados[1:]
    
    print(f"   📧 Email: {email}")
    print(f"      ✅ Mantener: ID {usuario_a_mantener.id} - {usuario_a_mantener.username}")
    
    for usuario in usuarios_a_eliminar:
        print(f"      ❌ Eliminar: ID {usuario.id} - {usuario.username}")
        usuario.delete()
        usuarios_eliminados += 1
    
    print()

print(f"   ✅ {usuarios_eliminados} usuario(s) eliminado(s)")

# ============================================================================
# PASO 4: Verificar resultado
# ============================================================================
print("\n4️⃣  VERIFICAR RESULTADO")
print("-" * 80)

# Agrupar usuarios nuevamente
usuarios_por_email = defaultdict(list)

for usuario in User.objects.all():
    usuarios_por_email[usuario.email].append(usuario)

# Encontrar duplicados
duplicados_nuevos = {email: usuarios for email, usuarios in usuarios_por_email.items() if len(usuarios) > 1}

if not duplicados_nuevos:
    print("   ✅ No hay usuarios duplicados")
else:
    print(f"   ⚠️  Aún hay {len(duplicados_nuevos)} emails con múltiples usuarios")

# ============================================================================
# PASO 5: Mostrar usuarios finales
# ============================================================================
print("\n5️⃣  USUARIOS FINALES")
print("-" * 80)

print(f"   Total de usuarios: {User.objects.count()}\n")

for usuario in User.objects.all():
    print(f"   ID: {usuario.id}")
    print(f"   Username: {usuario.username}")
    print(f"   Email: {usuario.email}")
    print(f"   Nombre: {usuario.first_name} {usuario.last_name}")
    print()

# ============================================================================
# RESUMEN
# ============================================================================
print("="*80)
print("✅ LIMPIEZA COMPLETADA")
print("="*80 + "\n")

print("📝 PRÓXIMOS PASOS:")
print("   1. Ejecutar test nuevamente: python test_e2e_reset_password.py")
print("   2. Verificar que el flujo funciona correctamente")
print("\n")
