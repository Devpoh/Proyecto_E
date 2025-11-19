/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📦 PAGE - Gestión de Pedidos
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { FiSearch, FiPackage, FiX, FiEye } from 'react-icons/fi';
import api from '@/shared/api/axios';
import { useAuthStore } from '@/app/store/useAuthStore';
import { useInvalidateAdminQueries } from '@/shared/hooks/useInvalidateAdminQueries';
import './PedidosPage.css';

interface DetallePedido {
  id: number;
  producto_nombre: string;
  producto_imagen: string | null;
  cantidad: number;
  precio_unitario: string;
  subtotal: string;
}

interface Pedido {
  id: number;
  usuario_nombre: string;
  usuario_email: string;
  estado: string;
  metodo_pago: string;
  total: string;
  direccion_entrega: string;
  telefono: string;
  notas: string | null;
  mensajero: number | null;
  mensajero_nombre: string | null;
  detalles: DetallePedido[];
  created_at: string;
  fecha_entrega: string | null;
}

const ESTADOS = [
  { value: 'pendiente', label: 'Pendiente', color: '#f59e0b' },
  { value: 'confirmado', label: 'Confirmado', color: '#3b82f6' },
  { value: 'en_preparacion', label: 'En Preparación', color: '#8b5cf6' },
  { value: 'en_camino', label: 'En Camino', color: '#06b6d4' },
  { value: 'entregado', label: 'Entregado', color: '#10b981' },
  { value: 'cancelado', label: 'Cancelado', color: '#ef4444' },
];

const fetchPedidos = async (filters: { search?: string; estado?: string }): Promise<Pedido[]> => {
  const params = new URLSearchParams();
  if (filters.search) params.append('search', filters.search);
  if (filters.estado) params.append('estado', filters.estado);
  
  const response = await api.get(`/admin/pedidos/?${params.toString()}`);
  return response.data.results || response.data;
};

const updatePedido = async (data: { id: number; updates: Partial<Pedido> }) => {
  const response = await api.patch(`/admin/pedidos/${data.id}/`, data.updates);
  return response.data;
};

