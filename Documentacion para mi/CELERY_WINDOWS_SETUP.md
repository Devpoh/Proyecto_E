# 🪟 CELERY SETUP - WINDOWS (Paso a Paso)

## 📋 Resumen Rápido

Tu error es: **`ModuleNotFoundError: No module named 'django_celery_beat'`**

**Solución**: Instalar todas las dependencias con `pip install -r requirements.txt`

---

## 🚀 Instalación Rápida (Recomendado)

### Opción 1: Ejecutar Script Batch (Más fácil)

```bash
# En PowerShell o CMD, en la carpeta backend
.\install_all.bat
```

Este script:
1. ✅ Activa el venv
2. ✅ Instala todas las dependencias
3. ✅ Muestra los próximos pasos

### Opción 2: Manual (Paso a paso)

```bash
# 1. Ir a la carpeta backend
cd backend

# 2. Activar venv
venv\Scripts\activate.bat

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Verificar instalación
pip list | findstr celery
```

**Esperado:**
```
celery                    5.3.4
django-celery-beat        2.5.0
django-celery-results     2.5.1
flower                    2.0.1
```

---

## 🔧 Configuración Inicial (Una sola vez)

### Paso 1: Ejecutar Migraciones

```bash
# En la carpeta backend (con venv activado)
python manage.py migrate
python manage.py migrate django_celery_beat
python manage.py migrate django_celery_results
```

**Esperado:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, messages, staticfiles, rest_framework, rest_framework.authtoken, corsheaders, django_celery_beat, django_celery_results, api
Running migrations:
  Applying django_celery_beat.0001_initial... OK
  Applying django_celery_beat.0002_auto_20160322_0159... OK
  ...
```

### Paso 2: Verificar que Redis está corriendo

```bash
# Abrir una terminal nueva y ejecutar:
redis-server

# O si tienes Redis en PATH:
redis-cli ping
# Esperado: PONG
```

---

## 🚀 Ejecutar Celery (3 Terminales)

### Terminal 1: Redis (si no está corriendo como servicio)

```bash
redis-server
```

**Esperado:**
```
* Ready to accept connections
```

### Terminal 2: Celery Worker

```bash
cd backend
venv\Scripts\activate.bat
celery -A config worker -l info
```

**Esperado:**
```
celery@DESKTOP-XXX ready.
[Tasks]
  . api.tasks.liberar_reservas_expiradas
  . api.tasks.limpiar_tokens_expirados
```

### Terminal 3: Celery Beat

```bash
cd backend
venv\Scripts\activate.bat
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

**Esperado:**
```
celery beat v5.3.6 (emerald-rush) is starting.
[2024-11-12 02:45:00,000: INFO/MainProcess] Scheduler: Scheduling Enabled.
```

---

## ✅ Verificar que Funciona

### 1️⃣ Acceder a Django Admin

```
http://localhost:8000/admin/
```

Login y ve a: **Periodic Tasks**

Deberías ver:
- ✅ `liberar-reservas-expiradas` (cada minuto)
- ✅ `limpiar-tokens-expirados` (cada hora)

### 2️⃣ Ver logs de tareas ejecutadas

En la **Terminal 2 (Worker)**, deberías ver cada minuto:

```
[2024-11-12 02:46:00,000: INFO/MainProcess] Task api.tasks.liberar_reservas_expiradas[xxx] succeeded in 0.123s: {'status': 'success', 'reservas_liberadas': 0, ...}
```

### 3️⃣ Usar Flower para monitoreo (Opcional)

```bash
# En una terminal nueva
cd backend
venv\Scripts\activate.bat
celery -A config flower --port=5555
```

Acceder a: `http://localhost:5555`

---

## ❌ Troubleshooting

### Error: "ModuleNotFoundError: No module named 'django_celery_beat'"

```bash
# Solución:
pip install -r requirements.txt

# Verificar:
pip list | findstr django-celery-beat
```

### Error: "Connection refused" (Redis)

```bash
# Solución 1: Instalar Redis
# Descargar desde: https://github.com/microsoftarchive/redis/releases

# Solución 2: Usar Docker
docker run -d -p 6379:6379 redis:latest

# Solución 3: Verificar que está corriendo
redis-cli ping
# Esperado: PONG
```

### Error: "No module named 'celery'"

```bash
# Solución:
pip install celery[redis]
```

### Las tareas no se ejecutan

```bash
# Verificar que Beat está corriendo (Terminal 3)
# Verificar que Worker está corriendo (Terminal 2)
# Verificar que Redis está corriendo (Terminal 1)

# Si todo está corriendo, revisar logs en Django Admin:
# Periodic Tasks → Task Results
```

### Error: "worker_state_db"

```bash
# Solución: Usar flag --without-gossip en worker
celery -A config worker -l info --without-gossip
```

---

## 📊 Checklist Final

- [ ] `pip install -r requirements.txt` ejecutado
- [ ] `python manage.py migrate django_celery_beat` ejecutado
- [ ] Redis corriendo (Terminal 1)
- [ ] Celery Worker corriendo (Terminal 2)
- [ ] Celery Beat corriendo (Terminal 3)
- [ ] Tareas visibles en Django Admin → Periodic Tasks
- [ ] Logs de tareas en Terminal 2 cada minuto
- [ ] Flower accesible en http://localhost:5555 (opcional)

---

## 🎯 Resumen

| Paso | Comando | Terminal |
|------|---------|----------|
| 1 | `redis-server` | 1 |
| 2 | `celery -A config worker -l info` | 2 |
| 3 | `celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler` | 3 |
| 4 | `python manage.py runserver` | 4 (opcional) |

---

## 🚀 ¡Listo!

Una vez que todo esté corriendo:
- ✅ Reservas se liberan automáticamente cada minuto
- ✅ Tokens se limpian automáticamente cada hora
- ✅ Sin intervención manual
- ✅ Listo para producción

**¿Necesitas ayuda? Revisa los logs en cada terminal.** 🎉
