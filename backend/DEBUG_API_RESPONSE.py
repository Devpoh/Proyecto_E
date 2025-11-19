#!/usr/bin/env python
"""
Script para debuggear qué retorna el endpoint /productos/
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from api.views import ProductoViewSet
from rest_framework.request import Request

# Crear un request fake
factory = RequestFactory()
django_request = factory.get('/api/productos/')
request = Request(django_request)

# Crear el viewset
viewset = ProductoViewSet()
viewset.request = request
viewset.format_kwarg = None
viewset.action = 'list'

# Llamar al método list
response = viewset.list(request)

print("=" * 80)
print("🔍 DEBUG - RESPUESTA DEL ENDPOINT /productos/")
print("=" * 80)

print(f"\n📊 Status: {response.status_code}")
print(f"\n📋 Estructura de respuesta:")
print(json.dumps(response.data, indent=2, default=str)[:1000])

print(f"\n{'=' * 80}")
