#!/usr/bin/env python
"""
🧪 SCRIPT DE TESTING - SISTEMA DE INVENTARIO
Ejecutar: python test_inventario.py
"""

import os
import django
import requests
import json
from datetime import timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Producto, StockReservation
from django.utils import timezone

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

BASE_URL = "http://localhost:8000/api"
TEST_USER = "ale"
TEST_PASSWORD = "ale.123Q"
TOKEN = None

# Colores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════════════

def print_test(num, titulo):
    """Imprime el título de un test"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}TEST {num}: {titulo}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")

def print_success(msg):
    """Imprime mensaje de éxito"""
    print(f"{GREEN}✅ {msg}{RESET}")

def print_error(msg):
    """Imprime mensaje de error"""
    print(f"{RED}❌ {msg}{RESET}")

def print_info(msg):
    """Imprime mensaje informativo"""
    print(f"{YELLOW}ℹ️  {msg}{RESET}")

def print_json(data):
    """Imprime JSON formateado"""
    print(json.dumps(data, indent=2, ensure_ascii=False))

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 1: OBTENER TOKEN
# ═══════════════════════════════════════════════════════════════════════════════

def test_1_obtener_token():
    """TEST 1: Obtener token de autenticación"""
    global TOKEN
    
    print_test(1, "Obtener Token de Autenticación")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json={"username": TEST_USER, "password": TEST_PASSWORD}
        )
        
        if response.status_code == 200:
            data = response.json()
            TOKEN = data.get('accessToken')
            
            if TOKEN:
                print_success(f"Token obtenido: {TOKEN[:50]}...")
                user_info = data.get('user', {})
                print_success(f"Usuario: {user_info.get('username', user_info.get('email', 'N/A'))}")
                return True
            else:
                print_error("No se obtuvo token en la respuesta")
                print_error(f"Respuesta: {data}")
                return False
        else:
            print_error(f"Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 2: VERIFICAR PRODUCTO CON STOCK
# ═══════════════════════════════════════════════════════════════════════════════

def test_2_verificar_producto():
    """TEST 2: Verificar producto con stock"""
    
    print_test(2, "Verificar Producto con Stock")
    
    try:
        response = requests.get(
            f"{BASE_URL}/productos/",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        
        if response.status_code == 200:
            productos = response.json()
            
            if isinstance(productos, dict) and 'results' in productos:
                productos = productos['results']
            
            if productos:
                producto = productos[0]
                print_success(f"Producto encontrado: {producto['nombre']}")
                print_info(f"  - ID: {producto['id']}")
                print_info(f"  - Stock Total: {producto.get('stock_total', 'N/A')}")
                print_info(f"  - Stock Disponible: {producto.get('stock_disponible', 'N/A')}")
                print_info(f"  - Stock Reservado: {producto.get('stock_reservado', 'N/A')}")
                return True, producto['id']
            else:
                print_error("No hay productos")
                return False, None
        else:
            print_error(f"Error {response.status_code}")
            return False, None
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return False, None

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 3: AGREGAR AL CARRITO (FASE 1)
# ═══════════════════════════════════════════════════════════════════════════════

def test_3_agregar_carrito(product_id):
    """TEST 3: Agregar al carrito (sin reservar)"""
    
    print_test(3, "Agregar al Carrito (FASE 1 - Sin Reservar)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/carrito/agregar/",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={"product_id": product_id, "quantity": 5}
        )
        
        if response.status_code == 201:
            data = response.json()
            print_success("Producto agregado al carrito")
            print_info(f"  - Items en carrito: {data.get('total_items', 'N/A')}")
            print_info(f"  - Total: ${data.get('total', 'N/A')}")
            return True
        else:
            print_error(f"Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 4: VERIFICAR STOCK NO FUE RESERVADO
# ═══════════════════════════════════════════════════════════════════════════════

def test_4_stock_no_reservado(product_id):
    """TEST 4: Verificar que stock NO fue reservado"""
    
    print_test(4, "Verificar Stock NO fue Reservado")
    
    try:
        response = requests.get(
            f"{BASE_URL}/productos/{product_id}/",
            headers={"Authorization": f"Bearer {TOKEN}"}
        )
        
        if response.status_code == 200:
            producto = response.json()
            stock_reservado = producto.get('stock_reservado', 0)
            
            if stock_reservado == 0:
                print_success("Stock NO fue reservado ✓")
                print_info(f"  - Stock Total: {producto.get('stock_total')}")
                print_info(f"  - Stock Reservado: {stock_reservado}")
                print_info(f"  - Stock Disponible: {producto.get('stock_disponible')}")
                return True
            else:
                print_error(f"Stock fue reservado: {stock_reservado}")
                return False
        else:
            print_error(f"Error {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 5: CHECKOUT (FASE 2 - RESERVAR STOCK)
# ═══════════════════════════════════════════════════════════════════════════════

def test_5_checkout():
    """TEST 5: Checkout (reservar stock)"""
    
    print_test(5, "Checkout (FASE 2 - Reservar Stock)")
    
    try:
        response = requests.post(
            f"{BASE_URL}/carrito/checkout/",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Stock reservado exitosamente")
            print_info(f"  - Reservas: {len(data.get('reservas', []))}")
            print_info(f"  - Total items: {data.get('total_items')}")
            print_info(f"  - TTL: {data.get('ttl_minutos')} minutos")
            
            if data.get('reservas'):
                for reserva in data['reservas']:
                    print_info(f"    • {reserva['producto']} x{reserva['cantidad']}")
            
            return True
        else:
            print_error(f"Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 6: VERIFICAR STOCK FUE RESERVADO
# ═══════════════════════════════════════════════════════════════════════════════

def test_6_stock_reservado(product_id):
    """TEST 6: Verificar que stock FUE reservado (verificar en BD)"""
    
    print_test(6, "Verificar Stock FUE Reservado")
    
    try:
        # Verificar directamente en BD
        from api.models import Producto
        producto = Producto.objects.get(id=product_id)
        stock_reservado = producto.stock_reservado
        
        if stock_reservado > 0:
            print_success("Stock FUE reservado ✓")
            print_info(f"  - Stock Total: {producto.stock_total}")
            print_info(f"  - Stock Reservado: {stock_reservado}")
            print_info(f"  - Stock Disponible: {producto.stock_disponible}")
            return True
        else:
            print_error(f"Stock no fue reservado: {stock_reservado}")
            return False
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 7: INTENTAR AGREGAR MÁS DE LO DISPONIBLE
# ═══════════════════════════════════════════════════════════════════════════════

def test_7_cantidad_insuficiente(product_id):
    """TEST 7: Intentar agregar más de lo disponible"""
    
    print_test(7, "Intentar Agregar Más de lo Disponible")
    
    try:
        response = requests.post(
            f"{BASE_URL}/carrito/agregar/",
            headers={"Authorization": f"Bearer {TOKEN}"},
            json={"product_id": product_id, "quantity": 1000}
        )
        
        if response.status_code == 400:
            data = response.json()
            print_success("Solicitud rechazada correctamente ✓")
            print_info(f"  - Error: {data.get('error')}")
            print_info(f"  - Disponible: {data.get('available')}")
            print_info(f"  - Solicitado: {data.get('requested')}")
            return True
        else:
            print_error(f"Debería ser 400, recibió {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 8: LIBERAR RESERVAS EXPIRADAS
# ═══════════════════════════════════════════════════════════════════════════════

def test_8_liberar_reservas():
    """TEST 8: Liberar reservas expiradas"""
    
    print_test(8, "Liberar Reservas Expiradas")
    
    try:
        # Obtener reserva pendiente
        reserva = StockReservation.objects.filter(status='pending').first()
        
        if not reserva:
            print_info("No hay reservas pendientes")
            return True
        
        # Cambiar expires_at al pasado
        reserva.expires_at = timezone.now() - timedelta(minutes=1)
        reserva.save()
        print_info(f"Reserva expirada manualmente: {reserva.producto.nombre}")
        
        # Ejecutar management command
        from django.core.management import call_command
        from io import StringIO
        
        out = StringIO()
        call_command('liberar_reservas_expiradas', '--verbose', stdout=out)
        output = out.getvalue()
        
        print_success("Management command ejecutado")
        print_info(output.strip())
        
        # Verificar que la reserva fue liberada
        reserva.refresh_from_db()
        if reserva.status == 'expired':
            print_success("Reserva liberada correctamente ✓")
            return True
        else:
            print_error(f"Reserva no fue liberada: {reserva.status}")
            return False
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# TEST 9: VERIFICAR STOCK LIBERADO
# ═══════════════════════════════════════════════════════════════════════════════

def test_9_stock_liberado(product_id):
    """TEST 9: Verificar que stock fue liberado (verificar en BD)"""
    
    print_test(9, "Verificar Stock Liberado")
    
    try:
        # Verificar directamente en BD
        from api.models import Producto
        producto = Producto.objects.get(id=product_id)
        stock_reservado = producto.stock_reservado
        
        if stock_reservado == 0:
            print_success("Stock fue liberado correctamente ✓")
            print_info(f"  - Stock Total: {producto.stock_total}")
            print_info(f"  - Stock Reservado: {stock_reservado}")
            print_info(f"  - Stock Disponible: {producto.stock_disponible}")
            return True
        else:
            print_error(f"Stock aún está reservado: {stock_reservado}")
            return False
    except Exception as e:
        print_error(f"Excepción: {str(e)}")
        return False

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Ejecutar todos los tests"""
    
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}🧪 TESTING - SISTEMA DE INVENTARIO{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    resultados = []
    
    # TEST 1
    if test_1_obtener_token():
        resultados.append(("TEST 1: Obtener Token", True))
    else:
        print_error("No se pudo obtener token. Abortando...")
        return
    
    # TEST 2
    success, product_id = test_2_verificar_producto()
    resultados.append(("TEST 2: Verificar Producto", success))
    
    if not success or not product_id:
        print_error("No se encontró producto. Abortando...")
        return
    
    # TEST 3
    if test_3_agregar_carrito(product_id):
        resultados.append(("TEST 3: Agregar Carrito", True))
    else:
        resultados.append(("TEST 3: Agregar Carrito", False))
    
    # TEST 4
    if test_4_stock_no_reservado(product_id):
        resultados.append(("TEST 4: Stock NO Reservado", True))
    else:
        resultados.append(("TEST 4: Stock NO Reservado", False))
    
    # TEST 5
    if test_5_checkout():
        resultados.append(("TEST 5: Checkout", True))
    else:
        resultados.append(("TEST 5: Checkout", False))
    
    # TEST 6
    if test_6_stock_reservado(product_id):
        resultados.append(("TEST 6: Stock Reservado", True))
    else:
        resultados.append(("TEST 6: Stock Reservado", False))
    
    # TEST 7
    if test_7_cantidad_insuficiente(product_id):
        resultados.append(("TEST 7: Cantidad Insuficiente", True))
    else:
        resultados.append(("TEST 7: Cantidad Insuficiente", False))
    
    # TEST 8
    if test_8_liberar_reservas():
        resultados.append(("TEST 8: Liberar Reservas", True))
    else:
        resultados.append(("TEST 8: Liberar Reservas", False))
    
    # TEST 9
    if test_9_stock_liberado(product_id):
        resultados.append(("TEST 9: Stock Liberado", True))
    else:
        resultados.append(("TEST 9: Stock Liberado", False))
    
    # ═══════════════════════════════════════════════════════════════════════════════
    # RESUMEN
    # ═══════════════════════════════════════════════════════════════════════════════
    
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}📊 RESUMEN DE TESTS{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    total = len(resultados)
    exitosos = sum(1 for _, success in resultados if success)
    fallidos = total - exitosos
    
    for test_name, success in resultados:
        status = f"{GREEN}✅ PASÓ{RESET}" if success else f"{RED}❌ FALLÓ{RESET}"
        print(f"{test_name}: {status}")
    
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"Total: {total} | {GREEN}Exitosos: {exitosos}{RESET} | {RED}Fallidos: {fallidos}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    if fallidos == 0:
        print(f"{GREEN}✅ ¡TODOS LOS TESTS PASARON!{RESET}\n")
    else:
        print(f"{RED}❌ {fallidos} test(s) fallaron{RESET}\n")

if __name__ == "__main__":
    main()
