# 🧪 GUÍA DE PRUEBA - SECCIÓN "TODOS NUESTROS PRODUCTOS"

## 🚀 Cómo Probar la Nueva Sección

### 1. Iniciar la Aplicación

```bash
# Terminal 1 - Backend
cd backend
python manage.py runserver

# Terminal 2 - Frontend
cd frontend/electro_isla
npm run dev
```

### 2. Acceder a la Página de Inicio

```
http://localhost:5173
```

---

## 📋 Checklist de Pruebas

### ✅ Visualización General

- [ ] La sección "Todos nuestros productos" aparece debajo del carrusel inferior
- [ ] El título tiene la línea dorada animada
- [ ] Se muestran exactamente 10 productos inicialmente (5 columnas × 2 filas)
- [ ] El botón "Ver más" es visible

### ✅ Grid Responsivo

**Desktop (1400px):**
- [ ] 5 columnas visibles
- [ ] Espaciado: 16px entre productos
- [ ] Padding: 48px en los lados
- [ ] Tarjetas tienen tamaño uniforme

**Tablet (1024px):**
- [ ] 4 columnas visibles
- [ ] Espaciado: 12px entre productos
- [ ] Padding: 24px en los lados

**Mobile (768px):**
- [ ] 2 columnas visibles
- [ ] Espaciado: 8px entre productos
- [ ] Padding: 16px en los lados

**Small Mobile (480px):**
- [ ] 1 columna visible
- [ ] Botones full-width
- [ ] Padding: 16px en los lados

### ✅ Tarjetas de Producto

Para cada tarjeta verificar:

- [ ] Imagen carga correctamente
- [ ] Badge de descuento visible (si aplica)
- [ ] Subcategoría en amarillo dorado
- [ ] Nombre del producto visible (máximo 2 líneas)
- [ ] Descripción visible (máximo 2 líneas)
- [ ] Precio actual en amarillo dorado
- [ ] Precio original tachado (si hay descuento)
- [ ] Botón "Agregar" funciona
- [ ] Botón "Detalles" funciona

### ✅ Animaciones

**Entrada:**
- [ ] Las tarjetas aparecen con fade + slide up
- [ ] Cada tarjeta tiene delay de 0.05s
- [ ] Animación dura ~0.5s total

**Hover en Tarjeta:**
- [ ] Tarjeta se eleva (-4px)
- [ ] Sombra aumenta
- [ ] Imagen hace zoom (1.08x)
- [ ] Transición suave (0.3s)

**Hover en Botones:**
- [ ] Botón se eleva
- [ ] Sombra aumenta
- [ ] Transición suave

**Active en Botones:**
- [ ] Botón hace scale(0.95)
- [ ] Feedback visual inmediato

### ✅ Botón "Ver más"

- [ ] Botón visible si hay más de 10 productos
- [ ] Icono es MdExpandMore (▼)
- [ ] Click expande la sección
- [ ] Animación suave (0.8s)
- [ ] Aparecen 5 productos adicionales
- [ ] Botón cambia a "Ver menos"
- [ ] Icono cambia a MdExpandLess (▲)

### ✅ Botón "Ver menos"

- [ ] Click contrae la sección
- [ ] Animación suave (0.6s)
- [ ] Vuelven a mostrar 10 productos
- [ ] Botón cambia a "Ver más"
- [ ] Icono cambia a MdExpandMore (▼)

### ✅ Título Animado

- [ ] Título "Todos nuestros productos" visible
- [ ] Línea dorada debajo del título
- [ ] Línea aparece con animación al entrar en viewport
- [ ] Animación es suave (scaleX)

### ✅ Lazy Loading

- [ ] Imágenes cargan progresivamente
- [ ] Atributo `loading="lazy"` funciona
- [ ] No hay saltos de layout

### ✅ Responsivo Dinámico

- [ ] Redimensionar ventana cambia número de columnas
- [ ] Transición es suave
- [ ] No hay errores en consola
- [ ] Layout se adapta correctamente

---

## 🔍 Pruebas en Navegadores

### Chrome/Edge
```bash
# Abrir DevTools
F12

# Verificar:
- Console: Sin errores
- Network: Imágenes cargan con lazy loading
- Performance: Animaciones suaves (60fps)
```

### Firefox
```bash
# Abrir DevTools
F12

# Verificar:
- Inspector: HTML semántico
- Estilos: CSS correcto
- Performance: Sin lag
```

### Safari
```bash
# Verificar:
- Animaciones suaves
- Responsive correcto
- Lazy loading funciona
```

---

## 📱 Pruebas en Dispositivos Móviles

### iPhone (375px)
- [ ] 1 columna visible
- [ ] Botones full-width
- [ ] Scroll suave
- [ ] Animaciones fluidas

### iPad (768px)
- [ ] 2 columnas visible
- [ ] Espaciado correcto
- [ ] Botones con tamaño adecuado

### Android (360px)
- [ ] 1 columna visible
- [ ] Responsive correcto
- [ ] Touch events funcionan

---

## 🎨 Pruebas de Diseño

