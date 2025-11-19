# 🧪 PRUEBA MANUAL - THROTTLING PRODUCCIÓN REALISTA

## 📋 Requisitos

- Django server corriendo: `python manage.py runserver`
- curl instalado
- Terminal con bash

---

## 🔐 TEST 1: LOGIN (5/minuto + LoginAttempt 5/minuto)

### Paso 1: Limpiar intentos previos
```bash
cd backend
python manage.py shell

>>> from api.models import LoginAttempt
>>> LoginAttempt.objects.all().delete()
>>> exit()
```

### Paso 2: Enviar 6 requests rápidos
```bash
for i in {1..6}; do
  echo "Request $i:"
  curl -X POST http://127.0.0.1:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"username": "test", "password": "wrong"}' \
    -w "\nStatus: %{http_code}\n\n"
  sleep 0.1
done
```

### Paso 3: Resultado esperado
```
Request 1:
{"error": "Por favor proporciona usuario/email y contraseña"}
Status: 400

Request 2:
{"error": "Por favor proporciona usuario/email y contraseña"}
Status: 400

Request 3:
{"error": "Por favor proporciona usuario/email y contraseña"}
Status: 400

Request 4:
{"error": "Por favor proporciona usuario/email y contraseña"}
Status: 400

Request 5:
{"error": "Por favor proporciona usuario/email y contraseña"}
Status: 400

Request 6:
{"detail": "Request was throttled. Expected available in 55 seconds."}
Status: 429 ✅ BLOQUEADO
```

### Paso 4: Verificar en BD
```bash
python manage.py shell

>>> from api.models import LoginAttempt
>>> LoginAttempt.objects.all().count()
6

>>> LoginAttempt.objects.filter(success=False).count()
6

>>> LoginAttempt.objects.all().values('ip_address', 'success', 'timestamp')
<QuerySet [
  {'ip_address': '127.0.0.1', 'success': False, 'timestamp': ...},
  {'ip_address': '127.0.0.1', 'success': False, 'timestamp': ...},
  ...
]>
```

---

## 🛒 TEST 2: CARRITO (30/minuto)

### Requisito: Usuario logueado
```bash
# Primero, obtener un token JWT
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}' \
  -s | jq '.accessToken'

# Copiar el token
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Paso 1: Enviar 35 requests rápidos
```bash
TOKEN="tu_token_aqui"

for i in {1..35}; do
  echo "Request $i:"
  curl -X POST http://127.0.0.1:8000/api/carrito/bulk-update/ \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"items": {"1": 1}}' \
    -w "Status: %{http_code}\n\n" \
    -s | head -1
  sleep 0.05
done
```

### Paso 2: Resultado esperado
```
Request 1-30: 200/201/400 ✅
Request 31-35: 429 ✅ BLOQUEADO
```

---

## 💳 TEST 3: CHECKOUT (5/hora)

### Requisito: Usuario logueado con carrito
```bash
TOKEN="tu_token_aqui"

# Agregar producto al carrito primero
curl -X POST http://127.0.0.1:8000/api/carrito/agregar/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"producto_id": 1, "cantidad": 1}' \
  -s
```

### Paso 1: Enviar 8 requests rápidos
```bash
TOKEN="tu_token_aqui"

for i in {1..8}; do
  echo "Request $i:"
  curl -X POST http://127.0.0.1:8000/api/carrito/checkout/ \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{}' \
    -w "Status: %{http_code}\n\n" \
    -s | head -1
  sleep 0.1
done
```

### Paso 2: Resultado esperado
```
Request 1-5: 200/400/409 ✅
Request 6-8: 429 ✅ BLOQUEADO
```

---

## 🧑‍💼 TEST 4: ADMIN (2000/hora)

### Requisito: Usuario admin logueado
```bash
# Obtener token admin
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}' \
  -s | jq '.accessToken'

TOKEN="tu_token_aqui"
```

### Paso 1: Enviar 100 requests rápidos
```bash
TOKEN="tu_token_aqui"

for i in {1..100}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    -H "Authorization: Bearer $TOKEN" \
    http://127.0.0.1:8000/api/admin/productos/
done
```

### Paso 2: Resultado esperado
```
100 x 200 ✅ (todos permitidos, límite es 2000/hora)
```

---

## 📖 TEST 5: ENDPOINTS PÚBLICOS (SIN THROTTLE RESTRICTIVO)

### Paso 1: Enviar 100 requests a /api/productos/
```bash
for i in {1..100}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    http://127.0.0.1:8000/api/productos/
done
```

### Paso 2: Resultado esperado
```
100 x 200 ✅ (todos permitidos, sin throttle restrictivo)
```

### Paso 3: Enviar 100 requests a /api/carrusel/
```bash
for i in {1..100}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    http://127.0.0.1:8000/api/carrusel/
done
```

### Paso 4: Resultado esperado
```
100 x 200 ✅ (todos permitidos, sin throttle restrictivo)
```

---

## 🧪 TEST PYTEST (AUTOMATIZADO)

### Ejecutar todos los tests
```bash
cd backend
pytest tests/test_throttles_production.py -v
```

### Ejecutar test específico
```bash
pytest tests/test_throttles_production.py::TestAnonLoginThrottle::test_anon_login_throttle_denies_requests_over_limit -v -s
```

### Resultado esperado
```
test_anon_login_throttle_allows_requests_under_limit PASSED
test_anon_login_throttle_denies_requests_over_limit PASSED
test_anon_login_throttle_429_response_format PASSED
test_cart_write_throttle_allows_requests_under_limit PASSED
test_cart_write_throttle_denies_requests_over_limit PASSED
test_checkout_throttle_allows_requests_under_limit PASSED
test_checkout_throttle_denies_requests_over_limit PASSED
test_admin_throttle_allows_many_requests PASSED
test_productos_endpoint_no_throttle PASSED
test_carrusel_endpoint_no_throttle PASSED
test_login_attempt_and_throttle_sync PASSED
test_login_attempt_tiempo_restante PASSED

