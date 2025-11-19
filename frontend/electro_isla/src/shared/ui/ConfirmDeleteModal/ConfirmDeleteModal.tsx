/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎨 COMPONENTE - ConfirmDeleteModal
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Modal de confirmación para eliminación.
 * Reutilizable en ProductosPage, UsuariosPage, PedidosPage, etc.
 * 
 * BENEFICIOS:
 * - Componente reutilizable
 * - Consistencia visual en todo el admin
 * - Reduce código duplicado (~80 líneas)
 * - Fácil de mantener y actualizar
 */

import React from 'react';
import { FiAlertTriangle } from 'react-icons/fi';
import './ConfirmDeleteModal.css';

export interface ConfirmDeleteModalProps {
  /** Si el modal está abierto */
  isOpen: boolean;
  /** Nombre del item a eliminar */
  itemName: string;
  /** Función para confirmar la eliminación */
  onConfirm: () => void;
  /** Función para cancelar */
  onCancel: () => void;
  /** Si está en estado de carga */
  isLoading?: boolean;
  /** Descripción adicional (opcional) */
  description?: string;
  /** Label del botón de confirmación */
  confirmLabel?: string;
  /** Label del botón de cancelación */
  cancelLabel?: string;
}

/**
 * Modal de confirmación para eliminación
 * 
 * @example
 * const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
 * const [selectedItem, setSelectedItem] = useState<Item | null>(null);
 * 
 * return (
 *   <ConfirmDeleteModal
 *     isOpen={showDeleteConfirm}
 *     itemName={selectedItem?.nombre || ''}
 *     onConfirm={handleDelete}
 *     onCancel={() => setShowDeleteConfirm(false)}
 *     isLoading={isDeleting}
 *     description="Esta acción no se puede deshacer"
 *   />
 * );
 */
export const ConfirmDeleteModal: React.FC<ConfirmDeleteModalProps> = ({
  isOpen,
  itemName,
  onConfirm,
  onCancel,
  isLoading = false,
  description,
  confirmLabel = 'Eliminar',
  cancelLabel = 'Cancelar',
}) => {
  if (!isOpen) return null;

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget && !isLoading) {
      onCancel();
    }
  };

  return (
    <div className="confirm-delete-overlay" onClick={handleBackdropClick}>
      <div className="confirm-delete-modal">
        {/* Icono de alerta */}
        <div className="confirm-delete-icon">
          <FiAlertTriangle />
        </div>

        {/* Título */}
        <h3 className="confirm-delete-title">Confirmar Eliminación</h3>

        {/* Mensaje */}
        <p className="confirm-delete-message">
          ¿Estás seguro de que deseas eliminar <strong>{itemName}</strong>?
        </p>

        {/* Descripción adicional */}
        {description && (
          <p className="confirm-delete-description">{description}</p>
        )}

        {/* Botones */}
        <div className="confirm-delete-actions">
          <button
            type="button"
            className="confirm-delete-btn confirm-delete-btn-cancel"
            onClick={onCancel}
            disabled={isLoading}
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            className="confirm-delete-btn confirm-delete-btn-confirm"
            onClick={onConfirm}
            disabled={isLoading}
          >
            {isLoading ? 'Eliminando...' : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDeleteModal;
