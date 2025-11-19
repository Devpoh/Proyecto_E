/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🚫 COMPONENTE - Rate Limit Block
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Componente profesional de bloqueo temporal con:
 * - Pantalla de bloqueo premium
 * - Persistencia en localStorage (sobrevive a navegación)
 * - React Icons
 * - Animaciones suaves y dramáticas
 * - Diseño moderno, responsivo y accesible
 */

import { useEffect, useState } from 'react';
import { 
  MdSecurity, 
  MdWarning, 
  MdAccessTime, 
  MdLightbulbOutline,
  MdLock 
} from 'react-icons/md';
import './RateLimitBlock.css';

interface RateLimitBlockProps {
  tiempoRestante: number;
  tipo: 'login' | 'register';
  onDesbloquear?: () => void;
}

const STORAGE_KEY = 'rate_limit_block';

export const RateLimitBlock = ({ 
  tiempoRestante: tiempoInicial, 
  tipo,
  onDesbloquear 
}: RateLimitBlockProps) => {
  const [segundosRestantes, setSegundosRestantes] = useState(() => {
    // Intentar recuperar tiempo restante de localStorage
    const stored = localStorage.getItem(`${STORAGE_KEY}_${tipo}`);
    if (stored) {
      const { expiraEn, timestamp } = JSON.parse(stored);
      const transcurrido = Math.floor((Date.now() - timestamp) / 1000);
      const restante = expiraEn - transcurrido;
      return restante > 0 ? restante : tiempoInicial;
    }
    return tiempoInicial;
  });

  // Guardar en localStorage cuando cambia el tiempo
  useEffect(() => {
    if (segundosRestantes > 0) {
      localStorage.setItem(`${STORAGE_KEY}_${tipo}`, JSON.stringify({
        expiraEn: segundosRestantes,
        timestamp: Date.now(),
      }));
    } else {
      localStorage.removeItem(`${STORAGE_KEY}_${tipo}`);
    }
  }, [segundosRestantes, tipo]);

  useEffect(() => {
    if (segundosRestantes <= 0) {
      localStorage.removeItem(`${STORAGE_KEY}_${tipo}`);
      onDesbloquear?.();
      return;
    }

    const interval = setInterval(() => {
      setSegundosRestantes((prev) => {
        const nuevo = prev - 1;
        if (nuevo <= 0) {
          clearInterval(interval);
          localStorage.removeItem(`${STORAGE_KEY}_${tipo}`);
          onDesbloquear?.();
          return 0;
        }
        return nuevo;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [segundosRestantes, onDesbloquear, tipo]);

  const formatearTiempo = (segundos: number): string => {
    const mins = Math.floor(segundos / 60);
    const secs = segundos % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const porcentajeRestante = (segundosRestantes / 60) * 100;
  const mensaje = tipo === 'login' 
    ? 'Demasiados intentos de inicio de sesión' 
    : 'Demasiados intentos de registro';

  return (
    <div className="rate-limit-container">
      {/* Fondo decorativo */}
      <div className="rate-limit-background" aria-hidden="true"></div>

      {/* Panel principal */}
      <div className="rate-limit-panel">
        
        {/* Header */}
        <div className="rate-limit-header">
          <div className="rate-limit-header-content">
            {/* Icono principal */}
            <div className="rate-limit-icon-wrapper">
              <div className="rate-limit-icon-bg"></div>
              <div className="rate-limit-icon">
                <MdSecurity />
              </div>
            </div>
            
            <h2 className="rate-limit-title">
              Acceso Temporalmente Bloqueado
            </h2>
            <p className="rate-limit-subtitle">
              Por tu seguridad, hemos bloqueado temporalmente los intentos de acceso
            </p>
          </div>
        </div>

        {/* Contenido */}
        <div className="rate-limit-content">
          
          {/* Alerta principal */}
          <div className="rate-limit-alert">
            <MdWarning className="rate-limit-alert-icon" />
            <div className="rate-limit-alert-text">
              <p className="rate-limit-alert-title">
                {mensaje}
              </p>
              <p className="rate-limit-alert-description">
                Has excedido el límite de <strong>5 intentos fallidos</strong>. Por favor intenta de nuevo en 1 minuto.
              </p>
            </div>
          </div>

          {/* Contador regresivo */}
          <div className="rate-limit-counter">
            <div className="rate-limit-counter-content">
              <MdAccessTime className="rate-limit-counter-icon" />
              <div className="rate-limit-counter-text">
                <p className="rate-limit-counter-label">
                  Tiempo restante
                </p>
                <p className="rate-limit-counter-time">
                  {formatearTiempo(segundosRestantes)}
                </p>
              </div>
            </div>
            
            {/* Barra de progreso */}
            <div className="rate-limit-progress-bar">
              <div 
                className="rate-limit-progress-fill"
                style={{ width: `${porcentajeRestante}%` }}
              ></div>
            </div>
          </div>

          {/* Sección: Por qué veo esto */}
          <div className="rate-limit-info-section rate-limit-why">
            <div className="rate-limit-section-header">
              <MdLightbulbOutline className="rate-limit-section-icon" />
              <h3 className="rate-limit-section-title">
                ¿Por qué veo esto?
              </h3>
            </div>
            <ul className="rate-limit-section-list">
              <li className="rate-limit-section-item">
                <span className="rate-limit-section-bullet">•</span>
                <span>Protección contra accesos no autorizados a tu cuenta</span>
              </li>
              <li className="rate-limit-section-item">
                <span className="rate-limit-section-bullet">•</span>
                <span>El bloqueo se levantará automáticamente al expirar el tiempo</span>
              </li>
              <li className="rate-limit-section-item">
                <span className="rate-limit-section-bullet">•</span>
                <span>Este mensaje persistirá aunque navegues a otra página</span>
              </li>
            </ul>
          </div>

          {/* Sección: Consejos de seguridad */}
          <div className="rate-limit-info-section rate-limit-tips">
            <div className="rate-limit-section-header">
              <MdLock className="rate-limit-section-icon" />
              <h3 className="rate-limit-section-title">
                Consejos de seguridad
              </h3>
            </div>
            <ul className="rate-limit-section-list">
              <li className="rate-limit-section-item">
                <span className="rate-limit-section-bullet">•</span>
                <span>Verifica que tu usuario/email esté escrito correctamente</span>
              </li>
              <li className="rate-limit-section-item">
                <span className="rate-limit-section-bullet">•</span>
                <span>Asegúrate de que Caps Lock esté desactivado</span>
              </li>
              <li className="rate-limit-section-item">
                <span className="rate-limit-section-bullet">•</span>
                <span>Si olvidaste tu contraseña, usa la opción de recuperación</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="rate-limit-footer">
          <MdAccessTime className="rate-limit-footer-icon" />
          <p className="rate-limit-footer-text">
            El acceso se restablecerá automáticamente cuando expire el contador
          </p>
        </div>
      </div>
    </div>
  );
};
