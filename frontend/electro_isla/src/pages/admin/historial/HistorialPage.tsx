/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📄 PAGE - Historial de Acciones (Solo Admin)
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useInvalidateAdminQueries } from '@/shared/hooks/useInvalidateAdminQueries';
import { 
  FiClock, 
  FiFilter, 
  FiSearch, 
  FiEye,
  FiX,
  FiUser,
  FiPackage,
  FiShoppingBag,
  FiTrash2,
  FiAlertTriangle
} from 'react-icons/fi';
import api from '@/shared/api/axios';
import { GlobalLoading } from '@/shared/ui/GlobalLoading';
import { ExportButtons } from '@/shared/ui/ExportButtons';
import { DateRangeFilter, getDateRange } from '@/shared/ui/DateRangeFilter';
import type { DateRangeOption } from '@/shared/ui/DateRangeFilter';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import './HistorialPage.css';

interface AuditLog {
  id: number;
  usuario_nombre: string;
  usuario_nombre_completo: string;
  accion: string;
  accion_display: string;
  modulo: string;
  modulo_display: string;
  objeto_id: number;
  objeto_repr: string;
  detalles: Record<string, any>;
  ip_address: string;
  user_agent: string;
  timestamp: string;
}

interface HistorialResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: AuditLog[];
}

const fetchHistorial = async (params: URLSearchParams): Promise<HistorialResponse> => {
  const response = await api.get(`/admin/historial/?${params.toString()}`);
  return response.data;
};

const deleteHistorial = async (id: number) => {
  await api.delete(`/admin/historial/${id}/`);
};

const deleteAllHistorial = async () => {
  await api.delete('/admin/historial/clear_all/');
};

