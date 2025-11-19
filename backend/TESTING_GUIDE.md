# 🧪 GUÍA DE TESTING - CARRITO DE COMPRAS

## 📋 REQUISITOS

✅ Ya instalados:
- pytest
- pytest-django
- Django
- DRF

## 🚀 EJECUTAR TESTS

### Opción 1: Todos los tests del carrito (RECOMENDADO)
```bash
pytest backend/api/tests/test_cart_flow.py -v
```

### Opción 2: Test específico
```bash
pytest backend/api/tests/test_cart_flow.py::TestCartFlow::test_agregar_producto_al_carrito -v
```

### Opción 3: Con salida detallada
```bash
pytest backend/api/tests/test_cart_flow.py -v --tb=short
```

### Opción 4: Con coverage (cobertura de código)
```bash
pytest backend/api/tests/test_cart_flow.py --cov=api --cov-report=html
```

---

## 📊 TESTS INCLUIDOS

### ✅ Tests Básicos
1. **test_obtener_carrito_vacio** - Obtener carrito vacío
2. **test_agregar_producto_al_carrito** - Agregar 1 producto
3. **test_incrementar_cantidad_existente** - Agregar mismo producto 2 veces

### ✅ Tests de Validación
4. **test_agregar_producto_sin_stock** - Error si stock insuficiente
5. **test_no_autenticado_no_puede_acceder** - Solo usuarios logueados

### ✅ Tests de Actualización
6. **test_actualizar_cantidad_item** - Cambiar cantidad de item
7. **test_eliminar_item_del_carrito** - Eliminar item
8. **test_vaciar_carrito** - Vaciar todos los items

### ✅ Tests de Sincronización
9. **test_carrito_persiste_entre_requests** - Persistencia en BD
10. **test_bulk_update_carrito** - Actualizar múltiples items en 1 request

### ✅ Tests de Checkout
11. **test_checkout_reserva_stock** - Reservar stock en checkout
12. **test_checkout_sin_stock_suficiente** - Error si stock insuficiente

---

## 📈 SALIDA ESPERADA

```
================== test session starts ==================
collected 12 items

backend/api/tests/test_cart_flow.py::TestCartFlow::test_obtener_carrito_vacio PASSED [8%]
backend/api/tests/test_cart_flow.py::TestCartFlow::test_agregar_producto_al_carrito PASSED [16%]
backend/api/tests/test_cart_flow.py::TestCartFlow::test_agregar_producto_sin_stock PASSED [25%]
backend/api/tests/test_cart_flow.py::TestCartFlow::test_actualizar_cantidad_item PASSED [33%]
backend/api/tests/test_cart_flow.py::TestCartFlow::test_eliminar_item_del_carrito PASSED [41%]
backend/api/tests/test_cart_flow.py::TestCartFlow::test_bulk_update_carrito PASSED [50%]
backend/api/tests/test_cart_flow.py::TestCartFlow::test_vaciar_carrito PASSED [58%]
backend/api/tests/test_cart_flow.py::TestCartFlow::test_carrito_persiste_entre_requests PASSED [66%]
backend/api/tests/test_cart_flow.py::TestCartFlow::test_checkout_reserva_stock PASSED [75%]
backend/api/tests/test_cart_flow.py::TestCartFlow::test_checkout_sin_stock_suficiente PASSED [83%]
backend/api/tests/test_cart_flow.py::TestCartFlow::test_no_autenticado_no_puede_acceder PASSED [91%]
backend/api/tests/test_cart_flow.py::TestCartFlow::test_incrementar_cantidad_existente PASSED [100%]

================== 12 passed in 2.34s ==================
```

---

## 🔍 ENTENDER LOS TESTS

### Estructura de cada test:

```python
def test_agregar_producto_al_carrito(self, api_client, test_user, test_products):
    """✅ Descripción del test"""
    
    # 1. SETUP: Autenticar usuario
    api_client.force_authenticate(user=test_user)
    producto = test_products[0]
    
    # 2. ACTION: Hacer la petición
    response = api_client.post(
        reverse('carrito-agregar'),
        data=json.dumps({'product_id': producto.id, 'quantity': 2}),
        content_type='application/json'
    )
    
    # 3. ASSERT: Verificar resultado
    assert response.status_code == 201
    data = response.json()
    assert len(data['items']) == 1
    assert data['items'][0]['quantity'] == 2
```

### Fixtures disponibles:

- **api_client**: Cliente API para hacer peticiones
- **test_user**: Usuario de prueba autenticado
- **test_products**: 3 productos de prueba con stock=100

---

## 🐛 DEBUGGING

### Si un test falla:

1. **Ver el error completo:**
```bash
pytest backend/api/tests/test_cart_flow.py::TestCartFlow::test_name -v --tb=long
```

2. **Ver qué datos se enviaron/recibieron:**
```bash
pytest backend/api/tests/test_cart_flow.py -v -s  # -s muestra prints
```

3. **Ejecutar solo 1 test:**
```bash
pytest backend/api/tests/test_cart_flow.py::TestCartFlow::test_agregar_producto_al_carrito -v
```

---

## 🔄 FLUJO DE TESTING COMPLETO

```
┌─────────────────────────────────────────┐
│ 1. Crear usuario de prueba              │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 2. Crear 3 productos con stock=100      │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 3. Autenticar usuario                   │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 4. Hacer petición a endpoint            │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 5. Verificar status code y datos        │
└────────────┬────────────────────────────┘
             ↓
┌─────────────────────────────────────────┐
│ 6. Limpiar BD (automático)              │
└─────────────────────────────────────────┘
```

---

## ✅ CHECKLIST DE TESTING

- ✅ Todos los tests pasan
- ✅ Coverage > 80%
- ✅ No hay errores 500
- ✅ Validaciones funcionan
- ✅ Stock se reserva correctamente
- ✅ Carrito persiste en BD
- ✅ Bulk-update funciona
- ✅ Checkout reserva stock

---

## 📝 NOTAS IMPORTANTES

1. **Base de datos de prueba:** Pytest crea una BD temporal para cada test
2. **Limpieza automática:** Los datos se limpian después de cada test
3. **Aislamiento:** Cada test es independiente
4. **Fixtures:** Se reutilizan en todos los tests
5. **Decorador @pytest.mark.django_db:** Permite acceso a BD

---

## 🚀 PRÓXIMOS PASOS

1. ✅ Ejecutar tests: `pytest backend/api/tests/test_cart_flow.py -v`
2. ✅ Verificar que todos pasen
3. ✅ Revisar coverage: `pytest --cov=api`
4. ✅ Agregar más tests si es necesario
5. ✅ Integrar en CI/CD (GitHub Actions, etc.)

---

## 💡 TIPS

- Ejecuta tests antes de hacer commit
- Mantén tests simples y enfocados
- Un test = una funcionalidad
- Usa nombres descriptivos
- Documenta casos edge

¡Feliz testing! 🎉
