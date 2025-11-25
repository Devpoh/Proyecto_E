/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎨 UI COMPONENT - PasswordStrengthMeter
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Medidor visual de fortaleza de contraseña en tiempo real
 */

import type { PasswordStrength } from '../types';
import './PasswordStrengthMeter.css';

interface PasswordStrengthMeterProps {
  strength: PasswordStrength;
  show: boolean;
}

export const PasswordStrengthMeter = ({ strength, show }: PasswordStrengthMeterProps) => {
  if (!show) return null;

  return (
    <div className="password-strength-meter">
      {/* Barra de progreso */}
      <div className="password-strength-bar">
        <div
          className="password-strength-bar-fill"
          style={{
            width: `${strength.percentage}%`,
            backgroundColor: strength.color,
          }}
        />
      </div>

      {/* Label y porcentaje */}
      <div className="password-strength-info">
        <span className="password-strength-label" style={{ color: strength.color }}>
          {strength.label}
        </span>
        <span className="password-strength-percentage">
          {strength.percentage}%
        </span>
      </div>
    </div>
  );
};
