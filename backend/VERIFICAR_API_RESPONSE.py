#!/usr/bin/env python
"""
═══════════════════════════════════════════════════════════════════════════════
🔍 SCRIPT DE VERIFICACIÓN - Respuesta HTTP de la API
═══════════════════════════════════════════════════════════════════════════════

Este script verifica que la API retorna imagen_url correctamente en las respuestas HTTP.

Uso:
    cd backend
    python manage.py shell < VERIFICAR_API_RESPONSE.py
"""

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Producto
from rest_framework.test import APIRequestFactory
from api.views import ProductoViewSet
from api.views_admin import ProductoManagementViewSet

print("\n" + "="*80)
print("🔍 VERIFICACIÓN DE RESPUESTAS HTTP DE LA API")
print("="*80 + "\n")

# Obtener un producto de ejemplo
producto = Producto.objects.first()

if not producto:
    print("❌ No hay productos en la base de datos")
    print("   Crea un producto primero\n")
    exit(1)

print(f"📦 Producto seleccionado: {producto.nombre} (ID: {producto.id})\n")

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 1: ProductoViewSet (Lectura pública)
# ═══════════════════════════════════════════════════════════════════════════════

print("─" * 80)
print("TEST 1: ProductoViewSet - GET /api/productos/{id}/")
print("─" * 80 + "\n")

factory = APIRequestFactory()
view = ProductoViewSet.as_view({'get': 'retrieve'})
request = factory.get(f'/api/productos/{producto.id}/')
response = view(request, pk=producto.id)

print("📊 Respuesta HTTP:")
print(f"   Status Code: {response.status_code}")

if response.status_code == 200:
    response.render()
    data = json.loads(response.content)
    
    print("\n✅ Datos del producto:")
    producto_data = data.get('producto', {})
    
    # Mostrar campos importantes
    for key in ['id', 'nombre', 'precio', 'imagen_url', 'imagen', 'stock']:
        if key in producto_data:
            value = producto_data[key]
            if key == 'imagen_url':
                print(f"   🖼️  {key}: {value[:60] if value else 'None'}...")
            elif key == 'imagen':
                print(f"   🖼️  {key}: {value[:60] if value else 'None'}...")
            else:
                print(f"   • {key}: {value}")
    
    print("\n📋 Verificación:")
    if 'imagen_url' in producto_data:
        print("   ✅ Campo 'imagen_url' presente en respuesta")
        if producto_data['imagen_url']:
            print(f"   ✅ 'imagen_url' tiene valor")
        else:
            print("   ⚠️  'imagen_url' está vacío (None)")
    else:
        print("   ❌ Campo 'imagen_url' NO está en respuesta")
else:
    print(f"   ❌ Error: {response.status_code}")

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 2: ProductoViewSet - GET /api/productos/ (lista)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "─" * 80)
print("TEST 2: ProductoViewSet - GET /api/productos/ (lista)")
print("─" * 80 + "\n")

view = ProductoViewSet.as_view({'get': 'list'})
request = factory.get('/api/productos/')
response = view(request)

print("📊 Respuesta HTTP:")
print(f"   Status Code: {response.status_code}")

if response.status_code == 200:
    response.render()
    data = json.loads(response.content)
    
    if isinstance(data, list) and len(data) > 0:
        print(f"\n✅ Productos en lista: {len(data)}")
        
        # Verificar el primer producto
        first_product = data[0]
        print(f"\n   Primer producto: {first_product.get('nombre', 'N/A')}")
        
        if 'imagen_url' in first_product:
            print("   ✅ Campo 'imagen_url' presente")
            if first_product['imagen_url']:
                print(f"   ✅ 'imagen_url' tiene valor: {first_product['imagen_url'][:50]}...")
            else:
                print("   ⚠️  'imagen_url' está vacío")
        else:
            print("   ❌ Campo 'imagen_url' NO está presente")
    else:
        print("   ⚠️  No hay productos en la lista")
else:
    print(f"   ❌ Error: {response.status_code}")

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 3: ProductoManagementViewSet (Admin)
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "─" * 80)
print("TEST 3: ProductoManagementViewSet - GET /admin/productos/{id}/")
print("─" * 80 + "\n")

view = ProductoManagementViewSet.as_view({'get': 'retrieve'})
request = factory.get(f'/admin/productos/{producto.id}/')

# Simular usuario admin
from django.contrib.auth.models import User
from api.models import UserProfile

admin_user = User.objects.filter(is_staff=True).first()
if not admin_user:
    print("⚠️  No hay usuario admin para probar")
else:
    request.user = admin_user
    response = view(request, pk=producto.id)
    
    print("📊 Respuesta HTTP:")
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        response.render()
        data = json.loads(response.content)
        
        print("\n✅ Datos del producto (Admin):")
        
        # Mostrar campos importantes
        for key in ['id', 'nombre', 'precio', 'imagen_url', 'imagen', 'stock']:
            if key in data:
                value = data[key]
                if key in ['imagen_url', 'imagen']:
                    print(f"   🖼️  {key}: {value[:60] if value else 'None'}...")
                else:
                    print(f"   • {key}: {value}")
        
        print("\n📋 Verificación:")
        if 'imagen_url' in data:
            print("   ✅ Campo 'imagen_url' presente en respuesta admin")
            if data['imagen_url']:
                print(f"   ✅ 'imagen_url' tiene valor")
            else:
                print("   ⚠️  'imagen_url' está vacío (None)")
        else:
            print("   ❌ Campo 'imagen_url' NO está en respuesta admin")
        
        if 'imagen' in data:
            print("   ✅ Campo 'imagen' presente (para escritura)")
        else:
            print("   ⚠️  Campo 'imagen' NO está presente")
    else:
        print(f"   ❌ Error: {response.status_code}")

# ═══════════════════════════════════════════════════════════════════════════════
# RESUMEN
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "="*80)
print("✅ RESUMEN")
print("="*80 + "\n")

print("Para verificar manualmente desde el navegador:")
print(f"   1. GET http://localhost:8000/api/productos/{producto.id}/")
print(f"      → Busca el campo 'imagen_url' en la respuesta JSON")
print(f"\n   2. GET http://localhost:8000/api/productos/")
print(f"      → Busca 'imagen_url' en cada producto de la lista")
print(f"\n   3. GET http://localhost:8000/admin/productos/{producto.id}/")
print(f"      → Busca 'imagen_url' e 'imagen' en la respuesta JSON")

print("\n" + "="*80 + "\n")
