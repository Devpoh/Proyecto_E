# 🚀 PLAN COMPLETO - FASES 2, 3 Y 4

**Fecha:** 9 de Noviembre, 2025  
**Status:** 📋 **INICIANDO FASE 2**

---

## 📊 RESUMEN DE FASES

```
FASE 1: ✅ COMPLETADA
├─ Hooks reutilizables (useInvalidateAdminQueries, usePermissions)
├─ Utilidades (roles.ts)
├─ Componentes reutilizables (AdminModal, ConfirmDeleteModal)
└─ Error 500 en historial RESUELTO

FASE 2: ⏳ EN PROGRESO
├─ Optimizaciones CSS (-30-40% tamaño)
├─ Lazy loading en rutas (-40% bundle inicial)
├─ React.memo en componentes puros (-50% re-renders)
└─ useMemo/useCallback (-30% cálculos)

FASE 3: 📋 PENDIENTE
├─ Eliminar código muerto (-20 líneas)
├─ Agregar prefers-reduced-motion (accesibilidad)
├─ Agregar dark mode (UX)
└─ Sanitización de HTML (seguridad)

FASE 4: 📋 PENDIENTE
├─ Integrar hooks en ProductosPage
├─ Integrar hooks en UsuariosPage
├─ Integrar hooks en PedidosPage
├─ Integrar hooks en HistorialPage
├─ Crear tests unitarios
└─ Tests de integración
```

---

## 🎯 FASE 2: OPTIMIZACIONES CSS Y RENDIMIENTO

### **Objetivo**
- Reducir bundle size en 40KB
- Mejorar tiempo de carga en 30%
- Optimizar re-renders
- Lazy loading en rutas

### **Tareas**

#### **2.1 Optimizaciones CSS**

**Archivos a revisar:**
- `frontend/electro_isla/src/pages/admin/productos/ProductosPage.css`
- `frontend/electro_isla/src/pages/admin/usuarios/UsuariosPage.css`
- `frontend/electro_isla/src/pages/admin/pedidos/PedidosPage.css`
- `frontend/electro_isla/src/pages/admin/historial/HistorialPage.css`
- `frontend/electro_isla/src/index.css`

**Cambios:**
1. Reducir selectores específicos (`.productos-page .productos-header .productos-title` → `.productos-title`)
2. Usar variables CSS en lugar de valores hardcodeados
3. Consolidar media queries
4. Eliminar propiedades redundantes
5. Agregar `contain: layout style paint` en componentes

**Impacto:** -30-40% tamaño CSS

#### **2.2 Lazy Loading en Rutas**

**Archivo:** `frontend/electro_isla/src/App.tsx`

**Cambio:**
```typescript
// ❌ ANTES
import ProductosPage from '@/pages/admin/productos/ProductosPage';
import UsuariosPage from '@/pages/admin/usuarios/UsuariosPage';

// ✅ DESPUÉS
const ProductosPage = lazy(() => import('@/pages/admin/productos/ProductosPage'));
const UsuariosPage = lazy(() => import('@/pages/admin/usuarios/UsuariosPage'));
```

**Impacto:** -40% bundle inicial

#### **2.3 React.memo en Componentes Puros**

**Componentes a optimizar:**
- `CarouselCard.tsx`
- `ProductCard.tsx`
- `UserCard.tsx`
- `PedidoCard.tsx`

**Cambio:**
```typescript
// ❌ ANTES
export const CarouselCard = ({ producto, onClick }) => { ... }

// ✅ DESPUÉS
export const CarouselCard = React.memo(({ producto, onClick }) => { ... })
```

**Impacto:** -50% re-renders innecesarios

#### **2.4 useMemo/useCallback**

**Ubicaciones:**
- ProductosPage: `productosEnCarrusel` cálculo
- HistorialPage: búsqueda y filtros
- PedidosPage: cálculos de totales

**Cambio:**
```typescript
// ❌ ANTES
const productosEnCarrusel = productos.filter(p => p.en_carrusel).length;

// ✅ DESPUÉS
const productosEnCarrusel = useMemo(
  () => productos.filter(p => p.en_carrusel).length,
  [productos]
);
```

**Impacto:** -30% cálculos innecesarios

---

## 🎯 FASE 3: CÓDIGO MUERTO Y ACCESIBILIDAD

### **Objetivo**
- Eliminar código no utilizado
- Mejorar accesibilidad
- Agregar dark mode
- Mejorar seguridad

### **Tareas**

#### **3.1 Eliminar Código Muerto**

**Identificados:**
1. `carouselLimitAlert` en ProductosPage (línea 87)
2. `console.debug` en axios.ts (múltiples líneas)
3. `handleCloseModal` innecesario en ProductosPage

**Cambios:**
- Eliminar variable no usada
- Usar variable de entorno para logs de debug
- Simplificar funciones

**Impacto:** -20 líneas

#### **3.2 Agregar prefers-reduced-motion**

**Archivo:** `frontend/electro_isla/src/index.css`

**Cambio:**
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

**Impacto:** Accesibilidad mejorada

#### **3.3 Agregar Dark Mode**

**Archivo:** `frontend/electro_isla/src/index.css`

**Cambio:**
```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-fondo: #0f172a;
    --color-texto-principal: #ffffff;
    /* ... más variables ... */
  }
}
```

**Impacto:** UX mejorada

#### **3.4 Sanitización de HTML**

**Ubicaciones:**
- ProductosPage: nombres de productos
- HistorialPage: objeto_repr
- UsuariosPage: nombres de usuarios

**Cambio:**
```typescript
// ✅ Usar DOMPurify si es necesario
import DOMPurify from 'dompurify';
<span>{DOMPurify.sanitize(producto.nombre)}</span>
```

**Impacto:** Protección contra XSS

---

