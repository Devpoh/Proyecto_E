/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📤 UNLOAD SYNC HOOK - Sincronizar al Cerrar/Recargar
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Hook que sincroniza cambios pendientes cuando el usuario:
 * - Cierra la pestaña
 * - Recarga la página
 * - Navega a otro sitio
 * 
 * Usa navigator.sendBeacon() para enviar datos sin bloquear la UI
 * No es 100% garantizado, pero aumenta significativamente la fiabilidad
 * 
 * FLUJO:
 * 1. Usuario cierra/recarga página
 * 2. beforeunload event se dispara
 * 3. Si hay cambios pendientes → sendBeacon()
 * 4. Backend recibe cambios incluso si la página se cierra
 */

import { useEffect } from 'react';
import { useCartStore } from '@/app/store/useCartStore';

export const useUnloadSync = () => {
  const { pending } = useCartStore();

  useEffect(() => {
    const handleBeforeUnload = () => {
      // Si hay cambios pendientes, intentar enviar con sendBeacon
      if (Object.keys(pending).length > 0 && navigator.sendBeacon) {
        try {
          const payload = JSON.stringify(pending);
          navigator.sendBeacon(
            '/api/carrito/items/sync/',
            new Blob([payload], { type: 'application/json' })
          );
        } catch (error) {
          console.error('[useUnloadSync] Error enviando beacon:', error);
        }
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => window.removeEventListener('beforeunload', handleBeforeUnload);
  }, [pending]);
};
