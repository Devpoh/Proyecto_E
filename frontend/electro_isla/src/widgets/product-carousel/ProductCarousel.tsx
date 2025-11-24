import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MdChevronLeft, MdChevronRight, MdArticle, MdShoppingCart, MdCheckCircle, MdVerified } from 'react-icons/md';
import { Button } from '../../shared/ui';
import { useAddToCart } from '../../shared/hooks/useAddToCart';
import './ProductCarousel.css';

export interface ProductCard {
  id: string | number;
  subcategory?: string;
  name: string;
  description: string;
  price: number;
  discount?: number;
  image?: string;
  // Campos del backend
  nombre?: string;
  descripcion?: string;
  precio?: number;
  descuento?: number;
  imagen_url?: string;
  imagen?: string;  // ✅ Nuevo: URL de archivo
  categoria?: string;
  stock?: number;
  en_carousel_card?: boolean;
  en_all_products?: boolean;
}

interface ProductCarouselProps {
  products: ProductCard[];
  title?: string;
}

const MAX_CAROUSEL_PRODUCTS = 5; // Límite máximo de productos en carrusel

export const ProductCarousel: React.FC<ProductCarouselProps> = ({
  products,
  title = 'Productos Destacados',
}) => {
  const navigate = useNavigate();
  const { addedProductId, handleAddToCart } = useAddToCart();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [slideDirection, setSlideDirection] = useState<'left' | 'right'>('left');
  const [resetAutoPlay, setResetAutoPlay] = useState(0); // Trigger para reiniciar auto-play
  
  // Filtrar solo los primeros 5 productos para mostrar en carrusel
  const carouselProducts = products.slice(0, MAX_CAROUSEL_PRODUCTS);

  // Auto-play carrusel cada 7 segundos
  useEffect(() => {
    if (carouselProducts.length === 0) return;

    const interval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % carouselProducts.length);
    }, 7000); // ✅ Cambiado a 7 segundos

    return () => clearInterval(interval);
  }, [carouselProducts.length, resetAutoPlay]); // ✅ Agregado resetAutoPlay para reiniciar el intervalo

  const handlePrev = () => {
    setSlideDirection('right');
    setIsTransitioning(true);
    setResetAutoPlay((prev) => prev + 1); // ✅ Reiniciar auto-play
    setTimeout(() => {
      setCurrentIndex((prev) => (prev - 1 + carouselProducts.length) % carouselProducts.length);
      setTimeout(() => setIsTransitioning(false), 50);
    }, 250);
  };

  const handleNext = () => {
    setSlideDirection('left');
    setIsTransitioning(true);
    setResetAutoPlay((prev) => prev + 1); // ✅ Reiniciar auto-play
    setTimeout(() => {
      setCurrentIndex((prev) => (prev + 1) % carouselProducts.length);
      setTimeout(() => setIsTransitioning(false), 50);
    }, 250);
  };

  const handleDotClick = (index: number) => {
    if (index === currentIndex) return;
    setSlideDirection(index > currentIndex ? 'left' : 'right');
    setIsTransitioning(true);
    setResetAutoPlay((prev) => prev + 1); // ✅ Reiniciar auto-play
    setTimeout(() => {
      setCurrentIndex(index);
      setTimeout(() => setIsTransitioning(false), 50);
    }, 250);
  };

  const handleCardClick = (e: React.MouseEvent, productId: string | number) => {
    // No navegar si se hace clic en botones
    const target = e.target as HTMLElement;
    if (target.closest('.product-card-actions')) {
      return;
    }
    navigate(`/producto/${productId}`);
  };

  if (carouselProducts.length === 0) {
    return <div className="product-carousel-empty">No hay productos disponibles</div>;
  }

  const currentProduct = carouselProducts[currentIndex];
  
  // Mapear campos del backend o frontend
  const productName = currentProduct.name || currentProduct.nombre || '';
  const productDescription = currentProduct.description || currentProduct.descripcion || '';
  const productPrice = currentProduct.price || currentProduct.precio || 0;
  const productDiscount = currentProduct.discount || currentProduct.descuento || 0;
  // Manejo correcto de imagen: prioridad imagen (archivo) > imagen_url (Base64 legado)
  const productImage = (currentProduct.image || currentProduct.imagen || currentProduct.imagen_url) || null;
  const productSubcategory = currentProduct.subcategory || currentProduct.categoria || '';
  
  const discountedPrice = productDiscount && productDiscount > 0
    ? productPrice * (1 - productDiscount / 100)
    : productPrice;

  return (
    <section className="product-carousel-section">
      <div className="product-carousel-header">
        <h2 className="product-carousel-title">{title}</h2>
      </div>

      <div className="product-carousel-container">
        {/* Botón anterior */}
        <button
          className="product-carousel-button product-carousel-button--prev"
          onClick={handlePrev}
          aria-label="Producto anterior"
        >
          <MdChevronLeft size={24} />
        </button>

        {/* Carrusel */}
        <div className={`product-carousel-wrapper ${isTransitioning ? `product-carousel-wrapper--sliding-${slideDirection}` : ''}`}>
          <div 
            key={currentProduct.id}
            className="product-carousel-slide product-carousel-slide--active"
          >
            <div 
              className="product-card" 
              onClick={(e) => handleCardClick(e, currentProduct.id)}
              style={{ cursor: 'pointer' }}
            >
              {/* Imagen */}
              <div className="product-card-image">
                {productImage ? (
                  <img src={productImage} alt={productName} />
                ) : (
                  <div className="product-card-image-placeholder">
                    <span>Imagen no disponible</span>
                  </div>
                )}
                {productDiscount > 0 && (
                  <div className="product-card-discount">
                    -{productDiscount}%
                  </div>
                )}
              </div>

              {/* Contenido */}
              <div className="product-card-content">
                {/* Subcategoría */}
                <p className="product-card-subcategory">{productSubcategory}</p>

                {/* Nombre */}
                <h3 className="product-card-name">{productName}</h3>

                {/* Descripción */}
                <p className="product-card-description">{productDescription}</p>

                {/* Precio */}
                <div className="product-card-price">
                  <span className="product-card-price-current">
                    ${discountedPrice.toFixed(2)}
                  </span>
                  {productDiscount > 0 && (
                    <span className="product-card-price-original">
                      ${productPrice.toFixed(2)}
                    </span>
                  )}
                </div>

                {/* Botones */}
                <div className="product-card-actions">
                  <Button
                    variant="outline"
                    size="md"
                    leftIcon={<MdArticle size={18} />}
                    onClick={() => navigate(`/producto/${currentProduct.id}`)}
                  >
                    Ver detalles
                  </Button>
                  <Button
                    variant={addedProductId === currentProduct.id ? "success" : "primary"}
                    size="md"
                    leftIcon={
                      currentProduct.stock === 0 ? (
                        <MdVerified size={18} />
                      ) : (
                        addedProductId === currentProduct.id ? (
                          <MdCheckCircle size={18} />
                        ) : (
                          <MdShoppingCart size={18} />
                        )
                      )
                    }
                    onClick={() => handleAddToCart(currentProduct.id, 1, currentProduct.stock || 0)}
                    disabled={currentProduct.stock === 0}
                    style={addedProductId === currentProduct.id ? { pointerEvents: 'none' } : undefined}
                  >
                    {currentProduct.stock === 0 ? 'Agotado!' : (addedProductId === currentProduct.id ? '¡AGREGADO!' : 'Agregar')}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Botón siguiente */}
        <button
          className="product-carousel-button product-carousel-button--next"
          onClick={handleNext}
          aria-label="Siguiente producto"
        >
          <MdChevronRight size={24} />
        </button>
      </div>

      {/* Indicadores - Fuera de la animación */}
      <div className="product-carousel-indicators">
        {carouselProducts.map((_, index) => (
          <button
            key={index}
            className={`product-carousel-dot ${
              index === currentIndex ? 'product-carousel-dot--active' : ''
            }`}
            onClick={() => handleDotClick(index)}
            aria-label={`Ir al producto ${index + 1}`}
            aria-current={index === currentIndex}
          />
        ))}
      </div>
    </section>
  );
};