## 🎯 FASE 4: INTEGRACIÓN Y TESTING

### **Objetivo**
- Integrar todos los hooks en componentes
- Crear tests unitarios
- Verificar que todo funciona

### **Tareas**

#### **4.1 Integración en ProductosPage**

**Cambios:**
1. Usar `useInvalidateProductosQueries()` en lugar de invalidación manual
2. Usar `usePermissions()` para permisos
3. Usar `AdminModal` para formulario
4. Usar `ConfirmDeleteModal` para confirmación
5. Usar `getRolLabel()` para mostrar roles

**Archivos:**
- `frontend/electro_isla/src/pages/admin/productos/ProductosPage.tsx`

#### **4.2 Integración en UsuariosPage**

**Cambios:**
1. Usar `useInvalidateUsuariosQueries()`
2. Usar `usePermissions()`
3. Usar `AdminModal`
4. Usar `ConfirmDeleteModal`
5. Usar `getRolLabel()` y `getRolBadgeClass()`

**Archivos:**
- `frontend/electro_isla/src/pages/admin/usuarios/UsuariosPage.tsx`

#### **4.3 Integración en PedidosPage**

**Cambios:**
1. Usar `useInvalidatePedidosQueries()`
2. Usar `usePermissions()`
3. Usar `AdminModal`
4. Usar `ConfirmDeleteModal`

**Archivos:**
- `frontend/electro_isla/src/pages/admin/pedidos/PedidosPage.tsx`

#### **4.4 Integración en HistorialPage**

**Cambios:**
1. Usar `useInvalidateHistorialQueries()`
2. Usar `usePermissions()`
3. Usar `ConfirmDeleteModal`

**Archivos:**
- `frontend/electro_isla/src/pages/admin/historial/HistorialPage.tsx`

#### **4.5 Tests Unitarios**

**Crear tests para:**
1. `useInvalidateAdminQueries` hook
2. `usePermissions` hook
3. `AdminModal` componente
4. `ConfirmDeleteModal` componente
5. Utilidades de roles

**Archivos:**
- `frontend/electro_isla/src/shared/hooks/__tests__/useInvalidateAdminQueries.test.ts`
- `frontend/electro_isla/src/shared/hooks/__tests__/usePermissions.test.ts`
- `frontend/electro_isla/src/shared/ui/AdminModal/__tests__/AdminModal.test.tsx`
- `frontend/electro_isla/src/shared/ui/ConfirmDeleteModal/__tests__/ConfirmDeleteModal.test.tsx`
- `frontend/electro_isla/src/shared/utils/__tests__/roles.test.ts`

#### **4.6 Tests de Integración**

**Crear tests para:**
1. ProductosPage con nuevos hooks
2. UsuariosPage con nuevos hooks
3. PedidosPage con nuevos hooks
4. HistorialPage con nuevos hooks

**Archivos:**
- `frontend/electro_isla/src/pages/admin/productos/__tests__/ProductosPage.integration.test.tsx`
- `frontend/electro_isla/src/pages/admin/usuarios/__tests__/UsuariosPage.integration.test.tsx`
- `frontend/electro_isla/src/pages/admin/pedidos/__tests__/PedidosPage.integration.test.tsx`
- `frontend/electro_isla/src/pages/admin/historial/__tests__/HistorialPage.integration.test.tsx`

---

## 📊 IMPACTO TOTAL

```
ANTES (FASE 1):
├─ Bundle size: ~450KB
├─ Tiempo carga: ~3.5s
├─ Código duplicado: ~500 líneas
└─ Mantenibilidad: Media

DESPUÉS (TODAS LAS FASES):
├─ Bundle size: ~360KB (-90KB, -20%)
├─ Tiempo carga: ~2.5s (-1s, -30%)
├─ Código duplicado: ~0 líneas (-500)
├─ Código muerto: ~0 líneas (-20)
├─ Mantenibilidad: Alta (+40%)
└─ Accesibilidad: Mejorada (+50%)
```

---

## ⏱️ ESTIMACIÓN DE TIEMPO

```
FASE 2: 8-10 horas
├─ Optimizaciones CSS: 2-3 horas
├─ Lazy loading: 1-2 horas
├─ React.memo: 2-3 horas
└─ useMemo/useCallback: 2-3 horas

FASE 3: 6-8 horas
├─ Código muerto: 1-2 horas
├─ prefers-reduced-motion: 1 hora
├─ Dark mode: 2-3 horas
└─ Sanitización: 1-2 horas

FASE 4: 10-12 horas
├─ Integración ProductosPage: 2-3 horas
├─ Integración UsuariosPage: 2-3 horas
├─ Integración PedidosPage: 1-2 horas
├─ Integración HistorialPage: 1-2 horas
└─ Tests: 3-4 horas

TOTAL: 24-30 horas
```

---

## ✅ CHECKLIST

### **FASE 2**
- [ ] Optimizar CSS
- [ ] Agregar lazy loading
- [ ] Agregar React.memo
- [ ] Agregar useMemo/useCallback
- [ ] Verificar bundle size
- [ ] Verificar tiempo de carga

### **FASE 3**
- [ ] Eliminar código muerto
- [ ] Agregar prefers-reduced-motion
- [ ] Agregar dark mode
- [ ] Agregar sanitización
- [ ] Verificar accesibilidad

### **FASE 4**
- [ ] Integrar en ProductosPage
- [ ] Integrar en UsuariosPage
- [ ] Integrar en PedidosPage
- [ ] Integrar en HistorialPage
- [ ] Crear tests unitarios
- [ ] Crear tests de integración
- [ ] Verificar que todo funciona

---

**Última actualización:** 9 de Noviembre, 2025  
**Status:** 📋 **PLAN COMPLETO LISTO PARA EJECUTAR**
