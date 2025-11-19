"""
═══════════════════════════════════════════════════════════════════════════════
🔧 SCRIPT - Verificar y Arreglar Productos
═══════════════════════════════════════════════════════════════════════════════

Este script:
1. Verifica cuántos productos hay en la BD
2. Verifica cuántos están marcados como en_carrusel=True
3. Marca automáticamente los primeros 5 productos para el carrusel
4. Activa todos los productos inactivos
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Producto

def main():
    print("\n" + "="*80)
    print("🔍 VERIFICANDO ESTADO DE PRODUCTOS")
    print("="*80 + "\n")
    
    # 1. Contar total de productos
    total_productos = Producto.objects.count()
    print(f"📊 Total de productos en BD: {total_productos}")
    
    # 2. Contar productos activos
    activos = Producto.objects.filter(activo=True).count()
    print(f"✅ Productos activos: {activos}")
    
    # 3. Contar productos inactivos
    inactivos = Producto.objects.filter(activo=False).count()
    print(f"❌ Productos inactivos: {inactivos}")
    
    # 4. Contar productos en carrusel
    en_carrusel = Producto.objects.filter(en_carrusel=True).count()
    print(f"🎠 Productos en carrusel: {en_carrusel}")
    
    print("\n" + "-"*80 + "\n")
    
    if total_productos == 0:
        print("⚠️  NO HAY PRODUCTOS EN LA BASE DE DATOS")
        print("Necesitas crear productos primero en Django Admin o importarlos.")
        return
    
    # 5. Activar todos los productos inactivos
    if inactivos > 0:
        print(f"🔄 Activando {inactivos} productos inactivos...")
        Producto.objects.filter(activo=False).update(activo=True)
        print(f"✅ {inactivos} productos activados")
    
    # 6. Marcar primeros 5 productos para carrusel si no hay
    if en_carrusel == 0:
        print(f"\n🎠 Marcando primeros 5 productos para el carrusel...")
        productos_para_carrusel = Producto.objects.filter(activo=True).order_by('id')[:5]
        
        for producto in productos_para_carrusel:
            producto.en_carrusel = True
            producto.save()
            print(f"   ✅ {producto.nombre} → en_carrusel=True")
        
        print(f"\n✅ {len(productos_para_carrusel)} productos marcados para carrusel")
    
    print("\n" + "="*80)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("="*80 + "\n")
    
    # Mostrar resumen final
    print("📊 ESTADO FINAL:")
    print(f"   • Total: {Producto.objects.count()}")
    print(f"   • Activos: {Producto.objects.filter(activo=True).count()}")
    print(f"   • En carrusel: {Producto.objects.filter(en_carrusel=True).count()}")
    print("\n✨ Los productos deberían aparecer en el frontend ahora.\n")

if __name__ == '__main__':
    main()
