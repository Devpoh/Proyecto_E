/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎣 HOOK - usePermissions
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Hook para centralizar la lógica de permisos.
 * Evita duplicación de código en ProductosPage, UsuariosPage, PedidosPage, etc.
 * 
 * BENEFICIOS:
 * - Centraliza la lógica de permisos
 * - Fácil de mantener y actualizar
 * - Consistencia en todo el admin panel
 * - Reduce código duplicado (~50 líneas)
 * - Mejora la seguridad (cambios en un solo lugar)
 */

import { useAuthStore } from '@/app/store/useAuthStore';
import { useMemo } from 'react';

type UserRole = 'admin' | 'trabajador' | 'mensajero' | 'cliente';

interface PermissionsResult {
  // Permisos generales
  canEdit: boolean;
  canDelete: boolean;
  canView: boolean;
  canCreate: boolean;

  // Permisos específicos por rol
  isAdmin: boolean;
  isTrabajador: boolean;
  isMensajero: boolean;
  isCliente: boolean;

  // Permisos específicos del admin
  canManageUsers: boolean;
  canManageProductos: boolean;
  canManagePedidos: boolean;
  canViewEstadisticas: boolean;
  canViewHistorial: boolean;

  // Utilidades
  hasRole: (role: UserRole | UserRole[]) => boolean;
  hasAnyRole: (roles: UserRole[]) => boolean;
  hasAllRoles: (roles: UserRole[]) => boolean;
}

/**
 * Hook para obtener permisos del usuario actual
 * 
 * @returns Objeto con todos los permisos y utilidades
 * 
 * @example
 * const permissions = usePermissions();
 * 
 * if (permissions.canEdit) {
 *   // Mostrar botón de editar
 * }
 * 
 * if (permissions.isAdmin) {
 *   // Mostrar opciones de admin
 * }
 * 
 * if (permissions.hasRole(['admin', 'trabajador'])) {
 *   // Mostrar opciones para admin o trabajador
 * }
 */
export const usePermissions = (): PermissionsResult => {
  const { user } = useAuthStore();

  return useMemo(() => {
    const userRole = (user?.rol || 'cliente') as UserRole;

    // Funciones auxiliares
    const hasRole = (role: UserRole | UserRole[]): boolean => {
      if (Array.isArray(role)) {
        return role.includes(userRole);
      }
      return userRole === role;
    };

    const hasAnyRole = (roles: UserRole[]): boolean => {
      return roles.includes(userRole);
    };

    const hasAllRoles = (roles: UserRole[]): boolean => {
      // Un usuario solo puede tener un rol, así que esto siempre es false
      // a menos que sea el mismo rol
      return roles.length === 1 && roles[0] === userRole;
    };

    // Permisos generales
    const canEdit = userRole === 'admin' || userRole === 'trabajador';
    const canDelete = userRole === 'admin';
    const canView = userRole === 'admin' || userRole === 'trabajador' || userRole === 'mensajero';
    const canCreate = userRole === 'admin' || userRole === 'trabajador';

    // Permisos específicos por rol
    const isAdmin = userRole === 'admin';
    const isTrabajador = userRole === 'trabajador';
    const isMensajero = userRole === 'mensajero';
    const isCliente = userRole === 'cliente';

    // Permisos específicos del admin
    const canManageUsers = userRole === 'admin';
    const canManageProductos = userRole === 'admin' || userRole === 'trabajador';
    const canManagePedidos = userRole === 'admin' || userRole === 'trabajador';
    const canViewEstadisticas = userRole === 'admin' || userRole === 'trabajador';
    const canViewHistorial = userRole === 'admin' || userRole === 'trabajador';

    return {
      // Permisos generales
      canEdit,
      canDelete,
      canView,
      canCreate,

      // Permisos específicos por rol
      isAdmin,
      isTrabajador,
      isMensajero,
      isCliente,

      // Permisos específicos del admin
      canManageUsers,
      canManageProductos,
      canManagePedidos,
      canViewEstadisticas,
      canViewHistorial,

      // Utilidades
      hasRole,
      hasAnyRole,
      hasAllRoles,
    };
  }, [user?.rol]);
};

/**
 * Hook especializado para permisos de admin
 */
export const useAdminPermissions = () => {
  const permissions = usePermissions();

  return useMemo(
    () => ({
      ...permissions,
      // Verificar que sea admin
      isAdmin: permissions.isAdmin,
      canManageEverything: permissions.isAdmin,
    }),
    [permissions]
  );
};

/**
 * Hook especializado para permisos de trabajador
 */
export const useTrabajadorPermissions = () => {
  const permissions = usePermissions();

  return useMemo(
    () => ({
      ...permissions,
      // Verificar que sea trabajador
      isTrabajador: permissions.isTrabajador,
      canManageProductosAndPedidos: permissions.isTrabajador,
    }),
    [permissions]
  );
};
