# 🚀 THROTTLING - GUÍA DE DESPLIEGUE

## ✅ Estado Actual

Todos los cambios han sido implementados:

- ✅ `backend/api/throttles.py` - Creado (4 clases de throttle)
- ✅ `backend/config/settings.py` - Actualizado (tasas por scope)
- ✅ `backend/api/views_admin.py` - Limpiado (sin duplicados)
- ✅ `backend/api/views.py` - Actualizado (throttles en carrito/checkout)
- ✅ `backend/tests/test_throttles.py` - Creado (tests pytest)
- ✅ `backend/scripts/verify_throttles.sh` - Creado (verificación manual)

---

## 🧪 PASO 1: Verificar en Local

### 1.1 Reiniciar Django Server
```bash
cd backend
python manage.py runserver
```

### 1.2 Ejecutar Tests Pytest
```bash
# En otra terminal
cd backend
pytest tests/test_throttles.py -v

# Output esperado:
# test_cart_write_throttle_allows_requests_under_limit PASSED
# test_cart_write_throttle_denies_requests_over_limit PASSED
# test_checkout_throttle_allows_requests_under_limit PASSED
# test_checkout_throttle_denies_requests_over_limit PASSED
# test_auth_throttle_allows_requests_under_limit PASSED
# test_auth_throttle_denies_requests_over_limit PASSED
# test_admin_throttle_allows_requests_under_limit PASSED
# test_admin_throttle_denies_requests_over_limit PASSED
# test_productos_endpoint_no_throttle PASSED
# test_carrusel_endpoint_no_throttle PASSED
```

### 1.3 Verificación Manual con Script
```bash
cd backend
bash scripts/verify_throttles.sh

# Output esperado:
# TEST 1: /api/productos/ (SIN THROTTLE)
# ✅ PASS: No hay throttle en /api/productos/
#
# TEST 2: /api/carrusel/ (SIN THROTTLE)
# ✅ PASS: No hay throttle en /api/carrusel/
#
# TEST 3: /api/auth/login/ (AUTH THROTTLE - 10/hora)
# ✅ PASS: Throttle funcionando en /api/auth/login/
```

### 1.4 Verificación Manual con cURL
```bash
# Test 1: Productos (sin throttle)
for i in {1..50}; do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8000/api/productos/
done
# Esperado: 50 x 200

# Test 2: Login (throttle 10/hora)
for i in {1..15}; do
  curl -s -o /dev/null -w "%{http_code}\n" -X POST http://localhost:8000/api/auth/login/ \
    -H "Content-Type: application/json" \
    -d '{"username": "test", "password": "wrong"}'
done
# Esperado: 10 x (200/401/400) + 5 x 429
```

---

## 🌍 PASO 2: Configurar Producción

### 2.1 Crear `.env.production`
```bash
# backend/.env.production

# ═══════════════════════════════════════════════════════════════════════════════
# 🚦 THROTTLING - Tasas para Producción (más restrictivas)
# ═══════════════════════════════════════════════════════════════════════════════

# Autenticación - Previene fuerza bruta
THROTTLE_AUTH=5/hour

# Carrito - Escritura masiva
THROTTLE_CART_WRITE=50/hour

# Checkout - Operación crítica
THROTTLE_CHECKOUT=25/hour

# Admin - Panel administrativo
THROTTLE_ADMIN=200/hour

# Usuario - Endpoints públicos (si se activa)
THROTTLE_USER=500/hour
```

### 2.2 Actualizar `config/settings.py` para Producción
```python
# En settings.py, asegurar que lee del .env

import os

# Leer DEBUG del .env
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Throttles se leen automáticamente del .env
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [],
    'DEFAULT_THROTTLE_RATES': {
        'auth': os.getenv('THROTTLE_AUTH', '10/hour'),
        'cart_write': os.getenv('THROTTLE_CART_WRITE', '100/hour'),
        'checkout': os.getenv('THROTTLE_CHECKOUT', '50/hour'),
        'admin': os.getenv('THROTTLE_ADMIN', '500/hour'),
        'user': os.getenv('THROTTLE_USER', '1000/hour'),
    },
}
```

### 2.3 Configurar Nginx (si usas reverse proxy)
```nginx
# /etc/nginx/sites-available/electro-isla

upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name electro-isla.com;

    # ✅ Importante: Forwarding de IP real para throttle basado en IP
    location / {
        proxy_pass http://django;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
    }
}
```

---

## 📊 PASO 3: Monitoreo en Producción

### 3.1 Configurar Logging de Throttles
```python
# En settings.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django/throttle.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'api': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
```

