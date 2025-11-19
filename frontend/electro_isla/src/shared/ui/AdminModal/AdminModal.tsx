/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎨 COMPONENTE - AdminModal
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Modal reutilizable para el panel admin.
 * Evita duplicación de código en ProductosPage, UsuariosPage, PedidosPage, etc.
 * 
 * BENEFICIOS:
 * - Componente reutilizable
 * - Consistencia visual en todo el admin
 * - Reduce código duplicado (~100 líneas)
 * - Fácil de mantener y actualizar
 */

import React from 'react';
import { FiX } from 'react-icons/fi';
import './AdminModal.css';

export interface AdminModalProps {
  /** Si el modal está abierto */
  isOpen: boolean;
  /** Título del modal */
  title: string;
  /** Función para cerrar el modal */
  onClose: () => void;
  /** Función para enviar el formulario */
  onSubmit?: () => void;
  /** Si está en estado de carga */
  isLoading?: boolean;
  /** Label del botón de envío */
  submitLabel?: string;
  /** Label del botón de cancelación */
  cancelLabel?: string;
  /** Tipo de modal (default, danger, success) */
  variant?: 'default' | 'danger' | 'success';
  /** Contenido del modal */
  children: React.ReactNode;
  /** Si mostrar el botón de cerrar (X) */
  showCloseButton?: boolean;
  /** Ancho máximo del modal */
  maxWidth?: string;
}

/**
 * Modal reutilizable para el panel admin
 * 
 * @example
 * const [showModal, setShowModal] = useState(false);
 * 
 * return (
 *   <AdminModal
 *     isOpen={showModal}
 *     title="Crear Producto"
 *     onClose={() => setShowModal(false)}
 *     onSubmit={handleSubmit}
 *     isLoading={isLoading}
 *     submitLabel="Crear"
 *   >
 *     <div>Contenido del formulario</div>
 *   </AdminModal>
 * );
 */
export const AdminModal: React.FC<AdminModalProps> = ({
  isOpen,
  title,
  onClose,
  onSubmit,
  isLoading = false,
  submitLabel = 'Guardar',
  cancelLabel = 'Cancelar',
  variant = 'default',
  children,
  showCloseButton = true,
  maxWidth = '600px',
}) => {
  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    // Solo cerrar si se hace click en el backdrop, no en el modal
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div className="admin-modal-overlay" onClick={handleBackdropClick}>
      <div className="admin-modal" style={{ maxWidth }}>
        {/* Header */}
        <div className="admin-modal-header">
          <h3 className="admin-modal-title">{title}</h3>
          {showCloseButton && (
            <button
              className="admin-modal-close"
              onClick={onClose}
              disabled={isLoading}
              aria-label="Cerrar modal"
            >
              <FiX />
            </button>
          )}
        </div>

        {/* Content */}
        <div className="admin-modal-content">{children}</div>

        {/* Footer (solo si hay onSubmit) */}
        {onSubmit && (
          <div className="admin-modal-footer">
            <button
              type="button"
              className="admin-modal-btn admin-modal-btn-cancel"
              onClick={onClose}
              disabled={isLoading}
            >
              {cancelLabel}
            </button>
            <button
              type="button"
              className={`admin-modal-btn admin-modal-btn-submit admin-modal-btn-${variant}`}
              onClick={onSubmit}
              disabled={isLoading}
            >
              {isLoading ? 'Procesando...' : submitLabel}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminModal;
