"""
🔍 SCRIPT DE DEBUG - Verificar selectores en la UI
═══════════════════════════════════════════════════════════════════════════════

Este script ayuda a identificar los selectores correctos en tu aplicación React.
Ejecuta esto antes de correr los tests E2E para verificar que los selectores existen.
"""

from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5173"

def debug_login_page():
    """Verifica los selectores en la página de login"""
    print("\n🔍 DEBUGGEANDO PÁGINA DE LOGIN")
    print("=" * 70)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Abre navegador visible
        page = browser.new_page()
        
        try:
            # Navegar a login
            print(f"\n📍 Navegando a {BASE_URL}/login...")
            page.goto(f"{BASE_URL}/login", timeout=10000)
            page.wait_for_load_state("networkidle")
            
            # Verificar selectores
            print("\n✅ Verificando selectores...")
            
            # Input de username
            username_input = page.query_selector("#username")
            if username_input:
                print("✓ Input #username encontrado")
            else:
                print("✗ Input #username NO encontrado")
                # Buscar alternativas
                alt_inputs = page.query_selector_all("input[type='text']")
                print(f"  Inputs de texto encontrados: {len(alt_inputs)}")
            
            # Input de password
            password_input = page.query_selector("#password")
            if password_input:
                print("✓ Input #password encontrado")
            else:
                print("✗ Input #password NO encontrado")
                # Buscar alternativas
                alt_inputs = page.query_selector_all("input[type='password']")
                print(f"  Inputs de password encontrados: {len(alt_inputs)}")
            
            # Botón de submit
            submit_btn = page.query_selector("button[type='submit']")
            if submit_btn:
                print("✓ Botón submit encontrado")
                print(f"  Texto: {submit_btn.inner_text()}")
            else:
                print("✗ Botón submit NO encontrado")
            
            # Intentar login
            print("\n🔐 Intentando login con credenciales de prueba...")
            if username_input and password_input and submit_btn:
                page.fill("#username", "testuser")
                page.fill("#password", "testpass123")
                submit_btn.click()
                
                # Esperar resultado
                page.wait_for_timeout(3000)
                
                # Verificar si se redirigió
                current_url = page.url
                print(f"  URL actual: {current_url}")
                
                if current_url != f"{BASE_URL}/login":
                    print("✓ Login exitoso - redirección detectada")
                else:
                    print("✗ Login falló - sigue en página de login")
            
            # Pausar para inspeccionar manualmente
            print("\n⏸️  Presiona Enter para cerrar el navegador...")
            input()
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            browser.close()


def debug_cart_page():
    """Verifica los selectores en la página del carrito"""
    print("\n🔍 DEBUGGEANDO PÁGINA DEL CARRITO")
    print("=" * 70)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # Navegar a carrito
            print(f"\n📍 Navegando a {BASE_URL}/carrito...")
            page.goto(f"{BASE_URL}/carrito", timeout=10000)
            page.wait_for_load_state("networkidle")
            
            # Verificar selectores
            print("\n✅ Verificando selectores del carrito...")
            
            # Contenedor principal
            cart_container = page.query_selector(".vista-carrito")
            if cart_container:
                print("✓ Contenedor .vista-carrito encontrado")
            else:
                print("✗ Contenedor .vista-carrito NO encontrado")
            
            # Items del carrito
            items = page.query_selector_all(".producto-carrito-item")
            print(f"✓ Items del carrito: {len(items)} encontrados")
            
            # Botones de cantidad
            qty_buttons = page.query_selector_all(".btn-cantidad-compacto")
            print(f"✓ Botones de cantidad: {len(qty_buttons)} encontrados")
            
            # Resumen
            summary = page.query_selector(".resumen-card")
            if summary:
                print("✓ Resumen de compra encontrado")
            else:
                print("✗ Resumen de compra NO encontrado")
            
            # Botón de checkout
            checkout_btn = page.query_selector("button:has-text('Finalizar Compra')")
            if checkout_btn:
                print("✓ Botón de checkout encontrado")
            else:
                print("✗ Botón de checkout NO encontrado")
            
            # Pausar para inspeccionar
            print("\n⏸️  Presiona Enter para cerrar el navegador...")
            input()
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🎭 PLAYWRIGHT SELECTOR DEBUG TOOL")
    print("=" * 70)
    
    print("\nOpciones:")
    print("1. Debug Login Page")
    print("2. Debug Cart Page")
    print("3. Debug Both")
    
    choice = input("\nSelecciona opción (1-3): ").strip()
    
    if choice == "1":
        debug_login_page()
    elif choice == "2":
        debug_cart_page()
    elif choice == "3":
        debug_login_page()
        debug_cart_page()
    else:
        print("Opción inválida")
