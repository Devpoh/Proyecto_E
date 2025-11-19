#!/usr/bin/env python
"""
Script para probar la API de autenticación
Funciona en Windows, macOS y Linux
"""

import requests
import json
import sys
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000/api"
TIMEOUT = 10

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Imprimir encabezado"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_success(text):
    """Imprimir mensaje de éxito"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    """Imprimir mensaje de error"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    """Imprimir mensaje de información"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_response(response):
    """Imprimir respuesta formateada"""
    print(f"\n{Colors.BOLD}Status Code:{Colors.ENDC} {response.status_code}")
    print(f"{Colors.BOLD}Headers:{Colors.ENDC}")
    for key, value in response.headers.items():
        if key.lower() in ['content-type', 'set-cookie']:
            print(f"  {key}: {value}")
    
    try:
        data = response.json()
        print(f"{Colors.BOLD}Response Body:{Colors.ENDC}")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(f"{Colors.BOLD}Response Body:{Colors.ENDC}")
        print(response.text)

def test_csrf_token():
    """Test: Obtener CSRF Token"""
    print_header("TEST 1: Obtener CSRF Token")
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/csrf-token/",
            timeout=TIMEOUT
        )
        
        print_response(response)
        
        if response.status_code == 200:
            print_success("CSRF Token obtenido exitosamente")
            csrf_token = response.json().get('csrfToken')
            print_info(f"CSRF Token: {csrf_token[:20]}...")
            return csrf_token
        else:
            print_error(f"Error: {response.status_code}")
            return None
    
    except requests.exceptions.ConnectionError:
        print_error("No se puede conectar al servidor. ¿Está corriendo Django?")
        print_info("Ejecuta: python manage.py runserver")
        return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_login(username="test_user", password="TestPassword123"):
    """Test: Login"""
    print_header("TEST 2: Login")
    
    print_info(f"Username: {username}")
    print_info(f"Password: {'*' * len(password)}")
    
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json=login_data,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        
        print_response(response)
        
        if response.status_code == 200:
            print_success("Login exitoso")
            data = response.json()
            access_token = data.get('accessToken')
            user = data.get('user', {})
            print_info(f"Usuario: {user.get('nombre')} ({user.get('rol')})")
            print_info(f"Access Token: {access_token[:20]}...")
            return access_token
        elif response.status_code == 429:
            print_error("Demasiados intentos. Rate limiting activo")
            data = response.json()
            print_info(f"Tiempo restante: {data.get('tiempo_restante')} segundos")
            return None
        elif response.status_code == 401:
            print_error("Credenciales inválidas")
            return None
        else:
            print_error(f"Error: {response.status_code}")
            return None
    
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_refresh(access_token):
    """Test: Refresh Token"""
    print_header("TEST 3: Refresh Token")
    
    print_info(f"Access Token: {access_token[:20]}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/refresh/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            timeout=TIMEOUT
        )
        
        print_response(response)
        
        if response.status_code == 200:
            print_success("Token refrescado exitosamente")
            data = response.json()
            new_access_token = data.get('accessToken')
            print_info(f"Nuevo Access Token: {new_access_token[:20]}...")
            return new_access_token
        else:
            print_error(f"Error: {response.status_code}")
            return None
    
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_logout(access_token):
    """Test: Logout"""
    print_header("TEST 4: Logout")
    
    print_info(f"Access Token: {access_token[:20]}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/logout/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            timeout=TIMEOUT
        )
        
        print_response(response)
        
        if response.status_code == 200:
            print_success("Logout exitoso")
            return True
        else:
            print_error(f"Error: {response.status_code}")
            return False
    
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_blacklist(access_token):
    """Test: Token en Blacklist"""
    print_header("TEST 5: Verificar Token en Blacklist")
    
    print_info("Intentando usar el token después de logout...")
    print_info(f"Access Token: {access_token[:20]}...")
    
    try:
        # Intentar usar el token invalidado
        response = requests.get(
            f"{BASE_URL}/productos/",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            timeout=TIMEOUT
        )
        
        print_response(response)
        
        if response.status_code == 401:
            print_success("Token correctamente invalidado en blacklist")
            return True
        else:
            print_error("Token no fue invalidado correctamente")
            return False
    
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def main():
    """Ejecutar todos los tests"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        PRUEBA DE API - AUTENTICACIÓN ELECTRO ISLA          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: CSRF Token
    csrf_token = test_csrf_token()
    if not csrf_token:
        print_error("No se puede continuar sin CSRF Token")
        return
    
    # Test 2: Login
    access_token = test_login()
    if not access_token:
        print_error("No se puede continuar sin Access Token")
        return
    
    # Test 3: Refresh Token
    new_access_token = test_refresh(access_token)
    if new_access_token:
        access_token = new_access_token
    
    # Test 4: Logout
    logout_success = test_logout(access_token)
    if not logout_success:
        print_error("No se puede continuar sin logout exitoso")
        return
    
    # Test 5: Verificar Blacklist
    test_blacklist(access_token)
    
    # Resumen
    print_header("RESUMEN")
    print_success("Todos los tests completados")
    print_info("Verifica los logs en: backend/logs/auth.log")
    print_info("Verifica los logs en: backend/logs/security.log")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Prueba cancelada por el usuario{Colors.ENDC}\n")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        sys.exit(1)