### Colores
- [ ] Amarillo dorado (#ffbb00) en subcategoría
- [ ] Amarillo dorado en precio
- [ ] Rojo (#ef4444) en badge de descuento
- [ ] Marrón oscuro (#423D37) en texto principal
- [ ] Blanco (#ffffff) en fondo

### Tipografía
- [ ] Títulos: Bold, legibles
- [ ] Cuerpo: Regular, legible
- [ ] Subcategoría: Uppercase, pequeña

### Espaciado
- [ ] Padding generoso en tarjetas
- [ ] Gap consistente entre productos
- [ ] Margin bottom en sección

### Sombras
- [ ] Sombra sutil en tarjetas (sm)
- [ ] Sombra aumenta en hover (lg)
- [ ] Sombra en botones

---

## 🐛 Pruebas de Errores

### Console
```javascript
// Verificar que no hay errores
console.error // No debe haber errores

// Verificar que no hay warnings
console.warn // No debe haber warnings
```

### Network
- [ ] Todas las imágenes cargan (200 OK)
- [ ] No hay 404s
- [ ] Tiempo de carga < 2s

### Performance
- [ ] Lighthouse score > 90
- [ ] FCP < 1.8s
- [ ] LCP < 2.5s
- [ ] CLS < 0.1

---

## 🔄 Pruebas de Interacción

### Secuencia 1: Expandir y Contraer
1. Página carga
2. Ver 10 productos
3. Click "Ver más"
4. Ver 15 productos
5. Click "Ver menos"
6. Ver 10 productos nuevamente
7. ✅ Funciona correctamente

### Secuencia 2: Hover en Tarjeta
1. Mover mouse sobre tarjeta
2. Tarjeta se eleva
3. Imagen hace zoom
4. Sombra aumenta
5. ✅ Funciona correctamente

### Secuencia 3: Click en Botones
1. Click "Agregar"
2. Botón hace feedback (scale 0.95)
3. Console.log se ejecuta
4. ✅ Funciona correctamente

### Secuencia 4: Responsive
1. Desktop (1400px): 5 columnas
2. Tablet (1024px): 4 columnas
3. Mobile (768px): 2 columnas
4. Small (480px): 1 columna
5. ✅ Funciona correctamente

---

## 📊 Pruebas de Datos

### Verificar Productos
```javascript
// En consola del navegador
// Verificar que displayProducts tiene 15 elementos
console.log(displayProducts.length) // Debe ser 15

// Verificar estructura de producto
console.log(displayProducts[0])
// {
//   id: '1',
//   subcategory: 'Laptops',
//   name: 'MacBook Pro 16"',
//   description: '...',
//   price: 2499.99,
//   discount: 10,
//   image: '...'
// }
```

### Verificar Precios
- [ ] Precio actual calculado correctamente
- [ ] Precio original mostrado si hay descuento
- [ ] Formato: $X,XXX.XX

### Verificar Descuentos
- [ ] Badge visible si discount > 0
- [ ] Texto: "-10%" (ejemplo)
- [ ] Precio recalculado: price * (1 - discount/100)

---

## 🎯 Pruebas de Accesibilidad

### Teclado
- [ ] Tab navega por botones
- [ ] Enter activa botones
- [ ] Esc cierra modales (si aplica)

### Pantalla
- [ ] Contraste WCAG AAA
- [ ] Texto legible
- [ ] Iconos claros

### Lectores de Pantalla
- [ ] aria-labels en botones
- [ ] Estructura semántica correcta
- [ ] Alt text en imágenes

---

## 📝 Reporte de Pruebas

### Template
```markdown
## Prueba: [Nombre]
- **Resultado:** ✅ Pasó / ❌ Falló
- **Navegador:** Chrome/Firefox/Safari
- **Dispositivo:** Desktop/Tablet/Mobile
- **Observaciones:** [Detalles]
- **Fecha:** [Fecha]
```

---

## 🚨 Problemas Comunes y Soluciones

### Problema: Grid no es responsivo
**Solución:** Verificar media queries en AllProducts.css

### Problema: Animaciones lentas
**Solución:** Verificar que no hay JavaScript bloqueante

### Problema: Imágenes no cargan
**Solución:** Verificar URLs de imágenes en datos de ejemplo

### Problema: Botón "Ver más" no aparece
**Solución:** Verificar que hay más de 10 productos

### Problema: Estilos no se aplican
**Solución:** Limpiar caché del navegador (Ctrl+Shift+Del)

---

## ✅ Checklist Final

- [ ] Todas las pruebas pasaron
- [ ] No hay errores en consola
- [ ] Responsive funciona en todos los tamaños
- [ ] Animaciones son suaves
- [ ] Colores son correctos
- [ ] Accesibilidad es buena
- [ ] Performance es excelente
- [ ] Datos se muestran correctamente
- [ ] Botones funcionan
- [ ] Documentación está completa

---

## 🎉 Conclusión

Si todas las pruebas pasan, la sección "Todos nuestros productos" está lista para producción.

**Estado:** ✅ LISTO PARA DEPLOY

---

*Guía de prueba: 5 de Noviembre de 2025*
*Proyecto: Electro Isla - E-commerce de Electrónica*
