/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🔄 CART SYNC HOOK - Sincronización con Debounce + Reintentos
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Hook que maneja:
 * - Debounce de 300ms para evitar saturación
 * - Reintentos con backoff exponencial (1s, 2s, 4s, 8s...)
 * - localStorage backup inmediato
 * - Tracking de cambios pendientes
 * 
 * FLUJO:
 * 1. Usuario hace clic en "+" → updateWithDebounce()
 * 2. UI actualiza inmediatamente (optimistic)
 * 3. localStorage guarda backup
 * 4. Espera 300ms sin clics
 * 5. Envía al backend con reintentos automáticos
 * 6. Si éxito → limpiar pending, mostrar toast ✅
 * 7. Si falla → mantener pending, mostrar toast ⚠️
 */

import { useCallback, useRef } from 'react';
import toast from 'react-hot-toast';
import { useCartStore } from '@/app/store/useCartStore';
import { useAuthStore } from '@/app/store/useAuthStore';

const DEBOUNCE_MS = 300;
const MAX_RETRIES = 5;

export const useCartSync = () => {
  const { pending, setPending, setSyncing, setRetryCount } = useCartStore();
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const isSyncingRef = useRef(false); // Flag para evitar race conditions
  const lastSyncedRef = useRef<Record<number, number>>({}); // Último estado sincronizado (para delta)

  /**
   * Reintento con backoff exponencial
   * Intenta ejecutar la función hasta MAX_RETRIES veces
   * Espera: 1s, 2s, 4s, 8s, 16s entre intentos
   */
  const retryWithBackoff = useCallback(
    async (fn: () => Promise<void>, attempt = 0): Promise<boolean> => {
      try {
        await fn();
        return true;
      } catch (error) {
        if (attempt < MAX_RETRIES) {
          const delay = Math.pow(2, attempt) * 1000; // 1s, 2s, 4s, 8s...
          console.warn(
            `[useCartSync] Reintentando (intento ${attempt + 1}/${MAX_RETRIES}) en ${delay / 1000}s`
          );
          await new Promise((r) => setTimeout(r, delay));
          return retryWithBackoff(fn, attempt + 1);
        }
        return false;
      }
    },
    []
  );

  /**
   * Calcular delta (solo cambios desde la última sincronización)
   * Reduce el payload de ~1MB a ~10KB
   * 
   * DELTA = cambios que NO estaban en lastSynced
   */
  const calculateDelta = (currentPending: Record<number, number>): Record<number, number> => {
    const delta: Record<number, number> = {};
    
    for (const [productIdStr, cantidad] of Object.entries(currentPending)) {
      const productId = parseInt(productIdStr);
      const lastSyncedCantidad = lastSyncedRef.current[productId];
      
      // Si la cantidad cambió desde la última sincronización, incluir en delta
      if (lastSyncedCantidad !== cantidad) {
        delta[productId] = cantidad;
      }
    }
    
    return delta;
  };

  /**
   * Sincronizar todos los cambios pendientes con el backend
   * Usa endpoint bulk-update para eficiencia (1 request para múltiples productos)
   * Se llama automáticamente después del debounce o manualmente con forceSync()
   * 
   * IMPORTANTE:
   * - Lee el estado actual de pending justo antes de sincronizar
   * - Calcula delta (solo cambios) para reducir payload
   * - Evita race conditions cuando se agregan cambios mientras se sincroniza
   */
  const syncPending = useCallback(async () => {
    // Leer el estado ACTUAL de pending (snapshot)
    const currentPending = useCartStore.getState().pending;
    
    if (Object.keys(currentPending).length === 0) {
      console.log('[useCartSync] No hay cambios pendientes');
      return true;
    }

    // Evitar sincronizaciones concurrentes
    if (isSyncingRef.current) {
      console.log('[useCartSync] ⏳ Ya hay una sincronización en curso, esperando...');
      return false;
    }

    isSyncingRef.current = true;
    
    // 🔥 OPTIMIZACIÓN: Calcular delta (solo cambios)
    const delta = calculateDelta(currentPending);
    
    if (Object.keys(delta).length === 0) {
      console.log('[useCartSync] ✅ No hay cambios nuevos desde la última sincronización');
      isSyncingRef.current = false;
      return true;
    }
    
    console.log('[useCartSync] Iniciando sincronización con delta (cambios):', delta);
    console.log('[useCartSync] Payload size: ~', JSON.stringify(delta).length, 'bytes (antes era ~1MB)');
    setSyncing(true);

    try {
      // Usar bulk-update para sincronizar todos los cambios en 1 request
      const syncBulk = async () => {
        // ✅ Obtener token desde Zustand (no desde storage)
        const { accessToken } = useAuthStore.getState();
        
        const headers: Record<string, string> = {
          'Content-Type': 'application/json',
        };
        
        // Agregar token JWT si existe
        if (accessToken) {
          headers['Authorization'] = `Bearer ${accessToken}`;
        }
        
        const response = await fetch('/api/carrito/bulk-update/', {
          method: 'POST',
          headers,
          credentials: 'include',
          body: JSON.stringify({ updates: delta }),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        
        // Verificar si hay error en la respuesta JSON
        if (data.error) {
          throw new Error(data.error);
        }
        
        return data;
      };

      // Reintentar con backoff si falla
      const success = await retryWithBackoff(syncBulk);

      if (!success) {
        console.error('[useCartSync] Sincronización falló después de reintentos');
        isSyncingRef.current = false;
        setSyncing(false);
        toast.error('⚠️ Error sincronizando carrito. Reintenta más tarde.');
        return false;
      }

      // Éxito: limpiar pending y guardar delta como "last synced"
      console.log('[useCartSync] ✅ Sincronización exitosa. Limpiando cambios pendientes.');
      
      // 🔥 OPTIMIZACIÓN: Guardar delta como "last synced" para próximas sincronizaciones
      lastSyncedRef.current = { ...lastSyncedRef.current, ...delta };
      console.log('[useCartSync] 💾 Guardado estado sincronizado:', lastSyncedRef.current);
      
      setPending({});
      setRetryCount(0);
      isSyncingRef.current = false;
      setSyncing(false);
      toast.success('✅ Carrito sincronizado');
      
      // Si llegaron cambios mientras se sincronizaba, dispara otra sincronización
      const newPending = useCartStore.getState().pending;
      if (Object.keys(newPending).length > 0) {
        console.log('[useCartSync] 🔄 Nuevos cambios detectados, sincronizando nuevamente...');
        setTimeout(() => syncPending(), 100);
      }
      
      return true;
    } catch (error) {
      console.error('[useCartSync] Error en try-catch:', error);
      isSyncingRef.current = false;
      setSyncing(false);
      toast.error('❌ Error al sincronizar carrito');
      return false;
    }
  }, [pending, setPending, setSyncing, setRetryCount, retryWithBackoff]);

  /**
   * Actualizar cantidad con debounce
   * 1. Actualizar pending inmediatamente
   * 2. Guardar en localStorage como backup
   * 3. Cancelar timer anterior (si no hay sincronización en curso)
   * 4. Debounce: sincronizar después de 300ms
   * 
   * IMPORTANTE: Si ya hay una sincronización en curso, los cambios se acumularán
   * en pending y se sincronizarán automáticamente después
   */
  const updateWithDebounce = useCallback(
    (productoId: number, cantidad: number) => {
      // Leer el estado actual de pending
      const currentPending = useCartStore.getState().pending;
      
      // 1. Actualizar pending inmediatamente
      const newPending = { ...currentPending, [productoId]: cantidad };
      setPending(newPending);

      // 2. Guardar en localStorage como backup
      localStorage.setItem('cart-backup', JSON.stringify(newPending));

      // 3. Cancelar timer anterior
      if (timerRef.current) clearTimeout(timerRef.current);

      // 4. Debounce: sincronizar después de 300ms
      timerRef.current = setTimeout(() => {
        syncPending();
      }, DEBOUNCE_MS);
    },
    [setPending, syncPending]
  );

  /**
   * Sincronización forzada (para checkout)
   * Cancela el debounce y sincroniza inmediatamente
   */
  const forceSync = useCallback(async () => {
    if (timerRef.current) clearTimeout(timerRef.current);
    return syncPending();
  }, [syncPending]);

  return {
    updateWithDebounce,
    forceSync,
    syncPending,
    pending,
  };
};
