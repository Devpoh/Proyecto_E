#!/usr/bin/env python
"""
Script para actualizar stock_total de todos los productos existentes.
Ejecutar: python actualizar_stock.py
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Producto

print("🔄 Actualizando stock_total de todos los productos...")
print()

count = 0
for producto in Producto.objects.all():
    stock_anterior = producto.stock_total
    producto.stock_total = producto.stock
    producto.save()
    count += 1
    print(f"✓ {producto.nombre}: stock_total={producto.stock_total}")

print()
print(f"✅ {count} productos actualizados exitosamente")
print()

# Verificar
print("📊 Verificación:")
for producto in Producto.objects.all()[:3]:
    print(f"""
  {producto.nombre}:
    - stock_total: {producto.stock_total}
    - stock_reservado: {producto.stock_reservado}
    - stock_vendido: {producto.stock_vendido}
    - stock_disponible: {producto.stock_disponible}
    """)
