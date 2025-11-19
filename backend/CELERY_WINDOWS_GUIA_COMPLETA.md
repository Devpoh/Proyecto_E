# 🚀 GUÍA COMPLETA: CELERY EN WINDOWS - ELECTRO ISLA

## 📋 Tabla de Contenidos
1. [Requisitos](#requisitos)
2. [Instalación](#instalación)
3. [Configuración](#configuración)
4. [Iniciar Servicios](#iniciar-servicios)
5. [Verificación](#verificación)
6. [Solución de Problemas](#solución-de-problemas)
7. [Monitoreo](#monitoreo)

---

## 📦 Requisitos

### Software Necesario
- **Python 3.8+** (instalado)
- **Redis** (para broker y result backend)
- **PostgreSQL** (para base de datos)
- **Django 4.2+** (instalado)
- **Celery 5.3+** (instalado)

### Verificar Instalación
```bash
python --version          # Python 3.8+
redis-cli --version       # Redis instalado
psql --version           # PostgreSQL instalado
pip show celery          # Celery instalado
```

---

## 🔧 Instalación

### 1. Instalar Redis en Windows

#### Opción A: Usar Windows Subsystem for Linux (WSL)
```bash
# En WSL (Ubuntu)
sudo apt-get install redis-server
redis-server
```

#### Opción B: Usar Docker
```bash
docker run -d -p 6379:6379 redis:latest
```

#### Opción C: Descargar binario Windows
1. Descargar desde: https://github.com/microsoftarchive/redis/releases
2. Ejecutar `redis-server.exe`

#### Opción D: Usar Windows Package Manager (Recomendado)
```bash
# Con Chocolatey
choco install redis-64

# Con Scoop
scoop install redis
```

### 2. Verificar Redis
```bash
# En una terminal
redis-server

# En otra terminal
redis-cli ping
# Respuesta: PONG
```

### 3. Instalar dependencias Python
```bash
cd backend
pip install -r requirements.txt
```

---

## ⚙️ Configuración

### 1. Configuración de Celery (Ya hecha)

**Archivo:** `config/celery.py`

```python
# Pool para Windows (CRÍTICO)
app.conf.update(
    worker_pool='solo',  # Single process, estable en Windows
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=True,
)
```

### 2. Configuración de Django (Ya hecha)

**Archivo:** `config/settings.py`

```python
# Broker (donde se almacenan las tareas)
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'

# Result backend (donde se guardan resultados)
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

# Scheduler para tareas programadas
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
```

### 3. Variables de Entorno

**Archivo:** `.env` (Ya configurado)

```env
DB_NAME=electroIsla
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=django-insecure-change-this-in-production-123456789
DEBUG=True
```

---

## 🚀 Iniciar Servicios

### Orden Correcto de Inicio

#### 1️⃣ Iniciar Redis
```bash
# Opción A: Desde WSL
wsl redis-server

# Opción B: Desde Docker
docker run -d -p 6379:6379 redis:latest

# Opción C: Desde binario Windows
redis-server.exe

# Opción D: Desde Chocolatey/Scoop
redis-server
```

**Verificar:**
```bash
redis-cli ping
# Respuesta: PONG
```

#### 2️⃣ Iniciar PostgreSQL
```bash
# Asegúrate de que PostgreSQL está corriendo
# En Windows, generalmente está como servicio
# Verificar: Services (services.msc) → PostgreSQL

psql -U postgres
# Debería conectar a la BD
```

#### 3️⃣ Iniciar Django Development Server
```bash
cd backend
python manage.py runserver
# Acceder a: http://localhost:8000
```

#### 4️⃣ Iniciar Celery Worker (Nueva Terminal)
```bash
cd backend
celery -A config worker -l info --pool=solo
```

**Salida esperada:**
```
[tasks]
  . api.tasks.liberar_reservas_expiradas
  . api.tasks.limpiar_tokens_expirados
  . config.celery.debug_task

celery@DESKTOP-XXXX ready.
```

#### 5️⃣ Iniciar Celery Beat (Nueva Terminal)
```bash
cd backend
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

**Salida esperada:**
```
celery beat v5.3.4 (immunity) is starting.
LocalTime -> 2025-11-17 01:28:10
Configuration ->
    . broker -> redis://127.0.0.1:6379/0
    . scheduler -> django_celery_beat.schedulers.DatabaseScheduler
```

#### 6️⃣ (Opcional) Iniciar Flower - Monitor de Celery
```bash
cd backend
celery -A config flower
# Acceder a: http://localhost:5555
```

---

## ✅ Verificación

### 1. Verificar Redis
```bash
redis-cli
> PING
PONG

> INFO
# Debería mostrar información del servidor Redis
```

### 2. Verificar Celery Worker
```bash
# En la terminal del worker, debería ver:
# [tasks]
#   . api.tasks.liberar_reservas_expiradas
#   . api.tasks.limpiar_tokens_expirados
#   . config.celery.debug_task
# celery@DESKTOP-XXXX ready.
```

### 3. Verificar Celery Beat
```bash
# En la terminal de Beat, debería ver:
# celery beat v5.3.4 (immunity) is starting.
# DatabaseScheduler: Schedule changed.
```

### 4. Probar Tarea Manual
```bash
cd backend
python manage.py shell

# En el shell de Django:
from api.tasks import liberar_reservas_expiradas
result = liberar_reservas_expiradas.delay()
print(result.get())  # Esperar resultado
```

### 5. Verificar en Base de Datos
```bash
psql -U postgres -d electroIsla

# Ver tareas programadas
SELECT * FROM django_celery_beat_periodictask;

# Ver resultados de tareas
SELECT * FROM django_celery_results_taskresult;
```

---

## 🔴 Solución de Problemas

### Error: "Cannot connect to redis://127.0.0.1:6379"

**Causa:** Redis no está corriendo

**Solución:**
```bash
# Verificar si Redis está corriendo
netstat -an | find "6379"

# Si no aparece, iniciar Redis:
redis-server
```

### Error: "ValueError: not enough values to unpack (expected 3, got 0)"

**Causa:** Celery está usando pool 'prefork' en Windows (no soportado)

**Solución:** Ya está solucionado en `config/celery.py`
```python
worker_pool='solo'  # Usar single process
```

**Si aún falla:**
```bash
# Usar --pool=solo explícitamente
celery -A config worker -l info --pool=solo

# O usar --pool=threads
celery -A config worker -l info --pool=threads
```

### Error: "Soft timeouts are not supported on this platform"

**Causa:** Windows no soporta SIGUSR1 signal

**Solución:** Es solo una advertencia, no afecta funcionamiento

```python
# Ya está configurado en config/celery.py
worker_disable_rate_limits=True
```

### Error: "No module named 'api.tasks'"

**Causa:** Celery no encontró las tareas

**Solución:**
```bash
# Verificar que estás en el directorio backend
cd backend

# Verificar que api/tasks.py existe
ls api/tasks.py

# Reiniciar Celery
celery -A config worker -l info --pool=solo
```

### Error: "django.core.exceptions.ImproperlyConfigured"

**Causa:** Django settings no están configurados

**Solución:**
```bash
# Verificar DJANGO_SETTINGS_MODULE
set DJANGO_SETTINGS_MODULE=config.settings

# O ejecutar desde el directorio backend
cd backend
celery -A config worker -l info --pool=solo
```

### Error: "Connection refused" en PostgreSQL

**Causa:** PostgreSQL no está corriendo

**Solución:**
```bash
# Verificar si PostgreSQL está corriendo
netstat -an | find "5432"

# Si no aparece, iniciar PostgreSQL
# En Windows, generalmente está como servicio
# Services (services.msc) → PostgreSQL → Start

# O desde línea de comandos
pg_ctl -D "C:\Program Files\PostgreSQL\14\data" start
```

---

## 📊 Monitoreo

### 1. Flower - Monitor Web
```bash
cd backend
celery -A config flower

# Acceder a: http://localhost:5555
```

**Características:**
- Ver tareas en tiempo real
- Ver workers activos
- Ver historial de tareas
- Ver estadísticas

### 2. Logs de Celery
```bash
# Ver logs en tiempo real
celery -A config worker -l debug

# Guardar logs en archivo
celery -A config worker -l info --logfile=celery.log
```

### 3. Verificar Tareas en BD
```bash
cd backend
python manage.py shell

from django_celery_results.models import TaskResult
from django_celery_beat.models import PeriodicTask

# Ver tareas completadas
TaskResult.objects.all()

# Ver tareas programadas
PeriodicTask.objects.all()
```

### 4. Redis Monitor
```bash
redis-cli
> MONITOR

# Verá todos los comandos ejecutados en Redis
```

---

## 📝 Tareas Programadas

### Tareas Actuales

#### 1. liberar_reservas_expiradas
- **Frecuencia:** Cada 20 minutos
- **Función:** Libera stock de reservas vencidas
- **Ubicación:** `api/tasks.py`

#### 2. limpiar_tokens_expirados
- **Frecuencia:** Cada hora
- **Función:** Limpia tokens JWT expirados de la blacklist
- **Ubicación:** `api/tasks.py`

### Agregar Nueva Tarea

**1. Crear función en `api/tasks.py`:**
```python
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def mi_nueva_tarea(self):
    """Descripción de la tarea"""
    try:
        # Código de la tarea
        return {'status': 'success'}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```

**2. Agregar a `config/celery.py`:**
```python
app.conf.beat_schedule = {
    'mi-nueva-tarea': {
        'task': 'api.tasks.mi_nueva_tarea',
        'schedule': crontab(minute='*/5'),  # Cada 5 minutos
    },
}
```

**3. Reiniciar Celery Beat**

---

## 🔒 Seguridad

### Recomendaciones para Producción

1. **Usar Redis con autenticación**
   ```python
   CELERY_BROKER_URL = 'redis://:password@127.0.0.1:6379/0'
   ```

2. **Usar SSL/TLS**
   ```python
   CELERY_BROKER_URL = 'rediss://:password@127.0.0.1:6379/0'
   ```

3. **Usar Supervisor para gestionar procesos**
   ```ini
   [program:celery_worker]
   command=celery -A config worker -l info --pool=solo
   directory=/path/to/backend
   autostart=true
   autorestart=true
   ```

4. **Usar systemd en Linux**
   ```ini
   [Unit]
   Description=Celery Worker
   After=network.target
   
   [Service]
   Type=forking
   User=www-data
   ExecStart=/path/to/venv/bin/celery -A config worker -l info
   ```

---

## 📚 Referencias

- [Celery Documentation](https://docs.celeryproject.org/)
- [Celery Windows Support](https://docs.celeryproject.org/en/stable/platforms/windows.html)
- [Django Celery Beat](https://github.com/celery/django-celery-beat)
- [Redis Documentation](https://redis.io/documentation)
- [Flower Documentation](https://flower.readthedocs.io/)

---

## 🆘 Soporte

Si encuentras problemas:

1. **Verifica los logs:**
   ```bash
   celery -A config worker -l debug
   ```

2. **Verifica Redis:**
   ```bash
   redis-cli ping
   ```

3. **Verifica PostgreSQL:**
   ```bash
   psql -U postgres -d electroIsla
   ```

4. **Reinicia todo:**
   ```bash
   # Detener todos los servicios (Ctrl+C)
   # Reiniciar Redis
   # Reiniciar Worker
   # Reiniciar Beat
   ```

---

**Última actualización:** 17 de Noviembre, 2025
**Versión:** 1.0
**Estado:** ✅ Funcional en Windows
