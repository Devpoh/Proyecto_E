/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📧 API - Recuperación de Contraseña
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Funciones para interactuar con los endpoints de recuperación de contraseña.
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

/**
 * ✅ Obtiene el token CSRF del documento
 * @returns Token CSRF o null si no existe
 */
const getCsrfToken = (): string | null => {
  const name = 'csrftoken';
  let cookieValue: string | null = null;
  
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  
  return cookieValue;
};

/**
 * Solicita un token de recuperación de contraseña
 * @param email - Email del usuario
 * @returns Promesa con la respuesta del servidor
 */
export const requestPasswordReset = async (email: string) => {
  try {
    const csrfToken = getCsrfToken();
    const response = await axios.post(
      `${API_BASE_URL}/auth/forgot-password/`,
      { email },
      {
        headers: {
          'Content-Type': 'application/json',
          ...(csrfToken && { 'X-CSRFToken': csrfToken }),  // ✅ Incluir CSRF token si existe
        },
      }
    );
    return response.data;
  } catch (error: any) {
    throw error.response?.data || { error: 'Error al solicitar recuperación' };
  }
};

/**
 * Confirma el código y actualiza la contraseña
 * @param email - Email del usuario
 * @param codigo - Código de 6 dígitos
 * @param password - Nueva contraseña
 * @param passwordConfirm - Confirmación de contraseña
 * @returns Promesa con la respuesta del servidor (incluye tokens)
 */
export const confirmPasswordReset = async (
  email: string,
  codigo: string,
  password: string,
  passwordConfirm: string
) => {
  try {
    const csrfToken = getCsrfToken();
    const response = await axios.post(
      `${API_BASE_URL}/auth/reset-password/`,
      {
        email,
        codigo,
        password,
        password_confirm: passwordConfirm,
      },
      {
        headers: {
          'Content-Type': 'application/json',
          ...(csrfToken && { 'X-CSRFToken': csrfToken }),  // ✅ Incluir CSRF token si existe
        },
      }
    );
    return response.data;
  } catch (error: any) {
    throw error.response?.data || { error: 'Error al actualizar contraseña' };
  }
};
