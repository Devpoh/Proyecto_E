/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🔐 PROVIDER - AuthProvider (Mejorado)
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Provider de autenticación que inicializa Zustand
 * Reemplaza el Context duplicado con el state manager único
 * 
 * CARACTERÍSTICAS:
 * - Inicializa Zustand al montar
 * - Valida tokens al cargar
 * - Sincroniza con sessionStorage/localStorage
 * - Limpia sesión si token está expirado
 */

import type { ReactNode } from 'react';
import { useEffect } from 'react';
import { useAuthStore } from '@/app/store/useAuthStore';

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const { initializeAuth } = useAuthStore();

  useEffect(() => {
    // ✅ Limpiar localStorage existente (datos legados inseguros)
    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
    localStorage.removeItem('auth-storage');
    localStorage.removeItem('cart-storage');
    
    // ✅ Restaurar sesión desde refresh token (HTTP-Only Cookie)
    initializeAuth();
    // ✅ NO incluir initializeAuth en dependencias
    // Esto evita llamadas múltiples
  }, []);

  return <>{children}</>;
};