export const PedidosPage = () => {
  const { user } = useAuthStore();
  const invalidateQueries = useInvalidateAdminQueries({ additionalKeys: ['admin-pedidos'] });
  
  const [search, setSearch] = useState('');
  const [estadoFilter, setEstadoFilter] = useState('');
  const [selectedPedido, setSelectedPedido] = useState<Pedido | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  // Query pedidos
  const { data: pedidos = [], isLoading } = useQuery({
    queryKey: ['admin-pedidos', search, estadoFilter],
    queryFn: () => fetchPedidos({ search, estado: estadoFilter }),
  });

  // Mutation actualizar
  const updateMutation = useMutation({
    mutationFn: updatePedido,
    onSuccess: () => {
      invalidateQueries();
      setShowDetailModal(false);
    },
  });

  const handleChangeEstado = (pedido: Pedido, nuevoEstado: string) => {
    updateMutation.mutate({
      id: pedido.id,
      updates: { estado: nuevoEstado },
    });
  };

  const getEstadoConfig = (estado: string) => {
    return ESTADOS.find(e => e.value === estado) || ESTADOS[0];
  };

  const canEdit = user?.rol === 'admin' || user?.rol === 'trabajador';

  return (
    <div className="pedidos-page">
      {/* Header */}
      <div className="pedidos-header">
        <div>
          <h1 className="pedidos-title">Gestión de Pedidos</h1>
          <p className="pedidos-subtitle">
            Administra y rastrea todos los pedidos
          </p>
        </div>
      </div>

      {/* Filtros */}
      <div className="pedidos-filters">
        <div className="pedidos-search">
          <FiSearch className="pedidos-search-icon" />
          <input
            type="text"
            placeholder="Buscar por ID, cliente o teléfono..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pedidos-search-input"
          />
        </div>

        <select
          value={estadoFilter}
          onChange={(e) => setEstadoFilter(e.target.value)}
          className="pedidos-filter-select"
        >
          <option value="">Todos los estados</option>
          {ESTADOS.map((estado) => (
            <option key={estado.value} value={estado.value}>
              {estado.label}
            </option>
          ))}
        </select>
      </div>

      {/* Tabla */}
      {isLoading ? (
        <div className="pedidos-loading">
          <div className="pedidos-spinner"></div>
          <p>Cargando pedidos...</p>
        </div>
      ) : (
        <div className="pedidos-table-container">
          <table className="pedidos-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Cliente</th>
                <th>Estado</th>
                <th>Total</th>
                <th>Método Pago</th>
                <th>Mensajero</th>
                <th>Fecha</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {pedidos.map((pedido) => {
                const estadoConfig = getEstadoConfig(pedido.estado);
                return (
                  <tr key={pedido.id}>
                    <td className="pedidos-table-id">#{pedido.id}</td>
                    <td>
                      <div className="pedidos-table-cliente">
                        <span className="pedidos-cliente-nombre">{pedido.usuario_nombre}</span>
                        <span className="pedidos-cliente-telefono">{pedido.telefono}</span>
                      </div>
                    </td>
                    <td>
                      {canEdit ? (
                        <select
                          value={pedido.estado}
                          onChange={(e) => handleChangeEstado(pedido, e.target.value)}
                          className="pedidos-estado-select"
                          style={{ borderColor: estadoConfig.color }}
                        >
                          {ESTADOS.map((estado) => (
                            <option key={estado.value} value={estado.value}>
                              {estado.label}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <span
                          className="pedidos-badge"
                          style={{ backgroundColor: `${estadoConfig.color}20`, color: estadoConfig.color }}
                        >
                          {estadoConfig.label}
                        </span>
                      )}
                    </td>
                    <td className="pedidos-table-total">${pedido.total}</td>
                    <td className="pedidos-table-pago">{pedido.metodo_pago}</td>
                    <td className="pedidos-table-mensajero">
                      {pedido.mensajero_nombre || 'Sin asignar'}
                    </td>
                    <td className="pedidos-table-fecha">
                      {new Date(pedido.created_at).toLocaleDateString('es-ES')}
                    </td>
                    <td>
                      <button
                        className="pedidos-action-btn pedidos-action-view"
                        onClick={() => {
                          setSelectedPedido(pedido);
                          setShowDetailModal(true);
                        }}
                        title="Ver detalles"
                      >
                        <FiEye />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>

          {pedidos.length === 0 && (
            <div className="pedidos-empty">
              <FiPackage size={48} />
              <p>No se encontraron pedidos</p>
            </div>
          )}
        </div>
      )}

      {/* Modal de detalles */}
      {showDetailModal && selectedPedido && (
        <div className="pedidos-modal-overlay" onClick={() => setShowDetailModal(false)}>
          <div className="pedidos-modal" onClick={(e) => e.stopPropagation()}>
            <div className="pedidos-modal-header">
              <h3 className="pedidos-modal-title">Pedido #{selectedPedido.id}</h3>
              <button
                className="pedidos-modal-close"
                onClick={() => setShowDetailModal(false)}
              >
                <FiX />
              </button>
            </div>

            <div className="pedidos-modal-content">
              {/* Info del cliente */}
              <div className="pedidos-detail-section">
                <h4>Información del Cliente</h4>
                <div className="pedidos-detail-grid">
                  <div>
                    <span className="pedidos-detail-label">Nombre:</span>
                    <span>{selectedPedido.usuario_nombre}</span>
                  </div>
                  <div>
                    <span className="pedidos-detail-label">Email:</span>
                    <span>{selectedPedido.usuario_email}</span>
                  </div>
                  <div>
                    <span className="pedidos-detail-label">Teléfono:</span>
                    <span>{selectedPedido.telefono}</span>
                  </div>
                  <div>
                    <span className="pedidos-detail-label">Dirección:</span>
                    <span>{selectedPedido.direccion_entrega}</span>
                  </div>
                </div>
              </div>

              {/* Productos */}
              <div className="pedidos-detail-section">
                <h4>Productos</h4>
                <div className="pedidos-productos-list">
                  {selectedPedido.detalles.map((detalle) => (
                    <div key={detalle.id} className="pedidos-producto-item">
                      {detalle.producto_imagen && (
                        <img
                          src={detalle.producto_imagen}
                          alt={detalle.producto_nombre}
                          className="pedidos-producto-img"
                        />
                      )}
                      <div className="pedidos-producto-info">
                        <span className="pedidos-producto-nombre">{detalle.producto_nombre}</span>
                        <span className="pedidos-producto-cantidad">x{detalle.cantidad}</span>
                      </div>
                      <span className="pedidos-producto-precio">${detalle.subtotal}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Resumen */}
              <div className="pedidos-detail-section">
                <div className="pedidos-detail-resumen">
                  <div className="pedidos-resumen-row">
                    <span>Método de pago:</span>
                    <strong>{selectedPedido.metodo_pago}</strong>
                  </div>
                  <div className="pedidos-resumen-row pedidos-resumen-total">
                    <span>Total:</span>
                    <strong>${selectedPedido.total}</strong>
                  </div>
                </div>
              </div>

              {selectedPedido.notas && (
                <div className="pedidos-detail-section">
                  <h4>Notas</h4>
                  <p className="pedidos-notas">{selectedPedido.notas}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