### 3.2 Monitorear Throttle Events
```bash
# Ver logs en tiempo real
tail -f /var/log/django/throttle.log

# Contar throttles por hora
grep "THROTTLE" /var/log/django/throttle.log | wc -l

# Filtrar por scope
grep "scope=auth" /var/log/django/throttle.log
grep "scope=checkout" /var/log/django/throttle.log
```

### 3.3 Alertas (Sentry / CloudWatch)
```python
# Integración con Sentry (opcional)
import sentry_sdk

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    traces_sample_rate=1.0,
)

# Los throttles se registrarán automáticamente en Sentry
```

---

## 🔄 PASO 4: Despliegue

### 4.1 Despliegue en Heroku
```bash
# Agregar variables de entorno
heroku config:set THROTTLE_AUTH=5/hour
heroku config:set THROTTLE_CART_WRITE=50/hour
heroku config:set THROTTLE_CHECKOUT=25/hour
heroku config:set THROTTLE_ADMIN=200/hour

# Desplegar
git push heroku main
```

### 4.2 Despliegue en AWS / DigitalOcean
```bash
# Actualizar .env en servidor
ssh user@server
cd /app/backend
nano .env.production
# Agregar variables de throttle

# Reiniciar Django
systemctl restart django
```

### 4.3 Despliegue en Docker
```dockerfile
# Dockerfile
FROM python:3.11

WORKDIR /app

# Copiar requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copiar código
COPY . .

# Variables de entorno (desde .env)
ENV THROTTLE_AUTH=5/hour
ENV THROTTLE_CART_WRITE=50/hour
ENV THROTTLE_CHECKOUT=25/hour
ENV THROTTLE_ADMIN=200/hour

# Ejecutar
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---

## ✅ Checklist de Despliegue

### Antes de Desplegar
- [ ] Ejecutar tests: `pytest tests/test_throttles.py -v`
- [ ] Verificar en local: `bash scripts/verify_throttles.sh`
- [ ] Revisar logs: `python manage.py runserver` (sin errores)
- [ ] Crear `.env.production` con tasas apropiadas
- [ ] Configurar Nginx/reverse proxy (X-Forwarded-For)
- [ ] Configurar logging de throttles
- [ ] Configurar alertas (Sentry/CloudWatch)

### Despliegue
- [ ] Hacer backup de BD
- [ ] Desplegar código
- [ ] Configurar variables de entorno
- [ ] Reiniciar Django/Gunicorn
- [ ] Verificar que throttles funcionan en producción

### Post-Despliegue
- [ ] Monitorear logs de throttle
- [ ] Revisar métricas de 429 responses
- [ ] Ajustar tasas si es necesario
- [ ] Documentar cambios en wiki/docs

---

## 🎯 Tasas Recomendadas por Ambiente

### Desarrollo
```
THROTTLE_AUTH=100/hour
THROTTLE_CART_WRITE=1000/hour
THROTTLE_CHECKOUT=500/hour
THROTTLE_ADMIN=5000/hour
```

### Staging
```
THROTTLE_AUTH=20/hour
THROTTLE_CART_WRITE=200/hour
THROTTLE_CHECKOUT=100/hour
THROTTLE_ADMIN=1000/hour
```

### Producción
```
THROTTLE_AUTH=5/hour
THROTTLE_CART_WRITE=50/hour
THROTTLE_CHECKOUT=25/hour
THROTTLE_ADMIN=200/hour
```

---

## 🚨 Troubleshooting

### Problema: "No default throttle rate set for 'admin' scope"
**Solución**: Verificar que `DEFAULT_THROTTLE_RATES` en settings.py incluye 'admin'

### Problema: Throttles no funcionan en producción
**Solución**: Verificar que Nginx/reverse proxy forwarda `X-Forwarded-For`

### Problema: Usuarios legítimos siendo throttled
**Solución**: Aumentar tasas en `.env.production`

### Problema: Ataques no siendo bloqueados
**Solución**: Disminuir tasas en `.env.production`

---

## 📞 Soporte

Si tienes problemas:

1. Revisar logs: `tail -f /var/log/django/throttle.log`
2. Ejecutar tests: `pytest tests/test_throttles.py -v`
3. Verificar configuración: `python manage.py shell`
4. Contactar al equipo de backend

---

## 🎉 ¡Listo para Producción!

Tu sistema de throttling está configurado profesionalmente:

✅ Protege endpoints críticos (auth, checkout)
✅ Mantiene rendimiento de API pública (sin throttle)
✅ Configurable vía env vars
✅ Monitoreable y escalable
✅ Listo para producción

**¡Vamos a hacer una web increíble! 🚀**
