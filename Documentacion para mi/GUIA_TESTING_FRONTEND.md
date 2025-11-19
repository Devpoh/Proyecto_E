# 🧪 GUÍA DE TESTING - FRONTEND

**Fecha:** 9 de Noviembre, 2025  
**Status:** 📋 **GUÍA DE TESTING**

---

## 📋 TESTING MANUAL

### **1. Testing de useInvalidateAdminQueries**

#### **Caso de Prueba 1: Invalidación de Queries por Defecto**

```typescript
// ProductosPage.tsx
import { useInvalidateProductosQueries } from '@/shared/hooks/useInvalidateAdminQueries';

export const ProductosPage = () => {
  const invalidateQueries = useInvalidateProductosQueries();
  
  const createMutation = useMutation({
    mutationFn: createProducto,
    onSuccess: () => {
      invalidateQueries(); // Debe invalidar: admin-productos, dashboard-stats, historial
      handleCloseModal();
    },
  });
  
  // ...
};
```

**Pasos de Testing:**
1. Abrir ProductosPage
2. Crear un nuevo producto
3. Verificar en React Query DevTools que se invalidan:
   - ✅ `admin-productos`
   - ✅ `dashboard-stats`
   - ✅ `historial`
4. Verificar que la página se actualiza automáticamente

**Resultado Esperado:** ✅ Queries invalidadas correctamente

---

#### **Caso de Prueba 2: Invalidación Personalizada**

```typescript
const invalidateQueries = useInvalidateAdminQueries({
  additionalKeys: ['custom-key']
});

invalidateQueries(['extra-key']);
// Debe invalidar: dashboard-stats, historial, custom-key, extra-key
```

**Pasos de Testing:**
1. Crear un hook personalizado
2. Llamar con keys adicionales
3. Verificar en React Query DevTools

**Resultado Esperado:** ✅ Todas las keys se invalidan

---

### **2. Testing de usePermissions**

#### **Caso de Prueba 1: Permisos de Admin**

```typescript
// Simular usuario admin
const mockUser = { rol: 'admin', id: 1, username: 'admin' };

// En ProductosPage
const { canEdit, canDelete, isAdmin } = usePermissions();

// Debe retornar:
// canEdit: true
// canDelete: true
// isAdmin: true
```

**Pasos de Testing:**
1. Loguear como admin
2. Ir a ProductosPage
3. Verificar que aparecen botones de editar y eliminar
4. Verificar que `isAdmin` es true

**Resultado Esperado:** ✅ Permisos correctos para admin

---

#### **Caso de Prueba 2: Permisos de Trabajador**

```typescript
// Simular usuario trabajador
const mockUser = { rol: 'trabajador', id: 2, username: 'trabajador' };

// En ProductosPage
const { canEdit, canDelete, isAdmin } = usePermissions();

// Debe retornar:
// canEdit: true
// canDelete: false
// isAdmin: false
```

**Pasos de Testing:**
1. Loguear como trabajador
2. Ir a ProductosPage
3. Verificar que aparece botón de editar
4. Verificar que NO aparece botón de eliminar
5. Verificar que `isAdmin` es false

**Resultado Esperado:** ✅ Permisos correctos para trabajador

---

#### **Caso de Prueba 3: Permisos de Cliente**

```typescript
// Simular usuario cliente
const mockUser = { rol: 'cliente', id: 3, username: 'cliente' };

// En ProductosPage
const { canEdit, canDelete, isAdmin } = usePermissions();

// Debe retornar:
// canEdit: false
// canDelete: false
// isAdmin: false
```

**Pasos de Testing:**
1. Loguear como cliente
2. Intentar acceder a ProductosPage
3. Verificar que se redirige o no ve botones de editar/eliminar

**Resultado Esperado:** ✅ Acceso denegado o sin permisos

---

### **3. Testing de getRolLabel y getRolBadgeClass**

#### **Caso de Prueba 1: Labels de Roles**

```typescript
import { getRolLabel, getRolBadgeClass } from '@/shared/utils/roles';

// Pruebas
console.assert(getRolLabel('admin') === 'Administrador');
console.assert(getRolLabel('trabajador') === 'Trabajador');
console.assert(getRolLabel('mensajero') === 'Mensajero');
console.assert(getRolLabel('cliente') === 'Cliente');
console.assert(getRolLabel('invalid') === 'Cliente'); // default
```

