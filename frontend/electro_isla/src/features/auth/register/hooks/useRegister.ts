/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🪝 HOOK - useRegister
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Hook personalizado para manejar la lógica de registro
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
import { registerUser } from '../api/registerApi';

interface RateLimitError {
  bloqueado: boolean;
  tiempo_restante: number;
  mensaje: string;
}

const STORAGE_KEY = 'rate_limit_block_register';

export const useRegister = () => {
  const navigate = useNavigate();
  
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
    mutationFn: registerUser,
    onSuccess: (data) => {
      // Limpiar rate limit si existía
      setRateLimitInfo(null);
      localStorage.removeItem(STORAGE_KEY);
      
      console.info('[useRegister] Registro exitoso. Redirigiendo a verificación de email.');

      // Redirigir a página de verificación con el email como parámetro
      navigate(`/auth/verify-email?email=${encodeURIComponent(data.email)}`);
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
      console.error('Error en registro:', errorMessage);
    },
  });

  const clearRateLimit = () => {
    setRateLimitInfo(null);
  };

  return {
    register: mutation.mutate,
    isLoading: mutation.isPending,
    error: (mutation.error as any)?.response?.data?.error || mutation.error?.message,
    isSuccess: mutation.isSuccess,
    rateLimitInfo,
    clearRateLimit,
  };
};
