# ⚡ FEATURES - Funcionalidades de Negocio

Esta carpeta contiene las funcionalidades específicas del negocio. Cada feature es independiente y reutilizable.

## 📂 Estructura

```
features/
├── auth/
│   ├── login/           # Formulario de login
│   └── register/        # Formulario de registro
├── carrito/
│   ├── add-to-cart/     # Botón agregar al carrito
│   └── cart-summary/    # Resumen del carrito
├── checkout/
│   ├── payment/         # Formulario de pago
│   └── shipping/        # Formulario de envío
└── producto/
    ├── product-search/  # Barra de búsqueda
    └── product-filters/ # Filtros de productos
```

## 🎯 Responsabilidades

- Lógica de negocio específica
- Interacción con APIs
- Validación de datos
- Manejo de estados locales
- Reutilizable en múltiples páginas/widgets

## 📖 Ejemplo de Uso

```tsx
// features/carrito/add-to-cart/AddToCartButton.tsx
import { useMutation } from '@tanstack/react-query';
import { useCartStore } from '@/app/store/useCartStore';
import toast from 'react-hot-toast';

interface Props {
  productoId: number;
}

export function AddToCartButton({ productoId }: Props) {
  const addItem = useCartStore((state) => state.addItem);

  const mutation = useMutation({
    mutationFn: async () => {
      // Lógica para agregar al carrito
      await api.post('/carrito/', { producto_id: productoId });
    },
    onSuccess: () => {
      addItem(productoId);
      toast.success('Producto agregado al carrito');
    },
  });

  return (
    <button onClick={() => mutation.mutate()}>
      Agregar al Carrito
    </button>
  );
}
```

## 🔄 Composición

Las features se componen en widgets:

```tsx
// widgets/product-catalog/ProductCatalog.tsx
import { ProductSearch } from '@/features/producto/product-search';
import { ProductFilters } from '@/features/producto/product-filters';
import { ProductGrid } from '@/features/producto/product-grid';

export function ProductCatalog() {
  return (
    <div>
      <ProductSearch />
      <ProductFilters />
      <ProductGrid />
    </div>
  );
}
```
