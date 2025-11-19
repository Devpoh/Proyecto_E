/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🔄 GLOBAL LOADING - Componente de carga global
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Componente de loading profesional con fondo borroso y spinner dorado.
 * Se usa para cargas iniciales de la app y operaciones críticas.
 */

import './GlobalLoading.css';

interface GlobalLoadingProps {
  isLoading: boolean;
  message?: string;
}

export const GlobalLoading = ({ 
  isLoading, 
  message = 'Espere un segundo...' 
}: GlobalLoadingProps) => {
  if (!isLoading) return null;

  return (
    <div className="global-loading-overlay">
      <div className="global-loading-content">
        <div className="global-loading-spinner"></div>
        <p className="global-loading-message">{message}</p>
      </div>
    </div>
  );
};
