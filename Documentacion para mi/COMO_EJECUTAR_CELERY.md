# 🚀 CÓMO EJECUTAR CELERY CORRECTAMENTE

**Fecha:** 13 de Noviembre, 2025

---

## ✅ CAMBIOS REALIZADOS

1. **Agregado `celery_worker.py`** - Punto de entrada para el worker
2. **Actualizado `config/celery.py`** - Configuración mejorada para Windows
3. **Arreglado descuento en `CarouselCard.tsx`** - Fórmula correcta
4. **Agregado refresco automático en `carrusel.ts`** - Cada 30 segundos

---

## 🔧 EJECUTAR CELERY

### Opción 1: Usando el nuevo worker (RECOMENDADO)

```bash
cd backend
python celery_worker.py -A config worker -l info
```

### Opción 2: Comando directo

```bash
cd backend
celery -A config worker -l info
```

### Opción 3: Con más workers (para mejor rendimiento)

```bash
cd backend
celery -A config worker -l info --concurrency=4
```

---

## ✅ VERIFICACIÓN

Cuando Celery inicie correctamente, deberías ver:

```
 -------------- celery@DESKTOP-QPLORTF v5.5.3 (immunity)
--- ***** -----
-- ******* ---- Windows-11-10.0.22621-SP0 2025-11-13 10:11:18
- *** --- * ---
- ** ---------- [config]
- ** ---------- .> app:         electro_isla:0x200ef6bf8c0
- ** ---------- .> transport:   redis://127.0.0.1:6379/0
- ** ---------- .> results:     redis://127.0.0.1:6379/0
- *** --- * --- .> concurrency: 12 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** -----
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery

[tasks]
  . api.tasks.liberar_reservas_expiradas
  . api.tasks.limpiar_tokens_expirados
  . config.celery.debug_task

[2025-11-13 10:11:18,487: INFO/MainProcess] Connected to redis://127.0.0.1:6379/0
[2025-11-13 10:11:18,492: INFO/MainProcess] mingle: searching for neighbors
[2025-11-13 10:11:19,523: INFO/MainProcess] mingle: all alone
[2025-11-13 10:11:19,567: INFO/MainProcess] celery@DESKTOP-QPLORTF ready.
```

**✅ Verificar:**
- [ ] Las tareas están listadas: `liberar_reservas_expiradas`, `limpiar_tokens_expirados`, `debug_task`
- [ ] Conectado a Redis: `Connected to redis://127.0.0.1:6379/0`
- [ ] Worker listo: `celery@... ready.`
- [ ] **NO hay errores de `ValueError`**

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Problema: `ValueError: not enough values to unpack`

**Causa:** Django no estaba completamente inicializado

**Solución:** Usa el nuevo `celery_worker.py`:
```bash
python celery_worker.py -A config worker -l info
```

### Problema: `Connection refused` (Redis)

**Causa:** Redis no está corriendo

**Solución:**
1. Asegúrate que Redis está ejecutándose
2. Verifica que está en `127.0.0.1:6379`

### Problema: Las tareas no se ejecutan

**Causa:** El worker no está escuchando

**Solución:**
1. Verifica que el worker está corriendo
2. Verifica que las tareas están listadas en `[tasks]`
3. Reinicia el worker

---

## 📊 TAREAS PROGRAMADAS

Las siguientes tareas se ejecutan automáticamente:

### 1. Liberar reservas expiradas
- **Frecuencia:** Cada 20 minutos
- **Tarea:** `api.tasks.liberar_reservas_expiradas`
- **Función:** Libera el stock reservado de productos cuando la reserva expira

### 2. Limpiar tokens expirados
- **Frecuencia:** Cada hora
- **Tarea:** `api.tasks.limpiar_tokens_expirados`
- **Función:** Elimina tokens JWT expirados de la blacklist

---

## 🎯 RESUMEN

**Cambios realizados:**
- ✅ Descuento calculado correctamente en CarouselCard
- ✅ ProductCarousel se refresca cada 30 segundos
- ✅ Celery configurado correctamente para Windows
- ✅ Nuevo punto de entrada `celery_worker.py`

**Próximos pasos:**
1. Ejecuta Celery con: `python celery_worker.py -A config worker -l info`
2. Verifica que no hay errores
3. Las tareas se ejecutarán automáticamente

