/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎣 HOOK - useInvalidateAdminQueries
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Hook reutilizable para invalidar queries del panel admin.
 * Evita duplicación de código en ProductosPage, UsuariosPage, PedidosPage, etc.
 * 
 * BENEFICIOS:
 * - Centraliza la lógica de invalidación
 * - Fácil de mantener y actualizar
 * - Consistencia en todo el admin panel
 * - Reduce código duplicado (~50 líneas)
 */

import { useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';

interface InvalidateOptions {
  includeDefaults?: boolean;
  additionalKeys?: string[];
}

/**
 * Hook para invalidar queries del admin panel
 * 
 * @param options - Opciones de invalidación
 * @returns Función para invalidar queries
 * 
 * @example
 * const invalidateQueries = useInvalidateAdminQueries();
 * 
 * // Invalidar queries por defecto
 * invalidateQueries();
 * 
 * // Invalidar queries específicas
 * invalidateQueries({ additionalKeys: ['productos', 'usuarios'] });
 * 
 * // Invalidar solo queries específicas (sin defaults)
 * invalidateQueries({ includeDefaults: false, additionalKeys: ['productos'] });
 */
export const useInvalidateAdminQueries = (options: InvalidateOptions = {}) => {
  const queryClient = useQueryClient();
  const { includeDefaults = true, additionalKeys = [] } = options;

  return useCallback(
    (customKeys?: string[]) => {
      // Keys por defecto que siempre se invalidan
      const defaultKeys = ['dashboard-stats', 'historial'];

      // Combinar keys
      const keysToInvalidate = includeDefaults
        ? [...defaultKeys, ...additionalKeys, ...(customKeys || [])]
        : [...additionalKeys, ...(customKeys || [])];

      // Invalidar cada key
      keysToInvalidate.forEach((key) => {
        queryClient.invalidateQueries({ queryKey: [key] });
      });

      console.debug(
        `[useInvalidateAdminQueries] Invalidadas queries: ${keysToInvalidate.join(', ')}`
      );
    },
    [queryClient, includeDefaults, additionalKeys]
  );
};

/**
 * Hook especializado para invalidar queries de productos
 */
export const useInvalidateProductosQueries = () => {
  return useInvalidateAdminQueries({
    includeDefaults: true,
    additionalKeys: ['admin-productos'],
  });
};

/**
 * Hook especializado para invalidar queries de usuarios
 */
export const useInvalidateUsuariosQueries = () => {
  return useInvalidateAdminQueries({
    includeDefaults: true,
    additionalKeys: ['admin-users'],
  });
};

/**
 * Hook especializado para invalidar queries de pedidos
 */
export const useInvalidatePedidosQueries = () => {
  return useInvalidateAdminQueries({
    includeDefaults: true,
    additionalKeys: ['admin-pedidos'],
  });
};

/**
 * Hook especializado para invalidar queries del historial
 */
export const useInvalidateHistorialQueries = () => {
  return useInvalidateAdminQueries({
    includeDefaults: true,
    additionalKeys: ['admin-historial'],
  });
};
