/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🛡️ COMPONENT - ProtectedRoute
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Componente para proteger rutas según autenticación y rol del usuario
 * 
 * CARACTERÍSTICAS:
 * - Valida autenticación
 * - Valida rol del usuario
 * - Redirige a login si no está autenticado
 * - Redirige a home si no tiene rol requerido
 * - Tipado completo
 */

import React, { useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/app/store/useAuthStore';
import { isTokenExpired } from '@/shared/utils/jwt';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRoles?: string[];
  fallbackPath?: string;
}

/**
 * ProtectedRoute - Protege rutas según autenticación y rol
 * 
 * @param children - Componente a renderizar si está autorizado
 * @param requiredRoles - Array de roles permitidos (si está vacío, solo requiere autenticación)
 * @param fallbackPath - Ruta a redirigir si no está autorizado (default: '/login')
 * 
 * @example
 * <Route 
 *   path="/admin" 
 *   element={
 *     <ProtectedRoute requiredRoles={['admin']}>
 *       <AdminLayout />
 *     </ProtectedRoute>
 *   } 
 * />
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRoles = [],
  fallbackPath = '/login',
}) => {
  const { isAuthenticated, user, logout, isInitializing } = useAuthStore();

  // Verificar si el token está expirado
  useEffect(() => {
    if (isAuthenticated) {
      // ✅ Obtener token desde Zustand (solo en memoria)
      const { accessToken } = useAuthStore.getState();
      
      if (accessToken && isTokenExpired(accessToken)) {
        console.warn('[ProtectedRoute] Token expirado detectado. Limpiando sesión.');
        logout();
      }
    }
  }, [isAuthenticated, logout]);

  // ✅ IMPORTANTE: Esperar a que se complete la inicialización
  // Si aún se está inicializando, no redirigir (puede estar restaurando sesión)
  if (isInitializing) {
    console.debug('[ProtectedRoute] Esperando inicialización de autenticación...');
    return null; // O mostrar un loading si prefieres
  }

  // Verificar si está autenticado
  if (!isAuthenticated || !user) {
    console.warn('[ProtectedRoute] Usuario no autenticado. Redirigiendo a login.');
    return <Navigate to={fallbackPath} replace />;
  }

  // Si se especifican roles requeridos, validar
  if (requiredRoles.length > 0) {
    // Obtener rol del usuario
    const userRole = user.rol;

    // Verificar si el usuario tiene uno de los roles requeridos
    if (!userRole || !requiredRoles.includes(userRole)) {
      console.warn(
        `[ProtectedRoute] Usuario sin rol requerido. Rol actual: ${userRole}, Requeridos: ${requiredRoles.join(', ')}`
      );
      return <Navigate to="/" replace />;
    }

    console.debug(`[ProtectedRoute] Acceso permitido. Rol: ${userRole}`);
  } else {
    console.debug('[ProtectedRoute] Acceso permitido. Usuario autenticado.');
  }

  // Usuario autorizado, renderizar componente
  return <>{children}</>;
};