====== 12 passed in X.XXs ======
```

---

## 📊 TABLA DE RESULTADOS

| Test | Endpoint | Límite | Requests | Esperado | Resultado |
|------|----------|--------|----------|----------|-----------|
| 1 | /api/auth/login/ | 5/min | 6 | 5x OK + 1x 429 | ✅ |
| 2 | /api/carrito/bulk-update/ | 30/min | 35 | 30x OK + 5x 429 | ✅ |
| 3 | /api/carrito/checkout/ | 5/h | 8 | 5x OK + 3x 429 | ✅ |
| 4 | /api/admin/productos/ | 2000/h | 100 | 100x OK | ✅ |
| 5 | /api/productos/ | ∞ | 100 | 100x OK | ✅ |
| 6 | /api/carrusel/ | ∞ | 100 | 100x OK | ✅ |

---

## 🔍 DEBUGGING

### Ver logs en tiempo real
```bash
tail -f logs/django.log
```

### Ver throttle events
```bash
grep "THROTTLE\|429" logs/django.log
```

### Ver LoginAttempt events
```bash
cd backend
python manage.py shell

>>> from api.models import LoginAttempt
>>> from django.utils import timezone
>>> from datetime import timedelta

# Últimos 10 intentos
>>> LoginAttempt.objects.all().order_by('-timestamp')[:10]

# Intentos de hoy
>>> desde = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
>>> LoginAttempt.objects.filter(timestamp__gte=desde)

# Intentos fallidos
>>> LoginAttempt.objects.filter(success=False)

# Por IP
>>> LoginAttempt.objects.filter(ip_address='127.0.0.1')
```

---

## ⚠️ TROUBLESHOOTING

### Problema: No se devuelve 429
**Solución**: Verificar que throttles.py está importado correctamente
```bash
cd backend
python manage.py shell
>>> from api.throttles import AnonLoginRateThrottle
>>> print(AnonLoginRateThrottle.scope)
anon_auth
```

### Problema: LoginAttempt no registra intentos
**Solución**: Verificar que views.py llama a LoginAttempt
```bash
grep "LoginAttempt" backend/api/views.py
```

### Problema: .env no se carga
**Solución**: Verificar que python-dotenv está instalado
```bash
pip install python-dotenv
```

### Problema: Throttle no se aplica a endpoint
**Solución**: Verificar que endpoint tiene throttle_classes
```python
# En views.py
class CartViewSet(viewsets.ViewSet):
    throttle_classes = [CartWriteRateThrottle]  # ✅ Debe estar aquí
```

---

## 🎯 CHECKLIST DE VERIFICACIÓN

- [ ] Django server corriendo sin errores
- [ ] .env tiene variables de throttle
- [ ] settings.py tiene scopes configurados
- [ ] throttles.py tiene clases correctas
- [ ] Test 1 (Login): 5 OK + 1x 429 ✅
- [ ] Test 2 (Carrito): 30 OK + 5x 429 ✅
- [ ] Test 3 (Checkout): 5 OK + 3x 429 ✅
- [ ] Test 4 (Admin): 100 OK ✅
- [ ] Test 5 (Públicos): 100 OK ✅
- [ ] Pytest: 12 passed ✅
- [ ] LoginAttempt registra intentos ✅
- [ ] Tiempo restante se calcula correctamente ✅

---

## 🚀 PRÓXIMOS PASOS

1. **Ejecutar tests**:
   ```bash
   pytest tests/test_throttles_production.py -v
   ```

2. **Pruebas manuales**:
   ```bash
   # Test 1
   for i in {1..6}; do curl -X POST http://127.0.0.1:8000/api/auth/login/ ...; done
   ```

3. **Verificar en BD**:
   ```bash
   python manage.py shell
   >>> from api.models import LoginAttempt
   >>> LoginAttempt.objects.all().count()
   ```

4. **Monitorear logs**:
   ```bash
   tail -f logs/django.log
   ```

5. **Desplegar a producción**:
   - Actualizar .env.production con tasas
   - Hacer backup de BD
   - Desplegar código
   - Reiniciar Django

---

**¡Throttling producción realista implementado! 🎉**
