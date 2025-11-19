/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📄 PAGE - ProductDetail
 * ═══════════════════════════════════════════════════════════════════════════════
 * Vista detallada de un producto con imagen, detalles, y productos relacionados
 */

import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { FiShoppingCart, FiHeart } from 'react-icons/fi';
import { MdCheckCircle, MdVerified } from 'react-icons/md';
import toast from 'react-hot-toast';
import { useAddToCart } from '@/shared/hooks/useAddToCart';
import { useAuthStore } from '@/app/store/useAuthStore';
import { Button } from '@/shared/ui';
import './ProductDetail.css';

interface Product {
  id: number;
  nombre: string;
  descripcion: string;
  categoria: string;
  precio: number;
  descuento: number;
  imagen_url: string;
  stock: number;
  favoritos_count?: number;
}

interface ProductDetailResponse {
  producto: Product;
  productos_relacionados: Product[];
}

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api';

export const ProductDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [product, setProduct] = useState<Product | null>(null);
  const [relatedProducts, setRelatedProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [quantity, setQuantity] = useState(1);
  const [isFavorite, setIsFavorite] = useState(false);
  const { handleAddToCart: addProductToCart, addedProductId } = useAddToCart();
  const { isAuthenticated } = useAuthStore();

  // Fetch product details
  useEffect(() => {
    const fetchProductDetail = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(`${API_BASE_URL}/productos/${id}/`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error('Producto no encontrado');
        }

        const data: ProductDetailResponse = await response.json();
        
        // Convertir precio a número (puede venir como string del backend)
        const productoNormalizado = {
          ...data.producto,
          precio: typeof data.producto.precio === 'string' 
            ? parseFloat(data.producto.precio) 
            : data.producto.precio,
        };
        
        const productosRelacionadosNormalizados = (data.productos_relacionados || []).map(p => ({
          ...p,
          precio: typeof p.precio === 'string' ? parseFloat(p.precio) : p.precio,
        }));
        
        setProduct(productoNormalizado);
        setRelatedProducts(productosRelacionadosNormalizados);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Error al cargar el producto');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchProductDetail();
    }
  }, [id]);

  // Cargar estado de favorito
  useEffect(() => {
    if (!product || !isAuthenticated) {
      setIsFavorite(false);
      return;
    }

    const checkFavorite = async () => {
      try {
        // ✅ Obtener token desde Zustand (no desde storage)
        const { accessToken } = useAuthStore.getState();
        
        // Validar que el token exista
        if (!accessToken) {
          setIsFavorite(false);
          return;
        }
        
        const token = accessToken;

        const response = await fetch(`${API_BASE_URL}/favoritos/es-favorito/${product.id}/`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          setIsFavorite(data.es_favorito);
        } else if (response.status === 401) {
          // Token inválido o expirado
          setIsFavorite(false);
        }
      } catch (err) {
        console.error('Error al verificar favorito:', err);
        setIsFavorite(false);
      }
    };

    checkFavorite();
  }, [product, isAuthenticated]);

  const handleAddToCart = () => {
    if (!product || !isAuthenticated) {
      navigate('/login');
      return;
    }

    // ✅ Agregar al carrito con la cantidad seleccionada Y el stock disponible
    addProductToCart(product.id, quantity, product.stock);
  };

  const handleToggleFavorite = async () => {
    // Verificación 1: Producto existe
    if (!product) return;

    // Verificación 2: Usuario autenticado
    if (!isAuthenticated) {
      navigate('/login', { replace: true });
      return;
    }

    // Verificación 3: Token válido
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
      const response = await fetch(`${API_BASE_URL}/favoritos/${endpoint}/${product.id}/`, {
        method,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      // Manejo de respuestas
      if (response.ok) {
        const data = await response.json();
        
        // Actualizar estado de favorito
        setIsFavorite(!isFavorite);
        
        // Actualizar contador de favoritos desde la respuesta del backend
        if (data.favoritos_count !== undefined) {
          setProduct(prev => (prev ? {
            ...prev,
            favoritos_count: data.favoritos_count,
          } : null));
        }
      } else if (response.status === 401) {
        // Token expirado o inválido
        console.warn('Token inválido, redirigiendo a login');
        navigate('/login', { replace: true });
      } else if (response.status === 404) {
        // Producto no encontrado
        console.error('Producto no encontrado');
      } else {
        // Otro error
        console.error('Error al actualizar favorito:', response.status);
      }
    } catch (err) {
      console.error('Error en handleToggleFavorite:', err);
    }
  };

  const handleQuantityChange = (value: number) => {
    // Validar que no sea menor a 1
    if (value < 1) {
      return;
    }
    
    // Validar que no exceda el stock disponible
    if (product && value > product.stock) {
      const maxDisponible = product.stock;
      // Solo mostrar toast si intenta agregar significativamente más
      if (value > maxDisponible + 5) {
        toast.error(
          `Máximo disponible: ${maxDisponible} unidades`,
          {
            icon: '⚠️',
            duration: 2000,
          }
        );
      }
      // Establecer a la cantidad máxima disponible silenciosamente
      setQuantity(maxDisponible);
      return;
    }
    
    // Cambiar cantidad sin notificación (es una acción normal)
    setQuantity(value);
  };

  const handleRelatedProductClick = (productId: number) => {
    navigate(`/producto/${productId}`);
    window.scrollTo(0, 0);
  };

  if (loading) {
    return (
      <div className="product-detail-container">
        <div className="loading-skeleton">
          <div className="skeleton-image" />
          <div className="skeleton-content">
            <div className="skeleton-line" />
            <div className="skeleton-line" />
            <div className="skeleton-line" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="product-detail-wrapper">
        <div className="product-detail-container">
          <div className="error-container">
            <h2>Producto no encontrado</h2>
            <p>{error}</p>
            <button onClick={() => navigate('/')} className="btn-back">
              Volver al inicio
            </button>
          </div>
        </div>
      </div>
    );
  }

  const discountedPrice = product.precio * (1 - product.descuento / 100);
  const savings = product.precio - discountedPrice;
  const favoritosCount = product.favoritos_count || 0;

  return (
    <div className="product-detail-wrapper">
      <div className="product-detail-container">
        {/* Main Product Card */}
        <div className="product-card-main">
          {/* Left: Image */}
          <div className="product-card-image-section">
            <div className="product-card-image-container">
              <img
                src={product.imagen_url}
                alt={product.nombre}
                className="product-card-image"
              />
              {product.descuento > 0 && (
                <div className="product-card-discount-badge">-{product.descuento}%</div>
              )}
            </div>
          </div>

          {/* Right: Details */}
          <div className="product-card-details">
            {/* Category */}
            <span className="product-card-category">{product.categoria}</span>

            {/* Title */}
            <h1 className="product-card-title">{product.nombre}</h1>

            {/* Favorites */}
            <button
              onClick={handleToggleFavorite}
              className={`product-card-favorites ${isFavorite ? 'is-favorite' : ''}`}
              aria-label={isFavorite ? 'Remover de favoritos' : 'Agregar a favoritos'}
            >
              <FiHeart size={18} fill={isFavorite ? 'currentColor' : 'none'} />
              <span>{favoritosCount.toLocaleString()} Personas lo Aman</span>
            </button>

            {/* Price */}
            <div className="product-card-price-section">
              <span className="product-card-price-current">${discountedPrice.toFixed(2)}</span>
              {product.descuento > 0 && (
                <>
                  <span className="product-card-price-original">${product.precio.toFixed(2)}</span>
                  <span className="product-card-savings">Ahorras ${savings.toFixed(2)}</span>
                </>
              )}
            </div>

            {/* Description - Moved after price */}
            <div className="product-card-description">
              <p>{product.descripcion}</p>
            </div>

            {/* Stock */}
            <div className="product-card-stock">
              {product.stock > 0 ? (
                <span className="stock-available">✓ En stock ({product.stock} disponibles)</span>
              ) : (
                <span className="stock-unavailable">✗ Agotado</span>
              )}
            </div>

            {/* Quantity Selector - Estilo VistaCarrito */}
            <div className="product-card-quantity-section">
              <label className="quantity-label">Cantidad:</label>
              <div className="cantidad-controles-compactos">
                <button
                  className="btn-cantidad-compacto"
                  onClick={() => handleQuantityChange(quantity - 1)}
                  aria-label="Disminuir cantidad"
                >
                  −
                </button>
                <span className="cantidad-display-compacto">{quantity}</span>
                <button
                  className="btn-cantidad-compacto"
                  onClick={() => handleQuantityChange(quantity + 1)}
                  aria-label="Aumentar cantidad"
                >
                  +
                </button>
              </div>
            </div>

            {/* Add to Cart Button */}
            <Button
              onClick={handleAddToCart}
              disabled={product.stock === 0}
              variant="primary"
              size="md"
              leftIcon={
                product.stock === 0 ? (
                  <MdVerified size={18} />
                ) : (
                  addedProductId === product.id ? (
                    <MdCheckCircle size={18} />
                  ) : (
                    <FiShoppingCart size={18} />
                  )
                )
              }
            >
              {product.stock === 0 ? 'Agotado!' : (addedProductId === product.id ? '¡AGREGADO!' : 'Agregar')}
            </Button>
          </div>
        </div>

        {/* Related Products Section */}
        {relatedProducts.length > 0 && (
          <div className="related-products-section">
            <h2>Productos relacionados</h2>
            <div className="related-products-grid">
              {relatedProducts.map((relatedProduct) => (
                <div
                  key={relatedProduct.id}
                  className="related-product-card"
                  onClick={() => handleRelatedProductClick(relatedProduct.id)}
                >
                  <div className="related-product-image">
                    <img
                      src={relatedProduct.imagen_url}
                      alt={relatedProduct.nombre}
                    />
                    {relatedProduct.descuento > 0 && (
                      <div className="discount-badge-small">
                        -{relatedProduct.descuento}%
                      </div>
                    )}
                  </div>
                  <div className="related-product-info">
                    <h4>{relatedProduct.nombre}</h4>
                    <p className="related-product-price">
                      ${(relatedProduct.precio * (1 - relatedProduct.descuento / 100)).toFixed(2)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
