# 🚀 PLAN DE OPTIMIZACIÓN - CarouselCard

**Objetivo:** Eliminar parpadeos/flickering sin romper funcionalidad  
**Fecha:** 19 de Noviembre, 2025  
**Riesgo:** BAJO - Solo cambios CSS + optimizaciones

---

## 📋 FASES DEL PLAN

### FASE 1: Remover/Optimizar Efecto Brillo
**Archivo:** `CarouselCard.css`  
**Línea:** 287-300  
**Cambio:** Desactivar efecto brillo durante animación

```css
/* ANTES: */
.efecto-brillo::before {
  transition: left 0.5s;  /* ← Causa flickering */
}

/* DESPUÉS: */
.efecto-brillo::before {
  transition: none;  /* ← Sin transición */
  will-change: auto;  /* ← Optimización */
}
```

**Por qué:** El efecto brillo se anima durante el hover, causando repaints innecesarios

---

### FASE 2: Optimizar Transiciones de Sombra
**Archivo:** `CarouselCard.css`  
**Línea:** 15, 25-28  
**Cambio:** Usar `transform` en lugar de `box-shadow`

```css
/* ANTES: */
.tarjeta {
  transition: box-shadow 0.3s ease, transform 0.3s ease;  /* ← Sombra causa repaints */
}

/* DESPUÉS: */
.tarjeta {
  transition: transform 0.3s ease;  /* ← Solo transform */
}

.tarjeta:hover {
  transform: translateY(-4px);  /* ← Mantener transform */
  box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.15);  /* ← Sin transición */
}
```

**Por qué:** `box-shadow` causa repaints costosos, `transform` usa GPU

---

### FASE 3: Agregar `will-change` y `contain`
**Archivo:** `CarouselCard.css`  
**Línea:** 8-23  
**Cambio:** Agregar optimizaciones de rendering

```css
/* ANTES: */
.tarjeta {
  will-change: auto;
}

/* DESPUÉS: */
.tarjeta {
  will-change: transform;  /* ← Optimización GPU */
  contain: layout style paint;  /* ← Aislamiento de rendering */
}
```

**Por qué:** Permite al navegador optimizar rendering

---

### FASE 4: Optimizar Pseudo-elementos
**Archivo:** `CarouselCard.css`  
**Línea:** 56-64, 287-300  
**Cambio:** Agregar `will-change` a pseudo-elementos

```css
/* ANTES: */
.tarjeta-imagen::after {
  background: linear-gradient(...);  /* ← Sin optimización */
}

/* DESPUÉS: */
.tarjeta-imagen::after {
  background: linear-gradient(...);
  will-change: auto;  /* ← Optimización */
}

.efecto-brillo::before {
  will-change: auto;  /* ← Optimización */
}
```

**Por qué:** Pseudo-elementos también necesitan optimización

---

### FASE 5: Desactivar Interacciones Durante Animación
**Archivo:** `BottomCarousel.tsx`  
**Línea:** 169  
**Cambio:** Agregar clase para desactivar hover durante animación

```tsx
/* ANTES: */
<div className={`carrusel ${isHovering ? 'carrusel--paused' : ''}`}>

/* DESPUÉS: */
<div className={`carrusel ${isHovering ? 'carrusel--paused' : ''} ${isAnimating ? 'carrusel--animating' : ''}`}>
```

**CSS:**
```css
.carrusel--animating .tarjeta {
  pointer-events: none;  /* ← Desactivar interacciones */
}

.carrusel--animating .tarjeta:hover {
  transform: none;  /* ← Sin hover effect */
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);  /* ← Sombra normal */
}

.carrusel--animating .tarjeta-favorito {
  pointer-events: none;  /* ← Desactivar favorito */
}
```

**Por qué:** Evita cambios de estado durante la animación

---

### FASE 6: Optimizar Imágenes
**Archivo:** `CarouselCard.css`  
**Línea:** 45-54  
**Cambio:** Agregar `will-change` a imágenes

```css
/* ANTES: */
.tarjeta-imagen img {
  transition: transform var(--transicion-normal);
}

/* DESPUÉS: */
.tarjeta-imagen img {
  transition: transform var(--transicion-normal);
  will-change: transform;  /* ← Optimización */
  backface-visibility: hidden;  /* ← Aceleración GPU */
}
```

