/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎨 COMPONENT - LoadingBar
 * ═══════════════════════════════════════════════════════════════════════════════
 * Barra de carga dorada que aparece al navegar + GlobalLoading
 */

import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { GlobalLoading } from '@/shared/ui/GlobalLoading';
import './LoadingBar.css';

export const LoadingBar = () => {
  const [isLoading, setIsLoading] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setIsLoading(true);
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 500); // ✅ Reducido a 500ms para navegación más rápida

    return () => clearTimeout(timer);
  }, [location]);

  return (
    <>
      <GlobalLoading isLoading={isLoading} message="Cargando..." />
      <div className={`loading-bar ${isLoading ? 'loading-bar--active' : ''}`}>
        <div className="loading-bar-progress"></div>
      </div>
      {isLoading && <div className="loading-bar-overlay"></div>}
    </>
  );
};
