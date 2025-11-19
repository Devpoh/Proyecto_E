/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🪝 HOOK - useEmailValidation
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Hook para validar email en tiempo real contra el backend
 * Detecta si un email ya está registrado
 * 
 * CARACTERÍSTICAS:
 * - Validación en tiempo real
 * - Debounce para no saturar el backend
 * - Caché de resultados
 * - Manejo de errores
 */

import { useState, useEffect, useRef } from 'react';
import api from '@/shared/api/axios';

interface EmailValidationResult {
  isValid: boolean;
  isChecking: boolean;
  error: string | null;
  isDuplicate: boolean;
}

const EMAIL_VALIDATION_CACHE = new Map<string, { isDuplicate: boolean; timestamp: number }>();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutos

export const useEmailValidation = (email: string) => {
  const [result, setResult] = useState<EmailValidationResult>({
    isValid: false,
    isChecking: false,
    error: null,
    isDuplicate: false,
  });

  const debounceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    // Limpiar timer anterior
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    // Si el email está vacío, no validar
    if (!email || email.trim() === '') {
      setResult({
        isValid: false,
        isChecking: false,
        error: null,
        isDuplicate: false,
      });
      return;
    }

    // Validación básica de formato
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setResult({
        isValid: false,
        isChecking: false,
        error: 'Formato de email inválido',
        isDuplicate: false,
      });
      return;
    }

    // Verificar caché
    const cached = EMAIL_VALIDATION_CACHE.get(email.toLowerCase());
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      setResult({
        isValid: !cached.isDuplicate,
        isChecking: false,
        error: cached.isDuplicate ? 'Este email ya está registrado' : null,
        isDuplicate: cached.isDuplicate,
      });
      return;
    }

    // Debounce: esperar 500ms antes de validar
    debounceTimer.current = setTimeout(async () => {
      setResult((prev) => ({ ...prev, isChecking: true }));

      try {
        // Hacer petición al backend para validar email
        const response = await api.post('/auth/check-email/', {
          email: email.toLowerCase(),
        });

        const isDuplicate = response.data.exists || false;

        // Guardar en caché
        EMAIL_VALIDATION_CACHE.set(email.toLowerCase(), {
          isDuplicate,
          timestamp: Date.now(),
        });

        setResult({
          isValid: !isDuplicate,
          isChecking: false,
          error: isDuplicate ? 'Este email ya está registrado' : null,
          isDuplicate,
        });

        console.debug(`[EmailValidation] Email ${email} - Duplicado: ${isDuplicate}`);
      } catch (error: any) {
        // Si hay error de conexión, permitir continuar (no bloquear)
        console.warn('[EmailValidation] Error al validar email:', error.message);

        setResult({
          isValid: true, // Permitir continuar si hay error
          isChecking: false,
          error: null,
          isDuplicate: false,
        });
      }
    }, 500);

    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, [email]);

  return result;
};
