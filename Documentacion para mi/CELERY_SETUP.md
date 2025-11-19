# 🚀 CELERY SETUP - Guía Completa

## 📋 Resumen

Tu sistema ahora tiene **Celery + Beat** configurado para:
- ✅ Liberar reservas de stock expiradas **cada minuto**
- ✅ Limpiar tokens JWT expirados **cada hora**
- ✅ Ejecutar tareas en segundo plano sin bloquear el servidor
- ✅ Listo para producción con Redis como broker

---

## 🔧 Instalación de Dependencias

```bash
# Instalar Celery y dependencias
pip install celery[redis] django-celery-beat django-celery-results

# Verificar instalación
celery --version
```

---

## 📦 Estructura Implementada

```
backend/
├── config/
│   ├── __init__.py          ← Importa Celery app
│   ├── celery.py            ← Configuración de Celery
│   ├── settings.py          ← Configuración de Django + Celery
│   └── ...
├── api/
│   ├── tasks.py             ← Tareas asincrónicas
│   ├── models.py
│   └── ...
└── manage.py
```

---

## 🚀 Ejecución en Desarrollo

### Terminal 1: Redis (si no está corriendo)

```bash
# En Windows (si tienes WSL o Redis instalado)
redis-server

# O si usas Docker
docker run -d -p 6379:6379 redis:latest
```

### Terminal 2: Celery Worker

```bash
cd backend
celery -A config worker -l info
```

**Esperado:**
```
celery@DESKTOP-XXX ready.
[Tasks]
  . api.tasks.liberar_reservas_expiradas
  . api.tasks.limpiar_tokens_expirados
```

### Terminal 3: Celery Beat (Scheduler)

```bash
cd backend
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

**Esperado:**
```
celery beat v5.x.x (...)
[2024-11-12 02:45:00,000: INFO/MainProcess] Scheduler: Scheduling Enabled.
```

---

## 📊 Verificar que Funciona

### 1️⃣ Crear una migración para django-celery-beat

```bash
cd backend
python manage.py migrate django_celery_beat
python manage.py migrate django_celery_results
```

### 2️⃣ Acceder a Django Admin

```
http://localhost:8000/admin/
```

Ir a: **Periodic Tasks** → Deberías ver:
- ✅ `liberar-reservas-expiradas` (cada minuto)
- ✅ `limpiar-tokens-expirados` (cada hora)

### 3️⃣ Monitorear tareas en tiempo real

```bash
# En otra terminal
celery -A config events

# O usar Flower (UI web)
pip install flower
celery -A config flower
# Acceder a http://localhost:5555
```

---

## 🔍 Logs y Debugging

### Ver logs de Celery

```bash
# En el terminal del worker, verás algo como:
[2024-11-12 02:46:00,000: INFO/MainProcess] Task api.tasks.liberar_reservas_expiradas[xxx] succeeded in 0.123s: {'status': 'success', 'reservas_liberadas': 3, ...}
```

### Logs en archivo

Los logs se guardan en:
- `backend/logs/celery.log` (si lo configuras)

### Verificar reservas liberadas

```python
# En Django shell
python manage.py shell

from api.models import StockReservation
from django.utils import timezone

# Ver reservas expiradas
expiradas = StockReservation.objects.filter(status='expired')
print(f"Total reservas expiradas: {expiradas.count()}")

# Ver última liberación
ultima = expiradas.order_by('-cancelled_at').first()
print(f"Última liberación: {ultima.cancelled_at}")
```

---

## 🌐 Configuración en Producción

### 1️⃣ Variables de Entorno (.env)

```env
# Redis
CELERY_BROKER_URL=redis://redis-server:6379/0
CELERY_RESULT_BACKEND=redis://redis-server:6379/0

# Django
DEBUG=False
ALLOWED_HOSTS=electro-isla.com,www.electro-isla.com
```

### 2️⃣ Usar Supervisor o Systemd

#### Opción A: Supervisor (recomendado)

```bash
# Instalar
pip install supervisor

