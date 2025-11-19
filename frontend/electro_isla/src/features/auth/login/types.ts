/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📝 TYPES - Login Feature
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Tipos TypeScript para la funcionalidad de login
 */

export interface LoginFormData {
  username: string;
  password: string;
}

export interface LoginResponse {
  accessToken: string;
  user: {
    id: number;
    email: string;
    nombre: string;
    rol: 'admin' | 'cliente';
  };
  message: string;
}

export interface LoginError {
  error: string;
}
