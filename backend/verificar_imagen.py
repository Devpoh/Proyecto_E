#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de verificacion - imagen_url en Serializers
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Producto
from api.serializers import ProductoSerializer
from api.serializers_admin import ProductoAdminSerializer
from rest_framework.test import APIRequestFactory

print("\n" + "="*80)
print("VERIFICACION DE imagen_url EN SERIALIZERS")
print("="*80 + "\n")

# Obtener un producto
producto = Producto.objects.first()

if not producto:
    print("ERROR: No hay productos en la base de datos")
    print("Crea un producto primero\n")
    sys.exit(1)

print(f"Producto: {producto.nombre} (ID: {producto.id})\n")

# TEST 1: ProductoSerializer
print("-" * 80)
print("TEST 1: ProductoSerializer (Lectura publica)")
print("-" * 80 + "\n")

factory = APIRequestFactory()
request = factory.get('/')

serializer = ProductoSerializer(producto, context={'request': request})
data = serializer.data

print("Campos retornados:")
if 'imagen_url' in data:
    print(f"  [OK] imagen_url: {data['imagen_url']}")
else:
    print(f"  [ERROR] imagen_url NO PRESENTE")

if 'id' in data:
    print(f"  [OK] id: {data['id']}")

if 'nombre' in data:
    print(f"  [OK] nombre: {data['nombre']}")

if 'precio' in data:
    print(f"  [OK] precio: {data['precio']}")

# TEST 2: ProductoAdminSerializer
print("\n" + "-" * 80)
print("TEST 2: ProductoAdminSerializer (Admin CRUD)")
print("-" * 80 + "\n")

admin_serializer = ProductoAdminSerializer(producto, context={'request': request})
admin_data = admin_serializer.data

print("Campos retornados:")
if 'imagen_url' in admin_data:
    print(f"  [OK] imagen_url: {admin_data['imagen_url']}")
else:
    print(f"  [ERROR] imagen_url NO PRESENTE")

if 'imagen' in admin_data:
    print(f"  [OK] imagen: {admin_data['imagen']}")
else:
    print(f"  [ERROR] imagen NO PRESENTE")

if 'id' in admin_data:
    print(f"  [OK] id: {admin_data['id']}")

if 'nombre' in admin_data:
    print(f"  [OK] nombre: {admin_data['nombre']}")

if 'precio' in admin_data:
    print(f"  [OK] precio: {admin_data['precio']}")

# RESUMEN
print("\n" + "="*80)
print("RESUMEN")
print("="*80 + "\n")

checks = {
    "ProductoSerializer retorna imagen_url": 'imagen_url' in data,
    "ProductoAdminSerializer retorna imagen_url": 'imagen_url' in admin_data,
    "ProductoAdminSerializer retorna imagen": 'imagen' in admin_data,
    "imagen_url tiene valor": bool(data.get('imagen_url') or admin_data.get('imagen_url')),
}

all_pass = True
for check, result in checks.items():
    status = "[OK]" if result else "[ERROR]"
    print(f"{status} {check}")
    if not result:
        all_pass = False

print("\n" + "="*80)
if all_pass:
    print("EXITO: TODO ESTA CORRECTO")
else:
    print("ERROR: HAY PROBLEMAS")
print("="*80 + "\n")
