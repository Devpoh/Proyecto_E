/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎨 COMPONENTE - LogoBrand
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Logo reutilizable de Electro Isla con palma dorada
 * - Enlace clickeable
 * - Lleva a inicio
 * - Scroll suave si está en la misma página
 * - Animación pulse
 * - Hover effects: palma blanca, Electro Isla dorada, .corp blanco
 */

import { useNavigate, useLocation } from 'react-router-dom';
import { GiPalmTree } from 'react-icons/gi';
import './LogoBrand.css';

interface LogoBrandProps {
  variant?: 'navbar' | 'login';
  className?: string;
}

export const LogoBrand = ({ variant = 'navbar', className = '' }: LogoBrandProps) => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    if (location.pathname === '/') {
      // Si estamos en inicio, scroll suave hacia arriba
      window.scrollTo({
        top: 0,
        behavior: 'smooth',
      });
    } else {
      // Si no estamos en inicio, navegar a inicio
      navigate('/');
    }
  };

  return (
    <a
      href="/"
      onClick={handleClick}
      className={`logo-brand logo-brand-${variant} ${className}`}
      aria-label="Ir al inicio"
    >
      <div className="logo-brand-icon">
        <GiPalmTree className="logo-brand-palm" />
      </div>
      <div className="logo-brand-text">
        <span className="logo-brand-main">Electro Isla</span>
        <span className="logo-brand-corp">.corp</span>
      </div>
    </a>
  );
};
