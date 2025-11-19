/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🔒 UTILS - Password Strength Checker
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Calculador profesional de fortaleza de contraseña
 * 
 * CRITERIOS:
 * - Longitud (mínimo 12 caracteres)
 * - Mayúsculas y minúsculas
 * - Números
 * - Caracteres especiales
 * - Patrones comunes
 * - Secuencias repetitivas
 */

import type { PasswordStrength } from '../types';

const COMMON_PASSWORDS = [
  'password', '123456', '12345678', 'qwerty', 'abc123',
  'password123', 'admin', 'letmein', 'welcome', 'monkey',
  '1234567890', 'password1', 'qwertyuiop', '123123'
];

/**
 * Calcula la fortaleza de una contraseña
 */
export const calculatePasswordStrength = (password: string): PasswordStrength => {
  if (!password) {
    return {
      score: 0,
      label: 'Muy débil',
      color: 'var(--color-peligro)',
      percentage: 0,
      suggestions: ['Ingresa una contraseña'],
    };
  }

  let score = 0;
  const suggestions: string[] = [];

  // 1. Longitud (máximo 2 puntos)
  if (password.length >= 12) {
    score += 2;
  } else if (password.length >= 8) {
    score += 1;
    suggestions.push('Usa al menos 12 caracteres para mayor seguridad');
  } else {
    suggestions.push('La contraseña debe tener al menos 8 caracteres');
  }

  // 2. Mayúsculas (1 punto)
  const hasUpperCase = /[A-Z]/.test(password);
  if (hasUpperCase) {
    score += 1;
  } else {
    suggestions.push('Falta: letra mayúscula');
  }

  // 3. Minúsculas (1 punto)
  const hasLowerCase = /[a-z]/.test(password);
  if (hasLowerCase) {
    score += 1;
  } else {
    suggestions.push('Falta: letra minúscula');
  }

  // 4. Números (1 punto)
  const hasNumber = /\d/.test(password);
  if (hasNumber) {
    score += 1;
  } else {
    suggestions.push('Falta: número');
  }

  // 5. Caracteres especiales (1 punto)
  const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
  if (hasSpecialChar) {
    score += 1;
  } else {
    suggestions.push('Falta: carácter especial (!@#$%^&*)');
  }

  // 6. Variedad de caracteres (1 punto)
  const uniqueChars = new Set(password).size;
  if (uniqueChars >= password.length * 0.6) {
    score += 1;
  }

  // Penalizaciones (solo mostrar si hay problemas)
  const lowerPassword = password.toLowerCase();

  // Contraseñas comunes (-3 puntos)
  if (COMMON_PASSWORDS.some(common => lowerPassword.includes(common))) {
    score = Math.max(0, score - 3);
    suggestions.unshift('Evita contraseñas comunes');
  }

  // Secuencias repetitivas (-1 punto)
  if (/(.)\1{2,}/.test(password)) {
    score = Math.max(0, score - 1);
  }

  // Secuencias numéricas (-1 punto)
  if (/(?:012|123|234|345|456|567|678|789|890)/.test(password)) {
    score = Math.max(0, score - 1);
  }

  // Secuencias de teclado (-1 punto)
  if (/(?:qwerty|asdfgh|zxcvbn)/i.test(password)) {
    score = Math.max(0, score - 1);
  }

  // Normalizar score a 0-4
  score = Math.min(4, Math.max(0, score));

  // Determinar label, color y porcentaje
  let label: string;
  let color: string;
  let percentage: number;

  switch (score) {
    case 0:
    case 1:
      label = 'Muy débil';
      color = 'var(--color-peligro)';
      percentage = 20;
      break;
    case 2:
      label = 'Débil';
      color = 'var(--color-advertencia)';
      percentage = 40;
      break;
    case 3:
      label = 'Aceptable';
      color = 'var(--color-info)';
      percentage = 60;
      break;
    case 4:
      label = 'Fuerte';
      color = 'var(--color-exito)';
      percentage = 80;
      break;
    default:
      label = 'Muy fuerte';
      color = 'var(--color-exito)';
      percentage = 100;
  }

  // Si cumple todos los criterios, es muy fuerte
  if (score >= 4 && password.length >= 12 && suggestions.length === 0) {
    label = 'Muy fuerte';
    percentage = 100;
  }

  return {
    score,
    label,
    color,
    percentage,
    suggestions: suggestions.slice(0, 3), // Máximo 3 sugerencias
  };
};
