/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎣 HOOK - Recuperación de Contraseña
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Hook personalizado para manejar la lógica de recuperación de contraseña.
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { requestPasswordReset } from '../api/forgotPasswordApi';

interface UseForgotPasswordReturn {
  email: string;
  setEmail: (email: string) => void;
  isLoading: boolean;
  error: string;
  success: string;
  requestReset: () => Promise<void>;
  clearMessages: () => void;
}

export const useForgotPassword = (): UseForgotPasswordReturn => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const requestReset = async () => {
    // Validar email
    if (!email.trim()) {
      setError('Por favor ingresa tu email');
      return;
    }

    // Validar formato de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('Por favor ingresa un email válido');
      return;
    }

    setIsLoading(true);
    setError('');
    setSuccess('');

    try {
      await requestPasswordReset(email);
      setSuccess('Código enviado. Revisa tu email para obtener el código.');
      
      // Guardar email en sessionStorage para la siguiente pantalla
      sessionStorage.setItem('recovery_email', email);
      
      // Redirigir a la pantalla de ingreso de código después de 2 segundos
      setTimeout(() => {
        navigate('/auth/reset-password');
      }, 2000);
    } catch (err: any) {
      setError(err.error || 'Error al solicitar recuperación');
    } finally {
      setIsLoading(false);
    }
  };

  const clearMessages = () => {
    setError('');
    setSuccess('');
  };

  return {
    email,
    setEmail,
    isLoading,
    error,
    success,
    requestReset,
    clearMessages,
  };
};
