#!/usr/bin/env python
"""
Script para debuggear qué retorna cada endpoint
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from api.views import productos_carrusel
from api.serializers import ProductoSerializer
from api.models import Producto

# Crear un request fake
factory = RequestFactory()
request = factory.get('/api/carrusel/')

print("=" * 80)
print("🔍 DEBUG - COMPARACIÓN DE ENDPOINTS")
print("=" * 80)

# Obtener productos
productos = Producto.objects.filter(en_carrusel=True, activo=True).order_by('-created_at')[:3]

print(f"\n📊 Total de productos en carrusel: {Producto.objects.filter(en_carrusel=True, activo=True).count()}")
print(f"📊 Primeros 3 productos:")

for p in productos:
    print(f"\n{'─' * 80}")
    print(f"ID: {p.id} | Nombre: {p.nombre}")
    print(f"  - imagen (ImageField): {p.imagen}")
    print(f"  - imagen.name: {p.imagen.name if p.imagen else 'None'}")
    print(f"  - imagen.url: {p.imagen.url if p.imagen else 'None'}")
    print(f"  - imagen_url (TextField): {p.imagen_url[:50] if p.imagen_url else 'None'}...")
    
    # Serializar con request
    serializer = ProductoSerializer(p, context={'request': request})
    print(f"\n  📤 SERIALIZADO (con request):")
    print(f"     imagen_url: {serializer.data.get('imagen_url')}")
    
    # Serializar sin request
    serializer_no_request = ProductoSerializer(p, context={})
    print(f"\n  📤 SERIALIZADO (sin request):")
    print(f"     imagen_url: {serializer_no_request.data.get('imagen_url')}")

print(f"\n{'=' * 80}")
print("✅ DEBUG COMPLETADO")
print("=" * 80)