**Pasos de Testing:**
1. Abrir consola del navegador
2. Ejecutar las pruebas
3. Verificar que todos los asserts pasen

**Resultado Esperado:** ✅ Todos los labels correctos

---

#### **Caso de Prueba 2: Clases CSS de Roles**

```typescript
import { getRolBadgeClass } from '@/shared/utils/roles';

// Pruebas
console.assert(getRolBadgeClass('admin') === 'badge-admin');
console.assert(getRolBadgeClass('trabajador') === 'badge-trabajador');
console.assert(getRolBadgeClass('mensajero') === 'badge-mensajero');
console.assert(getRolBadgeClass('cliente') === 'badge-cliente');
```

**Pasos de Testing:**
1. Abrir consola del navegador
2. Ejecutar las pruebas
3. Verificar que todos los asserts pasen

**Resultado Esperado:** ✅ Todas las clases correctas

---

### **4. Testing de AdminModal**

#### **Caso de Prueba 1: Abrir y Cerrar Modal**

```typescript
import { AdminModal } from '@/shared/ui/AdminModal';

export const TestComponent = () => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <>
      <button onClick={() => setIsOpen(true)}>Abrir Modal</button>
      
      <AdminModal
        isOpen={isOpen}
        title="Test Modal"
        onClose={() => setIsOpen(false)}
        onSubmit={() => console.log('Submitted')}
      >
        <p>Contenido del modal</p>
      </AdminModal>
    </>
  );
};
```

**Pasos de Testing:**
1. Hacer clic en "Abrir Modal"
2. Verificar que el modal aparece
3. Verificar que el título es "Test Modal"
4. Verificar que el contenido es visible
5. Hacer clic en el botón "Cancelar"
6. Verificar que el modal se cierra

**Resultado Esperado:** ✅ Modal abre y cierra correctamente

---

#### **Caso de Prueba 2: Envío del Modal**

```typescript
const [isOpen, setIsOpen] = useState(false);

<AdminModal
  isOpen={isOpen}
  title="Test Modal"
  onClose={() => setIsOpen(false)}
  onSubmit={() => {
    console.log('Modal submitted');
    setIsOpen(false);
  }}
  submitLabel="Enviar"
>
  <p>Contenido del modal</p>
</AdminModal>
```

**Pasos de Testing:**
1. Abrir modal
2. Hacer clic en "Enviar"
3. Verificar que se ejecuta la función onSubmit
4. Verificar que el modal se cierra

**Resultado Esperado:** ✅ Envío funciona correctamente

---

#### **Caso de Prueba 3: Estado de Carga**

```typescript
const [isOpen, setIsOpen] = useState(false);
const [isLoading, setIsLoading] = useState(false);

<AdminModal
  isOpen={isOpen}
  title="Test Modal"
  onClose={() => setIsOpen(false)}
  onSubmit={() => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 2000);
  }}
  isLoading={isLoading}
  submitLabel="Enviar"
>
  <p>Contenido del modal</p>
</AdminModal>
```

**Pasos de Testing:**
1. Abrir modal
2. Hacer clic en "Enviar"
3. Verificar que el botón muestra "Procesando..."
4. Verificar que los botones están deshabilitados
5. Esperar 2 segundos
6. Verificar que el botón vuelve a "Enviar"
7. Verificar que los botones están habilitados

**Resultado Esperado:** ✅ Estado de carga funciona correctamente

---

### **5. Testing de ConfirmDeleteModal**

#### **Caso de Prueba 1: Abrir y Cancelar**

```typescript
import { ConfirmDeleteModal } from '@/shared/ui/ConfirmDeleteModal';

export const TestComponent = () => {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <>
      <button onClick={() => setIsOpen(true)}>Eliminar</button>
      
      <ConfirmDeleteModal
        isOpen={isOpen}
        itemName="Producto Test"
        onConfirm={() => console.log('Eliminado')}
        onCancel={() => setIsOpen(false)}
      />
    </>
  );
};
```

**Pasos de Testing:**
1. Hacer clic en "Eliminar"
2. Verificar que aparece el modal de confirmación
3. Verificar que el nombre del item es "Producto Test"
4. Hacer clic en "Cancelar"
5. Verificar que el modal se cierra

**Resultado Esperado:** ✅ Modal de confirmación funciona correctamente

---

#### **Caso de Prueba 2: Confirmar Eliminación**

