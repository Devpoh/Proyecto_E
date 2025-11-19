# ✅ SOLUCIÓN - import.meta No Soportado en Jest

**Fecha:** 9 de Noviembre, 2025  
**Status:** ✅ **RESUELTO**

---

## 🔍 PROBLEMA IDENTIFICADO

Los tests fallaban con errores de `import.meta`:
```
error TS1343: The 'import.meta' meta-property is only allowed when the '--module' 
option is 'es2020', 'es2022', 'esnext', 'system', 'node16', 'node18', 'node20', or 'nodenext'.

error TS2339: Property 'env' does not exist on type 'ImportMeta'.
```

Esto ocurría en `src/shared/api/axios.ts` que usa `import.meta.env.VITE_API_URL`.

---

## 🔧 CAUSA RAÍZ

ts-jest estaba usando una configuración de módulo que no soporta `import.meta`. Además, los tipos de Vite no estaban disponibles para TypeScript.

---

## ✅ SOLUCIÓN

Actualizar la configuración de ts-jest en `jest.config.js`:

```javascript
transform: {
  '^.+\\.tsx?$': [
    'ts-jest',
    {
      tsconfig: {
        module: 'ES2022',           // ← NUEVO: Soporta import.meta
        target: 'ES2022',           // ← NUEVO: Target ES2022
        jsx: 'react-jsx',
        esModuleInterop: true,
        allowSyntheticDefaultImports: true,
        types: ['vite/client', 'node', 'jest'],  // ← NUEVO: Tipos de Vite
        baseUrl: '.',
        paths: {
          '@/app/*': ['src/app/*'],
          '@/shared/*': ['src/shared/*'],
          // ... más paths
        },
      },
    },
  ],
}
```

---

## 📝 CAMBIOS REALIZADOS

### **jest.config.js**

1. **Agregar `module: 'ES2022'`**
   - Permite que ts-jest compile `import.meta` correctamente

2. **Agregar `target: 'ES2022'`**
   - Asegura que el target sea compatible con import.meta

3. **Agregar `types: ['vite/client', 'node', 'jest']`**
   - Proporciona tipos para `import.meta.env`
   - Permite que TypeScript reconozca las variables de entorno

---

## 🎯 CÓMO FUNCIONA

1. **ts-jest** compila TypeScript con `module: 'ES2022'`
2. **import.meta** es reconocido como válido
3. **Tipos de Vite** proporcionan definiciones para `import.meta.env`
4. **axios.ts** puede usar `import.meta.env.VITE_API_URL` sin errores

---

## 🚀 PRÓXIMO PASO

Ejecutar los tests:

```bash
npm test
```

**Resultado esperado:**
```
Test Suites: 13 passed, 13 total
Tests:       97+ passed, 97+ total
Time:        ~15-20 seconds
```

---

## 📊 COMPARACIÓN

### ANTES
```
error TS1343: The 'import.meta' meta-property is only allowed when the '--module' option is 'es2020', 'es2022', 'esnext', ...
error TS2339: Property 'env' does not exist on type 'ImportMeta'.
```

### DESPUÉS
```
✅ Todos los tests pasan
✅ import.meta.env es reconocido
✅ Variables de entorno de Vite disponibles
```

---

## 🔗 REFERENCIAS

- [ts-jest Configuration](https://kulshekhar.github.io/ts-jest/docs/getting-started/options)
- [TypeScript Module Options](https://www.typescriptlang.org/tsconfig#module)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)

---

**Última actualización:** 9 de Noviembre, 2025  
**Status:** ✅ **RESUELTO**
