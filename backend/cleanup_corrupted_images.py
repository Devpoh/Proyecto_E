#!/usr/bin/env python
"""
Script para limpiar imágenes base64 corrupta o demasiado grandes
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Producto

# Encontrar productos con imágenes demasiado grandes
print("🔍 Buscando productos con imágenes corrupta...")
productos_corrupto = Producto.objects.filter(imagen_url__isnull=False)

count = 0
for producto in productos_corrupto:
    if producto.imagen_url and len(producto.imagen_url) > 100000:
        print(f"\n🔴 Producto ID {producto.id}: {producto.nombre}")
        print(f"   Tamaño imagen: {len(producto.imagen_url):,} caracteres")
        print(f"   Acción: Eliminando imagen...")
        
        # Opción 1: Eliminar la imagen
        producto.imagen_url = None
        producto.save()
        count += 1
        print(f"   ✅ Imagen eliminada")

print(f"\n✅ Total de productos limpiados: {count}")

# Verificar que quedó bien
print("\n🔍 Verificando productos después de limpieza...")
for producto in Producto.objects.all()[:5]:
    img_size = len(producto.imagen_url) if producto.imagen_url else 0
    print(f"   Producto {producto.id}: {img_size:,} caracteres")

print("\n✅ Limpieza completada")
