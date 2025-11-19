# 🎯 SOLUCIÓN FINAL - CELERY EN WINDOWS (ELECTRO ISLA)

## 📌 Resumen del Problema

**Error:** `ValueError: not enough values to unpack (expected 3, got 0)`

**Causa Raíz:** Celery 5.5.3 en Windows estaba usando el pool `prefork` que no es soportado en Windows.

**Solución:** Cambiar a pool `solo` (single process) que es estable en Windows.

---

## ✅ Cambios Realizados

### 1. Actualización de `config/celery.py`

```python
# ✅ Configuración para Windows - CRÍTICA
app.conf.update(
    # Pool: 'solo' = single process (más estable en Windows)
    worker_pool='solo',
    
    # Desabilitar prefetch multiplier
    worker_prefetch_multiplier=1,
    
    # Max tasks per child
    worker_max_tasks_per_child=1000,
    
    # Acks late
    task_acks_late=True,
    
    # Disable rate limits
    worker_disable_rate_limits=True,
    
    # Timeout para tareas
    task_soft_time_limit=300,  # 5 minutos
    task_time_limit=600,  # 10 minutos
)
```

**Cambio clave:** `worker_pool='solo'` en lugar de `prefork`

---

## 🚀 Cómo Usar

### Opción 1: Scripts Batch (Recomendado para Windows)

#### Iniciar Celery Worker
```bash
cd backend
INICIAR_CELERY_WINDOWS.bat
```

#### Iniciar Celery Beat
```bash
cd backend
INICIAR_CELERY_BEAT_WINDOWS.bat
```

---

### Opción 2: Línea de Comandos

#### Iniciar Celery Worker
```bash
cd backend
celery -A config worker -l info --pool=solo
```

#### Iniciar Celery Beat
```bash
cd backend
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

### Opción 3: Script PowerShell (Automatizado)

```bash
cd backend
.\INICIAR_TODO_CELERY.ps1
```

Este script inicia automáticamente:
1. Django Development Server
2. Celery Worker
3. Celery Beat
4. Flower (opcional)

---

## 📋 Requisitos

### Instalado ✅
- Python 3.13
- Django 4.2.7
- Celery 5.3.4
- django-celery-beat 2.5.0
- django-celery-results 2.5.1
- Redis 5.0.1

### Necesario en tu máquina
- **Redis** corriendo en `localhost:6379`
- **PostgreSQL** corriendo en `localhost:5432`

---

## 🔧 Configuración Actual

### Broker y Result Backend
```python
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
```

### Tareas Programadas
```python
app.conf.beat_schedule = {
    'liberar-reservas-expiradas': {
        'task': 'api.tasks.liberar_reservas_expiradas',
        'schedule': crontab(minute='*/20'),  # Cada 20 minutos
    },
    'limpiar-tokens-expirados': {
        'task': 'api.tasks.limpiar_tokens_expirados',
        'schedule': crontab(minute=0),  # Cada hora
    },
}
```

---

## ✅ Verificación Rápida

### 1. Verificar Redis
```bash
redis-cli ping
# Respuesta: PONG
```

### 2. Verificar PostgreSQL
```bash
netstat -an | find "5432"
# Debería mostrar conexión en puerto 5432
```

### 3. Iniciar Celery Worker
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

celery@DESKTOP-QPLORTF ready.
```

### 4. Probar Tarea
```bash
cd backend
python manage.py shell

from api.tasks import liberar_reservas_expiradas
result = liberar_reservas_expiradas.delay()
print(result.get())
```

---

## 📊 Archivos Creados/Modificados

### Modificados
- ✅ `config/celery.py` - Configuración para Windows

### Creados
- ✅ `INICIAR_CELERY_WINDOWS.bat` - Script para iniciar Worker
- ✅ `INICIAR_CELERY_BEAT_WINDOWS.bat` - Script para iniciar Beat
- ✅ `INICIAR_TODO_CELERY.ps1` - Script PowerShell automatizado
- ✅ `CELERY_WINDOWS_GUIA_COMPLETA.md` - Guía completa
- ✅ `VERIFICACION_CELERY.md` - Checklist de verificación
- ✅ `CELERY_SOLUCION_FINAL.md` - Este archivo

---

## 🎯 Flujo Correcto de Inicio

### Terminal 1: Redis
```bash
redis-server
```

### Terminal 2: Django
```bash
cd backend
python manage.py runserver
```

### Terminal 3: Celery Worker
```bash
cd backend
celery -A config worker -l info --pool=solo
```

### Terminal 4: Celery Beat
```bash
cd backend
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Terminal 5 (Opcional): Flower
```bash
cd backend
celery -A config flower
# Acceder a: http://localhost:5555
```

---

## 🔴 Solución de Problemas

### Error: "Cannot connect to redis://127.0.0.1:6379"
```bash
# Verificar Redis
redis-cli ping

# Si no responde, iniciar Redis
redis-server
```

### Error: "ValueError: not enough values to unpack"
```bash
# Ya está solucionado, pero si persiste:
celery -A config worker -l info --pool=solo

# O usar threads:
celery -A config worker -l info --pool=threads
```

### Error: "django.core.exceptions.ImproperlyConfigured"
```bash
# Asegúrate de estar en el directorio backend
cd backend

# Verifica que manage.py existe
ls manage.py

# Reinicia Celery
celery -A config worker -l info --pool=solo
```

---

## 📚 Documentación Relacionada

- **Guía Completa:** `CELERY_WINDOWS_GUIA_COMPLETA.md`
- **Verificación Rápida:** `VERIFICACION_CELERY.md`
- **Configuración:** `config/celery.py`
- **Tareas:** `api/tasks.py`
- **Settings:** `config/settings.py`

---

## 🎉 ¡Listo!

Celery ahora funciona correctamente en Windows. 

**Próximos pasos:**
1. Iniciar Redis
2. Iniciar Django
3. Iniciar Celery Worker
4. Iniciar Celery Beat
5. Monitorear con Flower (opcional)

---

**Última actualización:** 17 de Noviembre, 2025
**Versión:** 1.0
**Estado:** ✅ FUNCIONAL EN WINDOWS
