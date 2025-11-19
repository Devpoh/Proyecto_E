# 🎭 GUÍA DE TESTING E2E - CARRITO DE COMPRAS

## 📋 REQUISITOS

✅ Ya instalados:
- playwright
- pytest-playwright
- pytest

## 🚀 EJECUTAR TESTS E2E

### Opción 1: Todos los tests (RECOMENDADO)
```bash
pytest tests/e2e/test_cart_flow_e2e.py -v
```

### Opción 2: Test específico
```bash
pytest tests/e2e/test_cart_flow_e2e.py::test_agregar_producto_al_carrito -v
```

### Opción 3: Con modo visual (headless=false)
```bash
pytest tests/e2e/test_cart_flow_e2e.py -v --headed
```

### Opción 4: Solo tests E2E
```bash
pytest -m e2e -v
```

---

## 📊 TESTS INCLUIDOS

### ✅ Tests Básicos
1. **test_carrito_vacio** - Verificar carrito vacío al inicio
2. **test_agregar_producto_al_carrito** - Agregar 1 producto
3. **test_agregar_multiples_productos** - Agregar múltiples productos

### ✅ Tests de Cantidad
4. **test_actualizar_cantidad** - Aumentar cantidad
5. **test_disminuir_cantidad** - Disminuir cantidad
6. **test_debounce_actualizacion** - Verificar debounce funciona

### ✅ Tests de Operaciones
7. **test_eliminar_producto** - Eliminar producto del carrito
8. **test_vaciar_carrito** - Vaciar todos los productos

### ✅ Tests de UI
9. **test_resumen_compra_actualiza** - Resumen se actualiza
10. **test_checkout_flow** - Flujo de checkout

### ✅ Tests de Persistencia
11. **test_persistencia_carrito** - Carrito persiste al recargar

---

## 📈 SALIDA ESPERADA

```
================== test session starts ==================
collected 11 items

tests/e2e/test_cart_flow_e2e.py::test_carrito_vacio PASSED [9%]
tests/e2e/test_cart_flow_e2e.py::test_agregar_producto_al_carrito PASSED [18%]
tests/e2e/test_cart_flow_e2e.py::test_agregar_multiples_productos PASSED [27%]
tests/e2e/test_cart_flow_e2e.py::test_actualizar_cantidad PASSED [36%]
tests/e2e/test_cart_flow_e2e.py::test_disminuir_cantidad PASSED [45%]
tests/e2e/test_cart_flow_e2e.py::test_eliminar_producto PASSED [54%]
tests/e2e/test_cart_flow_e2e.py::test_vaciar_carrito PASSED [63%]
tests/e2e/test_cart_flow_e2e.py::test_resumen_compra_actualiza PASSED [72%]
tests/e2e/test_cart_flow_e2e.py::test_checkout_flow PASSED [81%]
tests/e2e/test_cart_flow_e2e.py::test_persistencia_carrito PASSED [90%]
tests/e2e/test_cart_flow_e2e.py::test_debounce_actualizacion PASSED [100%]

================== 11 passed in 45.23s ==================
```

---

## 🔍 ENTENDER LOS TESTS

### Estructura de cada test:

```python
@pytest.mark.e2e
def test_agregar_producto_al_carrito(page: Page):
    """✅ Agregar un producto al carrito"""
    
    # 1. LOGIN: Autenticar usuario
    login(page)
    
    # 2. ACTION: Agregar producto
    agregar_producto_desde_catalogo(page, 0)
    
    # 3. NAVIGATE: Ir al carrito
    ir_al_carrito(page)
    
    # 4. ASSERT: Verificar resultado
    items = page.query_selector_all(".producto-carrito-item")
    assert len(items) >= 1
```

### Funciones auxiliares disponibles:

- **login(page, username, password)** - Realiza login
- **agregar_producto_desde_catalogo(page, index)** - Agrega producto
- **ir_al_carrito(page)** - Navega al carrito

---

## 🐛 DEBUGGING

### Si un test falla:

1. **Ver el error completo:**
```bash
pytest tests/e2e/test_cart_flow_e2e.py::test_name -v --tb=long
```

2. **Ejecutar con modo visual:**
```bash
pytest tests/e2e/test_cart_flow_e2e.py::test_name -v --headed
```

3. **Ejecutar solo 1 test:**
```bash
pytest tests/e2e/test_cart_flow_e2e.py::test_agregar_producto_al_carrito -v
```

4. **Ver screenshots de fallos:**
```
test-results/
├── test_agregar_producto_al_carrito/
│   └── test-failed-1.png
```

---

## 🔄 FLUJO DE TESTING COMPLETO

```
┌─────────────────────────────────────────┐
│ 1. Iniciar navegador (Chromium)         │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 2. Navegar a http://localhost:3000      │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 3. Login con credenciales de prueba     │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 4. Interactuar con la UI (clicks, etc)  │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 5. Verificar estado esperado            │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 6. Cerrar navegador                     │
└─────────────────────────────────────────┘
```

---

## ✅ CHECKLIST DE TESTING

- ✅ Todos los tests pasan
- ✅ Carrito se actualiza en tiempo real
- ✅ Debounce funciona correctamente
- ✅ Persistencia en localStorage
- ✅ Checkout está disponible
- ✅ Eliminación de productos funciona
- ✅ Vaciar carrito funciona
- ✅ Resumen se actualiza

---

## 📝 NOTAS IMPORTANTES

1. **Selectores CSS**: Los tests usan selectores de tu componente React
2. **Timeouts**: Cada test tiene timeout de 30 segundos
3. **Paralelo**: Los tests corren secuencialmente (workers=1)
4. **Screenshots**: Se guardan en `test-results/` si falla
5. **Base URL**: Configurada en `playwright.config.ts`

---

## 🚀 PRÓXIMOS PASOS

1. ✅ Asegúrate que tu React corre en `http://localhost:3000`
2. ✅ Asegúrate que tu backend corre en `http://localhost:8000`
3. ✅ Ejecuta tests: `pytest tests/e2e/test_cart_flow_e2e.py -v`
4. ✅ Verifica que todos pasen
5. ✅ Integra en CI/CD (GitHub Actions, etc.)

---

## 💡 TIPS

- Usa `--headed` para ver visualmente qué hace el test
- Los tests son independientes (cada uno hace su propio login)
- Puedes agregar más tests siguiendo el mismo patrón
- Los selectores pueden necesitar ajustes según tu CSS
- Usa `page.pause()` para pausar y debuggear manualmente

¡Feliz testing! 🎉