# Crear config
sudo nano /etc/supervisor/conf.d/celery.conf
```

**Contenido:**
```ini
[program:celery_worker]
command=celery -A config worker -l info
directory=/home/user/electro-isla/backend
user=www-data
numprocs=1
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600

[program:celery_beat]
command=celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/home/user/electro-isla/backend
user=www-data
numprocs=1
stdout_logfile=/var/log/celery/beat.log
stderr_logfile=/var/log/celery/beat.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
```

```bash
# Aplicar cambios
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery_worker celery_beat
```

#### Opción B: Systemd

```bash
# Crear servicio
sudo nano /etc/systemd/system/celery-worker.service
```

**Contenido:**
```ini
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/home/user/electro-isla/backend
ExecStart=/usr/bin/celery -A config worker -l info --logfile=/var/log/celery/worker.log --pidfile=/var/run/celery/worker.pid
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y iniciar
sudo systemctl enable celery-worker
sudo systemctl start celery-worker
sudo systemctl status celery-worker
```

### 3️⃣ Monitoreo

```bash
# Ver estado de workers
celery -A config inspect active

# Ver estadísticas
celery -A config inspect stats

# Ver tareas registradas
celery -A config inspect registered
```

---

## ⚠️ Troubleshooting

### Problema: "Connection refused" (Redis no está corriendo)

```bash
# Solución: Iniciar Redis
redis-server

# O verificar que está corriendo
redis-cli ping
# Esperado: PONG
```

### Problema: "No module named 'celery'"

```bash
# Solución: Instalar Celery
pip install celery[redis]
```

### Problema: Tareas no se ejecutan

```bash
# 1. Verificar que Beat está corriendo
# 2. Verificar que Worker está corriendo
# 3. Revisar logs en Django Admin → Periodic Tasks → Task Results
# 4. Ejecutar manualmente:

python manage.py shell
from api.tasks import liberar_reservas_expiradas
liberar_reservas_expiradas.delay()
```

### Problema: "DatabaseScheduler not found"

```bash
# Solución: Ejecutar migraciones
python manage.py migrate django_celery_beat
```

---

## 📈 Monitoreo en Producción

### Usar Flower (UI Web)

```bash
# Instalar
pip install flower

# Ejecutar
celery -A config flower --port=5555

# Acceder a http://localhost:5555
```

**Flower muestra:**
- ✅ Estado de workers
- ✅ Tareas ejecutadas
- ✅ Errores y excepciones
- ✅ Estadísticas en tiempo real

---

## 🎯 Resumen de Tareas Configuradas

| Tarea | Frecuencia | Función |
|-------|-----------|---------|
| `liberar_reservas_expiradas` | Cada minuto | Libera stock de reservas vencidas |
| `limpiar_tokens_expirados` | Cada hora | Limpia tokens JWT expirados |

---

## ✅ Checklist Final

- [ ] Redis instalado y corriendo
- [ ] Celery instalado (`pip install celery[redis]`)
- [ ] `django-celery-beat` y `django-celery-results` instalados
- [ ] Migraciones ejecutadas (`python manage.py migrate`)
- [ ] Worker corriendo (`celery -A config worker -l info`)
- [ ] Beat corriendo (`celery -A config beat -l info`)
- [ ] Tareas visibles en Django Admin → Periodic Tasks
- [ ] Reservas se liberan automáticamente cada minuto
- [ ] Logs en `backend/logs/` (si está configurado)

---

## 🚀 ¡Listo para Producción!

Tu sistema ahora:
- ✅ Libera reservas expiradas automáticamente
- ✅ Limpia tokens JWT expirados
- ✅ Escala con múltiples workers
- ✅ Monitoreable con Flower
- ✅ Listo para producción con Redis

**No necesitas hacer nada más. Celery se encargará de todo en segundo plano.** 🎉
