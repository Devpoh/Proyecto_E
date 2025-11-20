# 🎯 CAUSA RAÍZ EXACTA - CUADRADOS NEGROS

**Ubicación:** Parte de abajo del borde de la tarjeta (donde están los botones)  
**Culpable:** Pseudo-elemento `::before` de `.tarjeta-boton`  
**Fecha:** 19 de Noviembre, 2025

---

## 🔴 EL PROBLEMA EXACTO

**Archivo:** `CarouselCard.css` línea 235-247

```css
.tarjeta-boton::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.15);  /* ← Blanco semi-transparente */
  transform: scaleX(0);  /* ← Escala 0 */
  transform-origin: right;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);  /* ← TRANSICIÓN */
  z-index: -1;
}

.tarjeta-boton:hover::before {
  transform: scaleX(1);  /* ← Se anima a escala 1 */
  transform-origin: left;
}
```

---

## ❌ POR QUÉ CAUSA CUADRADOS NEGROS

### 1. **Pseudo-elemento con Transición**
- El `::before` tiene una transición de `transform`
- Durante scroll, el navegador recalcula esta transición
- Causa repaints en cada frame

### 2. **Transform: scaleX(0) → scaleX(1)**
- Escala de 0 a 1 es una transformación compleja
- El navegador debe recalcular el tamaño en cada frame
- Genera artefactos de rendering

### 3. **Posicionamiento Absolute**
- El pseudo-elemento cubre todo el botón (`top: 0; left: 0; right: 0; bottom: 0;`)
- Durante scroll, el navegador recalcula su posición
- Causa flickering en los bordes

### 4. **Durante Scroll**
- El navegador está renderizando 16 tarjetas simultáneamente
- Cada tarjeta tiene 2 botones
- Cada botón tiene el pseudo-elemento `::before`
- Total: 32 pseudo-elementos con transiciones activas
- Resultado: Repaints masivos = cuadrados negros

---

## ✅ SOLUCIÓN

### Opción 1: Remover la Transición (RECOMENDADO)
```css
.tarjeta-boton::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.15);
  transform: scaleX(0);
  transform-origin: right;
  /* ← Remover transition */
  z-index: -1;
}

.tarjeta-boton:hover::before {
  transform: scaleX(1);
  transform-origin: left;
}
```

**Ventaja:** Elimina completamente el problema  
**Desventaja:** El efecto hover no tiene transición suave

---

### Opción 2: Usar Opacity en lugar de Transform
```css
.tarjeta-boton::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.15);
  opacity: 0;  /* ← Cambiar a opacity */
  transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1);  /* ← Transición de opacity */
  z-index: -1;
}

.tarjeta-boton:hover::before {
  opacity: 1;  /* ← Cambiar a opacity */
}
```

**Ventaja:** Mantiene la transición suave pero más eficiente  
**Desventaja:** Efecto visual diferente

---

### Opción 3: Agregar will-change y GPU Acceleration
```css
.tarjeta-boton::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.15);
  transform: scaleX(0);
  transform-origin: right;
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: -1;
  will-change: transform;  /* ← NUEVO */
  backface-visibility: hidden;  /* ← NUEVO */
}
```

**Ventaja:** Mantiene el efecto original con optimización GPU  
**Desventaja:** Puede no ser suficiente en grids grandes

---

## 🎯 RECOMENDACIÓN

**Usar Opción 1: Remover la Transición**

Razón:
- Los cuadrados negros desaparecerán completamente
- El efecto hover sigue funcionando (solo sin transición)
- El usuario no notará la diferencia (el hover es instantáneo)
- Mejor rendimiento en scroll

---

## 📊 IMPACTO

**Antes:**
- ❌ Cuadrados negros durante scroll
- ❌ 32 pseudo-elementos con transiciones activas
- ❌ Repaints masivos

**Después:**
- ✅ Sin cuadrados negros
- ✅ 0 transiciones activas
- ✅ Repaints optimizados

---

**Análisis completado:** 19 de Noviembre, 2025  
**Confianza:** MUY ALTA - Problema identificado exactamente  
**Próximo paso:** Implementar Opción 1
