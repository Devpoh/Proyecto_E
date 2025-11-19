import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { FiShoppingCart, FiUser } from 'react-icons/fi';
import { SearchBar } from '../../features/producto/product-search';
import { useAuthStore } from '@/app/store/useAuthStore';
import { UserMenu } from './UserMenu';
import { LogoBrand } from '@/shared/ui/LogoBrand';
import { LoadingBar } from './LoadingBar';
import { ScrollBar } from './ScrollBar';
import styles from './Navbar.module.css';

interface NavbarProps {
  cartItemCount?: number;
}

const Navbar: React.FC<NavbarProps> = ({
  cartItemCount = 0,
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated } = useAuthStore();

  // Determinar si un enlace está activo
  const isActive = (path: string) => {
    return location.pathname === path;
  };
  return (
    <>
      <LoadingBar />
      <ScrollBar />
      <nav className={styles.nav}>
      <div className={styles.container}>
        <LogoBrand variant="navbar" className={styles.logo} />
        
        <div className={styles.searchWrapper}>
          <SearchBar />
        </div>
        
        <div className={styles.rightSection}>
          <div className={styles.navLinks}>
            <Link 
              to="/" 
              className={`${styles.navLink} ${isActive('/') ? styles.navLinkActive : ''}`}
            >
              Inicio
            </Link>
            <Link 
              to="/productos" 
              className={`${styles.navLink} ${isActive('/productos') ? styles.navLinkActive : ''}`}
            >
              Productos
            </Link>
            <Link 
              to="/nosotros" 
              className={`${styles.navLink} ${isActive('/nosotros') ? styles.navLinkActive : ''}`}
            >
              Nosotros
            </Link>
          </div>
          
          <div className={styles.cartButtonContainer}>
            <Link to="/carrito" className={styles.iconButton} aria-label="Carrito">
              <FiShoppingCart size={20} />
              {cartItemCount > 0 && (
                <span className={styles.cartBadge}>{cartItemCount}</span>
              )}
            </Link>
            <span className={styles.cartTooltip}>Carrito de compras</span>
          </div>
          
          <div className={styles.loginButtonContainer}>
            {isAuthenticated ? (
              <UserMenu />
            ) : (
              <>
                <button 
                  onClick={() => navigate('/login')} 
                  className={styles.loginButton}
                  aria-label="Iniciar sesión"
                >
                  <FiUser size={20} />
                </button>
                <span className={styles.loginTooltip}>Iniciar sesión</span>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
    </>
  );
};

export default Navbar;
