/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🛠️ UTILIDADES - Roles
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Utilidades para trabajar con roles de usuario.
 * Centraliza la lógica de roles para evitar duplicación.
 * 
 * BENEFICIOS:
 * - Centraliza la lógica de roles
 * - Fácil de mantener y actualizar
 * - Consistencia en todo el admin panel
 * - Reduce código duplicado (~40 líneas)
 */

export type UserRole = 'admin' | 'trabajador' | 'mensajero' | 'cliente';

export interface RolConfig {
  label: string;
  class: string;
  color: string;
  icon: string;
  description: string;
}

/**
 * Configuración de roles
 */
export const ROL_CONFIG: Record<UserRole, RolConfig> = {
  admin: {
    label: 'Administrador',
    class: 'badge-admin',
    color: '#ef4444',
    icon: '👑',
    description: 'Acceso total al sistema',
  },
  trabajador: {
    label: 'Trabajador',
    class: 'badge-trabajador',
    color: '#3b82f6',
    icon: '👨‍💼',
    description: 'Gestión de productos y pedidos',
  },
  mensajero: {
    label: 'Mensajero',
    class: 'badge-mensajero',
    color: '#f59e0b',
    icon: '🚚',
    description: 'Entrega de pedidos',
  },
  cliente: {
    label: 'Cliente',
    class: 'badge-cliente',
    color: '#10b981',
    icon: '👤',
    description: 'Usuario regular',
  },
};

/**
 * Obtener el label de un rol
 * 
 * @param rol - Rol del usuario
 * @returns Label del rol
 * 
 * @example
 * getRolLabel('admin') // 'Administrador'
 * getRolLabel('cliente') // 'Cliente'
 */
export const getRolLabel = (rol: string): string => {
  return ROL_CONFIG[rol as UserRole]?.label || 'Cliente';
};

/**
 * Obtener la clase CSS de un rol
 * 
 * @param rol - Rol del usuario
 * @returns Clase CSS del rol
 * 
 * @example
 * getRolBadgeClass('admin') // 'badge-admin'
 * getRolBadgeClass('cliente') // 'badge-cliente'
 */
export const getRolBadgeClass = (rol: string): string => {
  return ROL_CONFIG[rol as UserRole]?.class || 'badge-cliente';
};

/**
 * Obtener el color de un rol
 * 
 * @param rol - Rol del usuario
 * @returns Color del rol (hex)
 * 
 * @example
 * getRolColor('admin') // '#ef4444'
 */
export const getRolColor = (rol: string): string => {
  return ROL_CONFIG[rol as UserRole]?.color || '#10b981';
};

/**
 * Obtener el icono de un rol
 * 
 * @param rol - Rol del usuario
 * @returns Icono del rol (emoji)
 * 
 * @example
 * getRolIcon('admin') // '👑'
 */
export const getRolIcon = (rol: string): string => {
  return ROL_CONFIG[rol as UserRole]?.icon || '👤';
};

/**
 * Obtener la descripción de un rol
 * 
 * @param rol - Rol del usuario
 * @returns Descripción del rol
 * 
 * @example
 * getRolDescription('admin') // 'Acceso total al sistema'
 */
export const getRolDescription = (rol: string): string => {
  return ROL_CONFIG[rol as UserRole]?.description || 'Usuario regular';
};

/**
 * Obtener toda la configuración de un rol
 * 
 * @param rol - Rol del usuario
 * @returns Configuración completa del rol
 * 
 * @example
 * getRolConfig('admin')
 * // { label: 'Administrador', class: 'badge-admin', ... }
 */
export const getRolConfig = (rol: string): RolConfig => {
  return ROL_CONFIG[rol as UserRole] || ROL_CONFIG.cliente;
};

/**
 * Obtener lista de todos los roles
 * 
 * @returns Array de roles disponibles
 * 
 * @example
 * getAllRoles() // ['admin', 'trabajador', 'mensajero', 'cliente']
 */
export const getAllRoles = (): UserRole[] => {
  return Object.keys(ROL_CONFIG) as UserRole[];
};

/**
 * Obtener lista de roles con sus labels
 * 
 * @returns Array de objetos { value, label }
 * 
 * @example
 * getRolesWithLabels()
 * // [
 * //   { value: 'admin', label: 'Administrador' },
 * //   { value: 'trabajador', label: 'Trabajador' },
 * //   ...
 * // ]
 */
export const getRolesWithLabels = () => {
  return getAllRoles().map((rol) => ({
    value: rol,
    label: getRolLabel(rol),
  }));
};

/**
 * Validar si un rol es válido
 * 
 * @param rol - Rol a validar
 * @returns True si el rol es válido
 * 
 * @example
 * isValidRol('admin') // true
 * isValidRol('superadmin') // false
 */
export const isValidRol = (rol: string): rol is UserRole => {
  return rol in ROL_CONFIG;
};

/**
 * Comparar dos roles por jerarquía
 * 
 * @param rol1 - Primer rol
 * @param rol2 - Segundo rol
 * @returns -1 si rol1 < rol2, 0 si son iguales, 1 si rol1 > rol2
 * 
 * @example
 * compareRols('admin', 'cliente') // 1 (admin > cliente)
 * compareRols('cliente', 'admin') // -1 (cliente < admin)
 */
export const compareRols = (rol1: string, rol2: string): number => {
  const hierarchy: Record<UserRole, number> = {
    admin: 4,
    trabajador: 3,
    mensajero: 2,
    cliente: 1,
  };

  const level1 = hierarchy[rol1 as UserRole] || 0;
  const level2 = hierarchy[rol2 as UserRole] || 0;

  if (level1 > level2) return 1;
  if (level1 < level2) return -1;
  return 0;
};

/**
 * Verificar si un rol tiene mayor o igual jerarquía que otro
 * 
 * @param rol - Rol a verificar
 * @param minRol - Rol mínimo requerido
 * @returns True si rol >= minRol
 * 
 * @example
 * hasMinimumRol('admin', 'trabajador') // true
 * hasMinimumRol('cliente', 'trabajador') // false
 */
export const hasMinimumRol = (rol: string, minRol: string): boolean => {
  return compareRols(rol, minRol) >= 0;
};
