# 🔧 Troubleshooting: Celery + Redis Connection Issues

## ❌ Error Que Recibiste

```
redis.exceptions.ConnectionError: Error while reading from 127.0.0.1:6379
ConnectionResetError: [WinError 10054] Se ha forzado la interrupción de una conexión existente por el host remoto
```

## 🔍 ¿Qué significa?

Redis perdió la conexión con Celery. Esto puede ocurrir por:

1. **Redis se cayó** - El servicio se detuvo
2. **Timeout de conexión** - Redis cerró la conexión por inactividad
3. **Problema de memoria** - Redis se quedó sin memoria
4. **Windows cerró la conexión** - Problema temporal de red
5. **Firewall/Antivirus** - Bloqueó la conexión

---

## ✅ Soluciones

### 1️⃣ Verificar que Redis está corriendo

**En PowerShell:**
```powershell
# Ver si Redis está activo
Get-Process redis-server

# Si no está, inicia Redis
redis-server

# O si usas WSL/Docker
docker ps | grep redis
```

### 2️⃣ Reiniciar Redis

```powershell
# Detener Redis
redis-cli shutdown

# Esperar 2 segundos
Start-Sleep -Seconds 2

# Iniciar Redis nuevamente
redis-server
```

### 3️⃣ Limpiar la caché de Redis

```powershell
# Conectar a Redis
redis-cli

# Dentro de redis-cli:
FLUSHALL  # Limpiar todo
QUIT      # Salir
```

### 4️⃣ Verificar que Celery se reconecta automáticamente

**Configuración mejorada en `config/celery.py`:**
```python
app.conf.update(
    # ✅ Reconexión automática
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    
    # ✅ Heartbeat para mantener conexión viva
    broker_heartbeat=30,
    
    # ✅ Cancelar tareas largas en desconexión
    worker_cancel_long_running_tasks_on_connection_loss=True,
)
```

---

## 🚀 Cómo iniciar Celery correctamente en Windows

### **Opción 1: Worker solo (recomendado)**
```powershell
cd backend
celery -A config worker -l info --pool=solo
```

### **Opción 2: Worker + Beat (tareas programadas)**
```powershell
# Terminal 1: Worker
celery -A config worker -l info --pool=solo

# Terminal 2: Beat (scheduler)
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### **Opción 3: Usar threads en lugar de solo**
```powershell
celery -A config worker -l info --pool=threads
```

---

## 📊 Monitoreo de Celery

### **Ver tareas en tiempo real:**
```powershell
# Terminal separada
celery -A config events
```

### **Ver estado de workers:**
```powershell
celery -A config inspect active
celery -A config inspect stats
```

---

## 🛡️ Prevención

### **1. Mantener Redis siempre activo**
- En desarrollo: Iniciar Redis antes de Celery
- En producción: Usar systemd/supervisor para reiniciar automáticamente

### **2. Monitorear logs de Celery**
```bash
# Guardar logs en archivo
celery -A config worker -l info --logfile=celery.log
```

### **3. Configurar alertas**
- Si Redis se cae, recibir notificación
- Si Celery no se reconecta, reiniciar automáticamente

### **4. Usar Redis Sentinel (producción)**
```python
# Para alta disponibilidad
CELERY_BROKER_URL = 'sentinel://localhost:26379/0'
CELERY_BROKER_TRANSPORT_OPTIONS = {
    'master_name': 'mymaster',
    'sentinel_kwargs': {'password': 'sentinel_password'},
}
```

---

## 📝 Checklist de Verificación

- [ ] Redis está corriendo (`redis-cli ping` retorna PONG)
- [ ] Celery se inicia sin errores
- [ ] Las tareas se ejecutan correctamente
- [ ] Los logs no muestran errores de conexión
- [ ] Celery se reconecta automáticamente si Redis se cae

---

## 🔗 Recursos

- [Celery Documentation](https://docs.celeryproject.io/)
- [Redis Documentation](https://redis.io/documentation)
- [Celery Windows Guide](https://docs.celeryproject.io/en/stable/userguide/windows.html)

