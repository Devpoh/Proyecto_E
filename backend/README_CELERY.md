# 🚀 CELERY - ELECTRO ISLA

## 📌 Estado Actual

✅ **FUNCIONANDO CORRECTAMENTE EN WINDOWS**

---

## 🎯 Resumen Ejecutivo

### Problema
Celery 5.5.3 en Windows fallaba con: `ValueError: not enough values to unpack (expected 3, got 0)`

### Causa
Pool `prefork` no es soportado en Windows

### Solución
Cambiar a pool `solo` (single process)

### Resultado
✅ Celery funciona perfectamente en Windows

---

## 🚀 Inicio Rápido (2 minutos)

### Opción 1: Script Batch (Recomendado)
```bash
cd backend
INICIAR_CELERY_WINDOWS.bat
```

### Opción 2: Línea de Comandos
```bash
cd backend
celery -A config worker -l info --pool=solo
```

### Opción 3: Script PowerShell (Automatizado)
```bash
cd backend
.\INICIAR_TODO_CELERY.ps1
```

---

## 📋 Checklist de Inicio

- [ ] Redis corriendo: `redis-cli ping` → PONG
- [ ] PostgreSQL corriendo: `netstat -an | find "5432"`
- [ ] Django iniciado: `python manage.py runserver`
- [ ] Celery Worker: `celery -A config worker -l info --pool=solo`
- [ ] Celery Beat: `celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler`

---

## 📊 Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                    ELECTRO ISLA                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐      ┌──────────────┐                │
│  │   Django     │      │   Frontend   │                │
│  │   (8000)     │      │   (5173)     │                │
│  └──────┬───────┘      └──────────────┘                │
│         │                                               │
│         ├─────────────────────┬───────────────────┐    │
│         │                     │                   │    │
│    ┌────▼────┐          ┌─────▼──────┐    ┌──────▼──┐ │
│    │ Celery  │          │   Redis    │    │   PG    │ │
│    │ Worker  │          │  (6379)    │    │ (5432)  │ │
│    └────┬────┘          └────────────┘    └─────────┘ │
│         │                                               │
│    ┌────▼────┐                                         │
│    │ Celery  │                                         │
│    │  Beat   │                                         │
│    └─────────┘                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Archivos Importantes

### Configuración
- `config/celery.py` - Configuración de Celery
- `config/settings.py` - Configuración de Django
- `api/tasks.py` - Tareas asincrónicas

### Scripts
- `INICIAR_CELERY_WINDOWS.bat` - Iniciar Worker
- `INICIAR_CELERY_BEAT_WINDOWS.bat` - Iniciar Beat
- `INICIAR_TODO_CELERY.ps1` - Iniciar todo automáticamente

### Documentación
- `PASO_A_PASO_CELERY.md` - Guía paso a paso
- `CELERY_WINDOWS_GUIA_COMPLETA.md` - Guía completa
- `VERIFICACION_CELERY.md` - Checklist de verificación
- `CELERY_SOLUCION_FINAL.md` - Solución final

---

## 🎯 Tareas Programadas

### 1. Liberar Reservas Expiradas
- **Frecuencia:** Cada 20 minutos
- **Función:** Libera stock de reservas vencidas
- **Ubicación:** `api/tasks.py`

### 2. Limpiar Tokens Expirados
- **Frecuencia:** Cada hora
- **Función:** Limpia tokens JWT expirados
- **Ubicación:** `api/tasks.py`

---

## 🔧 Configuración Actual

```python
# Pool para Windows
worker_pool='solo'

# Broker (Redis)
CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'

# Result Backend (Redis)
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

# Scheduler
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
```

---

## 📊 Monitoreo

### Flower (Web UI)
```bash
celery -A config flower
# Acceder a: http://localhost:5555
```

### Logs en Tiempo Real
```bash
celery -A config worker -l debug
```

### Redis Monitor
```bash
redis-cli
> MONITOR
```

---

## 🔴 Solución de Problemas

### Error: "Cannot connect to redis"
```bash
redis-cli ping
# Si no responde, iniciar: redis-server
```

### Error: "ValueError: not enough values to unpack"
```bash
# Ya está solucionado, usar:
celery -A config worker -l info --pool=solo
```

### Error: "Connection refused" en PostgreSQL
```bash
# Verificar: netstat -an | find "5432"
# Si no aparece, iniciar PostgreSQL desde Services
```

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| `PASO_A_PASO_CELERY.md` | Guía paso a paso (5-10 min) |
| `CELERY_WINDOWS_GUIA_COMPLETA.md` | Guía completa y detallada |
| `VERIFICACION_CELERY.md` | Checklist de verificación |
| `CELERY_SOLUCION_FINAL.md` | Resumen de la solución |

---

## 🎉 ¡Listo!

Celery está configurado y listo para usar en Windows.

**Próximos pasos:**
1. Iniciar Redis
2. Iniciar Django
3. Iniciar Celery Worker
4. Iniciar Celery Beat
5. Monitorear con Flower

---

## 📞 Soporte

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

4. **Lee la documentación:**
   - `PASO_A_PASO_CELERY.md`
   - `CELERY_WINDOWS_GUIA_COMPLETA.md`

---

**Última actualización:** 17 de Noviembre, 2025
**Versión:** 1.0
**Estado:** ✅ FUNCIONAL EN WINDOWS
