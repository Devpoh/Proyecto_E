#!/usr/bin/env python
"""
═══════════════════════════════════════════════════════════════════════════════
🔍 SCRIPT DE VERIFICACIÓN - imagen_url en Serializers
═══════════════════════════════════════════════════════════════════════════════

Este script verifica que imagen_url se retorna correctamente en ambos serializers.

Uso:
    cd backend
    python manage.py shell < VERIFICAR_IMAGEN_URL.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Producto
from api.serializers import ProductoSerializer
from api.serializers_admin import ProductoAdminSerializer
from rest_framework.test import APIRequestFactory

print("\n" + "="*80)
print("🔍 VERIFICACIÓN DE imagen_url EN SERIALIZERS")
print("="*80 + "\n")

# Obtener un producto de ejemplo
producto = Producto.objects.first()

if not producto:
    print("❌ No hay productos en la base de datos")
    print("   Crea un producto primero\n")
    exit(1)

print(f"📦 Producto seleccionado: {producto.nombre} (ID: {producto.id})\n")

# Crear un request para el contexto
factory = APIRequestFactory()
request = factory.get('/')

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 1: ProductoSerializer
# ═══════════════════════════════════════════════════════════════════════════════

print("─" * 80)
print("TEST 1: ProductoSerializer (Lectura pública)")
print("─" * 80 + "\n")

serializer = ProductoSerializer(producto, context={'request': request})
data = serializer.data

print("✅ Campos retornados:")
for key in sorted(data.keys()):
    if key == 'imagen_url':
        print(f"   🖼️  {key}: {data[key]}")
    else:
        print(f"   • {key}: {data[key]}")

print("\n📋 Verificación:")
if 'imagen_url' in data:
    print("   ✅ Campo 'imagen_url' presente")
    if data['imagen_url']:
        print(f"   ✅ 'imagen_url' tiene valor: {data['imagen_url'][:50]}...")
        if data['imagen_url'].startswith('http'):
            print("   ✅ 'imagen_url' es una URL válida")
        elif data['imagen_url'].startswith('data:image'):
            print("   ✅ 'imagen_url' es Base64 legado")
        else:
            print("   ⚠️  'imagen_url' tiene formato desconocido")
    else:
        print("   ⚠️  'imagen_url' está vacío (None)")
else:
    print("   ❌ Campo 'imagen_url' NO está presente")

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 2: ProductoAdminSerializer
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "─" * 80)
print("TEST 2: ProductoAdminSerializer (Admin CRUD)")
print("─" * 80 + "\n")

admin_serializer = ProductoAdminSerializer(producto, context={'request': request})
admin_data = admin_serializer.data

print("✅ Campos retornados:")
for key in sorted(admin_data.keys()):
    if key == 'imagen_url':
        print(f"   🖼️  {key}: {admin_data[key]}")
    elif key == 'imagen':
        print(f"   🖼️  {key}: {admin_data[key]}")
    else:
        print(f"   • {key}: {admin_data[key]}")

print("\n📋 Verificación:")
if 'imagen_url' in admin_data:
    print("   ✅ Campo 'imagen_url' presente")
    if admin_data['imagen_url']:
        print(f"   ✅ 'imagen_url' tiene valor: {admin_data['imagen_url'][:50]}...")
        if admin_data['imagen_url'].startswith('http'):
            print("   ✅ 'imagen_url' es una URL válida")
        elif admin_data['imagen_url'].startswith('data:image'):
            print("   ✅ 'imagen_url' es Base64 legado")
        else:
            print("   ⚠️  'imagen_url' tiene formato desconocido")
    else:
        print("   ⚠️  'imagen_url' está vacío (None)")
else:
    print("   ❌ Campo 'imagen_url' NO está presente")

if 'imagen' in admin_data:
    print("   ✅ Campo 'imagen' presente (para escritura)")
else:
    print("   ⚠️  Campo 'imagen' NO está presente")

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 3: Comparación
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "─" * 80)
print("TEST 3: Comparación entre serializers")
print("─" * 80 + "\n")

print("📊 Comparación de imagen_url:")
print(f"   ProductoSerializer:      {data.get('imagen_url', 'NO PRESENTE')}")
print(f"   ProductoAdminSerializer: {admin_data.get('imagen_url', 'NO PRESENTE')}")

if data.get('imagen_url') == admin_data.get('imagen_url'):
    print("   ✅ AMBOS retornan el MISMO valor")
else:
    print("   ⚠️  DIFERENTES valores (puede ser normal si uno es None)")

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 4: Información del modelo
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "─" * 80)
print("TEST 4: Información del modelo")
print("─" * 80 + "\n")

print(f"📦 Producto: {producto.nombre}")
print(f"   • imagen (ImageField): {producto.imagen}")
print(f"   • imagen_url (TextField): {producto.imagen_url[:50] if producto.imagen_url else 'Vacío'}...")
print(f"   • stock_total: {producto.stock_total}")
print(f"   • stock_reservado: {producto.stock_reservado}")
print(f"   • stock_vendido: {producto.stock_vendido}")
print(f"   • stock (calculado): {producto.stock}")

# ═══════════════════════════════════════════════════════════════════════════════
# RESUMEN
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("✅ RESUMEN")
print("="*80 + "\n")

checks = {
    "ProductoSerializer retorna imagen_url": 'imagen_url' in data,
    "ProductoAdminSerializer retorna imagen_url": 'imagen_url' in admin_data,
    "ProductoAdminSerializer acepta imagen": 'imagen' in admin_data,
    "imagen_url tiene valor": bool(data.get('imagen_url') or admin_data.get('imagen_url')),
}

all_pass = True
for check, result in checks.items():
    status = "✅" if result else "❌"
    print(f"{status} {check}")
    if not result:
        all_pass = False

print("\n" + "="*80)
if all_pass:
    print("🎉 TODO ESTÁ CORRECTO - imagen_url se retorna en ambos serializers")
else:
    print("⚠️  HAY PROBLEMAS - Revisa los detalles arriba")
print("="*80 + "\n")
