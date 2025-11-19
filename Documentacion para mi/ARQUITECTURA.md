# 🏗️ ARQUITECTURA DEL PROYECTO - ELECTRÓNICA ISLA

## 📂 Estructura de Carpetas

```
src/
├── app/                    # ⚙️ Configuración global de la aplicación
│   ├── providers/         # Providers (QueryClient, Toaster, Router)
│   ├── store/            # Zustand stores (auth, cart, ui)
│   └── styles/           # Estilos globales adicionales
│
├── pages/                 # 📄 Páginas completas (rutas)
│   ├── home/             # Página principal
│   ├── productos/        # Catálogo de productos
│   ├── carrito/          # Carrito de compras
│   ├── checkout/         # Proceso de pago
│   └── auth/             # Login y registro
│
├── widgets/              # 🧩 Bloques UI complejos
│   ├── header/           # Navbar con menú, búsqueda, carrito
│   ├── footer/           # Footer con links, redes sociales
│   ├── product-catalog/  # Catálogo con filtros y grid
│   └── shopping-cart/    # Carrito flotante/sidebar
│
├── features/             # ⚡ Funcionalidades de negocio
│   ├── auth/
│   │   ├── login/       # Formulario de login
│   │   └── register/    # Formulario de registro
│   ├── carrito/
│   │   ├── add-to-cart/     # Botón agregar al carrito
│   │   └── cart-summary/    # Resumen del carrito
│   ├── checkout/
│   │   ├── payment/         # Formulario de pago
│   │   └── shipping/        # Formulario de envío
│   └── producto/
│       ├── product-search/  # Barra de búsqueda
│       └── product-filters/ # Filtros de productos
│
├── entities/             # 🎯 Entidades de negocio (modelos + API)
│   ├── user/
│   │   ├── model/       # Tipos e interfaces de User
│   │   └── api/         # Funciones API de User
│   ├── producto/
│   │   ├── model/       # Tipos e interfaces de Producto
│   │   └── api/         # Funciones API de Producto
│   ├── pedido/
│   │   ├── model/       # Tipos e interfaces de Pedido
│   │   └── api/         # Funciones API de Pedido
│   └── categoria/
│       ├── model/       # Tipos e interfaces de Categoria
│       └── api/         # Funciones API de Categoria
│
└── shared/               # 🔧 Código reutilizable
    ├── ui/              # Componentes UI básicos
    │   ├── button/      # Botón reutilizable
    │   ├── input/       # Input reutilizable
    │   ├── card/        # Card reutilizable
    │   ├── modal/       # Modal reutilizable
    │   ├── spinner/     # Spinner de carga
    │   └── toast/       # Toast notifications
    ├── lib/
    │   ├── utils/       # Utilidades generales
    │   ├── hooks/       # Custom hooks
    │   └── validators/  # Validadores con Zod
    ├── api/             # Configuración de Axios
    └── config/          # Constantes y configuraciones
```

---

## 🎯 RESPONSABILIDADES POR CAPA

### **1. APP** - Configuración Global
- **¿Qué va aquí?** Configuración que afecta toda la app
- **Ejemplos:**
  - `providers/QueryProvider.tsx` - React Query setup
  - `providers/AppProviders.tsx` - Wrapper de todos los providers
  - `store/useAuthStore.ts` - Estado global de autenticación
  - `store/useCartStore.ts` - Estado global del carrito

### **2. PAGES** - Páginas Completas
- **¿Qué va aquí?** Componentes de página que corresponden a rutas
- **Responsabilidades:**
  - Componer widgets y features
  - Manejar layout de la página
  - NO contener lógica de negocio
- **Ejemplo:**
  ```tsx
  // pages/home/HomePage.tsx
  export function HomePage() {
    return (
      <>
        <Header />
        <Hero />
        <ProductCatalog />
        <Footer />
      </>
    );
  }
  ```

### **3. WIDGETS** - Bloques UI Complejos
- **¿Qué va aquí?** Bloques grandes que combinan múltiples features
- **Responsabilidades:**
  - Combinar features relacionadas
  - Manejar layout interno complejo
  - Reutilizable en múltiples páginas
