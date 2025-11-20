# 🔍 ANÁLISIS DE RENDIMIENTO - CarouselCard

**Objetivo:** Investigar y resolver los pequeños cuadrados negros que aparecen durante la animación  
**Fecha:** 19 de Noviembre, 2025  
**Problema:** Parpadeos/flickering durante la animación del carrusel

---

## 📊 PROBLEMAS IDENTIFICADOS

### 1. **Efecto Brillo (Shine Effect) - PROBLEMA PRINCIPAL**

**Ubicación:** `CarouselCard.css` línea 287-300

```css
.efecto-brillo::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  transition: left 0.5s;  /* ← PROBLEMA: Transition en hover */
}

.efecto-brillo:hover::before {
  left: 100%;  /* ← Se anima de -100% a 100% */
}
```

**¿Por qué causa problemas?**
- El efecto brillo se anima en CADA hover
- Durante la animación infinita del carrusel, hay múltiples reflows/repaints
- El pseudo-elemento `::before` causa repaint innecesario
- Los pequeños cuadrados negros son artefactos de rendering causados por:
  - Transiciones simultáneas (carrusel + brillo)
  - Cambios en z-index y posicionamiento
  - Repaints no optimizados

---

### 2. **Animación Infinita Sin Optimización**

**Ubicación:** `BottomCarousel.css` línea 98-101

```css
.carrusel {
  display: flex;
  width: max-content;
  animation: desplazamiento 50s linear infinite;  /* ← Animación continua */
  height: 100%;
  align-items: center;
  will-change: transform;  /* ← Bien, pero insuficiente */
}
```

**Problemas:**
- `will-change: transform` solo en el contenedor, no en los items
- Los 25 items (5 duplicaciones) se renderizan aunque solo 3-4 son visibles
- Cada item tiene su propia animación de hover
- Las imágenes no tienen `will-change` ni optimizaciones

---

### 3. **Gradientes y Sombras Complejas**

**Ubicación:** `CarouselCard.css` línea 11-12, 27-28

```css
.tarjeta {
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 
              0 8px 10px -6px rgba(0, 0, 0, 0.1);  /* ← Doble sombra */
  transition: box-shadow 0.3s ease, transform 0.3s ease;  /* ← Transición de sombra */
}

.tarjeta:hover {
  box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.15),  /* ← Sombra diferente */
              0 10px 15px -8px rgba(0, 0, 0, 0.1);
}
```

**Problemas:**
- Transición de `box-shadow` causa repaints costosos
- Las sombras se recalculan en cada frame de la animación
- Múltiples sombras = más cálculos de rendering

---

### 4. **Transformaciones Múltiples**

**Ubicación:** `CarouselCard.css` línea 52-54

```css
.tarjeta:hover .tarjeta-imagen img {
  transform: scale(1.05);  /* ← Transform en hover */
}
```

**Problemas:**
- Durante la animación infinita, el hover se activa/desactiva constantemente
- Cada cambio de transform causa reflow
- Las imágenes se renderizan a diferentes escalas

---

### 5. **Pseudo-elementos con Gradientes**

**Ubicación:** `CarouselCard.css` línea 56-64

```css
.tarjeta-imagen::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, transparent 0%, rgba(0,0,0,0.1) 100%);
}
```

**Problemas:**
- Pseudo-elemento adicional = más rendering
- Gradiente se recalcula en cada frame
- No tiene `will-change`

---

### 6. **Animación de Favorito (Heart Beat)**

**Ubicación:** `CarouselCard.css` línea 147-163

```css
.tarjeta-favorito.active {
  color: #ef4444;
  animation: heartBeat 0.4s ease-out;  /* ← Animación con scale */
}

@keyframes heartBeat {
  0% { transform: scale(1); }
  25% { transform: scale(1.3); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1.2); }
}
```

**Problemas:**
- La animación usa `transform: scale()` que causa repaints
- Se ejecuta durante la animación del carrusel
- Múltiples cambios de escala = flickering

---

### 7. **Falta de `contain` CSS**

**Ubicación:** Ningún lugar (no existe)

```css
/* NO EXISTE: */
.carrusel-item {
  contain: layout style paint;  /* ← Falta esto */
}
```

**Problemas:**
- Sin `contain`, el navegador recalcula todo el árbol DOM
- Cada cambio en un item afecta a los demás
- No hay aislamiento de rendering

---

## 🎯 CAUSA RAÍZ EXACTA

Los pequeños cuadrados negros son **artefactos de rendering** causados por:

1. **Efecto brillo (shine effect)** que se anima durante el hover
2. **Múltiples transiciones simultáneas** (sombra + transform + brillo)
3. **Repaints no optimizados** en pseudo-elementos
4. **Falta de `will-change` y `contain`** en los items
5. **Animación de favorito (heartBeat)** que interfiere con la animación principal

---

## ✅ SOLUCIÓN PROPUESTA

### 1. **Desactivar efecto brillo durante animación**
- Remover o desactivar el efecto brillo
- Usar `pointer-events: none` durante la animación

### 2. **Optimizar transiciones**
- Usar solo `transform` (no `box-shadow`)
- Usar `opacity` en lugar de cambios de color

### 3. **Agregar `will-change` y `contain`**
- `will-change: transform` en items
- `contain: layout style paint` para aislamiento

### 4. **Optimizar pseudo-elementos**
- Remover gradientes innecesarios
- Usar `will-change` en `::before` y `::after`

### 5. **Desactivar animación de favorito durante carrusel**
- Usar `pointer-events: none` en favorito durante animación
- Desactivar heartBeat durante scroll

### 6. **Usar `transform: translateZ(0)`**
- Forzar aceleración de hardware
- Crear nuevo stacking context

---

## 📋 PLAN DE ACCIÓN

1. **Fase 1:** Remover/optimizar efecto brillo
2. **Fase 2:** Optimizar transiciones de sombra
3. **Fase 3:** Agregar `will-change` y `contain`
4. **Fase 4:** Optimizar pseudo-elementos
5. **Fase 5:** Desactivar interacciones durante animación
6. **Fase 6:** Pruebas y verificación

---

## 🧪 MÉTRICAS DE ÉXITO

- ✅ Sin cuadrados negros durante animación
- ✅ Animación suave (60 FPS)
- ✅ Sin flickering
- ✅ Funcionalidad intacta
- ✅ Favoritos siguen funcionando
- ✅ Hover effects siguen funcionando

---

**Análisis completado:** 19 de Noviembre, 2025  
**Confianza:** ALTA - Problemas claramente identificados  
**Próximo paso:** Implementar soluciones
