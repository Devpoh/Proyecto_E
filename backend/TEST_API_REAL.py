#!/usr/bin/env python
"""
Script para testear qué retorna la API real
"""
import requests
import json

API_URL = "http://localhost:8000/api/carrusel/"

print("=" * 80)
print("🔍 TESTEANDO API REAL")
print("=" * 80)

try:
    response = requests.get(API_URL)
    response.raise_for_status()
    
    data = response.json()
    
    print(f"\n✅ Status: {response.status_code}")
    print(f"📊 Total productos: {data.get('count', 0)}")
    
    # Mostrar primeros 3 productos
    productos = data.get('data', [])[:3]
    
    for i, p in enumerate(productos, 1):
        print(f"\n{'─' * 80}")
        print(f"{i}. {p.get('nombre')}")
        print(f"   imagen_url: {p.get('imagen_url')}")
        
        # Intentar acceder a la imagen
        imagen_url = p.get('imagen_url')
        if imagen_url and imagen_url.startswith('http'):
            print(f"   ✅ URL absoluta")
            try:
                img_response = requests.head(imagen_url, timeout=5)
                print(f"   📷 Status: {img_response.status_code}")
            except Exception as e:
                print(f"   ❌ Error al acceder: {e}")
        elif imagen_url and imagen_url.startswith('/media'):
            print(f"   ⚠️  URL relativa")
        elif imagen_url and imagen_url.startswith('data:'):
            print(f"   📊 Base64 ({len(imagen_url)} caracteres)")
        else:
            print(f"   ❌ Sin imagen")

except Exception as e:
    print(f"❌ Error: {e}")

print(f"\n{'=' * 80}")
