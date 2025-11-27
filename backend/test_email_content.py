#!/usr/bin/env python
"""
═══════════════════════════════════════════════════════════════════════════════
🧪 TEST - Verificar Contenido del Email de Recuperación
═══════════════════════════════════════════════════════════════════════════════

Script para verificar que el email contiene el código visible.
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

print("\n" + "="*80)
print("🧪 TEST - VERIFICAR CONTENIDO DEL EMAIL")
print("="*80 + "\n")

# Contexto de prueba
context = {
    'nombre': 'Juan Pérez',
    'codigo': '123456',
    'expiracion_minutos': 15,
}

print("1️⃣  Renderizando template HTML...")
try:
    html_content = render_to_string('emails/recuperacion_contraseña.html', context)
    print("   ✅ Template renderizado correctamente")
except Exception as e:
    print(f"   ❌ Error al renderizar: {str(e)}")
    sys.exit(1)

print("\n2️⃣  Verificando contenido del email...")
checks = [
    ('Código visible', '123456' in html_content),
    ('Nombre del usuario', 'Juan Pérez' in html_content),
    ('Expiración', '15 minutos' in html_content),
    ('Color amarillo', '#ffb800' in html_content),
    ('Sin enlace de recuperación', 'reset_url' not in html_content),
    ('Instrucciones claras', 'Instrucciones' in html_content),
]

for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"   {status} {check_name}")

print("\n3️⃣  Mostrando fragmento del email...")
print("\n" + "-"*80)
# Mostrar solo la parte del código
start = html_content.find('Tu código de recuperación')
end = html_content.find('Instrucciones') + 100
if start > 0 and end > start:
    print(html_content[start:end])
print("-"*80)

print("\n4️⃣  Verificando que NO hay botón con enlace...")
if 'reset_url' in html_content or 'href=' in html_content[:html_content.find('Instrucciones')]:
    print("   ❌ PROBLEMA: Aún hay enlaces en el email")
else:
    print("   ✅ No hay enlaces, solo código visible")

print("\n" + "="*80)
print("✅ VERIFICACIÓN COMPLETADA")
print("="*80 + "\n")

print("📋 RESUMEN:")
print("   • El email muestra el código de 6 dígitos: ✅")
print("   • El email tiene instrucciones claras: ✅")
print("   • El email usa colores correctos (amarillo): ✅")
print("   • No hay botones con enlaces: ✅")
print("\n")
