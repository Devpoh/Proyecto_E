# 🚀 CÓMO INICIAR CELERY (Reactivado)

**Fecha:** 12 de Noviembre, 2025  
**Status:** ✅ Celery 5.5.3 Reactivado

---

## 📋 REQUISITOS

- ✅ Redis corriendo en `127.0.0.1:6379`
- ✅ Django servidor corriendo en `http://0.0.0.0:8000`
- ✅ Celery 5.5.3 instalado (`pip show celery`)

---

## 🚀 INICIAR CELERY (3 Terminales)

### Terminal 1: Django Server
```bash
cd backend
python manage.py runserver 0.0.0.0:8000
```

Deberías ver:
```
Starting development server at http://0.0.0.0:8000/
```

---

### Terminal 2: Celery Worker
```bash
cd backend
celery -A config worker -l info
```

O usa el script:
```bash
.\INICIAR_CELERY.bat
```

Deberías ver:
```
celery@DESKTOP-QPLORTF v5.5.3 (immunity)
[tasks]
  . api.tasks.liberar_reservas_expiradas
  . api.tasks.limpiar_tokens_expirados
  . config.celery.debug_task

celery@DESKTOP-QPLORTF ready.
```

✅ **Sin errores `ValueError`**

---

### Terminal 3: Celery Beat (Tareas Programadas)
```bash
cd backend
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

O usa el script:
```bash
.\INICIAR_CELERY_BEAT.bat
```

Deberías ver:
```
celery beat v5.5.3 (emerald-rush) is starting.
Configuration ->
    . broker -> redis://127.0.0.1:6379/0
    . scheduler -> django_celery_beat.schedulers.DatabaseScheduler

[2025-11-12 23:27:03,048: INFO/MainProcess] beat: Starting...
```

---

## ✅ VERIFICACIÓN

### 1. Celery Worker ejecutando tareas
```
[2025-11-12 23:27:44,172: INFO/MainProcess] celery@DESKTOP-QPLORTF ready.
```

### 2. Celery Beat enviando tareas programadas
```
[2025-11-12 23:20:00,002: INFO/MainProcess] Scheduler: Sending due task liberar-reservas-expiradas
```

### 3. Tareas completándose sin errores
```
[2025-11-12 23:20:00,049: INFO/MainProcess] Task api.tasks.liberar_reservas_expiradas[...] succeeded
```

---

## 🔍 MONITOREO

### Ver tareas en tiempo real
```bash
celery -A config events
```

### Ver estado del worker
```bash
celery -A config inspect active
```

### Ver tareas completadas
```bash
celery -A config inspect registered
```

---

## 🐛 TROUBLESHOOTING

### Error: "Connection refused"
```
❌ Redis no está corriendo
✅ Solución: Inicia Redis en otra terminal
```

### Error: "ValueError: not enough values to unpack"
```
❌ Celery 5.3.4 (versión vieja)
✅ Solución: pip install --upgrade celery>=5.4.0
```

### Tareas no se ejecutan
```
❌ Worker no está corriendo
✅ Solución: Inicia Celery worker en Terminal 2
```

### Beat no envía tareas
```
❌ Beat no está corriendo
✅ Solución: Inicia Celery beat en Terminal 3
```

---

## 📊 TAREAS PROGRAMADAS

### Liberar Reservas Expiradas
- **Frecuencia:** Cada 20 minutos
- **Tarea:** `api.tasks.liberar_reservas_expiradas`
- **Función:** Libera stock reservado de pedidos expirados

### Limpiar Tokens Expirados
- **Frecuencia:** Cada hora
- **Tarea:** `api.tasks.limpiar_tokens_expirados`
- **Función:** Elimina tokens JWT expirados de la blacklist

---

## 🎯 RESUMEN

| Componente | Comando | Terminal |
|-----------|---------|----------|
| Django | `python manage.py runserver 0.0.0.0:8000` | 1 |
| Celery Worker | `celery -A config worker -l info` | 2 |
| Celery Beat | `celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler` | 3 |

---

## ✅ ESTADO

- ✅ Celery 5.5.3 instalado
- ✅ Bug ValueError solucionado
- ✅ Redis configurado
- ✅ Tareas programadas configuradas
- ✅ Invalidación de caché implementada

**¡Celery está listo para usar!**

