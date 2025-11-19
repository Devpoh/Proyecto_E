/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎣 HOOK - useScrollToTop
 * ═══════════════════════════════════════════════════════════════════════════════
 * Hook para hacer scroll al top cuando se navega entre vistas
 */

import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

export const useScrollToTop = () => {
  const { pathname } = useLocation();

  useEffect(() => {
    // Scroll al top cuando cambia la ruta
    window.scrollTo(0, 0);
  }, [pathname]);
};
