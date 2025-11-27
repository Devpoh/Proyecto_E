#!/usr/bin/env python
"""
Script para testear el filtro de roles en usuarios
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

django.setup()

from django.test import Client
from django.contrib.auth.models import User
from api.models import UserProfile
import json

# Crear cliente de test
client = Client()

# Crear usuario admin para autenticarse
admin = User.objects.create_user(username='admin_test', password='admin123', is_staff=True, is_superuser=True)
admin_profile = UserProfile.objects.create(user=admin, rol='admin')

# Crear usuarios de prueba con diferentes roles
cliente = User.objects.create_user(username='cliente_test', password='pass123', first_name='Cliente')
cliente_profile = UserProfile.objects.create(user=cliente, rol='cliente')

mensajero = User.objects.create_user(username='mensajero_test', password='pass123', first_name='Mensajero')
mensajero_profile = UserProfile.objects.create(user=mensajero, rol='mensajero')

trabajador = User.objects.create_user(username='trabajador_test', password='pass123', first_name='Trabajador')
trabajador_profile = UserProfile.objects.create(user=trabajador, rol='trabajador')

# Autenticarse
client.force_login(admin)

print("✅ Usuarios de prueba creados")
print(f"  - Admin: {admin.username}")
print(f"  - Cliente: {cliente.username}")
print(f"  - Mensajero: {mensajero.username}")
print(f"  - Trabajador: {trabajador.username}")

# Test 1: Obtener todos los usuarios (sin filtro)
print("\n📋 Test 1: Obtener todos los usuarios (sin filtro)")
response = client.get('/api/admin/users/')
data = response.json()
print(f"  Status: {response.status_code}")
print(f"  Total usuarios: {len(data.get('results', []))}")

# Test 2: Filtrar por rol "cliente"
print("\n📋 Test 2: Filtrar por rol 'cliente'")
response = client.get('/api/admin/users/?rol=cliente')
data = response.json()
print(f"  Status: {response.status_code}")
usuarios = data.get('results', [])
print(f"  Usuarios encontrados: {len(usuarios)}")
for u in usuarios:
    print(f"    - {u['username']} (rol: {u.get('profile', {}).get('rol', 'N/A')})")

# Test 3: Filtrar por rol "mensajero"
print("\n📋 Test 3: Filtrar por rol 'mensajero'")
response = client.get('/api/admin/users/?rol=mensajero')
data = response.json()
print(f"  Status: {response.status_code}")
usuarios = data.get('results', [])
print(f"  Usuarios encontrados: {len(usuarios)}")
for u in usuarios:
    print(f"    - {u['username']} (rol: {u.get('profile', {}).get('rol', 'N/A')})")

# Test 4: Filtrar por rol "trabajador"
print("\n📋 Test 4: Filtrar por rol 'trabajador'")
response = client.get('/api/admin/users/?rol=trabajador')
data = response.json()
print(f"  Status: {response.status_code}")
usuarios = data.get('results', [])
print(f"  Usuarios encontrados: {len(usuarios)}")
for u in usuarios:
    print(f"    - {u['username']} (rol: {u.get('profile', {}).get('rol', 'N/A')})")

# Test 5: Filtrar por rol "admin"
print("\n📋 Test 5: Filtrar por rol 'admin'")
response = client.get('/api/admin/users/?rol=admin')
data = response.json()
print(f"  Status: {response.status_code}")
usuarios = data.get('results', [])
print(f"  Usuarios encontrados: {len(usuarios)}")
for u in usuarios:
    print(f"    - {u['username']} (rol: {u.get('profile', {}).get('rol', 'N/A')})")

# Test 6: Filtrar por rol inválido
print("\n📋 Test 6: Filtrar por rol inválido")
response = client.get('/api/admin/users/?rol=superadmin')
print(f"  Status: {response.status_code}")
print(f"  Error: {response.json().get('error', 'N/A')}")

print("\n✅ Tests completados")

# Limpiar
admin.delete()
cliente.delete()
mensajero.delete()
trabajador.delete()
