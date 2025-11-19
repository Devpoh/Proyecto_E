/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🔧 CONFIGURACIÓN DE AXIOS - Cliente HTTP con JWT + Refresh Token
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Cliente HTTP configurado con:
 * - Base URL desde variables de entorno
 * - Timeout de 30 segundos
 * - withCredentials para enviar cookies HTTP-Only
 * - Interceptor para agregar Access Token JWT automáticamente
 * - Interceptor para refrescar token automáticamente cuando expira
 * - Validación de expiración antes de usar token
 * - Headers por defecto
 * 
 * SISTEMA DE TOKENS:
 * - Access Token (JWT): 15 minutos, almacenado SOLO en memoria (Zustand)
 * - Refresh Token: 2 horas, almacenado en HTTP-Only Cookie
 * - Refresh automático cuando Access Token expira
 * - Validación de exp claim antes de usar
 * 
 * REGLAS DE ORO:
 * - ✅ HTTPS obligatorio en producción
 * - ✅ withCredentials para cookies
 * - ✅ Refresh automático transparente
 * - ✅ Validación de expiración antes de usar
 * - ✅ Access Token SOLO en memoria (Zustand) - NO en sessionStorage/localStorage
 * - ✅ Refresh Token en HTTP-Only Cookie (no accesible desde JS)
 * - ❌ NO agregar tokens a dominios terceros
 */

import axios, { AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { isTokenExpired, isValidToken } from '@/shared/utils/jwt';
import { getCsrfToken } from '@/shared/utils/csrf';
import { useAuthStore } from '@/app/store/useAuthStore';

// Crear instancia de Axios con configuración base
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 30000, // 30 segundos
  withCredentials: true, // ¡IMPORTANTE! Para enviar cookies HTTP-Only
  headers: {
    'Content-Type': 'application/json',
  },
});

// Obtener CSRF token al iniciar la aplicación
async function initializeCsrfToken() {
  try {
    await api.get('/auth/csrf-token/');
    console.debug('[Axios] CSRF token obtenido exitosamente');
  } catch (error) {
    console.warn('[Axios] Error al obtener CSRF token:', error);
  }
}

// Inicializar CSRF token
initializeCsrfToken();

// Flag para evitar múltiples intentos de refresh simultáneos
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}> = [];

/**
 * Procesa la cola de peticiones que fallaron mientras se refrescaba el token
 */
const processQueue = (error: AxiosError | null, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

/**
 * Interceptor de Request
 * Agrega el Access Token JWT automáticamente a todas las peticiones
 * EXCEPTO en endpoints de autenticación (login, register)
 * 
 * VALIDACIONES:
 * - Verifica que el token no esté expirado
 * - Obtiene token desde Zustand (solo en memoria)
 * - Valida estructura del JWT antes de usar
 * - Valida claims requeridos (user_id, username, rol)
 */
api.interceptors.request.use(
  (config) => {
    // Lista de endpoints que NO requieren token (públicos)
    const publicEndpoints = ['/auth/login', '/auth/register', '/auth/refresh', '/auth/csrf-token'];
    
    // Verificar si la URL actual es un endpoint público
    const isPublicEndpoint = publicEndpoints.some(endpoint => 
      config.url?.includes(endpoint)
    );
    
    // Agregar token a TODAS las peticiones excepto endpoints públicos
    if (!isPublicEndpoint) {
      // ✅ Obtener token desde Zustand (solo en memoria)
      const { accessToken } = useAuthStore.getState();
      
      if (accessToken) {
        // VALIDACIÓN CRÍTICA 1: Verificar que el token no esté expirado
        if (isTokenExpired(accessToken)) {
          console.warn(`[Axios] Token expirado detectado. Será refrescado automáticamente.`);
          // No agregar token expirado, dejar que el interceptor de response lo maneje
        } else if (isValidToken(accessToken)) {
          // VALIDACIÓN CRÍTICA 2: Verificar estructura y claims
          config.headers.Authorization = `Bearer ${accessToken}`;
          console.debug(`[Axios] Token válido agregado a ${config.url}`);
        } else {
          console.warn(`[Axios] Token inválido para ${config.url}`);
        }
      }
    }
    
    // PROTECCIÓN CSRF: Agregar CSRF token a peticiones POST/PUT/DELETE/PATCH
    const method = config.method?.toUpperCase();
    if (method && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
      const csrfToken = getCsrfToken();
      if (csrfToken) {
        config.headers['X-CSRFToken'] = csrfToken;
        console.debug(`[Axios] CSRF token agregado a ${config.url}`);
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Interceptor de Response
 * Maneja errores globalmente:
 * - 401: Access Token expirado → Intenta refrescar automáticamente
 * - Si el refresh falla → Redirige a login
 * - Otros errores: Propagar para manejo específico
 */
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Si es 401 y no hemos intentado refrescar aún
    if (error.response?.status === 401 && !originalRequest._retry) {
      // Evitar refrescar en endpoints de autenticación
      if (originalRequest.url?.includes('/auth/login') || 
          originalRequest.url?.includes('/auth/register') ||
          originalRequest.url?.includes('/auth/refresh')) {
        return Promise.reject(error);
      }

      // Si ya estamos refrescando, agregar a la cola
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Intentar refrescar el token
        const { data } = await axios.post(
          `${import.meta.env.VITE_API_URL || 'http://localhost:8000/api'}/auth/refresh/`,
          {},
          { withCredentials: true }
        );

        // ✅ Actualizar token en Zustand (solo en memoria)
        const { login } = useAuthStore.getState();
        login(data.user, data.accessToken); // Esto guarda SOLO en Zustand (memoria)

        console.info('[Axios] Token refrescado exitosamente');

        // Procesar cola de peticiones pendientes
        processQueue(null, data.accessToken);

        // Reintentar petición original con nuevo token
        originalRequest.headers.Authorization = `Bearer ${data.accessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Si falla el refresh, limpiar y redirigir a login
        processQueue(refreshError as AxiosError, null);
        
        // ✅ Limpiar sesión en Zustand
        const { logout } = useAuthStore.getState();
        logout();
        
        console.error('[Axios] Error al refrescar token. Redirigiendo a login.');
        
        // Solo redirigir si no estamos ya en login
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login';
        }
        
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // Otros errores
    return Promise.reject(error);
  }
);

export default api;
