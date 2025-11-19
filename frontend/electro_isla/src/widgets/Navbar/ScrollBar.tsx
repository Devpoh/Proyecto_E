/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎨 COMPONENT - ScrollBar
 * ═══════════════════════════════════════════════════════════════════════════════
 * Barra de progreso de scroll que aparece debajo del navbar
 * 
 * 🎯 FUNCIONAMIENTO:
 * 1. Se posiciona dinámicamente debajo del navbar
 * 2. Aparece al hacer scroll > 10px
 * 3. Animación suave de izquierda a derecha
 * 4. No interfiere con interacciones (pointer-events: none)
 */

import { useEffect, useState, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import './ScrollBar.css';

export const ScrollBar = () => {
  const [mostrarLineaDorada, setMostrarLineaDorada] = useState(false);
  const [navbarHeight, setNavbarHeight] = useState(0);
  const location = useLocation();
  const navbarRef = useRef<HTMLElement | null>(null);

  // 📏 Efecto para medir la altura del navbar dinámicamente
  useEffect(() => {
    const medirNavbar = () => {
      // Buscar el navbar por su selector
      const navbar = document.querySelector('nav');
      if (navbar) {
        navbarRef.current = navbar;
        const altura = navbar.offsetHeight;
        setNavbarHeight(altura);
      }
    };

    // Medir al montar
    medirNavbar();

    // Remedir al cambiar tamaño de ventana
    window.addEventListener('resize', medirNavbar);

    return () => {
      window.removeEventListener('resize', medirNavbar);
    };
  }, []);

  // 🥇 Efecto para detectar el primer scroll y mostrar línea dorada
  useEffect(() => {
    const manejarPrimerScroll = () => {
      const scrollY = window.scrollY;
      
      // Activar línea dorada después de 10px de scroll
      if (scrollY > 10 && !mostrarLineaDorada) {
        setMostrarLineaDorada(true);
        // Una vez activada, remover el listener para optimizar performance
        window.removeEventListener('scroll', manejarPrimerScroll);
      }
    };

    // Agregar listener de scroll
    window.addEventListener('scroll', manejarPrimerScroll, { passive: true });

    // Cleanup
    return () => {
      window.removeEventListener('scroll', manejarPrimerScroll);
    };
  }, [mostrarLineaDorada]);

  // Resetear barra al cambiar de vista
  useEffect(() => {
    setMostrarLineaDorada(false);
  }, [location]);

  return (
    <div 
      className={`scroll-bar ${mostrarLineaDorada ? 'scroll-bar--visible' : ''}`}
      style={{ top: `${navbarHeight}px` }}
    >
      <div className="scroll-bar-progress"></div>
    </div>
  );
};
