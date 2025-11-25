#!/usr/bin/env python
"""
Script para reiniciar Celery y limpiar caché
"""

import os
import sys
import shutil
import subprocess

print("=" * 80)
print("🔄 REINICIANDO CELERY Y LIMPIANDO CACHÉ")
print("=" * 80)

# 1. Limpiar __pycache__ recursivamente
print("\n1️⃣ Limpiando __pycache__...")
for root, dirs, files in os.walk('.'):
    if '__pycache__' in dirs:
        pycache_path = os.path.join(root, '__pycache__')
        try:
            shutil.rmtree(pycache_path)
            print(f"   ✅ Eliminado: {pycache_path}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

# 2. Limpiar archivos .pyc
print("\n2️⃣ Limpiando archivos .pyc...")
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.pyc'):
            pyc_path = os.path.join(root, file)
            try:
                os.remove(pyc_path)
                print(f"   ✅ Eliminado: {pyc_path}")
            except Exception as e:
                print(f"   ❌ Error: {e}")

# 3. Limpiar .pytest_cache
print("\n3️⃣ Limpiando .pytest_cache...")
if os.path.exists('.pytest_cache'):
    try:
        shutil.rmtree('.pytest_cache')
        print("   ✅ Eliminado: .pytest_cache")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print("✅ CACHÉ LIMPIADO")
print("=" * 80)
print("\n📝 PRÓXIMOS PASOS:")
print("1. Detén Celery (Ctrl+C si está corriendo)")
print("2. Ejecuta: celery -A config worker -l info")
print("3. Prueba a registrarte nuevamente")
print("\n" + "=" * 80)
