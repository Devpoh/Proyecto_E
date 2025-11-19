/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎠 WIDGET - BottomCarousel
 * ═══════════════════════════════════════════════════════════════════════════════
 * Carrusel infinito con navegación manual por botones
 * 
 * Estrategia: Usar transform: translateX() en lugar de scrollBy()
 * para que funcione con la animación infinita CSS
 */

import { useRef, useState, useEffect } from 'react';
import { MdChevronLeft, MdChevronRight } from 'react-icons/md';
import { useFavoritosBatch } from '@/shared/hooks/useFavoritosBatch';
import { AnimatedTitle } from './AnimatedTitle';
import { CarouselCard } from './CarouselCard';
import type { ProductoCarrusel } from '@/shared/api/carrusel';
import './BottomCarousel.css';

interface BottomCarouselProps {
  productos: ProductoCarrusel[];
}

export const BottomCarousel = ({ productos }: BottomCarouselProps) => {
  const carouselRef = useRef<HTMLDivElement>(null);
  const [isAnimating, setIsAnimating] = useState(false);
  const [isHovering, setIsHovering] = useState(false);
  const autoPlayTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const isMouseOverButtonRef = useRef(false);

  // Duplicar productos para efecto infinito sin saltos
  const displayProducts = productos && productos.length > 0 ? productos : [];
  const infiniteProducts = [...displayProducts, ...displayProducts, ...displayProducts, ...displayProducts, ...displayProducts];
  
  // Obtener favoritos en batch (optimización)
  const productIds = displayProducts.map(p => p.id);
  const { favoritos } = useFavoritosBatch(productIds);

  // Calcular ancho del item según viewport
  const getItemWidth = () => {
    if (window.innerWidth <= 480) return 200 + 8; // mobile
    if (window.innerWidth <= 768) return 240 + 16; // tablet
    if (window.innerWidth <= 1024) return 240 + 16; // small desktop
    return 280 + 16; // desktop
  };

  const itemWidth = getItemWidth();
  const itemsToScroll = 3;
  const scrollAmount = itemWidth * itemsToScroll;

  // Función para reanudar la animación
  const resumeAnimation = () => {
    if (!carouselRef.current) return;
    
    // Limpiar todos los estilos inline
    carouselRef.current.style.removeProperty('transition');
    carouselRef.current.style.removeProperty('transform');
    carouselRef.current.style.removeProperty('animation');
    carouselRef.current.style.removeProperty('animation-delay');
    
    // Forzar reflow
    void carouselRef.current.offsetHeight;
    
    // Reanudar animación infinita
    carouselRef.current.style.animation = 'desplazamiento 50s linear infinite';
  };

  const handleScroll = (direction: 'left' | 'right') => {
    if (!carouselRef.current || isAnimating) return;

    setIsAnimating(true);

    // Pausar animación infinita
    if (carouselRef.current) {
      carouselRef.current.style.animation = 'none';
    }

    // Obtener posición actual del transform
    const computedStyle = window.getComputedStyle(carouselRef.current);
    const transform = computedStyle.transform;
    let currentTranslateX = 0;
    
    if (transform && transform !== 'none') {
      const matrix = transform.match(/matrix.*\((.+)\)/);
      if (matrix) {
        const values = matrix[1].split(', ');
        currentTranslateX = parseFloat(values[4]);
      }
    }

    // Calcular nueva posición
    const newTranslateX = direction === 'right' 
      ? currentTranslateX - scrollAmount 
      : currentTranslateX + scrollAmount;

    // Aplicar transform con transición suave
    if (carouselRef.current) {
      carouselRef.current.style.transition = 'transform 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)';
      carouselRef.current.style.transform = `translateX(${newTranslateX}px)`;
    }

    // Permitir siguiente click después de animación
    setTimeout(() => setIsAnimating(false), 800);

    // Reanudar animación infinita después de 2 segundos (SOLO si el mouse NO está sobre el botón)
    if (autoPlayTimeoutRef.current) {
      clearTimeout(autoPlayTimeoutRef.current);
    }

    autoPlayTimeoutRef.current = setTimeout(() => {
      // NO reanudar si el mouse está sobre el botón
      if (isMouseOverButtonRef.current) return;
      resumeAnimation();
    }, 2000);
  };

  const handleMouseEnter = () => {
    isMouseOverButtonRef.current = true;
    setIsHovering(true);
    // Pausar animación infinita
    if (carouselRef.current) {
      carouselRef.current.style.animationPlayState = 'paused';
    }
  };

  const handleMouseLeave = () => {
    isMouseOverButtonRef.current = false;
    setIsHovering(false);
    // Reanudar animación infinita
    if (carouselRef.current && carouselRef.current.style.animation !== 'none') {
      carouselRef.current.style.animationPlayState = 'running';
    }
  };

  // Limpiar timeout al desmontar
  useEffect(() => {
    return () => {
      if (autoPlayTimeoutRef.current) {
        clearTimeout(autoPlayTimeoutRef.current);
      }
    };
  }, []);

  if (!displayProducts || displayProducts.length === 0) {
    return null;
  }

  return (
    <section className="seccion-carrusel">
      <AnimatedTitle text="Productos Destacados" />
      
      <div className="carrusel-wrapper">
        {/* Botón izquierdo */}
        <button
          className="carrusel-nav-btn carrusel-nav-btn-left"
          onClick={() => handleScroll('left')}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          disabled={isAnimating}
          aria-label="Desplazar carrusel a la izquierda"
        >
          <MdChevronLeft size={28} />
        </button>

        <div className="carrusel-container">
          {/* Difuminado izquierdo */}
          <div className="carrusel-fade carrusel-fade-left" />
          
          <div 
            className={`carrusel ${isHovering ? 'carrusel--paused' : ''}`}
            ref={carouselRef}
          >
            {infiniteProducts.map((product, index) => (
              <div key={`${product.id}-${index}`} className="carrusel-item">
                <CarouselCard
                  id={product.id}
                  nombre={product.nombre}
                  categoria={product.categoria}
                  precio={product.precio}
                  descuento={product.descuento}
                  imagen_url={product.imagen_url}
                  stock={product.stock}
                  initialIsFavorite={favoritos[String(product.id)] || false}
                />
              </div>
            ))}
          </div>
          
          {/* Difuminado derecho */}
          <div className="carrusel-fade carrusel-fade-right" />
        </div>

        {/* Botón derecho */}
        <button
          className="carrusel-nav-btn carrusel-nav-btn-right"
          onClick={() => handleScroll('right')}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          disabled={isAnimating}
          aria-label="Desplazar carrusel a la derecha"
        >
          <MdChevronRight size={28} />
        </button>
      </div>
    </section>
  );
};
