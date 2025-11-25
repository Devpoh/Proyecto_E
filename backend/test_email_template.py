#!/usr/bin/env python
"""
Script para verificar que el template de email se renderiza correctamente
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.template.loader import render_to_string

# Contexto de prueba
context = {
    'nombre': 'Test User',
    'codigo': '123456',
    'username': 'testuser',
}

# Renderizar template
html_content = render_to_string('emails/verificacion_email.html', context)

# Imprimir resultado
print("=" * 80)
print("TEMPLATE RENDERIZADO:")
print("=" * 80)
print(html_content)
print("=" * 80)

# Verificar que contiene los textos correctos
checks = [
    ('🌴', 'Palma emoji'),
    ('Electronica Isla', 'Nombre correcto'),
    ('5 minutos', 'Tiempo correcto'),
    ('123456', 'Código'),
]

print("\nVERIFICACIONES:")
print("-" * 80)
for text, description in checks:
    if text in html_content:
        print(f"✅ {description}: '{text}' encontrado")
    else:
        print(f"❌ {description}: '{text}' NO encontrado")

print("-" * 80)