export const HistorialPage = () => {
  const invalidateQueries = useInvalidateAdminQueries({ additionalKeys: ['historial'] });
  const [search, setSearch] = useState('');
  const [moduloFilter, setModuloFilter] = useState('');
  const [accionFilter, setAccionFilter] = useState('');
  const [dateRangeOption, setDateRangeOption] = useState<DateRangeOption>('month');
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showClearAllModal, setShowClearAllModal] = useState(false);
  const [logToDelete, setLogToDelete] = useState<AuditLog | null>(null);

  // Construir parámetros de búsqueda
  const dateRange = getDateRange(dateRangeOption);
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (moduloFilter) params.append('modulo', moduloFilter);
  if (accionFilter) params.append('accion', accionFilter);
  if (dateRange.desde) params.append('fecha_desde', dateRange.desde);
  if (dateRange.hasta) params.append('fecha_hasta', dateRange.hasta);

  const { data, isLoading } = useQuery({
    queryKey: ['historial', search, moduloFilter, accionFilter, dateRangeOption],
    queryFn: () => fetchHistorial(params),
  });

  // Mutación para eliminar
  const deleteMutation = useMutation({
    mutationFn: deleteHistorial,
    onSuccess: () => {
      invalidateQueries();
      setShowDeleteModal(false);
      setLogToDelete(null);
    },
  });

  // Mutación para limpiar todo
  const clearAllMutation = useMutation({
    mutationFn: deleteAllHistorial,
    onSuccess: () => {
      invalidateQueries();
      setShowClearAllModal(false);
    },
  });

  const handleDeleteClick = (log: AuditLog) => {
    setLogToDelete(log);
    setShowDeleteModal(true);
  };

  const handleConfirmDelete = () => {
    if (logToDelete) {
      deleteMutation.mutate(logToDelete.id);
    }
  };

  const handleCancelDelete = () => {
    setShowDeleteModal(false);
    setLogToDelete(null);
  };

  const handleViewDetails = (log: AuditLog) => {
    setSelectedLog(log);
    setShowDetailsModal(true);
  };

  const getAccionBadgeClass = (accion: string) => {
    switch (accion) {
      case 'crear':
        return 'historial-badge-success';
      case 'editar':
        return 'historial-badge-warning';
      case 'eliminar':
        return 'historial-badge-danger';
      case 'cambiar_rol':
        return 'historial-badge-info';
      case 'activar':
        return 'historial-badge-success';
      case 'desactivar':
        return 'historial-badge-secondary';
      default:
        return 'historial-badge-default';
    }
  };

  const getModuloIcon = (modulo: string) => {
    switch (modulo) {
      case 'usuario':
        return <FiUser />;
      case 'producto':
        return <FiPackage />;
      case 'pedido':
        return <FiShoppingBag />;
      default:
        return <FiClock />;
    }
  };

  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  };

  const exportToPDF = () => {
    if (!data?.results) return;

    const doc = new jsPDF();
    
    doc.setFontSize(18);
    doc.text('Historial de Acciones', 14, 22);
    
    doc.setFontSize(10);
    doc.text(`Generado: ${new Date().toLocaleDateString('es-ES')} ${new Date().toLocaleTimeString('es-ES')}`, 14, 30);
    
    const tableData = data.results.map(log => {
      const detalles = formatDetalles(log.detalles);
      let detallesStr = 'Sin detalles';
      
      if (detalles && detalles.length > 0) {
        detallesStr = detalles.map((d: any) => {
          if (!d) return '';
          if (d.esCreacion || d.esEliminacion) {
            return `${d.label}: ${d.valor}`;
          } else if (d.anterior !== undefined && d.nuevo !== undefined) {
            return `${d.label}: ${d.anterior} -> ${d.nuevo}`;
          }
          return '';
        }).filter(Boolean).join(' | ').substring(0, 150);
      }
      
      return [
        log.timestamp.split('T')[0],
        log.usuario_nombre_completo,
        log.accion_display,
        log.modulo_display,
        log.objeto_repr,
        detallesStr || 'N/A'
      ];
    });

    autoTable(doc, {
      head: [['Fecha', 'Usuario', 'Acción', 'Tipo', 'Elemento', 'Cambios']],
      body: tableData,
      startY: 35,
      styles: { 
        fontSize: 9,
        cellPadding: 4,
        overflow: 'linebreak',
        halign: 'left',
        valign: 'top',
        textColor: [40, 40, 40]
      },
      headStyles: { 
        fillColor: [255, 187, 0],
        textColor: [255, 255, 255],
        fontStyle: 'bold',
        halign: 'center',
        fontSize: 10
      },
      columnStyles: {
        0: { cellWidth: 18 },
        1: { cellWidth: 25 },
        2: { cellWidth: 22 },
        3: { cellWidth: 22 },
        4: { cellWidth: 28 },
        5: { cellWidth: 55 }
      },
      didDrawPage: (data) => {
        // Pie de página
        const pageCount = (doc as any).internal.getNumberOfPages();
        const pageSize = (doc as any).internal.pageSize;
        const pageHeight = pageSize.getHeight();
        const pageWidth = pageSize.getWidth();
        
        doc.setFontSize(9);
        doc.text(
          `Página ${data.pageNumber} de ${pageCount}`,
          pageWidth / 2,
          pageHeight - 10,
          { align: 'center' }
        );
      }
    });

    doc.save(`historial-${new Date().toISOString().split('T')[0]}.pdf`);
  };

  const exportToExcel = () => {
    if (!data?.results) return;

    const excelData = data.results.map(log => {
      const detalles = formatDetalles(log.detalles);
      const baseData: Record<string, string> = {
        'Fecha': formatDate(log.timestamp),
        'Usuario': log.usuario_nombre_completo,
        'Acción': log.accion_display,
        'Tipo': log.modulo_display,
      };

      // Agregar detalles como columnas separadas
      if (detalles && detalles.length > 0) {
        detalles.forEach((detalle: any) => {
          if (detalle) {
            if (detalle.esCreacion || detalle.esEliminacion) {
              baseData[detalle.label] = detalle.valor;
            } else {
              baseData[`${detalle.label} (Antes)`] = detalle.anterior;
              baseData[`${detalle.label} (Después)`] = detalle.nuevo;
            }
          }
        });
      }

      return baseData;
    });

    const ws = XLSX.utils.json_to_sheet(excelData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Historial');
    
    XLSX.writeFile(wb, `historial-${new Date().toISOString().split('T')[0]}.xlsx`);
  };

  const formatDetalles = (detalles: Record<string, any>) => {
    if (!detalles || typeof detalles !== 'object') return null;

    const labels: Record<string, string> = {
      // Productos
      'nombre': 'Nombre',
      'descripcion': 'Descripción',
      'precio': 'Precio (S/.)',
      'stock': 'Stock',
      'categoria': 'Categoría',
      'activo': 'Estado',
      'descuento': 'Descuento (%)',
      'en_carrusel': 'En Carrusel',
      
      // Usuarios
      'username': 'Usuario',
      'email': 'Correo',
      'first_name': 'Nombre',
      'last_name': 'Apellido',
      'rol': 'Rol',
      'is_active': 'Activo',
      'is_staff': 'Staff',
      'is_superuser': 'Superusuario',
      
      // Pedidos
      'estado': 'Estado',
      'total': 'Total (S/.)',
      'direccion_envio': 'Dirección',
      'metodo_pago': 'Pago',
    };

    const formatValue = (value: any): string => {
      if (value === null || value === undefined) return '-';
      if (typeof value === 'boolean') return value ? 'Si' : 'No';
      if (typeof value === 'number') return String(value);
      // Solo limpiar caracteres HTML entities, preservar espacios
      let str = String(value).trim();
      str = str.replace(/&amp;/g, '&');
      str = str.replace(/&lt;/g, '<');
      str = str.replace(/&gt;/g, '>');
      str = str.replace(/&quot;/g, '"');
      str = str.replace(/&#039;/g, "'");
      // Limitar a 50 caracteres
      return str.length > 50 ? str.substring(0, 50) : str;
    };

    // Procesar cambios_realizados (ediciones)
    const cambios = detalles.cambios_realizados || {};
    if (Object.keys(cambios).length > 0) {
      return Object.entries(cambios)
        .map(([key, change]: [string, any]) => {
          if (typeof change !== 'object' || !change.anterior || change.nuevo === undefined) {
            return null;
          }
          
          const anterior = formatValue(change.anterior);
          const nuevo = formatValue(change.nuevo);
          
          return {
            label: labels[key] || key.replace(/_/g, ' '),
            anterior: anterior,
            nuevo: nuevo
          };
        })
        .filter(Boolean);
    }

    // Procesar datos_creados (creaciones)
    const datosCreados = detalles.datos_creados || {};
    if (Object.keys(datosCreados).length > 0) {
      return Object.entries(datosCreados)
        .map(([key, value]: [string, any]) => {
          return {
            label: labels[key] || key.replace(/_/g, ' '),
            valor: formatValue(value),
            esCreacion: true
          };
        })
        .filter(Boolean);
    }

    // Procesar datos_eliminados (eliminaciones)
    const datosEliminados = detalles.datos_eliminados || {};
    if (Object.keys(datosEliminados).length > 0) {
      return Object.entries(datosEliminados)
        .map(([key, value]: [string, any]) => {
          return {
            label: labels[key] || key.replace(/_/g, ' '),
            valor: formatValue(value),
            esEliminacion: true
          };
        })
        .filter(Boolean);
    }

    return null;
  };

  if (isLoading) {
    return (
      <div className="historial-loading">
        <div className="historial-spinner"></div>
        <p>Cargando historial...</p>
      </div>
    );
  }

  return (
    <div className="historial-page">
      {/* Header */}
      <div className="historial-header">
        <div>
          <h1 className="historial-title">
            <FiClock />
            Historial de Acciones
          </h1>
          <p className="historial-subtitle">
            Registro completo de todas las acciones realizadas en el sistema
          </p>
        </div>
        <div className="historial-header-actions">
          <ExportButtons 
            onExportPDF={exportToPDF}
            onExportExcel={exportToExcel}
            pdfLabel="PDF"
            excelLabel="Excel"
          />
          <button 
            className="historial-btn-clear-all"
            onClick={() => setShowClearAllModal(true)}
            title="Limpiar todo el historial"
          >
            <FiTrash2 />
            <span>Limpiar Todo</span>
          </button>
        </div>
      </div>

      {/* Filtros */}
      <div className="historial-filters">
        <div className="historial-search">
          <FiSearch className="historial-search-icon" />
          <input
            type="text"
            placeholder="Buscar por objeto o usuario..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="historial-search-input"
          />
        </div>

        <DateRangeFilter 
          value={dateRangeOption}
          onChange={setDateRangeOption}
          label=""
        />

        <select
          value={moduloFilter}
          onChange={(e) => setModuloFilter(e.target.value)}
          className="historial-filter-select"
        >
          <option value="">Todos los módulos</option>
          <option value="producto">Productos</option>
          <option value="usuario">Usuarios</option>
          <option value="pedido">Pedidos</option>
        </select>

        <select
          value={accionFilter}
          onChange={(e) => setAccionFilter(e.target.value)}
          className="historial-filter-select"
        >
          <option value="">Todas las acciones</option>
          <option value="crear">Crear</option>
          <option value="editar">Editar</option>
          <option value="eliminar">Eliminar</option>
          <option value="cambiar_rol">Cambiar Rol</option>
          <option value="activar">Activar</option>
          <option value="desactivar">Desactivar</option>
        </select>

        {(search || moduloFilter || accionFilter) && (
          <button
            className="historial-btn-clear"
            onClick={() => {
              setSearch('');
              setModuloFilter('');
              setAccionFilter('');
            }}
          >
            <FiX />
            Limpiar
          </button>
        )}
      </div>

      {/* Tabla */}
      <div className="historial-table-container">
        <table className="historial-table">
          <thead>
            <tr>
              <th>Fecha y Hora</th>
              <th>Usuario</th>
              <th>Acción</th>
              <th>Módulo</th>
              <th>Objeto</th>
              <th>IP</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {data?.results.map((log) => (
              <tr key={log.id}>
                <td className="historial-cell-date">
                  {formatDate(log.timestamp)}
                </td>
                <td className="historial-cell-user">
                  <div className="historial-user-info">
                    <span className="historial-user-name">
                      {log.usuario_nombre_completo}
                    </span>
                    <span className="historial-user-username">
                      @{log.usuario_nombre}
                    </span>
                  </div>
                </td>
                <td>
                  <span className={`historial-badge ${getAccionBadgeClass(log.accion)}`}>
                    {log.accion_display}
                  </span>
                </td>
                <td>
                  <div className="historial-modulo">
                    {getModuloIcon(log.modulo)}
                    <span>{log.modulo_display}</span>
                  </div>
                </td>
                <td className="historial-cell-objeto">
                  {log.objeto_repr}
                </td>
                <td className="historial-cell-ip">
                  {log.ip_address}
                </td>
                <td>
                  <div className="historial-actions">
                    <button
                      className="historial-btn-view"
                      onClick={() => handleViewDetails(log)}
                      title="Ver detalles"
                    >
                      <FiEye />
                    </button>
                    <button
                      className="historial-btn-delete"
                      onClick={() => handleDeleteClick(log)}
                      title="Eliminar registro"
                    >
                      <FiTrash2 />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {data?.results.length === 0 && (
          <div className="historial-empty">
            <FiFilter />
            <p>No se encontraron registros</p>
          </div>
        )}
      </div>

      {/* Modal de Detalles */}
      {showDetailsModal && selectedLog && (
        <div className="historial-modal-overlay">
          <div className="historial-modal">
            <div className="historial-modal-header">
              <h3>Detalles de la Acción</h3>
              <button
                className="historial-modal-close"
                onClick={() => setShowDetailsModal(false)}
              >
                <FiX />
              </button>
            </div>

            <div className="historial-modal-body">
              <div className="historial-detail-group">
                <label>📅 Fecha y Hora:</label>
                <p>{formatDate(selectedLog.timestamp)}</p>
              </div>

              <div className="historial-detail-group">
                <label>👤 Usuario:</label>
                <p>{selectedLog.usuario_nombre_completo}</p>
              </div>

              <div className="historial-detail-group">
                <label>⚡ Acción Realizada:</label>
                <p>
                  <span className={`historial-badge ${getAccionBadgeClass(selectedLog.accion)}`}>
                    {selectedLog.accion_display}
                  </span>
                </p>
              </div>

              <div className="historial-detail-group">
                <label>📦 Tipo:</label>
                <p>{selectedLog.modulo_display}</p>
              </div>

              <div className="historial-detail-group">
                <label>🎯 Elemento Afectado:</label>
                <p>{selectedLog.objeto_repr}</p>
              </div>

              <div className="historial-detail-group">
                <label>🌐 Dirección IP:</label>
                <p>{selectedLog.ip_address}</p>
              </div>

              {formatDetalles(selectedLog.detalles) && formatDetalles(selectedLog.detalles)!.length > 0 && (
                <div className="historial-detail-group">
                  <label>📋 {
                    selectedLog.accion === 'crear' ? 'Datos Creados:' : 
                    selectedLog.accion === 'eliminar' ? 'Datos Eliminados:' :
                    'Cambios Realizados:'
                  }</label>
                  <div className="historial-details-list">
                    {formatDetalles(selectedLog.detalles)!.map((item: any, index: number) => (
                      item && (
                        <div key={index} className="historial-detail-item">
                          <span className="historial-detail-label">{item.label}:</span>
                          {item.esCreacion ? (
                            <div className="historial-creation-value">
                              <span className="historial-creation-icon">✓</span>
                              <span className="historial-creation-text">{item.valor}</span>
                            </div>
                          ) : item.esEliminacion ? (
                            <div className="historial-deletion-value">
                              <span className="historial-deletion-icon">✕</span>
                              <span className="historial-deletion-text">{item.valor}</span>
                            </div>
                          ) : (
                            <div className="historial-change">
                              <span className="historial-change-before">{item.anterior}</span>
                              <span className="historial-change-arrow">→</span>
                              <span className="historial-change-after">{item.nuevo}</span>
                            </div>
                          )}
                        </div>
                      )
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Modal de Confirmación de Eliminación */}
      {showDeleteModal && logToDelete && (
        <div className="historial-modal-overlay">
          <div className="historial-modal historial-modal-confirm">
            <div className="historial-modal-header">
              <h3>Confirmar Eliminación</h3>
              <button
                className="historial-modal-close"
                onClick={handleCancelDelete}
              >
                <FiX />
              </button>
            </div>

            <div className="historial-modal-body">
              <p className="historial-confirm-message">
                ¿Estás seguro de que deseas eliminar el registro de <strong>{logToDelete.accion_display}</strong> realizado por <strong>{logToDelete.usuario_nombre_completo}</strong>?
              </p>
              <p className="historial-confirm-warning">
                Esta acción no se puede deshacer.
              </p>
            </div>

            <div className="historial-modal-actions">
              <button
                className="historial-modal-btn historial-modal-btn-cancel"
                onClick={handleCancelDelete}
                disabled={deleteMutation.isPending}
              >
                Cancelar
              </button>
              <button
                className="historial-modal-btn historial-modal-btn-delete"
                onClick={handleConfirmDelete}
                disabled={deleteMutation.isPending}
              >
                {deleteMutation.isPending ? 'Eliminando...' : 'Eliminar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de Confirmación para Limpiar Todo */}
      {showClearAllModal && (
        <div className="historial-modal-overlay">
          <div className="historial-modal historial-modal-confirm historial-modal-danger">
            <div className="historial-modal-header">
              <h3>⚠️ Confirmar Limpieza Total</h3>
              <button
                className="historial-modal-close"
                onClick={() => setShowClearAllModal(false)}
              >
                <FiX />
              </button>
            </div>

            <div className="historial-modal-body">
              <div className="historial-danger-icon">
                <FiAlertTriangle />
              </div>
              <p className="historial-confirm-message">
                ¿Estás seguro de que deseas <strong>eliminar TODO el historial</strong>?
              </p>
              <p className="historial-confirm-warning">
                Esta acción eliminará <strong>TODOS los registros</strong> del historial de forma permanente y <strong>NO SE PUEDE DESHACER</strong>.
              </p>
              <p className="historial-confirm-warning">
                Total de registros a eliminar: <strong>{data?.count || 0}</strong>
              </p>
            </div>

            <div className="historial-modal-actions">
              <button
                className="historial-modal-btn historial-modal-btn-cancel"
                onClick={() => setShowClearAllModal(false)}
                disabled={clearAllMutation.isPending}
              >
                Cancelar
              </button>
              <button
                className="historial-modal-btn historial-modal-btn-delete"
                onClick={() => clearAllMutation.mutate()}
                disabled={clearAllMutation.isPending}
              >
                {clearAllMutation.isPending ? 'Eliminando...' : 'Sí, Eliminar Todo'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Loading Global */}
      <GlobalLoading 
        isLoading={deleteMutation.isPending || clearAllMutation.isPending} 
        message={
          deleteMutation.isPending ? 'Eliminando registro...' :
          'Limpiando todo el historial...'
        } 
      />
    </div>
  );
};
