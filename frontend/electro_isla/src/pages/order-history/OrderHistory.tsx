/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📦 PAGE - Order History
 * ═══════════════════════════════════════════════════════════════════════════════
 * Historial de pedidos y favoritos del usuario autenticado
 */

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MdFavoriteBorder, MdFavorite, MdShoppingBag } from 'react-icons/md';
import { FiCalendar, FiDollarSign } from 'react-icons/fi';
import { useAuthStore } from '@/app/store/useAuthStore';
import { Button } from '@/shared/ui';
import './OrderHistory.css';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api';

interface Producto {
  id: number;
  nombre: string;
  precio: number;
  descuento: number;
  imagen_url: string;
}

interface DetallePedido {
  id: number;
  producto: Producto;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
}

interface Pedido {
  id: number;
  estado: string;
  metodo_pago: string;
  total: number;
  direccion_entrega: string;
  telefono: string;
  created_at: string;
  detalles: DetallePedido[];
}

export function OrderHistory() {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuthStore();
  const [activeTab, setActiveTab] = useState<'pedidos' | 'favoritos'>('pedidos');
  const [pedidos, setPedidos] = useState<Pedido[]>([]);
  const [favoritos, setFavoritos] = useState<Producto[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Redirigir si no está autenticado
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  // Datos de ejemplo para demostración
  const pedidosEjemplo: Pedido[] = [
    {
      id: 1001,
      estado: 'entregado',
      metodo_pago: 'tarjeta',
      total: 2599.99,
      direccion_entrega: 'Calle Principal 123, Apto 4B, Santo Domingo',
      telefono: '+1-829-555-0123',
      created_at: '2025-11-05T14:30:00Z',
      detalles: [
        {
          id: 1,
          producto: {
            id: 1,
            nombre: 'Laptop ASUS VivoBook 15',
            precio: 1299.99,
            descuento: 15,
            imagen_url: 'https://images.unsplash.com/photo-1515378791036-0648a3e4d747?w=300&h=300&fit=crop',
          },
          cantidad: 1,
          precio_unitario: 1299.99,
          subtotal: 1299.99,
        },
        {
          id: 2,
          producto: {
            id: 2,
            nombre: 'Mouse Inalámbrico Logitech',
            precio: 49.99,
            descuento: 10,
            imagen_url: 'https://images.unsplash.com/photo-1527814050087-3793815479db?w=300&h=300&fit=crop',
          },
          cantidad: 2,
          precio_unitario: 49.99,
          subtotal: 99.98,
        },
        {
          id: 3,
          producto: {
            id: 3,
            nombre: 'Cable USB-C 2m',
            precio: 19.99,
            descuento: 0,
            imagen_url: 'https://images.unsplash.com/photo-1625948515291-69613efd103f?w=300&h=300&fit=crop',
          },
          cantidad: 2,
          precio_unitario: 19.99,
          subtotal: 39.98,
        },
      ],
    },
    {
      id: 1002,
      estado: 'en_camino',
      metodo_pago: 'efectivo',
      total: 899.99,
      direccion_entrega: 'Avenida Independencia 456, Santo Domingo',
      telefono: '+1-829-555-0124',
      created_at: '2025-11-07T10:15:00Z',
      detalles: [
        {
          id: 4,
          producto: {
            id: 4,
            nombre: 'Monitor LG 24" Full HD',
            precio: 899.99,
            descuento: 20,
            imagen_url: 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=300&h=300&fit=crop',
          },
          cantidad: 1,
          precio_unitario: 899.99,
          subtotal: 899.99,
        },
      ],
    },
    {
      id: 1003,
      estado: 'confirmado',
      metodo_pago: 'tarjeta',
      total: 349.97,
      direccion_entrega: 'Calle Duarte 789, Santiago',
      telefono: '+1-829-555-0125',
      created_at: '2025-11-08T09:45:00Z',
      detalles: [
        {
          id: 5,
          producto: {
            id: 5,
            nombre: 'Teclado Mecánico RGB',
            precio: 149.99,
            descuento: 25,
            imagen_url: 'https://images.unsplash.com/photo-1587829191301-dc798b83add3?w=300&h=300&fit=crop',
          },
          cantidad: 2,
          precio_unitario: 149.99,
          subtotal: 299.98,
        },
        {
          id: 6,
          producto: {
            id: 6,
            nombre: 'Mousepad Grande',
            precio: 24.99,
            descuento: 0,
            imagen_url: 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=300&h=300&fit=crop',
          },
          cantidad: 2,
          precio_unitario: 24.99,
          subtotal: 49.98,
        },
      ],
    },
  ];

  const favoritosEjemplo: Producto[] = [];

  // Cargar pedidos
  useEffect(() => {
    const cargarPedidos = async () => {
      try {
        // ✅ Obtener token desde Zustand (no desde storage)
        const { accessToken } = useAuthStore.getState();
        if (!accessToken) return;
        const token = accessToken;

        const response = await fetch(`${API_BASE_URL}/mis-pedidos/`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          setPedidos(data.pedidos || pedidosEjemplo); // Usar ejemplo si está vacío
        } else if (response.status === 401) {
          navigate('/login', { replace: true });
        } else {
          // Usar datos de ejemplo en desarrollo
          setPedidos(pedidosEjemplo);
        }
      } catch (err) {
        console.error('Error al cargar pedidos:', err);
        setError('Error al cargar el historial de pedidos');
        // Usar datos de ejemplo en caso de error
        setPedidos(pedidosEjemplo);
      }
    };

    if (activeTab === 'pedidos') {
      cargarPedidos();
    }
  }, [activeTab, navigate]);

  // Cargar favoritos (al montar el componente, no solo cuando se hace click en el tab)
  useEffect(() => {
    const cargarFavoritos = async () => {
      try {
        // ✅ Obtener token desde Zustand (no desde storage)
        const { accessToken } = useAuthStore.getState();
        if (!accessToken) return;
        const token = accessToken;

        const response = await fetch(`${API_BASE_URL}/mis-favoritos/`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (response.ok) {
          const data = await response.json();
          setFavoritos(data.favoritos || favoritosEjemplo); // Usar ejemplo si está vacío
        } else {
          // Usar datos de ejemplo en desarrollo
          setFavoritos(favoritosEjemplo);
        }
      } catch (err) {
        console.error('Error al cargar favoritos:', err);
        // Usar datos de ejemplo en caso de error
        setFavoritos(favoritosEjemplo);
      }
    };

    // ✅ Cargar favoritos siempre al montar el componente
    cargarFavoritos();
  }, []);

  useEffect(() => {
    setLoading(false);
  }, []);

  const formatearFecha = (fecha: string) => {
    return new Date(fecha).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const obtenerColorEstado = (estado: string) => {
    const colores: { [key: string]: string } = {
      'pendiente': '#f59e0b',
      'confirmado': '#3b82f6',
      'en_preparacion': '#8b5cf6',
      'en_camino': '#06b6d4',
      'entregado': '#10b981',
      'cancelado': '#ef4444',
    };
    return colores[estado] || '#6b7280';
  };

  const obtenerEtiquetaEstado = (estado: string) => {
    const etiquetas: { [key: string]: string } = {
      'pendiente': 'Pendiente',
      'confirmado': 'Confirmado',
      'en_preparacion': 'En Preparación',
      'en_camino': 'En Camino',
      'entregado': 'Entregado',
      'cancelado': 'Cancelado',
    };
    return etiquetas[estado] || estado;
  };

  if (loading) {
    return (
      <main className="order-history-page">
        <div className="order-history-container">
          <div className="loading">Cargando...</div>
        </div>
      </main>
    );
  }

  return (
    <main className="order-history-page">
      <div className="order-history-container">
        {/* Encabezado */}
        <div className="order-history-header">
          <h1>Mi Historial</h1>
        </div>

        {/* Tabs */}
        <div className="order-history-tabs">
          <button
            className={`tab ${activeTab === 'pedidos' ? 'active' : ''}`}
            onClick={() => setActiveTab('pedidos')}
          >
            <MdShoppingBag size={20} />
            Mis Pedidos ({pedidos.length})
          </button>
          <button
            className={`tab ${activeTab === 'favoritos' ? 'active' : ''}`}
            onClick={() => setActiveTab('favoritos')}
          >
            <MdFavorite size={20} />
            Mis Favoritos ({favoritos.length})
          </button>
        </div>

        {/* Contenido */}
        <div className="order-history-content">
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {/* Tab: Pedidos */}
          {activeTab === 'pedidos' && (
            <div className="pedidos-section">
              {pedidos.length === 0 ? (
                <div className="empty-state">
                  <MdShoppingBag size={64} />
                  <h2>No tienes pedidos aún</h2>
                  <p>Comienza a comprar y tu historial aparecerá aquí</p>
                  <Button
                    variant="primary"
                    size="lg"
                    onClick={() => navigate('/productos')}
                  >
                    Explorar Productos
                  </Button>
                </div>
              ) : (
                <div className="pedidos-grid">
                  {pedidos.map((pedido) => (
                    <div key={pedido.id} className="pedido-card">
                      {/* Encabezado del pedido */}
                      <div className="pedido-header">
                        <div className="pedido-id">
                          <h3>Pedido #{pedido.id}</h3>
                          <span
                            className="estado-badge"
                            style={{ backgroundColor: obtenerColorEstado(pedido.estado) }}
                          >
                            {obtenerEtiquetaEstado(pedido.estado)}
                          </span>
                        </div>
                        <div className="pedido-fecha">
                          <FiCalendar size={16} />
                          {formatearFecha(pedido.created_at)}
                        </div>
                      </div>

                      {/* Detalles de productos */}
                      <div className="pedido-detalles">
                        <h4>Productos:</h4>
                        <div className="detalles-lista">
                          {pedido.detalles.map((detalle) => (
                            <div key={detalle.id} className="detalle-item">
                              {detalle.producto.imagen_url && (
                                <img
                                  src={detalle.producto.imagen_url}
                                  alt={detalle.producto.nombre}
                                  className="detalle-imagen"
                                />
                              )}
                              <div className="detalle-info">
                                <p className="detalle-nombre">{detalle.producto.nombre}</p>
                                <p className="detalle-cantidad">Cantidad: {detalle.cantidad}</p>
                                <p className="detalle-precio">
                                  ${detalle.precio_unitario.toFixed(2)} x {detalle.cantidad} = ${detalle.subtotal.toFixed(2)}
                                </p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Información de entrega */}
                      <div className="pedido-entrega">
                        <div className="entrega-item">
                          <label>Dirección:</label>
                          <p>{pedido.direccion_entrega}</p>
                        </div>
                        <div className="entrega-item">
                          <label>Teléfono:</label>
                          <p>{pedido.telefono}</p>
                        </div>
                        <div className="entrega-item">
                          <label>Método de Pago:</label>
                          <p className="metodo-pago">{pedido.metodo_pago}</p>
                        </div>
                      </div>

                      {/* Total */}
                      <div className="pedido-total">
                        <FiDollarSign size={20} />
                        <span>Total: ${pedido.total.toFixed(2)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Tab: Favoritos */}
          {activeTab === 'favoritos' && (
            <div className="favoritos-section">
              {favoritos.length === 0 ? (
                <div className="empty-state">
                  <MdFavoriteBorder size={64} />
                  <h2>No tienes favoritos aún</h2>
                  <p>Agrega productos a favoritos para verlos aquí</p>
                  <Button
                    variant="primary"
                    size="lg"
                    onClick={() => navigate('/productos')}
                  >
                    Explorar Productos
                  </Button>
                </div>
              ) : (
                <div className="favoritos-grid">
                  {favoritos.map((producto) => (
                    <div key={producto.id} className="favorito-card">
                      <div className="favorito-imagen">
                        {producto.imagen_url && (
                          <img
                            src={producto.imagen_url}
                            alt={producto.nombre}
                          />
                        )}
                        {producto.descuento > 0 && (
                          <div className="descuento-badge">
                            -{producto.descuento}%
                          </div>
                        )}
                      </div>
                      <div className="favorito-info">
                        <h3>{producto.nombre}</h3>
                        <div className="favorito-precios">
                          <span className="precio-actual">
                            ${(parseFloat(String(producto.precio)) * (1 - producto.descuento / 100)).toFixed(2)}
                          </span>
                          {producto.descuento > 0 && (
                            <span className="precio-original">
                              ${parseFloat(String(producto.precio)).toFixed(2)}
                            </span>
                          )}
                        </div>
                        <Button
                          variant="primary"
                          size="md"
                          onClick={() => navigate(`/producto/${producto.id}`)}
                          style={{ width: '100%', marginTop: '12px' }}
                        >
                          Ver Detalles
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
