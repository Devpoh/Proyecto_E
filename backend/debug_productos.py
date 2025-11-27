#!/usr/bin/env python
"""
Script para debuggear cuántos productos retorna la API
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from api.models import Producto

# Contar productos totales
total = Producto.objects.count()
print(f"✅ Total de productos en BD: {total}")

# Contar productos activos
activos = Producto.objects.filter(activo=True).count()
print(f"✅ Productos activos: {activos}")

# Contar productos en all_products
en_all = Producto.objects.filter(en_all_products=True).count()
print(f"✅ Productos con en_all_products=True: {en_all}")

# Contar productos en carrusel
en_carrusel = Producto.objects.filter(en_carrusel=True).count()
print(f"✅ Productos con en_carrusel=True: {en_carrusel}")

# Contar productos en all_products Y activos
en_all_activos = Producto.objects.filter(en_all_products=True, activo=True).count()
print(f"✅ Productos con en_all_products=True Y activo=True: {en_all_activos}")

# Listar los productos
print("\n📋 Productos con en_all_products=True:")
productos = Producto.objects.filter(en_all_products=True, activo=True).values('id', 'nombre', 'en_carrusel', 'en_all_products')
for p in productos:
    print(f"  - ID: {p['id']}, Nombre: {p['nombre']}, Carrusel: {p['en_carrusel']}, All: {p['en_all_products']}")
