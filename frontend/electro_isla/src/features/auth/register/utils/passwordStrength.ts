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
 * Calcula la fortaleza de una contraseña con algoritmo balanceado
 */
export const calculatePasswordStrength = (password: string): PasswordStrength => {
  if (!password) {
    return {
      score: 0,
      label: 'Muy débil',
      color: '#ef4444',
      percentage: 0,
      suggestions: [],
    };
  }

  let points = 0;
  const suggestions: string[] = [];
  const length = password.length;

  // 1. LONGITUD - Progresivo (0-40 puntos)
  if (length <= 4) {
    points += length * 3; // 3, 6, 9, 12
  } else if (length <= 7) {
    points += 12 + (length - 4) * 4; // 16, 20, 24, 28
  } else if (length <= 11) {
    points += 28 + (length - 7) * 2; // 30, 32, 34, 36, 38
  } else {
    points += 40; // 12+ caracteres
  }

  // 2. MAYÚSCULAS (0-10 puntos)
  const hasUpperCase = /[A-Z]/.test(password);
  if (hasUpperCase) {
    const upperCount = (password.match(/[A-Z]/g) || []).length;
    points += Math.min(10, upperCount * 5);
  }

  // 3. MINÚSCULAS (0-10 puntos)
  const hasLowerCase = /[a-z]/.test(password);
  if (hasLowerCase) {
    const lowerCount = (password.match(/[a-z]/g) || []).length;
    points += Math.min(10, lowerCount * 2);
  }

  // 4. NÚMEROS (0-15 puntos)
  const hasNumber = /\d/.test(password);
  if (hasNumber) {
    const numberCount = (password.match(/\d/g) || []).length;
    points += Math.min(15, numberCount * 5);
  }

  // 5. CARACTERES ESPECIALES (0-20 puntos)
  const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password);
  if (hasSpecialChar) {
    const specialCount = (password.match(/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/g) || []).length;
    points += Math.min(20, specialCount * 10);
  }

  // 6. VARIEDAD (0-5 puntos bonus)
  const uniqueChars = new Set(password).size;
  const varietyRatio = uniqueChars / length;
  if (varietyRatio >= 0.7) {
    points += 5;
  } else if (varietyRatio >= 0.5) {
    points += 3;
  }

  // PENALIZACIONES
  const lowerPassword = password.toLowerCase();

  // Contraseñas comunes (-40 puntos)
  if (COMMON_PASSWORDS.some(common => lowerPassword === common || lowerPassword.includes(common))) {
    points = Math.max(0, points - 40);
  }

  // Secuencias repetitivas (-20 puntos)
  if (/(.)\1{2,}/.test(password)) {
    points = Math.max(0, points - 20);
  }

  // Secuencias numéricas (-15 puntos)
  if (/(?:012|123|234|345|456|567|678|789|890)/.test(password)) {
    points = Math.max(0, points - 15);
  }

  // Secuencias de teclado (-15 puntos)
  if (/(?:qwerty|asdfgh|zxcvbn)/i.test(password)) {
    points = Math.max(0, points - 15);
  }

  // Solo letras o solo números (-10 puntos)
  if (/^[a-zA-Z]+$/.test(password) || /^\d+$/.test(password)) {
    points = Math.max(0, points - 10);
  }

  // Normalizar a 0-100
  const percentage = Math.min(100, Math.max(0, points));

  // Determinar label y color basado en porcentaje
  let label: string;
  let color: string;
  let score: number;

  if (percentage >= 85) {
    label = 'Muy fuerte';
    color = '#10b981'; // Verde brillante
    score = 5;
  } else if (percentage >= 65) {
    label = 'Fuerte';
    color = '#22c55e'; // Verde
    score = 4;
  } else if (percentage >= 45) {
    label = 'Aceptable';
    color = '#3b82f6'; // Azul
    score = 3;
  } else if (percentage >= 25) {
    label = 'Débil';
    color = '#f59e0b'; // Naranja
    score = 2;
  } else {
    label = 'Muy débil';
    color = '#ef4444'; // Rojo
    score = 1;
  }

  return {
    score,
    label,
    color,
    percentage,
    suggestions,
  };
};
