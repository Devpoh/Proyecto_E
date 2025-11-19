#!/usr/bin/env python
"""Script para limpiar el cache de Redis/Django"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.cache import cache

print("Limpiando cache...")
cache.clear()
print("✅ Cache limpiado exitosamente")
