/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🌐 API - Login Service
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Servicio de API para autenticación de usuarios
 * 
 * REGLAS DE ORO:
 * - ✅ Manejo de errores robusto
 * - ✅ Validación de respuestas
 * - ✅ Tipado completo
 * - ❌ NO guardar contraseñas en logs
 */

import api from '@/shared/api/axios';
import type { LoginFormData, LoginResponse } from '../types';

/**
 * Iniciar sesión
 * @param credentials - Credenciales del usuario (username, password)
 * @returns Respuesta con token y datos del usuario
 */
export const loginUser = async (credentials: LoginFormData): Promise<LoginResponse> => {
  try {
    const response = await api.post<LoginResponse>('/auth/login/', credentials);
    return response.data;
  } catch (error: any) {
    // Propagar el error completo de Axios para que el hook pueda acceder a response.data
    // Esto es necesario para el rate limiting (error 429)
    throw error;
  }
};

/**
 * Cerrar sesión
 * Invalida el token en el servidor y limpia la sesión
 * @returns Mensaje de confirmación
 */
export const logoutUser = async (): Promise<{ message: string }> => {
  try {
    // Llamar al endpoint de logout en el servidor
    // El servidor invalidará el token en su blacklist
    // El token se envía automáticamente en el header (interceptor de Axios)
    const response = await api.post('/auth/logout/', {});

    console.info('[loginApi] Logout exitoso. Token invalidado en servidor.');
    
    return response.data;
  } catch (error: any) {
    // Incluso si falla el logout en servidor, continuamos limpiando el cliente
    console.warn('[loginApi] Error al logout en servidor:', error.message);
    console.info('[loginApi] Continuando con limpieza local...');
    
    // Limpiar tokens locales de todas formas (datos legados)
    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
    localStorage.removeItem('auth-storage');
    localStorage.removeItem('cart-storage');
    sessionStorage.removeItem('accessToken');
    sessionStorage.removeItem('user');
    
    // Retornar un mensaje de éxito parcial
    return { message: 'Sesión cerrada localmente' };
  }
};
