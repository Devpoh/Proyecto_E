/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🛒 VISTA CARRITO - Página de Carrito de Compras
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Componente que muestra el carrito de compras con:
 * - Lista de productos agregados
 * - Controles para modificar cantidades
 * - Resumen de compra con totales
 * - Cálculo de impuestos y envío
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MdShoppingCart } from 'react-icons/md';
import toast from 'react-hot-toast';
import { useCartStore } from '@/app/store/useCartStore';
import { useSyncCart } from '@/shared/hooks/useSyncCart';
import { useCartSync } from '@/shared/hooks/useCartSync';
import { useUnloadSync } from '@/shared/hooks/useUnloadSync';
import { GlobalLoading } from '@/shared/ui/GlobalLoading';
import api from '@/shared/api/axios';
import './VistaCarrito.css';

interface ProductoCarritoDisplay {
  productoId: number;
  nombre: string;
  precio: number;
  precioOriginal?: number;
  imagen: string;
  categoria: string;
  cantidad: number;
  descuento?: number;
  stock: number;
}

const VistaCarrito: React.FC = () => {
  const navigate = useNavigate();
  const { items, updateQuantity } = useCartStore();
  const { syncRemoveFromBackend } = useSyncCart();
  const { updateWithDebounce, forceSync, pending } = useCartSync();
  
  // Sincronizar al cerrar/recargar página
  useUnloadSync();
  
  const [productosCarrito, setProductosCarrito] = useState<ProductoCarritoDisplay[]>([]);
  const [productosData, setProductosData] = useState<Record<number, ProductoCarritoDisplay>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [showPaymentForm, setShowPaymentForm] = useState(false);

  // Cargar productos desde API
  useEffect(() => {
    const cargarProductos = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/productos/');
        const productos = response.data.results || response.data;

        // Mapear productos a formato de display
        const productosMap: Record<number, ProductoCarritoDisplay> = {};
        productos.forEach((p: any) => {
          productosMap[p.id] = {
            productoId: p.id,
            nombre: p.nombre,
            precio: parseFloat(p.precio),
            imagen: p.imagen_url || 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop',
            categoria: p.categoria,
            cantidad: 1,
            descuento: p.descuento || 0,
            stock: p.stock || 0,
          };
        });

        setProductosData(productosMap);
      } catch (error) {
        console.error('Error cargando productos:', error);
      } finally {
        setIsLoading(false);
      }
    };

    cargarProductos();
  }, []);

  // Convertir items del store a formato de display
  useEffect(() => {
    const productos = items
      .map((item) => {
        const producto = productosData[item.productoId];
        if (producto) {
          return { ...producto, cantidad: item.cantidad };
        }
        return null;
      })
      .filter((p) => p !== null) as ProductoCarritoDisplay[];

    setProductosCarrito(productos);
  }, [items, productosData]);

  const actualizarCantidad = (productoId: number, nuevaCantidad: number) => {
    // Obtener el stock disponible del producto
    const producto = productosData[productoId];
    if (!producto) {
      toast.error('Producto no encontrado', {
        icon: '❌',
        duration: 2000,
      });
      return;
    }

    // Validar que no sea menor a 1
    if (nuevaCantidad < 1) {
      return;
    }

    // Validar que no exceda el stock disponible
    if (nuevaCantidad > producto.stock) {
      const maxDisponible = producto.stock;
      // Solo mostrar toast si intenta agregar significativamente más
      if (nuevaCantidad > maxDisponible + 5) {
        toast.error(
          `Máximo disponible: ${maxDisponible} unidades`,
          {
            icon: '⚠️',
            duration: 2000,
          }
        );
      }
      // Establecer a la cantidad máxima disponible silenciosamente
      updateQuantity(productoId, maxDisponible);
      
      // Debounce + sincronizar con backend
      updateWithDebounce(productoId, maxDisponible);
      return;
    }

    // Actualizar sin notificación (es una acción normal)
    updateQuantity(productoId, nuevaCantidad);
    
    // Debounce + sincronizar con backend
    updateWithDebounce(productoId, nuevaCantidad);
  };

  const eliminarProducto = (productoId: number) => {
    // CRÍTICO: SOLO sincronizar con backend
    // NO eliminar localmente porque:
    // 1. syncRemoveFromBackend procesa eliminaciones secuencialmente
    // 2. El backend responde con el carrito actualizado
    // 3. syncRemoveFromBackend actualiza el estado local con la respuesta del backend
    // 4. Esto evita desincronización y que reaparezcan items
    syncRemoveFromBackend(productoId);
  };

  const calcularSubtotal = () => {
    return productosCarrito.reduce((total, producto) => total + producto.precio * producto.cantidad, 0);
  };

  const calcularSubtotalSinDescuento = () => {
    return productosCarrito.reduce((total, producto) => {
      const descuento = producto.descuento || 0;
      const precioOriginal = descuento > 0 
        ? (producto.precio / (1 - descuento / 100)) 
        : producto.precio;
      return total + precioOriginal * producto.cantidad;
    }, 0);
  };

  const calcularDescuentoTotal = () => {
    return calcularSubtotalSinDescuento() - calcularSubtotal();
  };

  const subtotal = calcularSubtotal();
  const total = subtotal;

  const formatearPrecio = (precio: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(precio);
  };

  const totalProductos = productosCarrito.reduce((total, producto) => total + producto.cantidad, 0);

  return (
    <div className="vista-carrito">
      {/* Contenido Principal */}
      <main className="carrito-contenido carrito-contenido-padding">
        <div className="carrito-container">
          {/* Estado Vacío */}
          {productosCarrito.length === 0 ? (
            <div className="carrito-vacio-moderno">
              <div className="vacio-icono">
                <MdShoppingCart size={80} />
              </div>
              <h2>Tu carrito está vacío</h2>
              <p>Descubre productos increíbles y comienza tu experiencia de compra</p>
              <button
                className="btn-explorar-moderno"
                onClick={() => navigate('/productos')}
              >
                <span>Explorar Productos</span>
                <div className="btn-shine" />
              </button>
            </div>
          ) : (
            <>
              {/* Columna Izquierda - Lista de Productos */}
              <div className="productos-columna">
                <div className="productos-header">
                  <h2 className="productos-titulo">Tu Selección</h2>
                  <span className="productos-contador">
                    {totalProductos} {totalProductos === 1 ? 'artículo' : 'artículos'}
                  </span>
                </div>

                {productosCarrito.map((producto) => (
                  <div key={producto.productoId} className="producto-carrito-item">
                    {/* Botón eliminar */}
                    <button
                      className="btn-eliminar-integrado"
                      onClick={() => eliminarProducto(producto.productoId)}
                      aria-label={`Eliminar ${producto.nombre}`}
                      title="Eliminar producto"
                    >
                      ✕
                    </button>

                    {/* Imagen */}
                    <img
                      src={producto.imagen}
                      alt={producto.nombre}
                      className="producto-imagen-compacta"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.src =
                          'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=300&fit=crop';
                      }}
                      loading="lazy"
                    />

                    {/* Info del Producto */}
                    <div className="producto-info-compacta">
                      <span className="producto-nombre-compacto">{producto.nombre}</span>
                      <span className="producto-categoria-compacta">{producto.categoria}</span>
                      {producto.descuento && producto.descuento > 0 && (
                        <span className="producto-descuento-badge">-{producto.descuento}%</span>
                      )}
                    </div>

                    {/* Controles de Cantidad */}
                    <div className="cantidad-controles-compactos">
                      <button
                        className="btn-cantidad-compacto"
                        onClick={() => actualizarCantidad(producto.productoId, producto.cantidad - 1)}
                        aria-label="Disminuir cantidad"
                      >
                        −
                      </button>
                      <span className="cantidad-display-compacto">{producto.cantidad}</span>
                      <button
                        className="btn-cantidad-compacto"
                        onClick={() => actualizarCantidad(producto.productoId, producto.cantidad + 1)}
                        aria-label="Aumentar cantidad"
                      >
                        +
                      </button>
                    </div>

                    {/* Precio */}
                    <div className="producto-precio-seccion">
                      <div className="producto-precio-compacto">
                        {formatearPrecio(producto.precio * producto.cantidad)}
                      </div>
                      {producto.descuento && producto.descuento > 0 && (
                        <div className="producto-precio-original-tachado">
                          {formatearPrecio(
                            (producto.precio / (1 - producto.descuento / 100)) * producto.cantidad
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Columna Derecha - Resumen de Compra */}
              <div className="resumen-columna">
                <div className="resumen-card">
                  <h2 className="seccion-titulo">Resumen de Compra</h2>

                  <div className="resumen-detalles">
                    <div className="linea-resumen">
                      <span>Subtotal sin descuento</span>
                      <span>{formatearPrecio(calcularSubtotalSinDescuento())}</span>
                    </div>

                    {calcularDescuentoTotal() > 0 && (
                      <div className="linea-resumen descuento">
                        <span>Descuento total</span>
                        <span className="descuento-valor">-{formatearPrecio(calcularDescuentoTotal())}</span>
                      </div>
                    )}

                    <div className="linea-resumen total">
                      <span>Total a pagar</span>
                      <span>{formatearPrecio(total)}</span>
                    </div>
                  </div>

                  {Object.keys(pending).length > 0 && (
                    <div className="alerta-cambios-pendientes">
                      <span>⏳ Cambios pendientes de sincronizar...</span>
                    </div>
                  )}

                  <button 
                    className="boton-finalizar-compra"
                    onClick={async () => {
                      if (Object.keys(pending).length > 0) {
                        const synced = await forceSync();
                        if (synced) {
                          setShowPaymentForm(true);
                        }
                      } else {
                        setShowPaymentForm(true);
                      }
                    }}
                    disabled={Object.keys(pending).length > 0}
                  >
                    Finalizar Compra
                    <span className="precio-boton">{formatearPrecio(total)}</span>
                  </button>

                  <button
                    className="boton-seguir-comprando-secundario"
                    onClick={() => navigate('/productos')}
                  >
                    Seguir Comprando
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </main>

      {/* Modal de Formulario de Pago */}
      {showPaymentForm && (
        <div className="pago-modal-overlay">
          <div className="pago-modal">
            <div className="pago-modal-header">
              <h2>Formulario de Pago</h2>
              <button
                className="pago-modal-close"
                onClick={() => setShowPaymentForm(false)}
                aria-label="Cerrar"
              >
                ✕
              </button>
            </div>

            <div className="pago-modal-content">
              <div className="pago-resumen">
                <h3>Resumen del Pedido</h3>
                <div className="pago-resumen-item">
                  <span>Subtotal:</span>
                  <span>{formatearPrecio(subtotal)}</span>
                </div>
                <div className="pago-resumen-total">
                  <span>Total:</span>
                  <span>{formatearPrecio(total)}</span>
                </div>
              </div>

              <form className="pago-form">
                <div className="pago-form-group">
                  <label htmlFor="nombre">Nombre Completo</label>
                  <input
                    id="nombre"
                    type="text"
                    placeholder="Juan Pérez"
                    required
                  />
                </div>

                <div className="pago-form-group">
                  <label htmlFor="email">Correo Electrónico</label>
                  <input
                    id="email"
                    type="email"
                    placeholder="juan@example.com"
                    required
                  />
                </div>

                <div className="pago-form-group">
                  <label htmlFor="telefono">Teléfono</label>
                  <input
                    id="telefono"
                    type="tel"
                    placeholder="+1 (555) 000-0000"
                    required
                  />
                </div>

                <div className="pago-form-group">
                  <label htmlFor="direccion">Dirección de Envío</label>
                  <input
                    id="direccion"
                    type="text"
                    placeholder="Calle Principal 123"
                    required
                  />
                </div>

                <div className="pago-form-group">
                  <label htmlFor="ciudad">Ciudad</label>
                  <input
                    id="ciudad"
                    type="text"
                    placeholder="Santo Domingo"
                    required
                  />
                </div>

                <div className="pago-form-group">
                  <label htmlFor="metodo-pago">Método de Pago</label>
                  <select id="metodo-pago" required>
                    <option value="">Selecciona un método</option>
                    <option value="tropipay">Tropipay</option>
                    <option value="zelle">Zelle</option>
                  </select>
                </div>

                <div className="pago-form-actions">
                  <button
                    type="button"
                    className="pago-form-btn-cancel"
                    onClick={() => setShowPaymentForm(false)}
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="pago-form-btn-submit"
                  >
                    Continuar con el Pago
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Global Loading */}
      <GlobalLoading 
        isLoading={isLoading}
        message="Cargando productos..."
      />
    </div>
  );
};

export default VistaCarrito;
