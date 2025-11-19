/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * ⚠️ COMPONENT - RateLimitAlert
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Componente para mostrar alertas de rate limiting
 * Muestra contador regresivo de tiempo restante
 */

import React, { useEffect, useState } from 'react';
import { FiAlertTriangle, FiClock } from 'react-icons/fi';
import './RateLimitAlert.css';

interface RateLimitAlertProps {
  visible: boolean;
  tiempoRestante: number;
  mensaje: string;
  onExpire?: () => void;
}

export const RateLimitAlert: React.FC<RateLimitAlertProps> = ({
  visible,
  tiempoRestante,
  mensaje,
  onExpire,
}) => {
  const [tiempoActual, setTiempoActual] = useState(tiempoRestante);
  const [tiempoInicial] = useState(tiempoRestante);

  useEffect(() => {
    if (!visible || tiempoActual <= 0) {
      return;
    }

    const interval = setInterval(() => {
      setTiempoActual((prev) => {
        const nuevoTiempo = prev - 1;
        
        if (nuevoTiempo <= 0) {
          clearInterval(interval);
          onExpire?.();
          return 0;
        }
        
        return nuevoTiempo;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [visible, tiempoActual, onExpire]);

  // Actualizar cuando cambia tiempoRestante desde props
  useEffect(() => {
    setTiempoActual(tiempoRestante);
  }, [tiempoRestante]);

  if (!visible) {
    return null;
  }

  const minutos = Math.floor(tiempoActual / 60);
  const segundos = tiempoActual % 60;
  const porcentaje = (tiempoActual / tiempoInicial) * 100;
  
  // Determinar intensidad del color según tiempo restante
  const getAlertIntensity = () => {
    if (tiempoActual <= 10) return 'critical'; // Rojo intenso
    if (tiempoActual <= 30) return 'warning'; // Naranja
    return 'normal'; // Rojo normal
  };
  
  const intensity = getAlertIntensity();

  return (
    <div className={`rate-limit-alert rate-limit-alert--${intensity}`}>
      <div className="rate-limit-alert-content">
        <div className="rate-limit-alert-icon">
          <FiAlertTriangle size={24} />
        </div>
        
        <div className="rate-limit-alert-text">
          <h3 className="rate-limit-alert-title">Demasiados intentos</h3>
          <p className="rate-limit-alert-message">{mensaje}</p>
        </div>

        <div className="rate-limit-alert-timer">
          <div className="rate-limit-alert-timer-icon">
            <FiClock size={20} />
          </div>
          <div className="rate-limit-alert-timer-content">
            <p className="rate-limit-alert-timer-label">Tiempo restante</p>
            <p className="rate-limit-alert-timer-value">
              {minutos}:{segundos.toString().padStart(2, '0')}
            </p>
          </div>
        </div>
      </div>

      {/* Barra de progreso */}
      <div className="rate-limit-alert-progress-bar">
        <div 
          className="rate-limit-alert-progress-fill"
          style={{ width: `${porcentaje}%` }}
        />
      </div>
    </div>
  );
};
