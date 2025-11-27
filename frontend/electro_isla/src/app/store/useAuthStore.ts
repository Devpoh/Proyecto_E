/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🔐 AUTH STORE - Estado Global de Autenticación (SEGURO PARA PRODUCCIÓN)
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Maneja el estado de autenticación del usuario:
 * - isAuthenticated: Boolean que indica si el usuario está logueado
 * - user: Datos del usuario actual (SOLO EN MEMORIA)
 * - accessToken: Token JWT (SOLO EN MEMORIA - Zustand)
 * - login: Función para iniciar sesión
 * - logout: Función para cerrar sesión
 * - initializeAuth: Restaura sesión desde refresh token (HTTP-Only Cookie)
 * 
 * 🔒 SEGURIDAD (DESARROLLO Y PRODUCCIÓN):
 * - ✅ Access Token SOLO en memoria (Zustand) - NO en sessionStorage/localStorage
 * - ✅ Refresh Token en HTTP-Only Cookie (automático, no accesible desde JS)
 * - ✅ Protegido contra XSS (tokens no accesibles desde JS malicioso)
 * - ✅ Sesión se pierde al recargar (necesita refresh token para restaurar)
 * - ✅ Dos pestañas = dos sesiones independientes
 * - ✅ En HTTPS: Cookies con Secure + SameSite=Strict
 * 
 * 📝 FLUJO SEGURO:
 * 1. Login: Backend retorna accessToken (JWT) + Refresh Token en Cookie
 * 2. Frontend: Guarda accessToken en Zustand (memoria)
 * 3. Recargar: initializeAuth() intenta refrescar usando Cookie
 * 4. Logout: Limpia Zustand + Backend invalida Cookie
 */

import { create } from 'zustand';
import { useCartStore } from './useCartStore';

// Interfaz del Usuario
interface User {
  id: number;
  email: string;
  nombre?: string;
  rol?: 'cliente' | 'mensajero' | 'trabajador' | 'admin';
}

// Interfaz del Store
interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  accessToken: string | null;
  isInitializing: boolean; // Flag para saber si se está inicializando
  _isInitializing?: boolean; // Flag interno para evitar múltiples inicializaciones
  login: (user: User, token: string) => void;
  logout: () => void;
  setUser: (user: User | null) => void;
  initializeAuth: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  // Estado inicial
  isAuthenticated: false,
  user: null,
  accessToken: null,
  isInitializing: true, // Comienza como true para esperar a que se inicialice

  // Iniciar sesión
  login: (user: User, token: string) => {
    // ✅ SOLO guardar en memoria (Zustand)
    // ✅ Refresh token ya está en HTTP-Only Cookie (seguro)
    // ✅ NO guardar en sessionStorage/localStorage (vulnerable a XSS)
    set({ 
      isAuthenticated: true, 
      user,
      accessToken: token
    });
    
    console.debug('[useAuthStore] Login exitoso. Token guardado en memoria (Zustand).');
  },

  // Cerrar sesión
  logout: () => {
    // ✅ NOTA: El backend limpia el carrito automáticamente en POST /api/auth/logout/
    // No necesitamos llamar a DELETE /api/carrito/vaciar/ porque:
    // 1. Los tokens ya se revocan en el endpoint de logout
    // 2. El backend limpia el carrito en la BD
    // 3. Llamar a DELETE después del logout fallaría con 401
    
    // ✅ Limpiar localStorage (datos legados inseguros)
    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
    localStorage.removeItem('auth-storage');
    localStorage.removeItem('cart-storage');
    localStorage.removeItem('cart-backup');
    
    // ✅ Limpiar sessionStorage
    sessionStorage.removeItem('accessToken');
    sessionStorage.removeItem('user');
    
    // ✅ Limpiar carrito en Zustand (para evitar fantasmas)
    try {
      useCartStore.getState().clearCart();
    } catch (error) {
      console.warn('[useAuthStore] No se pudo limpiar carrito:', error);
    }
    
    // ✅ Limpiar estado en memoria
    set({ 
      isAuthenticated: false, 
      user: null,
      accessToken: null
    });
  },

  // Actualizar usuario
  setUser: (user: User | null) => {
    set({ user, isAuthenticated: user !== null });
  },

  // Inicializar autenticación desde refresh token (HTTP-Only Cookie) al recargar
  initializeAuth: async () => {
    // ✅ IDEMPOTENTE: Si ya está autenticado o inicializando, no hacer nada
    // Esto permite que se llame múltiples veces sin problemas (ej: React StrictMode)
    const currentState = get();
    if (currentState.isAuthenticated && currentState.accessToken) {
      console.debug('[useAuthStore] Ya autenticado, saltando refresh token');
      return;
    }
    
    // ✅ Evitar múltiples inicializaciones simultáneas
    if (currentState._isInitializing) {
      console.debug('[useAuthStore] Ya inicializando, esperando...');
      return;
    }
    
    // Marcar como inicializando
    set({ _isInitializing: true, isInitializing: true });
    
    // ✅ Intentar refrescar usando el refresh token en HTTP-Only Cookie
    // ✅ Si falla, sesión se pierde (seguro)
    const attemptRefresh = async (retries = 3) => {
      for (let attempt = 0; attempt < retries; attempt++) {
        try {
          const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
          
          if (attempt === 0) {
            console.debug('[useAuthStore] Intentando restaurar sesión desde refresh token...');
          } else {
            console.debug(`[useAuthStore] Reintentando refresh token (intento ${attempt + 1}/${retries})...`);
          }
          
          const response = await fetch(`${apiUrl}/auth/refresh/`, {
            method: 'POST',
            credentials: 'include', // ✅ Enviar cookies (refresh token)
            headers: {
              'Content-Type': 'application/json',
            },
          });

          if (response.ok) {
            const data = await response.json();
            set({ 
              isAuthenticated: true, 
              user: data.user,
              accessToken: data.accessToken,
              _isInitializing: false,
              isInitializing: false
            });
            console.debug('[useAuthStore] ✅ Sesión restaurada desde refresh token');
            return true;
          } else if (response.status === 401 || response.status === 403) {
            // Token expirado o inválido - no reintentar
            const errorData = await response.json().catch(() => ({}));
            console.debug('[useAuthStore] ⚠️ Refresh token inválido o expirado:', {
              status: response.status,
              error: errorData.error
            });
            set({ isAuthenticated: false, user: null, accessToken: null, _isInitializing: false, isInitializing: false });
            return false;
          } else {
            // Otro error - reintentar
            console.warn(`[useAuthStore] Error ${response.status} al refrescar, reintentando...`);
            if (attempt < retries - 1) {
              await new Promise(resolve => setTimeout(resolve, 500 * (attempt + 1)));
              continue;
            }
          }
        } catch (error) {
          console.error(`[useAuthStore] Error en intento ${attempt + 1}:`, error);
          if (attempt < retries - 1) {
            await new Promise(resolve => setTimeout(resolve, 500 * (attempt + 1)));
            continue;
          }
        }
      }
      
      // Si llegamos aquí, todos los intentos fallaron
      console.error('[useAuthStore] ❌ Todos los intentos de refresh fallaron');
      set({ isAuthenticated: false, user: null, accessToken: null, _isInitializing: false, isInitializing: false });
      return false;
    };
    
    await attemptRefresh();
  },
}));
