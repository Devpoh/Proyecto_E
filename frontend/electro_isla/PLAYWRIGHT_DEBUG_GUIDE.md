# 🔍 GUÍA DE DEBUG - PLAYWRIGHT E2E TESTS

## ❌ PROBLEMA ENCONTRADO

Los tests fallaban con `TimeoutError` porque:

1. **URL incorrecta**: Tests buscaban en `http://localhost:3000` pero React corre en `http://localhost:5173` (Vite)
2. **Selectores incorrectos**: Tests usaban `input[name='username']` pero el HTML real usa `id="username"`

## ✅ SOLUCIONES APLICADAS

### 1. URL Base Actualizada
```python
# ❌ ANTES
BASE_URL = "http://localhost:3000"

# ✅ AHORA
BASE_URL = "http://localhost:5173"  # Vite dev server
```

### 2. Selectores Corregidos
```python
# ❌ ANTES
page.fill("input[name='username']", username)
page.fill("input[name='password']", password)

# ✅ AHORA
page.fill("#username", username)  # Usa ID, no name
page.fill("#password", password)  # Usa ID, no name
```

### 3. Esperas Explícitas Agregadas
```python
# Esperar a que el formulario esté visible
page.wait_for_selector("#username", timeout=10000)

# Esperar a que redirija correctamente
page.wait_for_url(f"{BASE_URL}/*", timeout=10000)
```

---

## 🔧 CÓMO DEBUGGEAR SELECTORES

### Opción 1: Script de Debug Automático

```bash
cd frontend/electro_isla
python tests/e2e/debug_selectors.py
```

Este script:
- ✅ Abre el navegador visualmente
- ✅ Verifica que los selectores existen
- ✅ Intenta hacer login automáticamente
- ✅ Muestra qué selectores funcionan y cuáles no

### Opción 2: Inspeccionar Manualmente

1. Abre `http://localhost:5173/login` en tu navegador
2. Abre DevTools (F12)
3. Busca los elementos:
   ```javascript
   // En la consola del navegador
   document.querySelector("#username")  // Debe retornar el input
   document.querySelector("#password")  // Debe retornar el input
   document.querySelector("button[type='submit']")  // Debe retornar el botón
   ```

### Opción 3: Ejecutar Test con `--headed`

```bash
pytest tests/e2e/test_cart_flow_e2e.py::test_carrito_vacio -v --headed
```

Esto abre el navegador y puedes ver exactamente dónde falla.

---

## 📋 CHECKLIST ANTES DE EJECUTAR TESTS

- ✅ Backend corriendo: `http://localhost:8000`
- ✅ Frontend corriendo: `http://localhost:5173`
- ✅ Usuario `testuser` existe en BD
- ✅ Contraseña es `testpass123`
- ✅ Hay productos en BD
- ✅ Selectores verificados con script de debug

---

## 🚀 EJECUTAR TESTS (ORDEN CORRECTO)

### Terminal 1: Backend
```bash
cd backend
python manage.py runserver
```

### Terminal 2: Frontend
```bash
cd frontend/electro_isla
npm run dev
```

### Terminal 3: Debug (OPCIONAL)
```bash
cd frontend/electro_isla
python tests/e2e/debug_selectors.py
```

### Terminal 4: Tests
```bash
cd frontend/electro_isla
pytest tests/e2e/test_cart_flow_e2e.py -v
```

---

## 🐛 TROUBLESHOOTING

### Error: `TimeoutError: waiting for locator("#username")`
**Causa**: El selector no existe en el HTML
**Solución**: 
1. Ejecuta `debug_selectors.py`
2. Verifica que el input tiene `id="username"`
3. Si no, actualiza el selector en el test

### Error: `net::ERR_CONNECTION_REFUSED`
**Causa**: Frontend no está corriendo
**Solución**: Ejecuta `npm run dev` en terminal 2

### Error: `Page.goto: net::ERR_NAME_NOT_RESOLVED`
**Causa**: URL incorrecta
**Solución**: Verifica que BASE_URL = "http://localhost:5173"

### Error: Login falla pero no hay error visible
**Solución**: 
1. Ejecuta con `--headed` para ver visualmente
2. Verifica credenciales en BD
3. Revisa que el backend está corriendo

---

## 📊 ESTRUCTURA DE SELECTORES ESPERADOS

```html
<!-- Login Form -->
<input id="username" type="text" placeholder="..." />
<input id="password" type="password" placeholder="..." />
<button type="submit">Iniciar Sesión</button>

<!-- Cart Page -->
<div class="vista-carrito">
  <div class="producto-carrito-item">
    <button class="btn-cantidad-compacto">−</button>
    <span class="cantidad-display-compacto">1</span>
    <button class="btn-cantidad-compacto">+</button>
  </div>
  <div class="resumen-card">
    <!-- Resumen -->
  </div>
  <button>Finalizar Compra</button>
</div>
```

---

## 💡 TIPS

1. **Usa `--headed`** para ver qué hace el test en tiempo real
2. **Usa `debug_selectors.py`** antes de ejecutar todos los tests
3. **Verifica URLs** - Backend ≠ Frontend
4. **Espera explícitamente** - No confíes solo en timeouts automáticos
5. **Inspecciona el HTML** - Los selectores deben coincidir exactamente

---

## ✅ PRÓXIMO PASO

Ejecuta el debug script:
```bash
python tests/e2e/debug_selectors.py
```

Selecciona opción 1 (Debug Login Page) y verifica que todo funciona.

Luego ejecuta los tests:
```bash
pytest tests/e2e/test_cart_flow_e2e.py -v
```

¡Deberían pasar ahora! 🎉
