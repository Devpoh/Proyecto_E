# 📄 PAGES - Páginas Completas

Esta carpeta contiene las páginas completas de la aplicación. Cada página es una ruta independiente.

## 📂 Estructura

```
pages/
├── home/          # Página principal
├── productos/     # Catálogo de productos
├── carrito/       # Carrito de compras
├── checkout/      # Proceso de pago
└── auth/          # Login y registro (páginas)
```

## 🎯 Responsabilidades

- Componer widgets y features
- Manejar el layout de la página
- Conectar con React Router
- NO contener lógica de negocio (usar features)

## 📖 Ejemplo de Uso

```tsx
// pages/home/HomePage.tsx
import { Header } from '@/widgets/header';
import { Footer } from '@/widgets/footer';
import { Hero } from '@/widgets/hero';
import { ProductCatalog } from '@/widgets/product-catalog';

export function HomePage() {
  return (
    <>
      <Header />
      <main>
        <Hero />
        <ProductCatalog />
      </main>
      <Footer />
    </>
  );
}
```

## 🔗 Routing

```tsx
// App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { HomePage } from '@/pages/home';
import { ProductosPage } from '@/pages/productos';

<Routes>
  <Route path="/" element={<HomePage />} />
  <Route path="/productos" element={<ProductosPage />} />
  <Route path="/carrito" element={<CarritoPage />} />
  <Route path="/checkout" element={<CheckoutPage />} />
</Routes>
```
