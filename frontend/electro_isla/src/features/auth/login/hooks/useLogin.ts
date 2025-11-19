/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🪝 HOOK - useLogin
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Hook personalizado para manejar la lógica de login
 * 
 * CARACTERÍSTICAS:
 * - React Query para manejo de estado
 * - Integración con Zustand
 * - Manejo de errores
 * - Persistencia en localStorage
 * - Rate limiting con bloqueo temporal
 */

import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuthStore } from '@/app/store/useAuthStore';
import { loginUser } from '../api/loginApi';

interface RateLimitError {
  bloqueado: boolean;
  tiempo_restante: number;
  mensaje: string;
}

const STORAGE_KEY = 'rate_limit_block_login';

export const useLogin = () => {
  const navigate = useNavigate();
  const { login: setAuthState } = useAuthStore();
  
  // Verificar si hay un bloqueo activo en localStorage al inicializar
  const [rateLimitInfo, setRateLimitInfo] = useState<RateLimitError | null>(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const { expiraEn, timestamp } = JSON.parse(stored);
        const transcurrido = Math.floor((Date.now() - timestamp) / 1000);
        const restante = expiraEn - transcurrido;
        
        if (restante > 0) {
          return {
            bloqueado: true,
            tiempo_restante: restante,
            mensaje: `Bloqueado. Intenta de nuevo en ${restante} segundos.`
          };
        } else {
          localStorage.removeItem(STORAGE_KEY);
        }
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
    return null;
  });

  const mutation = useMutation({
    mutationFn: loginUser,
    onSuccess: (data) => {
      // Limpiar rate limit si existía
      setRateLimitInfo(null);
      localStorage.removeItem(STORAGE_KEY);
      
      // ✅ Limpiar localStorage (datos legados inseguros)
      localStorage.removeItem('accessToken');
      localStorage.removeItem('user');
      localStorage.removeItem('auth-storage');
      localStorage.removeItem('cart-storage');
      
      // ✅ Limpiar sessionStorage (datos legados)
      sessionStorage.removeItem('accessToken');
      sessionStorage.removeItem('user');

      // ✅ Actualizar estado global con token (solo en memoria)
      setAuthState(data.user, data.accessToken);

      console.info('[useLogin] Login exitoso. Usuario autenticado.');

      // Redirigir según el rol
      if (data.user.rol === 'admin') {
        navigate('/admin');
      } else {
        navigate('/');
      }
    },
    onError: (error: any) => {
      // Verificar si es error de rate limiting (429)
      if (error.response?.status === 429 && error.response?.data?.bloqueado) {
        setRateLimitInfo({
          bloqueado: true,
          tiempo_restante: error.response.data.tiempo_restante,
          mensaje: error.response.data.mensaje,
        });
      } else {
        setRateLimitInfo(null);
      }
      
      // Log del error
      const errorMessage = error.response?.data?.error || error.message || 'Error desconocido';
      console.error('Error en login:', errorMessage);
    },
  });

  const clearRateLimit = () => {
    setRateLimitInfo(null);
  };

  return {
    login: mutation.mutate,
    isLoading: mutation.isPending,
    error: (mutation.error as any)?.response?.data?.error || mutation.error?.message,
    isSuccess: mutation.isSuccess,
    rateLimitInfo,
    clearRateLimit,
  };
};
