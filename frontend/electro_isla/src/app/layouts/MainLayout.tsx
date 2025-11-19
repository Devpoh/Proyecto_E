/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🏗️ LAYOUT - Main Layout
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Layout principal con header y footer
 * Usado en páginas que requieren navegación
 */

import { Outlet } from 'react-router-dom';
import { Navbar } from '@/widgets/Navbar';
import { useScrollToTop } from '@/shared/hooks';
import { useCartStore } from '@/app/store/useCartStore';

export const MainLayout = () => {
  // Scroll al top cuando cambia la ruta
  useScrollToTop();

  // ✅ Usar selector de Zustand para evitar re-renders innecesarios
  const cartItemCount = useCartStore((state) => 
    state.items.reduce((total, item) => total + item.cantidad, 0)
  );

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      <Navbar cartItemCount={cartItemCount} />
      <main>
        <Outlet />
      </main>
    </div>
  );
};
