# 🔍 INVESTIGACIÓN PROFUNDA - Cuadrados Negros en Scroll

**Problema:** Los cuadrados negros siguen apareciendo en PaginaProductos durante scroll  
**Contexto:** Grid de tarjetas (12-16 productos visibles)  
**Síntoma:** Pequeños cuadrados negros que aparecen/desaparecen durante scroll

---

## 🎯 ANÁLISIS DEL PROBLEMA

### Lo que hemos hecho:
1. ✅ Remover efecto brillo completamente
2. ✅ Cambiar `will-change: transform` → `will-change: auto`
3. ✅ Agregar `contain: layout style paint` al grid
4. ✅ Agregar `transform: translateZ(0)` y `backface-visibility`

### Pero el problema persiste...

---

## 🔴 POSIBLES CAUSAS RESTANTES

### 1. **Badge de Descuento** (SOSPECHOSO)
**Ubicación:** `CarouselCard.css` línea 73-88

```css
.tarjeta-descuento-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-weight: var(--peso-bold);
  font-size: 14px;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
  z-index: 10;
  min-width: 50px;
  text-align: center;
  letter-spacing: 0.5px;
}
```

**Problema:**
- Posicionamiento `absolute` dentro de `.tarjeta-imagen`
- Gradiente + box-shadow complejos
- Sin `will-change`
- Sin `transform: translateZ(0)`
- El z-index puede causar repaints

**Solución:**
- Agregar `will-change: auto`
- Agregar `transform: translateZ(0)`
- Usar `backface-visibility: hidden`

---

### 2. **Imagen con Transición** (SOSPECHOSO)
**Ubicación:** `CarouselCard.css` línea 47-58

```css
.tarjeta-imagen img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transicion-normal);
  will-change: transform;  /* ← Muy agresivo */
  backface-visibility: hidden;
}

.tarjeta:hover .tarjeta-imagen img {
  transform: scale(1.05);
}
```

**Problema:**
- `will-change: transform` es MUY agresivo en un grid con 16 imágenes
- Cada imagen crea un nuevo stacking context
- Durante scroll, el navegador recalcula 16 contextos simultáneamente

**Solución:**
- Cambiar a `will-change: auto`
- O remover `will-change` completamente

---

### 3. **Pseudo-elemento ::after** (POSIBLE)
**Ubicación:** `CarouselCard.css` línea 60-70

```css
.tarjeta-imagen::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.1) 100%);
  will-change: auto;
  pointer-events: none;
}
```

**Problema:**
- Gradiente se recalcula durante scroll
- Pseudo-elemento adicional = más rendering

**Solución:**
- Remover `will-change: auto`
- Agregar `transform: translateZ(0)`

---

### 4. **Hero Section con background-attachment: fixed** (POSIBLE)
**Ubicación:** `PaginaProductos.css` línea 24

```css
.productos-hero {
  background-attachment: fixed;  /* ← PROBLEMA POTENCIAL */
}
```

**Problema:**
- `background-attachment: fixed` causa repaints durante scroll
- Afecta al rendering de toda la página
- Puede interferir con el rendering de las tarjetas

**Solución:**
- Cambiar a `background-attachment: scroll`

---

### 5. **Grid sin `scroll-behavior`** (POSIBLE)
**Ubicación:** `PaginaProductos.css` línea 394-401

```css
.grid-productos {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: var(--espaciado-xl);
  margin-top: var(--espaciado-lg);
  padding: 0 var(--espaciado-md);
  contain: layout style paint;
}
```

**Problema:**
- Sin optimización de scroll
- Sin `scroll-behavior: smooth`
- Sin `overflow-anchor: auto`

**Solución:**
- Agregar `scroll-behavior: smooth` al body
- Agregar `overflow-anchor: auto` al grid

---

## ✅ SOLUCIÓN PROPUESTA

### Cambio 1: Optimizar imagen
```css
.tarjeta-imagen img {
  will-change: auto;  /* ← Cambiar de transform a auto */
}
```

### Cambio 2: Optimizar badge
```css
.tarjeta-descuento-badge {
  will-change: auto;  /* ← NUEVO */
  transform: translateZ(0);  /* ← NUEVO */
}
```

### Cambio 3: Optimizar pseudo-elemento
```css
.tarjeta-imagen::after {
  transform: translateZ(0);  /* ← NUEVO */
}
```

### Cambio 4: Cambiar background-attachment
```css
.productos-hero {
  background-attachment: scroll;  /* ← Cambiar de fixed */
}
```

### Cambio 5: Agregar scroll-behavior
```css
html {
  scroll-behavior: smooth;
}
```

---

## 📋 ORDEN DE IMPLEMENTACIÓN

1. **Primero:** Cambiar `will-change: transform` → `will-change: auto` en imágenes
2. **Segundo:** Optimizar badge de descuento
3. **Tercero:** Cambiar `background-attachment: fixed` → `scroll`
4. **Cuarto:** Agregar `scroll-behavior: smooth`

---

**Investigación completada:** 19 de Noviembre, 2025  
**Confianza:** ALTA - Problemas identificados en detalle
