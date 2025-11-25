/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🌐 API - Register Service
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import api from '@/shared/api/axios';
import type { RegisterResponse } from '../types';

interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

/**
 * Registrar nuevo usuario con verificación de email
 */
export const registerUser = async (data: {
  firstName: string;
  lastName: string;
  email: string;
  username: string;
  password: string;
}): Promise<RegisterResponse> => {
  try {
    const payload: RegisterPayload = {
      username: data.username,
      email: data.email,
      password: data.password,
      first_name: data.firstName,
      last_name: data.lastName,
    };

    const response = await api.post<RegisterResponse>('/auth/register-with-verification/', payload);
    return response.data;
  } catch (error: any) {
    // Propagar el error completo de Axios para que el hook pueda acceder a response.data
    // Esto es necesario para el rate limiting (error 429)
    throw error;
  }
};
