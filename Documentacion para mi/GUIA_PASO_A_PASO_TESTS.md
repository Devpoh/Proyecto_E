# 🧪 GUÍA PASO A PASO - EJECUTAR TESTS

**Fecha:** 9 de Noviembre, 2025  
**Status:** ✅ **LISTA PARA EJECUTAR**

---

## 📋 TABLA DE CONTENIDOS

1. [Preparación](#preparación)
2. [Ejecutar Todos los Tests](#ejecutar-todos-los-tests)
3. [Ejecutar Tests Individuales](#ejecutar-tests-individuales)
4. [Ejecutar Tests por Categoría](#ejecutar-tests-por-categoría)
5. [Verificar Coverage](#verificar-coverage)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Preparación

### **Paso 1: Abrir Terminal**

```bash
# En Windows PowerShell o CMD
# Navega a la carpeta del frontend
cd c:\Users\Alejandro\Desktop\Electro-Isla\frontend\electro_isla
```

### **Paso 2: Instalar Dependencias (si es necesario)**

```bash
# Instalar todas las dependencias
npm install

# O si solo necesitas actualizar
npm ci
```

### **Paso 3: Verificar que Jest está instalado**

```bash
# Ver versión de Jest
npm list jest

# Debería mostrar: jest@29.x.x (o similar)
```

---

## 🚀 Ejecutar Todos los Tests

### **Paso 1: Ejecutar todos los tests**

```bash
npm test
```

**Resultado esperado:**
```
PASS  src/pages/admin/productos/ProductosPage.test.tsx
PASS  src/pages/admin/usuarios/UsuariosPage.test.tsx
PASS  src/pages/admin/pedidos/PedidosPage.test.tsx
PASS  src/pages/admin/historial/HistorialPage.test.tsx
PASS  src/shared/ui/AdminModal/AdminModal.test.tsx
PASS  src/shared/ui/ConfirmDeleteModal/ConfirmDeleteModal.test.tsx
PASS  src/shared/hooks/__tests__/useInvalidateAdminQueries.test.ts
PASS  src/shared/hooks/__tests__/useSanitize.test.ts
PASS  src/shared/hooks/__tests__/usePermissions.test.ts
PASS  src/shared/utils/__tests__/roles.test.ts

Test Suites: 10 passed, 10 total
Tests:       50+ passed, 50+ total
Time:        5-10s
```

### **Paso 2: Si hay errores, presiona `a` para ejecutar todos los tests nuevamente**

```
Watch Usage
 › Press a to run all test suites.
 › Press f to run only failed tests.
 › Press p to filter by a filename regex pattern.
 › Press t to filter by a test name regex pattern.
 › Press q to quit watch mode.
 › Press Enter to trigger a test run.
```

---

## 🎯 Ejecutar Tests Individuales

### **Test 1: ProductosPage**

```bash
npm test -- ProductosPage.test.tsx
```

**Tests que se ejecutarán:**
- ✅ Renderizar ProductosPage
- ✅ Mostrar contador de productos en carrusel
- ✅ Mostrar botón agregar para usuarios admin
- ✅ Filtrar productos por búsqueda
- ✅ Abrir modal al hacer click en agregar
- ✅ Manejar errores de API

**Resultado esperado:**
```
PASS  src/pages/admin/productos/ProductosPage.test.tsx
  ProductosPage
    ✓ should render ProductosPage
    ✓ should display products count in carrusel
    ✓ should show add button for admin users
    ✓ should filter products by search
    ✓ should open modal when clicking add button
    ✓ should handle API errors gracefully

Tests: 6 passed, 6 total
```

---

### **Test 2: UsuariosPage**

```bash
npm test -- UsuariosPage.test.tsx
```

**Tests que se ejecutarán:**
- ✅ Renderizar UsuariosPage
- ✅ Mostrar lista de usuarios
- ✅ Filtrar usuarios por búsqueda
- ✅ Abrir modal de edición
- ✅ Mostrar roles de usuarios
- ✅ Manejar errores de API

---

### **Test 3: PedidosPage**

```bash
npm test -- PedidosPage.test.tsx
```

**Tests que se ejecutarán:**
- ✅ Renderizar PedidosPage
- ✅ Mostrar lista de pedidos
- ✅ Filtrar pedidos por búsqueda
- ✅ Mostrar estado de pedidos
- ✅ Cambiar estado de pedidos
- ✅ Manejar errores de API

---

### **Test 4: HistorialPage**

```bash
npm test -- HistorialPage.test.tsx
```

**Tests que se ejecutarán:**
- ✅ Renderizar sin error 500
- ✅ Mostrar registros de auditoría
- ✅ Filtrar por búsqueda
- ✅ Filtrar por módulo
- ✅ Filtrar por acción
- ✅ Filtrar por rango de fechas
- ✅ Manejar errores de API
- ✅ Eliminar registro

---

### **Test 5: AdminModal**

```bash
npm test -- AdminModal.test.tsx
```

**Tests que se ejecutarán:**
- ✅ No renderizar cuando isOpen es false
- ✅ Renderizar cuando isOpen es true
- ✅ Llamar onClose al hacer click en cerrar
- ✅ Llamar onSubmit al hacer click en enviar
- ✅ Mostrar estado de carga
- ✅ Mostrar label personalizado en botón

---

### **Test 6: ConfirmDeleteModal**

```bash
npm test -- ConfirmDeleteModal.test.tsx
```

**Tests que se ejecutarán:**
- ✅ No renderizar cuando isOpen es false
- ✅ Renderizar cuando isOpen es true
- ✅ Llamar onConfirm al confirmar
- ✅ Llamar onCancel al cancelar
- ✅ Mostrar estado de carga
- ✅ Mostrar icono de advertencia

---

### **Test 7: useInvalidateAdminQueries Hook**

```bash
npm test -- useInvalidateAdminQueries.test.ts
```

**Tests que se ejecutarán:**
- ✅ Retornar una función
- ✅ Invalidar queries por defecto
- ✅ Invalidar keys adicionales
- ✅ Invalidar keys personalizadas
- ✅ No invalidar defaults cuando se especifica

---

### **Test 8: useSanitize Hook**

```bash
npm test -- useSanitize.test.ts
```

**Tests que se ejecutarán:**
- ✅ Remover caracteres peligrosos
- ✅ Recortar espacios en blanco
- ✅ Retornar string vacío para input vacío
- ✅ Manejar texto normal
- ✅ Sanitizar HTML
- ✅ Sanitizar URLs
- ✅ Rechazar URLs peligrosas

---

### **Test 9: usePermissions Hook**

```bash
npm test -- usePermissions.test.ts
```

**Tests que se ejecutarán:**
- ✅ Retornar false para usuario no autenticado
- ✅ Permisos correctos para admin
- ✅ Permisos correctos para trabajador
- ✅ Permisos correctos para mensajero
- ✅ Permisos correctos para cliente

---

### **Test 10: Roles Utilities**

```bash
npm test -- roles.test.ts
```

**Tests que se ejecutarán:**
- ✅ getRolLabel para cada rol
- ✅ getRolBadgeClass para cada rol
- ✅ getRolColor para cada rol
- ✅ Estructura correcta de ROL_CONFIG
- ✅ Manejar roles desconocidos

---

## 📂 Ejecutar Tests por Categoría

### **Todos los tests de Páginas**

```bash
npm test -- src/pages/admin
```

**Resultado:** Ejecuta ProductosPage, UsuariosPage, PedidosPage, HistorialPage

---

### **Todos los tests de Componentes**

```bash
npm test -- src/shared/ui
```

**Resultado:** Ejecuta AdminModal, ConfirmDeleteModal

---

### **Todos los tests de Hooks**

```bash
npm test -- src/shared/hooks/__tests__
```

**Resultado:** Ejecuta useInvalidateAdminQueries, useSanitize, usePermissions

---

### **Todos los tests de Utilidades**

```bash
npm test -- src/shared/utils/__tests__
```

**Resultado:** Ejecuta roles.test.ts

---

## 📊 Verificar Coverage

### **Paso 1: Ejecutar tests con coverage**

```bash
npm test -- --coverage
```

**Resultado esperado:**
```
File                  | % Stmts | % Branch | % Funcs | % Lines
---------------------|---------|----------|---------|----------
All files            |   70.5  |   65.3   |   72.1  |   70.2
 ProductosPage       |   75.0  |   70.0   |   80.0  |   75.0
 UsuariosPage        |   72.0  |   68.0   |   75.0  |   72.0
 PedidosPage         |   68.0  |   65.0   |   70.0  |   68.0
 HistorialPage       |   80.0  |   75.0   |   85.0  |   80.0
 AdminModal          |   85.0  |   80.0   |   90.0  |   85.0
 ConfirmDeleteModal  |   82.0  |   78.0   |   85.0  |   82.0
 Hooks               |   70.0  |   65.0   |   72.0  |   70.0
 Utilities           |   75.0  |   70.0   |   78.0  |   75.0
```

### **Paso 2: Ver reporte HTML (opcional)**

```bash
npm test -- --coverage --collectCoverageFrom="src/**/*.{ts,tsx}"
```

Esto genera un reporte en `coverage/index.html`

---

## 🔍 Watch Mode

### **Ejecutar tests en modo watch**

```bash
npm test -- --watch
```

**Comandos disponibles en watch mode:**
- `a` - Ejecutar todos los tests
- `f` - Ejecutar solo tests fallidos
- `p` - Filtrar por nombre de archivo
- `t` - Filtrar por nombre de test
- `q` - Salir del modo watch
- `Enter` - Ejecutar tests nuevamente

---

## ⚠️ Troubleshooting

### **Problema 1: "Cannot find module"**

```bash
# Solución: Reinstalar dependencias
rm -r node_modules
npm install
```

### **Problema 2: "Jest is not recognized"**

```bash
# Solución: Instalar Jest globalmente
npm install -g jest

# O ejecutar con npx
npx jest
```

### **Problema 3: Tests timeout**

```bash
# Solución: Aumentar timeout
npm test -- --testTimeout=10000
```

### **Problema 4: Mocks no funcionan**

```bash
# Solución: Limpiar cache de Jest
npm test -- --clearCache
```

### **Problema 5: Errores de TypeScript**

```bash
# Solución: Verificar tipos
npm run type-check

# O ejecutar tsc
npx tsc --noEmit
```

---

## ✅ Checklist de Ejecución

- [ ] Terminal abierta en `frontend/electro_isla`
- [ ] Dependencias instaladas (`npm install`)
- [ ] Ejecutar todos los tests (`npm test`)
- [ ] Verificar que todos los tests pasan
- [ ] Ejecutar tests individuales para verificar
- [ ] Verificar coverage (`npm test -- --coverage`)
- [ ] Revisar reporte de coverage
- [ ] Todos los tests pasan ✅

---

## 📝 Notas Importantes

1. **Mocks:** Todos los tests usan mocks de API y useAuthStore
2. **Async:** Se usa `waitFor` para esperar actualizaciones asincrónicas
3. **Cleanup:** Jest limpia automáticamente después de cada test
4. **Isolation:** Cada test es independiente y no afecta a otros
5. **Performance:** Los tests deben ejecutarse en menos de 10 segundos

---

## 🎯 Próximos Pasos

1. ✅ Ejecutar `npm test` para verificar todos los tests
2. ✅ Revisar coverage con `npm test -- --coverage`
3. ✅ Ejecutar tests individuales según sea necesario
4. ✅ Corregir cualquier fallo de test
5. ✅ Confirmar que todos los tests pasan

---

**Última actualización:** 9 de Noviembre, 2025  
**Status:** ✅ **LISTO PARA EJECUTAR**
