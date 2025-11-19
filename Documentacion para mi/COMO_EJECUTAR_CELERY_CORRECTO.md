# 🚀 CÓMO EJECUTAR CELERY CORRECTAMENTE

**Fecha:** 13 de Noviembre, 2025

---

## ✅ CAMBIOS REALIZADOS

1. **Actualizado `celery_worker.py`** - Punto de entrada correcto
2. **Actualizado `carrusel.ts`** - Refresco INTELIGENTE (solo cuando cambian productos)
3. **Actualizado `ProductosPage.tsx`** - Dispara evento cuando se crea/edita/elimina
4. **Arreglado descuento en `CarouselCard.tsx`** - Fórmula correcta

---

## 🔧 EJECUTAR CELERY

### Opción 1: Comando directo (RECOMENDADO)

```bash
cd backend
celery -A config worker -l info
```

### Opción 2: Con más workers (para mejor rendimiento)

```bash
cd backend
celery -A config worker -l info --concurrency=4
```

### Opción 3: Con pool de procesos (Windows)

```bash
cd backend
celery -A config worker -l info --pool=solo
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
- [ ] Las tareas están listadas
- [ ] Conectado a Redis
- [ ] Worker listo
- [ ] **NO hay errores de `ValueError`**

---

## 🖼️ REFRESCO INTELIGENTE DE IMÁGENES

El carrusel ahora se refresca INTELIGENTEMENTE:

### Cómo funciona:

1. **Creas un producto en admin** → Se dispara evento `productChanged`
2. **El carrusel escucha el evento** → Se refresca INMEDIATAMENTE
3. **La imagen aparece en 1-2 segundos** ✅

### Antes (❌ INCORRECTO):
- Refresco cada 30 segundos
- Esperas hasta 30 segundos para ver cambios

### Ahora (✅ CORRECTO):
- Refresco SOLO cuando cambian productos
- Cambios aparecen en 1-2 segundos

---

## 📊 FLUJO COMPLETO

```
Admin Panel
  ↓
Crear/Editar/Eliminar Producto
  ↓
window.dispatchEvent(new Event('productChanged'))
  ↓
useProductosCarrusel() escucha el evento
  ↓
Llama a obtenerProductosCarrusel()
  ↓
ProductCarousel se actualiza
  ↓
Imagen aparece en 1-2 segundos ✅
```

---

## 🎯 VERIFICACIÓN COMPLETA

### 1. Descuento correcto

```
Precio: 100
Descuento: 10%
Muestra: $90.00 (actual)
Tachado: $100.00 (original)
```

### 2. Imágenes se actualizan

```
1. Edita un producto en admin
2. Cambia la imagen
3. Espera 1-2 segundos
4. La imagen aparece en ProductCarousel ✅
```

### 3. Celery funciona

```
celery -A config worker -l info
→ Sin errores de ValueError ✅
→ Tareas listadas ✅
→ Conectado a Redis ✅
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Problema: Celery no inicia

**Solución:**
```bash
celery -A config worker -l info
```

### Problema: `Connection refused` (Redis)

**Solución:** Asegúrate que Redis está corriendo

### Problema: Las imágenes no se actualizan

**Solución:** Verifica que el evento se dispara:
1. Abre DevTools (F12)
2. Ve a Console
3. Crea/edita un producto
4. Busca `[CARRUSEL] Producto cambió, refrescando...`

---

## 📁 ARCHIVOS MODIFICADOS

| Archivo | Cambio |
|---------|--------|
| `backend/celery_worker.py` | Punto de entrada correcto |
| `frontend/electro_isla/src/shared/api/carrusel.ts` | Refresco inteligente |
| `frontend/electro_isla/src/pages/admin/productos/ProductosPage.tsx` | Dispara evento |
| `frontend/electro_isla/src/widgets/bottom-carousel/CarouselCard.tsx` | Descuento correcto |

---

## ✅ CONCLUSIÓN

**Todos los problemas están solucionados:**
- ✅ Descuento calcula correctamente
- ✅ Imágenes se actualizan en 1-2 segundos
- ✅ Celery funciona sin errores
- ✅ Refresco es inteligente (no cada 30 segundos)

