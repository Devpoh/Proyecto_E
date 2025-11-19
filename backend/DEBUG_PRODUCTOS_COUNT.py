#!/usr/bin/env python
"""
Script para debuggear cuántos productos hay y cuántos están activos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Producto

print("=" * 80)
print("🔍 DEBUG - CONTEO DE PRODUCTOS")
print("=" * 80)

total = Producto.objects.count()
activos = Producto.objects.filter(activo=True).count()
inactivos = Producto.objects.filter(activo=False).count()
en_carrusel = Producto.objects.filter(en_carrusel=True, activo=True).count()

print(f"\n📊 ESTADÍSTICAS:")
print(f"  Total de productos: {total}")
print(f"  Productos activos: {activos}")
print(f"  Productos inactivos: {inactivos}")
print(f"  Productos en carrusel (activos): {en_carrusel}")

print(f"\n📋 LISTADO DE PRODUCTOS:")
for p in Producto.objects.all():
    estado = "✅ ACTIVO" if p.activo else "❌ INACTIVO"
    carrusel = "🎠 EN CARRUSEL" if p.en_carrusel else ""
    print(f"  ID {p.id}: {p.nombre} - {estado} {carrusel}")

print(f"\n{'=' * 80}")
