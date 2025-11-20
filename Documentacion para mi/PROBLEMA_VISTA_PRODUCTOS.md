# 🔍 PROBLEMA EN VISTA DE PRODUCTOS

**Ubicación:** PaginaProductos.tsx - Grid de tarjetas  
**Síntoma:** Pequeños cuadrados negros en tarjetas durante scroll/interacción  
**Causa:** Las optimizaciones de CarouselCard no son suficientes en contexto estático

---

## 🎯 DIFERENCIA ENTRE CONTEXTOS

### BottomCarousel (Carrusel Infinito)
- Animación continua: `animation: desplazamiento 50s linear infinite`
- Clase `carrusel--animating` desactiva interacciones
- Optimizaciones aplicadas: ✅ FUNCIONAN

### PaginaProductos (Grid Estático)
- NO hay animación infinita
- Scroll de página normal
- Cambios de estado (hover, favorito) constantes
- Optimizaciones parciales: ⚠️ INSUFICIENTES

---

## 🔴 PROBLEMAS ESPECÍFICOS EN GRID

1. **Scroll de página causa repaints**
   - Las tarjetas se renderizan mientras se hace scroll
   - Sin `carrusel--animating`, los hover effects se activan

2. **Múltiples tarjetas simultáneamente**
   - En carrusel: 3-4 tarjetas visibles
   - En grid: 12-16 tarjetas visibles
   - Más repaints = más flickering

3. **Cambios de estado frecuentes**
   - Hover en múltiples tarjetas
   - Favoritos se activan/desactivan
   - Botones de agregar al carrito

4. **Sin desactivación de interacciones**
   - No hay mecanismo para pausar durante scroll
   - Los efectos hover se aplican constantemente

---

## ✅ SOLUCIÓN

Aplicar las mismas optimizaciones pero de forma más agresiva en el grid:

1. **Remover completamente el efecto brillo** (no solo desactivar transición)
2. **Agregar `pointer-events: none` durante scroll** (si es posible)
3. **Usar `transform: translateZ(0)` en todas las tarjetas**
4. **Agregar `will-change: auto` en lugar de `will-change: transform`** (menos agresivo)
5. **Optimizar el grid CSS** para mejor rendering

---

## 📋 CAMBIOS A REALIZAR

### 1. CarouselCard.css - Remover efecto brillo completamente
```css
/* ANTES: */
.efecto-brillo::before {
  will-change: auto;
  pointer-events: none;
}

/* DESPUÉS: */
.efecto-brillo::before {
  display: none;  /* ← Remover completamente */
}
```

### 2. CarouselCard.css - Cambiar will-change a auto
```css
/* ANTES: */
.tarjeta {
  will-change: transform;
}

/* DESPUÉS: */
.tarjeta {
  will-change: auto;  /* ← Menos agresivo */
}
```

### 3. PaginaProductos.css - Optimizar grid
```css
.grid-productos {
  contain: layout style paint;  /* ← Aislamiento */
}
```

---

**Análisis completado:** 19 de Noviembre, 2025