**Por qué:** Las imágenes se transforman durante hover

---

### FASE 7: Optimizar Carrusel Container
**Archivo:** `BottomCarousel.css`  
**Línea:** 95-102  
**Cambio:** Agregar optimizaciones al contenedor

```css
/* ANTES: */
.carrusel {
  display: flex;
  width: max-content;
  animation: desplazamiento 50s linear infinite;
  height: 100%;
  align-items: center;
  will-change: transform;
}

/* DESPUÉS: */
.carrusel {
  display: flex;
  width: max-content;
  animation: desplazamiento 50s linear infinite;
  height: 100%;
  align-items: center;
  will-change: transform;
  transform: translateZ(0);  /* ← Forzar GPU */
  backface-visibility: hidden;  /* ← Aceleración */
}
```

**Por qué:** Fuerza aceleración de hardware

---

### FASE 8: Optimizar Items del Carrusel
**Archivo:** `BottomCarousel.css`  
**Línea:** 109-116  
**Cambio:** Agregar optimizaciones a items

```css
/* ANTES: */
.carrusel-item {
  flex: 0 0 auto;
  width: 280px;
  margin: 0 var(--espaciado-md);
  display: flex;
  justify-content: center;
  height: 100%;
}

/* DESPUÉS: */
.carrusel-item {
  flex: 0 0 auto;
  width: 280px;
  margin: 0 var(--espaciado-md);
  display: flex;
  justify-content: center;
  height: 100%;
  will-change: transform;  /* ← Optimización */
  contain: layout style paint;  /* ← Aislamiento */
}
```

**Por qué:** Cada item necesita optimización

---

## 📊 RESUMEN DE CAMBIOS

| Fase | Archivo | Cambio | Impacto |
|------|---------|--------|--------|
| 1 | CarouselCard.css | Remover transición brillo | Alto |
| 2 | CarouselCard.css | Optimizar sombra | Alto |
| 3 | CarouselCard.css | Agregar will-change | Medio |
| 4 | CarouselCard.css | Optimizar pseudo-elementos | Medio |
| 5 | BottomCarousel.tsx + CSS | Desactivar interacciones | Alto |
| 6 | CarouselCard.css | Optimizar imágenes | Medio |
| 7 | BottomCarousel.css | Optimizar contenedor | Medio |
| 8 | BottomCarousel.css | Optimizar items | Medio |

---

## ✅ CRITERIOS DE ÉXITO

- ✅ Sin cuadrados negros
- ✅ Animación suave (60 FPS)
- ✅ Sin flickering
- ✅ Favoritos funcionan
- ✅ Hover effects funcionan
- ✅ Botones de navegación funcionan
- ✅ Responsive funciona

---

## 🔄 ORDEN DE IMPLEMENTACIÓN

1. **Primero:** Fase 1 (Remover brillo) - Impacto máximo
2. **Segundo:** Fase 2 (Optimizar sombra) - Impacto máximo
3. **Tercero:** Fase 5 (Desactivar interacciones) - Impacto alto
4. **Cuarto:** Fases 3, 4, 6, 7, 8 (Optimizaciones)

---

## 🧪 PRUEBAS DESPUÉS DE CADA FASE

```
1. Abrir DevTools (F12)
2. Ir a Performance
3. Grabar 5 segundos de animación
4. Verificar:
   - FPS (debe ser 60)
   - No hay cuadrados negros
   - No hay flickering
   - Funcionalidad intacta
```

---

## ⚠️ PRECAUCIONES

- ✅ Hacer backup de archivos CSS
- ✅ Probar en múltiples navegadores
- ✅ Verificar en móvil
- ✅ No cambiar HTML (solo CSS + mínimos cambios TS)
- ✅ Mantener funcionalidad de favoritos
- ✅ Mantener hover effects

---

**Plan completado:** 19 de Noviembre, 2025  
**Riesgo:** BAJO - Solo optimizaciones CSS  
**Tiempo estimado:** 30-45 minutos  
**Próximo paso:** Implementación
