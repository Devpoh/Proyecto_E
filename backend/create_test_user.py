#!/usr/bin/env python
"""
Script para crear un usuario de prueba en Django
Ejecutar desde: python manage.py shell < create_test_user.py
O: python create_test_user.py (si se ejecuta como script independiente)
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import UserProfile

def create_test_user():
    """Crear usuario de prueba"""
    
    username = 'test_user'
    email = 'test@example.com'
    password = 'TestPassword123'
    
    print("=" * 60)
    print("CREAR USUARIO DE PRUEBA")
    print("=" * 60)
    
    # Verificar si el usuario ya existe
    if User.objects.filter(username=username).exists():
        print(f"✓ Usuario '{username}' ya existe")
        user = User.objects.get(username=username)
        print(f"  Email: {user.email}")
        print(f"  Rol: {user.profile.rol if hasattr(user, 'profile') else 'cliente'}")
        return user
    
    # Crear usuario
    print(f"\nCreando usuario: {username}")
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name='Test',
        last_name='User'
    )
    
    print(f"✓ Usuario creado exitosamente")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Nombre: {user.first_name} {user.last_name}")
    
    # Verificar perfil
    if hasattr(user, 'profile'):
        print(f"  Rol: {user.profile.rol}")
    
    return user

def create_admin_user():
    """Crear usuario admin de prueba"""
    
    username = 'admin_test'
    email = 'admin_test@example.com'
    password = 'AdminPassword123'
    
    print("\n" + "=" * 60)
    print("CREAR USUARIO ADMIN DE PRUEBA")
    print("=" * 60)
    
    # Verificar si el usuario ya existe
    if User.objects.filter(username=username).exists():
        print(f"✓ Usuario '{username}' ya existe")
        user = User.objects.get(username=username)
        print(f"  Email: {user.email}")
        print(f"  Es superusuario: {user.is_superuser}")
        return user
    
    # Crear usuario admin
    print(f"\nCreando usuario admin: {username}")
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    
    print(f"✓ Usuario admin creado exitosamente")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Es superusuario: {user.is_superuser}")
    
    return user

def main():
    """Crear usuarios de prueba"""
    
    print("\n")
    
    # Crear usuario regular
    test_user = create_test_user()
    
    # Crear usuario admin
    admin_user = create_admin_user()
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print("\nUsuarios creados:")
    print(f"\n1. Usuario Regular:")
    print(f"   Username: test_user")
    print(f"   Password: TestPassword123")
    print(f"   Email: test@example.com")
    
    print(f"\n2. Usuario Admin:")
    print(f"   Username: admin_test")
    print(f"   Password: AdminPassword123")
    print(f"   Email: admin_test@example.com")
    
    print(f"\n3. Panel de Admin:")
    print(f"   URL: http://localhost:8000/admin/")
    print(f"   Username: admin_test")
    print(f"   Password: AdminPassword123")
    
    print(f"\nPuedes usar cualquiera de estos usuarios para probar la API")
    print(f"Ejecuta: python test_api.py")
    print("\n")

if __name__ == '__main__':
    main()
