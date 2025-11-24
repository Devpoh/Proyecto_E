/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎯 WIDGET - All Products Section
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Sección de grid de productos con expansión elegante.
 * Muestra 10 productos inicialmente (5 columnas × 2 filas) y permite expandir
 * para ver más con animación suave y profesional.
 */

import React, { useState, useEffect, memo } from 'react';
import { MdExpandMore, MdExpandLess } from 'react-icons/md';
import { Button } from '../../shared/ui';
import { AnimatedTitle } from '../bottom-carousel/AnimatedTitle';
import { CarouselCard } from '../bottom-carousel/CarouselCard';
import type { ProductCard } from '../product-carousel/ProductCarousel';
import { useFavoritosBatch } from '@/shared/hooks/useFavoritosBatch';
import './AllProducts.css';

interface AllProductsProps {
  products: ProductCard[];
  loading?: boolean;
}

const PRODUCTS_PER_PAGE = 8; // 4 columnas × 2 filas
const PRODUCTS_PER_PAGE_MOBILE = 5; // 1 columna × 5 filas en móviles

export const AllProducts: React.FC<AllProductsProps> = ({
  products,
  loading = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [displayedProducts, setDisplayedProducts] = useState<ProductCard[]>([]);
  const [isMobile, setIsMobile] = useState(false);
  
  // Obtener todos los IDs de productos para verificar favoritos en batch
  const productIds = products.map(p => Number(p.id));
  const { favoritos } = useFavoritosBatch(productIds);

  // Detectar si es móvil
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 767);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    // Filtrar productos por en_all_products
    const filteredProducts = products.filter(p => p.en_all_products !== false);
    // Mostrar 5 productos en móvil, 8 en desktop
    const productsToShow = isMobile ? PRODUCTS_PER_PAGE_MOBILE : PRODUCTS_PER_PAGE;
    const initialCount = Math.min(productsToShow, filteredProducts.length);
    setDisplayedProducts(filteredProducts.slice(0, initialCount));
  }, [products, isMobile]);

  const handleToggleExpand = () => {
    if (isExpanded) {
      // Contraer: mostrar 5 productos en móvil, 8 en desktop
      const filteredProducts = products.filter(p => p.en_all_products !== false);
      const productsToShow = isMobile ? PRODUCTS_PER_PAGE_MOBILE : PRODUCTS_PER_PAGE;
      setIsExpanded(false);
      setTimeout(() => {
        setDisplayedProducts(filteredProducts.slice(0, productsToShow));
      }, 400);
    } else {
      // Expandir: mostrar todos los productos filtrados
      const filteredProducts = products.filter(p => p.en_all_products !== false);
      setDisplayedProducts(filteredProducts);
      setIsExpanded(true);
    }
  };

  if (loading) {
    return (
      <section className="all-products-section">
        <div className="all-products-container">
          <div className="all-products-loading">
            <p>Cargando productos...</p>
          </div>
        </div>
      </section>
    );
  }

  if (products.length === 0) {
    return null;
  }

  const productsToShow = isMobile ? PRODUCTS_PER_PAGE_MOBILE : PRODUCTS_PER_PAGE;
  const hasMoreProducts = products.length > productsToShow; // Mostrar botón si hay más productos

  return (
    <section className="all-products-section">
      <div className="all-products-container">
        {/* Título con animación */}
        <div className="all-products-header">
          <AnimatedTitle text="Explora nuestra Colección" />
        </div>

        {/* Grid de productos */}
        <div className={`all-products-grid ${isExpanded ? 'all-products-grid--expanded' : ''}`}>
          {displayedProducts.map((product, index) => {
            const productsToShow = isMobile ? PRODUCTS_PER_PAGE_MOBILE : PRODUCTS_PER_PAGE;
            const isNewProduct = index >= productsToShow;
            const animationStyle = isNewProduct
              ? isExpanded
                ? `slideInUp 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94) ${(index - productsToShow) * 0.05}s both`
                : `slideOutDown 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94) ${(index - productsToShow) * 0.03}s both`
              : 'none';
            
            return (
            <div 
              key={product.id}
              className="all-products-item"
              style={{
                animation: animationStyle
              }}
            >
              <ProductGridCard 
                product={product} 
                isFavorite={favoritos[String(product.id)] || false}
              />
            </div>
            );
          })}
        </div>

        {/* Botón Ver más/Ver menos */}
        {hasMoreProducts && (
          <div className="all-products-footer">
            <Button
              variant="secondary"
              size="lg"
              onClick={handleToggleExpand}
              rightIcon={isExpanded ? <MdExpandLess size={20} /> : <MdExpandMore size={20} />}
              className="all-products-toggle-button"
            >
              {isExpanded ? 'Ver menos' : 'Ver más'}
            </Button>
          </div>
        )}
      </div>
    </section>
  );
};

/**
 * Componente de tarjeta de producto para el grid
 */
interface ProductGridCardProps {
  product: ProductCard;
  isFavorite: boolean;
}

const ProductGridCardComponent: React.FC<ProductGridCardProps> = ({ product, isFavorite }) => {
  // Mapear campos del backend o frontend
  const productName = product.name || product.nombre || '';
  const productPrice = product.price || product.precio || 0;
  const productDiscount = product.discount || product.descuento || 0;
  const productImage = product.image || product.imagen_url || '';
  const productSubcategory = product.subcategory || product.categoria || '';

  return (
    <CarouselCard
      id={product.id}
      nombre={productName}
      categoria={productSubcategory}
      precio={productPrice}
      descuento={productDiscount}
      imagen_url={productImage}
      stock={product.stock}
      initialIsFavorite={isFavorite}
    />
  );
};

// Exportar con React.memo para evitar re-renders innecesarios
const ProductGridCard = memo(ProductGridCardComponent);
