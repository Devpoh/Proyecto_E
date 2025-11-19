/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🏗️ LAYOUT - Admin Panel
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { useState, useRef, useEffect } from 'react';
import { Outlet, NavLink, Navigate, useNavigate } from 'react-router-dom';
import { 
  FiHome, 
  FiPackage, 
  FiUsers, 
  FiShoppingBag, 
  FiBarChart2,
  FiMenu,
  FiX,
  FiLogOut,
  FiChevronUp,
  FiClock
} from 'react-icons/fi';
import { useAuthStore } from '@/app/store/useAuthStore';
import { useScrollToTop } from '@/shared/hooks';
import './AdminLayout.css';

export const AdminLayout = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  
  // Scroll al top cuando cambia la ruta
  useScrollToTop();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);

  // Cerrar menú al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleGoHome = () => {
    navigate('/');
  };

  // Verificar acceso
  const hasAccess = user?.rol && ['admin', 'trabajador', 'mensajero'].includes(user.rol);

  if (!hasAccess) {
    return <Navigate to="/" replace />;
  }

  const menuItems = [
    { path: '/admin', icon: FiHome, label: 'Dashboard', exact: true },
    { path: '/admin/productos', icon: FiPackage, label: 'Productos' },
    { path: '/admin/usuarios', icon: FiUsers, label: 'Usuarios' },
    { path: '/admin/pedidos', icon: FiShoppingBag, label: 'Pedidos' },
    { path: '/admin/estadisticas', icon: FiBarChart2, label: 'Estadísticas' },
    { path: '/admin/historial', icon: FiClock, label: 'Historial', adminOnly: true },
  ];

  // Filtrar menú según rol
  const filteredMenu = menuItems.filter(item => {
    // Historial solo para admin
    if (item.adminOnly && user.rol !== 'admin') {
      return false;
    }
    
    if (user.rol === 'mensajero') {
      // Mensajeros solo ven pedidos
      return item.path === '/admin' || item.path === '/admin/pedidos';
    }
    return true;
  });

  return (
    <div className="admin-layout">
      {/* Sidebar */}
      <aside className={`admin-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="admin-sidebar-header">
          <div className="admin-sidebar-logo">
            <span className="admin-sidebar-logo-icon">⚡</span>
            {sidebarOpen && <span className="admin-sidebar-logo-text">Admin Panel</span>}
          </div>
          <button
            className="admin-sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? <FiX /> : <FiMenu />}
          </button>
        </div>

        <nav className="admin-sidebar-nav">
          {filteredMenu.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.exact}
              className={({ isActive }) =>
                `admin-sidebar-link ${isActive ? 'active' : ''}`
              }
            >
              <item.icon className="admin-sidebar-link-icon" />
              {sidebarOpen && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        {sidebarOpen && (
          <div className="admin-sidebar-footer" ref={userMenuRef}>
            <button
              className="admin-sidebar-user"
              onClick={() => setUserMenuOpen(!userMenuOpen)}
            >
              <div className="admin-sidebar-user-avatar">
                {user?.nombre?.charAt(0).toUpperCase() || 'U'}
              </div>
              <div className="admin-sidebar-user-info">
                <p className="admin-sidebar-user-name">{user?.nombre}</p>
                <p className="admin-sidebar-user-role">
                  {user?.rol === 'admin' && 'Administrador'}
                  {user?.rol === 'trabajador' && 'Trabajador'}
                  {user?.rol === 'mensajero' && 'Mensajero'}
                </p>
              </div>
              <FiChevronUp className={`admin-sidebar-user-chevron ${userMenuOpen ? 'open' : ''}`} />
            </button>

            {userMenuOpen && (
              <div className="admin-sidebar-user-menu">
                <button
                  className="admin-sidebar-user-menu-item"
                  onClick={handleGoHome}
                >
                  <FiHome />
                  <span>Ir a Inicio</span>
                </button>
                <button
                  className="admin-sidebar-user-menu-item admin-sidebar-user-menu-item-logout"
                  onClick={handleLogout}
                >
                  <FiLogOut />
                  <span>Cerrar Sesión</span>
                </button>
              </div>
            )}
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="admin-main">
        <Outlet />
      </main>
    </div>
  );
};
