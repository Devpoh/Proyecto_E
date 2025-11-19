# ✅ VERIFICACIÓN RÁPIDA - CELERY EN WINDOWS

## 🎯 Checklist de Verificación

### ✓ Paso 1: Verificar Redis
```bash
# Terminal 1
redis-server

# Terminal 2
redis-cli ping
# Respuesta esperada: PONG
```

**Estado:** ✅ / ❌

---

### ✓ Paso 2: Verificar PostgreSQL
```bash
# Verificar que PostgreSQL está corriendo
netstat -an | find "5432"

# O conectar directamente
psql -U postgres -d electroIsla
```

**Estado:** ✅ / ❌

---

### ✓ Paso 3: Iniciar Django
```bash
cd backend
python manage.py runserver
# Acceder a: http://localhost:8000
```

**Estado:** ✅ / ❌

---

### ✓ Paso 4: Iniciar Celery Worker
```bash
# Terminal nueva
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

**Estado:** ✅ / ❌

---

### ✓ Paso 5: Iniciar Celery Beat
```bash
# Terminal nueva
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

**Estado:** ✅ / ❌

---

### ✓ Paso 6: Probar Tarea Manual
```bash
# Terminal nueva
cd backend
python manage.py shell

# En el shell:
from api.tasks import liberar_reservas_expiradas
result = liberar_reservas_expiradas.delay()
print(result.get())
```

**Salida esperada:**
```python
{
    'status': 'success',
    'reservas_liberadas': 0,
    'timestamp': '2025-11-17T01:30:00.000000'
}
```

**Estado:** ✅ / ❌

---

### ✓ Paso 7: Verificar en Flower (Opcional)
```bash
# Terminal nueva
cd backend
celery -A config flower

# Acceder a: http://localhost:5555
```

**Características visibles:**
- Workers activos
- Tareas completadas
- Historial de tareas
- Estadísticas

**Estado:** ✅ / ❌

---

## 🔴 Errores Comunes y Soluciones

### Error: "Cannot connect to redis://127.0.0.1:6379"

**Solución:**
```bash
# Verificar si Redis está corriendo
redis-cli ping

# Si no responde, iniciar Redis
redis-server
```

---

### Error: "ValueError: not enough values to unpack (expected 3, got 0)"

**Solución:** Ya está solucionado en `config/celery.py`

```bash
# Usar explícitamente --pool=solo
celery -A config worker -l info --pool=solo
```

---

### Error: "django.core.exceptions.ImproperlyConfigured"

**Solución:**
```bash
# Asegúrate de estar en el directorio backend
cd backend

# Verifica que manage.py existe
ls manage.py

# Reinicia Celery
celery -A config worker -l info --pool=solo
```

---

### Error: "Connection refused" en PostgreSQL

**Solución:**
```bash
# Verificar si PostgreSQL está corriendo
netstat -an | find "5432"

# Si no aparece, iniciar PostgreSQL
# Services (services.msc) → PostgreSQL → Start
```

---

## 📊 Verificación de Configuración

### Verificar config/celery.py
```bash
cd backend
python -c "from config.celery import app; print(app.conf)"
```

**Debería mostrar:**
```
worker_pool='solo'
worker_prefetch_multiplier=1
task_acks_late=True
```

---

### Verificar config/settings.py
```bash
cd backend
python -c "from django.conf import settings; print(settings.CELERY_BROKER_URL)"
```

**Debería mostrar:**
```
redis://127.0.0.1:6379/0
```

---

### Verificar api/tasks.py
```bash
cd backend
python -c "from api.tasks import liberar_reservas_expiradas, limpiar_tokens_expirados; print('Tareas cargadas correctamente')"
```

**Debería mostrar:**
```
Tareas cargadas correctamente
```

---

## 🎯 Resumen de Verificación

| Componente | Estado | Comando de Verificación |
|-----------|--------|------------------------|
| Redis | ✅/❌ | `redis-cli ping` |
| PostgreSQL | ✅/❌ | `psql -U postgres -d electroIsla` |
| Django | ✅/❌ | `python manage.py runserver` |
| Celery Worker | ✅/❌ | `celery -A config worker -l info --pool=solo` |
| Celery Beat | ✅/❌ | `celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler` |
| Tareas | ✅/❌ | `python manage.py shell` → `liberar_reservas_expiradas.delay()` |
| Flower | ✅/❌ | `celery -A config flower` |

---

## 🚀 Próximos Pasos

Si todo está ✅:

1. **Verificar logs en tiempo real:**
   ```bash
   celery -A config worker -l debug
   ```

2. **Monitorear con Flower:**
   ```bash
   celery -A config flower
   # Acceder a: http://localhost:5555
   ```

3. **Crear tareas personalizadas:**
   - Editar `api/tasks.py`
   - Agregar a `config/celery.py`
   - Reiniciar Celery Beat

4. **Implementar en producción:**
   - Usar Supervisor o systemd
   - Configurar SSL/TLS para Redis
   - Usar autenticación en Redis

---

**Última actualización:** 17 de Noviembre, 2025
**Estado:** ✅ Listo para usar
