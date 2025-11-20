/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎴 COMPONENT - Carousel Card
 * ═══════════════════════════════════════════════════════════════════════════════
 * Tarjeta individual para el carrusel inferior con botón de favorito y agregar al carrito
 */

import { useState, useEffect, memo } from 'react';
import { useNavigate } from 'react-router-dom';
import { MdShoppingCart, MdArticle, MdFavoriteBorder, MdFavorite, MdCheckCircle, MdVerified } from 'react-icons/md';
import { useAddToCart } from '@/shared/hooks/useAddToCart';
import { useAuthStore } from '@/app/store/useAuthStore';
import { Button } from '@/shared/ui';
import './CarouselCard.css';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api';

interface CarouselCardProps {
  id: string | number;
  nombre: string;
  categoria: string;
  precio: string | number;
  descuento: number;
  imagen_url: string | null;
  stock?: number;
  initialIsFavorite?: boolean; // Estado inicial de favorito (optimización batch)
}

const CarouselCardComponent = ({
  id,
  nombre,
  categoria,
  precio,
  descuento,
  imagen_url,
  stock = 1,
  initialIsFavorite,
}: CarouselCardProps) => {
  const navigate = useNavigate();
  const [isFavorite, setIsFavorite] = useState(initialIsFavorite ?? false);
  const { addedProductId, handleAddToCart } = useAddToCart();
  const { isAuthenticated } = useAuthStore();

  // Mapeo de categorías a nombres legibles
  const nombreCategoria: { [key: string]: string } = {
    'electrodomesticos': 'Electrodomésticos',
    'energia_tecnologia': 'Energía y Tecnología',
    'herramientas': 'Herramientas',
    'hogar_entretenimiento': 'Hogar y Entretenimiento',
    'otros': 'Otros Artículos',
  };

  // Actualizar estado cuando cambia initialIsFavorite
  useEffect(() => {
    if (initialIsFavorite !== undefined) {
      setIsFavorite(initialIsFavorite);
    }
  }, [initialIsFavorite]);

  // Solo cargar estado de favorito si no se proporcionó initialIsFavorite
  useEffect(() => {
    // Si ya tenemos el estado inicial, no hacer petición
    if (initialIsFavorite !== undefined) {
      return;
    }

    if (!isAuthenticated) {
      setIsFavorite(false);
      return;
    }

    const checkFavorite = async () => {
      try {
        // ✅ Obtener token desde Zustand (no desde storage)
        const { accessToken } = useAuthStore.getState();
        if (!accessToken) {
          setIsFavorite(false);
          return;
        }
        const token = accessToken;

        const response = await fetch(`${API_BASE_URL}/favoritos/es-favorito/${id}/`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          setIsFavorite(data.es_favorito);
        } else {
          setIsFavorite(false);
        }
      } catch (err) {
        console.error('Error al verificar favorito:', err);
        setIsFavorite(false);
      }
    };

    checkFavorite();
  }, [id, isAuthenticated, initialIsFavorite]);

  const handleFavoriteToggle = async () => {
    // Verificación 1: Usuario autenticado
    if (!isAuthenticated) {
      navigate('/login', { replace: true });
      return;
    }

    // Verificación 2: Token válido
    // ✅ Obtener token desde Zustand (solo en memoria)
    const { accessToken } = useAuthStore.getState();
    if (!accessToken) {
      navigate('/login', { replace: true });
      return;
    }
    const token = accessToken;

    try {
      // Determinar endpoint y método
      const endpoint = isFavorite ? 'remover' : 'agregar';
      const method = isFavorite ? 'DELETE' : 'POST';

      // Realizar petición al backend
      const response = await fetch(`${API_BASE_URL}/favoritos/${endpoint}/${id}/`, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      // Manejo de respuestas
      if (response.ok) {
        setIsFavorite(!isFavorite);
      } else if (response.status === 401) {
        // Token expirado o inválido - solo redirigir si es necesario
        console.warn('Token inválido al agregar favorito');
      }
    } catch (err) {
      console.error('Error en handleFavoriteToggle:', err);
    }
  };

  const handleViewDetails = () => {
    navigate(`/producto/${id}`);
  };

  const numPrice = parseFloat(String(precio));
  // ✅ CORRECCIÓN: Calcular precio con descuento correctamente
  const discountedPrice = descuento > 0 ? numPrice * (1 - descuento / 100) : numPrice;

  return (
    <div className="tarjeta efecto-brillo">
      <div className="tarjeta-imagen">
        {imagen_url ? (
          <img src={imagen_url} alt={nombre} />
        ) : (
          <span>📦</span>
        )}
        
        {/* Badge de Descuento */}
        {descuento > 0 && (
          <div className="tarjeta-descuento-badge">
            -{descuento}%
          </div>
        )}
      </div>
      <div className="tarjeta-contenido">
        <div className="tarjeta-info">
          <div className="tarjeta-categoria">{nombreCategoria[categoria] || categoria}</div>
          <div className="tarjeta-titulo-container">
            <h3 className="tarjeta-titulo">{nombre}</h3>
            <button
              className={`tarjeta-favorito ${isFavorite ? 'active' : ''}`}
              onClick={handleFavoriteToggle}
              aria-label={isFavorite ? 'Quitar de favoritos' : 'Agregar a favoritos'}
              title={isFavorite ? 'Quitar de favoritos' : 'Agregar a favoritos'}
            >
              {isFavorite ? (
                <MdFavorite size={20} />
              ) : (
                <MdFavoriteBorder size={20} />
              )}
            </button>
          </div>
          
          {/* Precios con Descuento */}
          <div className="tarjeta-precios">
            <span className="tarjeta-precio-actual">
              ${discountedPrice.toFixed(2)}
            </span>
            {descuento > 0 && (
              <span className="tarjeta-precio-anterior">
                ${numPrice.toFixed(2)}
              </span>
            )}
          </div>
        </div>
        <div className="tarjeta-botones">
          <Button 
            variant="outline"
            size="md"
            leftIcon={<MdArticle size={16} />}
            onClick={handleViewDetails}
          >
            Ver detalles
          </Button>
          <Button
            variant={addedProductId === id ? "success" : "primary"}
            size="md"
            leftIcon={
              stock === 0 ? (
                <MdVerified size={16} />
              ) : (
                addedProductId === id ? (
                  <MdCheckCircle size={16} />
                ) : (
                  <MdShoppingCart size={16} />
                )
              )
            }
            onClick={() => handleAddToCart(id, 1, stock || 0)}
            disabled={stock === 0}
            style={addedProductId === id ? { pointerEvents: 'none' } : undefined}
          >
            {stock === 0 ? 'Agotado!' : (addedProductId === id ? '¡AGREGADO!' : 'Agregar')}
          </Button>
        </div>
      </div>
    </div>
  );
};

// Exportar con React.memo para evitar re-renders innecesarios
export const CarouselCard = memo(CarouselCardComponent);
