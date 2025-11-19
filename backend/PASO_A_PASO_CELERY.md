# 📝 PASO A PASO - CELERY EN WINDOWS

## 🎯 Objetivo
Tener Celery funcionando perfectamente en Windows para Electro Isla.

---

## ⏱️ Tiempo Estimado: 5-10 minutos

---

## 📋 Paso 1: Verificar Requisitos (1 minuto)

### 1.1 Verificar Python
```bash
python --version
# Debería mostrar: Python 3.13.x
```

### 1.2 Verificar que estamos en el directorio correcto
```bash
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
ls manage.py
# Debería mostrar: manage.py
```

### 1.3 Verificar Redis
```bash
redis-cli ping
# Debería mostrar: PONG
```

**Si Redis no está corriendo:**
```bash
# Opción A: Desde WSL
wsl redis-server

# Opción B: Desde Docker
docker run -d -p 6379:6379 redis:latest

# Opción C: Desde binario
redis-server.exe

# Opción D: Desde Chocolatey
redis-server
```

### 1.4 Verificar PostgreSQL
```bash
netstat -an | find "5432"
# Debería mostrar: TCP 127.0.0.1:5432 LISTENING
```

**Si PostgreSQL no está corriendo:**
```bash
# Abrir Services (services.msc)
# Buscar "PostgreSQL"
# Click derecho → Start
```

---

## 🔧 Paso 2: Verificar Configuración (1 minuto)

### 2.1 Verificar config/celery.py
```bash
cd backend
type config\celery.py | find "worker_pool"
# Debería mostrar: worker_pool='solo'
```

### 2.2 Verificar config/settings.py
```bash
python -c "from django.conf import settings; print(settings.CELERY_BROKER_URL)"
# Debería mostrar: redis://127.0.0.1:6379/0
```

### 2.3 Verificar api/tasks.py
```bash
python -c "from api.tasks import liberar_reservas_expiradas; print('OK')"
# Debería mostrar: OK
```

---

## 🚀 Paso 3: Iniciar Servicios (3-5 minutos)

### 3.1 Abrir Terminal 1 - Django
```bash
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
python manage.py runserver
```

**Salida esperada:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

**Verificar:** Acceder a http://localhost:8000 en el navegador

---

### 3.2 Abrir Terminal 2 - Celery Worker
```bash
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
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

**Verificar:** Ver "celery@DESKTOP-XXXX ready."

---

### 3.3 Abrir Terminal 3 - Celery Beat
```bash
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
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

**Verificar:** Ver "celery beat v5.3.4 (immunity) is starting."

---

## ✅ Paso 4: Verificación Final (1 minuto)

### 4.1 Verificar que todo está corriendo
```bash
# Terminal 4 - Verificar servicios
netstat -an | find "6379"   # Redis
netstat -an | find "5432"   # PostgreSQL
netstat -an | find "8000"   # Django
```

**Debería mostrar:**
```
TCP 127.0.0.1:6379 LISTENING    # Redis
TCP 127.0.0.1:5432 LISTENING    # PostgreSQL
TCP 127.0.0.1:8000 LISTENING    # Django
```

### 4.2 Probar Tarea Manual
```bash
# Terminal 4 - Nuevo shell
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
python manage.py shell

# En el shell de Django:
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

### 4.3 Verificar en Flower (Opcional)
```bash
# Terminal 5 - Flower
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
celery -A config flower

# Acceder a: http://localhost:5555
```

**Debería mostrar:**
- Workers activos
- Tareas completadas
- Historial

---

## 🎉 ¡Listo!

Si todo está ✅, Celery está funcionando correctamente.

---

## 📊 Resumen de Terminales

| Terminal | Comando | Puerto | Estado |
|----------|---------|--------|--------|
| 1 | `python manage.py runserver` | 8000 | ✅ |
| 2 | `celery -A config worker -l info --pool=solo` | - | ✅ |
| 3 | `celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler` | - | ✅ |
| 4 | `python manage.py shell` (para pruebas) | - | ✅ |
| 5 | `celery -A config flower` (opcional) | 5555 | ✅ |

---

## 🔴 Si Algo Falla

### Error: "Cannot connect to redis"
```bash
# Verificar Redis
redis-cli ping

# Si no responde, iniciar Redis
redis-server
```

### Error: "ValueError: not enough values to unpack"
```bash
# Usar --pool=solo explícitamente
celery -A config worker -l info --pool=solo
```

### Error: "Connection refused" en PostgreSQL
```bash
# Verificar PostgreSQL
netstat -an | find "5432"

# Si no aparece, iniciar desde Services
# services.msc → PostgreSQL → Start
```

### Error: "django.core.exceptions.ImproperlyConfigured"
```bash
# Asegúrate de estar en el directorio backend
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend

# Verifica que manage.py existe
ls manage.py

# Reinicia Celery
celery -A config worker -l info --pool=solo
```

---

## 💡 Tips Útiles

### Ver logs en tiempo real
```bash
celery -A config worker -l debug
```

### Guardar logs en archivo
```bash
celery -A config worker -l info --logfile=celery.log
```

### Detener un servicio
```bash
# En la terminal donde está corriendo
Ctrl+C
```

### Reiniciar todo
```bash
# Detener todas las terminales (Ctrl+C)
# Cerrar todas las ventanas
# Reiniciar desde el Paso 3
```

---

## 📚 Documentación Completa

- **Guía Completa:** `CELERY_WINDOWS_GUIA_COMPLETA.md`
- **Verificación Rápida:** `VERIFICACION_CELERY.md`
- **Solución Final:** `CELERY_SOLUCION_FINAL.md`

---

## 🎯 Próximos Pasos

1. ✅ Celery funcionando
2. ⏳ Crear tareas personalizadas
3. ⏳ Implementar en producción
4. ⏳ Configurar alertas

---

**Última actualización:** 17 de Noviembre, 2025
**Versión:** 1.0
**Estado:** ✅ LISTO PARA USAR