- **Ejemplo:**
  ```tsx
  // widgets/header/Header.tsx
  export function Header() {
    return (
      <header>
        <Logo />
        <ProductSearch />
        <CartButton />
        <UserMenu />
      </header>
    );
  }
  ```

### **4. FEATURES** - Funcionalidades de Negocio
- **¿Qué va aquí?** Funcionalidades específicas del negocio
- **Responsabilidades:**
  - Lógica de negocio
  - Interacción con APIs
  - Validación de datos
  - Estados locales
- **Ejemplo:**
  ```tsx
  // features/carrito/add-to-cart/AddToCartButton.tsx
  export function AddToCartButton({ productoId }) {
    const mutation = useMutation({
      mutationFn: () => api.post('/carrito/', { producto_id: productoId }),
      onSuccess: () => toast.success('Agregado al carrito'),
    });
    
    return <button onClick={() => mutation.mutate()}>Agregar</button>;
  }
  ```

### **5. ENTITIES** - Entidades de Negocio
- **¿Qué va aquí?** Modelos de datos y funciones API
- **Estructura:**
  - `model/` - Tipos TypeScript e interfaces
  - `api/` - Funciones para llamar al backend
- **Ejemplo:**
  ```tsx
  // entities/producto/model/types.ts
  export interface Producto {
    id: number;
    nombre: string;
    precio: number;
    imagen_url: string;
  }
  
  // entities/producto/api/getProductos.ts
  export async function getProductos() {
    const { data } = await api.get<Producto[]>('/productos/');
    return data;
  }
  ```

### **6. SHARED** - Código Reutilizable
- **¿Qué va aquí?** Código que se usa en toda la app
- **Subcarpetas:**
  - `ui/` - Componentes básicos (Button, Input, Card)
  - `lib/utils/` - Funciones utilitarias
  - `lib/hooks/` - Custom hooks
  - `lib/validators/` - Esquemas de validación Zod
  - `api/` - Configuración de Axios
  - `config/` - Constantes

---

## 🔄 FLUJO DE DATOS

```
User Action
    ↓
Feature Component (lógica)
    ↓
Entity API (petición HTTP)
    ↓
Backend Django
    ↓
Entity API (respuesta)
    ↓
React Query (caché)
    ↓
Zustand Store (estado global)
    ↓
UI Update
```

---

## 📖 CONVENCIONES DE CÓDIGO

### **Nombres de Archivos**
- **Carpetas:** `kebab-case` (ej: `add-to-cart/`)
- **Componentes:** `PascalCase.tsx` (ej: `AddToCartButton.tsx`)
- **Funciones:** `camelCase.ts` (ej: `getProductos.ts`)
- **Tipos:** `types.ts` o `interfaces.ts`

### **Imports**
Usar path aliases configurados en `tsconfig.json`:
```tsx
// ✅ CORRECTO
import { Button } from '@/shared/ui/button';
import { useAuthStore } from '@/app/store/useAuthStore';
import { Producto } from '@/entities/producto/model';

// ❌ INCORRECTO
import { Button } from '../../../shared/ui/button';
```

### **Exports**
Cada carpeta debe tener un `index.ts` para facilitar imports:
```tsx
// shared/ui/button/index.ts
export { Button } from './Button';
export type { ButtonProps } from './Button';

// Uso:
import { Button } from '@/shared/ui/button';
```

---

## 🎨 REGLAS DE ORO

1. ✅ **Usar SOLO variables CSS** de la paleta oficial
2. ✅ **NO usar 'any'** en TypeScript
3. ✅ **Validar en frontend Y backend**
4. ✅ **Sanitizar con DOMPurify** antes de usar `dangerouslySetInnerHTML`
5. ✅ **Principios Apple/iOS** para animaciones y UX
6. ✅ **Mobile First** en todo el diseño
7. ✅ **Accesibilidad WCAG AA/AAA**

---

## 🚀 PRÓXIMOS PASOS

1. ✅ Estructura de carpetas creada
2. ⏭️ Definir tipos TypeScript (entities)
3. ⏭️ Configurar Axios y React Query
4. ⏭️ Crear componentes UI básicos (shared/ui)
5. ⏭️ Implementar autenticación
6. ⏭️ Crear catálogo de productos
7. ⏭️ Implementar carrito de compras
8. ⏭️ Crear proceso de checkout
