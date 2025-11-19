# 🧩 WIDGETS - Bloques UI Complejos

Esta carpeta contiene bloques de UI complejos que combinan múltiples features y componentes.

## 📂 Estructura

```
widgets/
├── header/              # Navbar con menú, búsqueda, carrito
├── footer/              # Footer con links, redes sociales
├── product-catalog/     # Catálogo con filtros y grid
└── shopping-cart/       # Carrito flotante/sidebar
```

## 🎯 Responsabilidades

- Combinar múltiples features
- Manejar layout complejo
- Coordinar interacciones entre features
- Reutilizable en múltiples páginas

## 📖 Ejemplo de Uso

```tsx
// widgets/header/Header.tsx
import { SearchBar } from '@/features/producto/product-search';
import { CartButton } from '@/features/carrito/cart-button';
import { UserMenu } from '@/features/auth/user-menu';

export function Header() {
  return (
    <header>
      <Logo />
      <SearchBar />
      <nav>
        <CartButton />
        <UserMenu />
      </nav>
    </header>
  );
}
```

## 🔄 Diferencia con Features

- **Widget**: Bloque UI complejo que combina features
- **Feature**: Funcionalidad específica de negocio

Ejemplo:
- Widget: `product-catalog` (grid + filtros + paginación)
- Features: `product-search`, `product-filters`
