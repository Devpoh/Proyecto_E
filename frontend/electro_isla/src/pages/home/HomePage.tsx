/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📄 PAGE - Home
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Página principal de la aplicación con lazy loading de componentes pesados.
 * Implementa code splitting para optimizar el rendimiento inicial.
 */

import { useEffect, useState, Suspense, lazy } from 'react';
import { ProductCarousel, type ProductCard } from '../../widgets/product-carousel';
import { AllProducts } from '../../widgets/all-products';
import { CategoriesSection } from '../../widgets/categories-section';
import { Footer } from '../../widgets/footer';
import { useProductosCarrusel } from '@/shared/api/carrusel';
import './HomePage.css';

// Lazy load de componentes pesados para optimizar rendimiento inicial
const TrustSectionLazy = lazy(() => 
  import('../../widgets/trust-section').then(m => ({ default: m.TrustSection }))
);
const BottomCarouselLazy = lazy(() => 
  import('../../widgets/bottom-carousel/BottomCarousel').then(m => ({ default: m.BottomCarousel }))
);

/**
 * 🎯 SOLUCIÓN QUIRÚRGICA: Productos ficticios removidos
 * 
 * Se removieron completamente los datos de ejemplo (FEATURED_PRODUCTS).
 * Ahora SOLO se muestran productos del backend.
 * 
 * Ventajas:
 * - No hay confusión entre productos reales y ficticios
 * - El cliente no puede comprar productos que no existen
 * - Mejor rendimiento (menos datos en memoria)
 * - Sincronización perfecta con el dashboard
 */

export const HomePage = () => {
  const { productos, loading } = useProductosCarrusel();
  const [displayProducts, setDisplayProducts] = useState<ProductCard[]>([]);

  useEffect(() => {
    // SOLO mostrar productos del backend
    if (productos && productos.length > 0) {
      const mappedProducts = productos.map((p) => ({
        id: p.id,
        nombre: p.nombre,
        descripcion: p.descripcion,
        precio: parseFloat(p.precio),
        descuento: p.descuento,
        imagen_url: p.imagen_url,
        categoria: p.categoria,
        stock: p.stock,
      }));
      setDisplayProducts(mappedProducts as ProductCard[]);
    } else {
      // Si no hay productos del backend, mostrar array vacío
      setDisplayProducts([]);
    }
  }, [productos]);

  return (
    <>
    <main className="home-page">
      {/* Hero Section con Carrusel */}
      <section className="home-hero-section">
        <div className="home-container">
          {/* Carrusel de Productos Destacados */}
          {!loading && displayProducts.length > 0 ? (
            <ProductCarousel
              products={displayProducts}
              title=""
            />
          ) : (
            <div className="home-loading">
              <p>Cargando productos...</p>
            </div>
          )}
        </div>
      </section>

      {/* Sección de Confianza y Beneficios - Lazy Loading */}
      <Suspense fallback={<div style={{ minHeight: '200px' }} />}>
        <TrustSectionLazy />
      </Suspense>

      {/* Carrusel Inferior - Lazy Loading */}
      <Suspense fallback={<div style={{ minHeight: '300px' }} />}>
        <BottomCarouselLazy productos={productos} />
      </Suspense>

      {/* Sección de Todos los Productos */}
      {!loading && displayProducts.length > 0 && (
        <AllProducts products={displayProducts} loading={loading} />
      )}

      {/* Sección de Nuestras Categorías */}
      <CategoriesSection />
    </main>

    {/* Footer */}
    <Footer />
    </>
  );
};