```typescript
const [isOpen, setIsOpen] = useState(false);

<ConfirmDeleteModal
  isOpen={isOpen}
  itemName="Producto Test"
  onConfirm={() => {
    console.log('Producto eliminado');
    setIsOpen(false);
  }}
  onCancel={() => setIsOpen(false)}
/>
```

**Pasos de Testing:**
1. Abrir modal
2. Hacer clic en "Eliminar"
3. Verificar que se ejecuta la función onConfirm
4. Verificar que el modal se cierra

**Resultado Esperado:** ✅ Eliminación confirmada correctamente

---

#### **Caso de Prueba 3: Estado de Carga en Eliminación**

```typescript
const [isOpen, setIsOpen] = useState(false);
const [isLoading, setIsLoading] = useState(false);

<ConfirmDeleteModal
  isOpen={isOpen}
  itemName="Producto Test"
  onConfirm={() => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setIsOpen(false);
    }, 2000);
  }}
  onCancel={() => setIsOpen(false)}
  isLoading={isLoading}
/>
```

**Pasos de Testing:**
1. Abrir modal
2. Hacer clic en "Eliminar"
3. Verificar que el botón muestra "Eliminando..."
4. Verificar que los botones están deshabilitados
5. Esperar 2 segundos
6. Verificar que el modal se cierra

**Resultado Esperado:** ✅ Estado de carga funciona correctamente

---

## 🧬 TESTING UNITARIO (Próximo)

```typescript
// useInvalidateAdminQueries.test.ts
import { renderHook, act } from '@testing-library/react';
import { useInvalidateAdminQueries } from '@/shared/hooks/useInvalidateAdminQueries';

describe('useInvalidateAdminQueries', () => {
  it('should invalidate default queries', () => {
    const { result } = renderHook(() => useInvalidateAdminQueries());
    
    act(() => {
      result.current();
    });
    
    // Verificar que se invalidaron las queries
  });
});
```

---

## 🔄 TESTING DE INTEGRACIÓN (Próximo)

```typescript
// ProductosPage.integration.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ProductosPage } from '@/pages/admin/productos/ProductosPage';

describe('ProductosPage Integration', () => {
  it('should create a product and invalidate queries', async () => {
    render(<ProductosPage />);
    
    // Abrir modal
    fireEvent.click(screen.getByText('Nuevo Producto'));
    
    // Llenar formulario
    fireEvent.change(screen.getByLabelText('Nombre'), {
      target: { value: 'Test Producto' }
    });
    
    // Enviar
    fireEvent.click(screen.getByText('Crear'));
    
    // Verificar que se invalidaron las queries
  });
});
```

---

## ✅ CHECKLIST DE TESTING

### **Manual Testing**
- [ ] useInvalidateAdminQueries - Invalidación por defecto
- [ ] useInvalidateAdminQueries - Invalidación personalizada
- [ ] usePermissions - Permisos de admin
- [ ] usePermissions - Permisos de trabajador
- [ ] usePermissions - Permisos de cliente
- [ ] getRolLabel - Labels correctos
- [ ] getRolBadgeClass - Clases correctas
- [ ] AdminModal - Abrir y cerrar
- [ ] AdminModal - Envío
- [ ] AdminModal - Estado de carga
- [ ] ConfirmDeleteModal - Abrir y cancelar
- [ ] ConfirmDeleteModal - Confirmar eliminación
- [ ] ConfirmDeleteModal - Estado de carga

### **Integración Testing**
- [ ] ProductosPage con nuevos hooks
- [ ] UsuariosPage con nuevos hooks
- [ ] PedidosPage con nuevos hooks
- [ ] HistorialPage con nuevos hooks

### **Performance Testing**
- [ ] Bundle size reducido
- [ ] Tiempo de carga mejorado
- [ ] Re-renders reducidos
- [ ] Memoria optimizada

---

## 🚀 COMANDOS DE TESTING

```bash
# Ejecutar tests unitarios
npm run test

# Ejecutar tests con coverage
npm run test:coverage

# Ejecutar tests en modo watch
npm run test:watch

# Ejecutar tests de integración
npm run test:integration

# Ejecutar tests de performance
npm run test:performance

# Ejecutar todos los tests
npm run test:all
```

---

**Última actualización:** 9 de Noviembre, 2025  
**Status:** 📋 **GUÍA COMPLETA DE TESTING**
