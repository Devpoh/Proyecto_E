/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📝 TYPES - Register Feature
 * ═══════════════════════════════════════════════════════════════════════════════
 */

export interface RegisterFormData {
  firstName: string;
  lastName: string;
  email: string;
  username: string;
  password: string;
  confirmPassword: string;
}

export interface RegisterResponse {
  accessToken: string;
  user: {
    id: number;
    email: string;
    nombre: string;
    rol: 'admin' | 'cliente';
  };
  message: string;
}

export interface PasswordStrength {
  score: number; // 0-4
  label: string; // 'Muy débil', 'Débil', 'Aceptable', 'Fuerte', 'Muy fuerte'
  color: string; // Color para la barra
  percentage: number; // 0-100
  suggestions: string[];
}
