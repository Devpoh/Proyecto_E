/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎨 COMPONENT - UserMenu
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Menú desplegable de usuario con avatar de letra
 */

import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiPackage, FiLogOut, FiSettings } from 'react-icons/fi';
import { useAuthStore } from '@/app/store/useAuthStore';
import { logoutUser } from '@/features/auth/login/api/loginApi';
import './UserMenu.css';

export const UserMenu = () => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  // Cerrar menú al hacer click fuera
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // Obtener primera letra del nombre
  const getInitial = () => {
    if (!user?.nombre) return 'U';
    return user.nombre.charAt(0).toUpperCase();
  };

  // Manejar logout
  const handleLogout = async () => {
    try {
      await logoutUser();
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    } finally {
      logout();
      setIsOpen(false);
      navigate('/');
    }
  };

  // Verificar si es admin, trabajador o mensajero
  const hasAdminAccess = user?.rol === 'admin' || user?.rol === 'trabajador' || user?.rol === 'mensajero';

  return (
    <div className="user-menu" ref={menuRef}>
      {/* Avatar Button */}
      <button
        className="user-menu-avatar"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Menú de usuario"
        aria-expanded={isOpen}
      >
        {getInitial()}
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="user-menu-dropdown">
          {/* User Info */}
          <div className="user-menu-header">
            <div className="user-menu-avatar-large">{getInitial()}</div>
            <div className="user-menu-info">
              <p className="user-menu-name">{user?.nombre}</p>
              <p className="user-menu-email">{user?.email}</p>
            </div>
          </div>

          <div className="user-menu-divider" />

          {/* Menu Items */}
          <div className="user-menu-items">
            {/* Historial de Pedidos */}
            <Link
              to="/historial-pedidos"
              className="user-menu-item"
              onClick={() => setIsOpen(false)}
            >
              <FiPackage className="user-menu-item-icon" />
              <span>Historial de Pedidos</span>
            </Link>

            {/* Panel de Admin (solo para admin, trabajador, mensajero) */}
            {hasAdminAccess && (
              <>
                <div className="user-menu-divider" />
                <Link
                  to="/admin"
                  className="user-menu-item user-menu-item-admin"
                  onClick={() => setIsOpen(false)}
                >
                  <FiSettings className="user-menu-item-icon" />
                  <span>Panel de Administración</span>
                </Link>
              </>
            )}

            <div className="user-menu-divider" />

            {/* Cerrar Sesión */}
            <button
              className="user-menu-item user-menu-item-logout"
              onClick={handleLogout}
            >
              <FiLogOut className="user-menu-item-icon" />
              <span>Cerrar Sesión</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
