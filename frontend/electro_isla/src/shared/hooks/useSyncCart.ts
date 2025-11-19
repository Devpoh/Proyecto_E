/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🔄 SYNC CART HOOK - Sincronización Bidireccional del Carrito
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Hook para sincronizar el carrito local con el backend.
 * 
 * FLUJO:
 * 1. Al login: Obtiene carrito del backend y lo carga en local
 * 2. Al agregar: Agrega localmente, luego sincroniza con backend
 * 3. Al actualizar cantidad: Actualiza localmente, luego sincroniza
 * 4. Al eliminar: Elimina localmente, luego sincroniza
 * 5. Al logout: Limpia carrito local
 * 
 * IMPORTANTE:
 * - Backend es la fuente de verdad
 * - Siempre sincronizar después de cambios locales
 * - Guardar itemId para operaciones en backend
 */

import { useEffect, useCallback } from 'react';
import { useAuthStore } from '@/app/store/useAuthStore';
import { useCartStore } from '@/app/store/useCartStore';
import toast from 'react-hot-toast';

// API Configuration
const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api';
const REQUEST_TIMEOUT = 5000; // 5 segundos
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 segundo

// OPTIMIZACIÓN: Flag global para evitar múltiples cargas simultáneas del carrito
let isCartLoading = false;
let cartLoadPromise: Promise<void> | null = null;

// OPTIMIZACIÓN: Rastrear usuarios cuyo carrito ya se cargó en esta sesión
// Se reinicia al recargar la página (lo que queremos)
let cartLoadedForUser: Set<number> = new Set();

// RACE CONDITION FIX: Queue para procesar eliminaciones con concurrencia limitada
let deleteQueue: Set<number> = new Set();
let activeDeletes = 0;
const MAX_CONCURRENT_DELETES = 3;  // Permitir hasta 3 eliminaciones simultáneas
let pendingDeletes: number[] = [];

interface BackendCartItem {
  id: number;
  product: {
    id: number;
    nombre: string;
  };
  quantity: number;
  price_at_addition: string;
}

interface BackendCart {
  id: number;
  items: BackendCartItem[];
  total: number;
  total_items: number;
}

// MERGE FIX: Función para hacer merge de items inteligentemente
// Para eliminaciones: usar respuesta del backend directamente (ya tiene el estado correcto)
// Para adiciones/actualizaciones: hacer merge para evitar flickering
const mergeCartItems = (current: any[], incoming: any[], isDelete: boolean = false): any[] => {
  // Para eliminaciones: el backend devuelve el carrito actualizado sin el item eliminado
  // Usar la respuesta directamente es más seguro que intentar hacer merge
  if (isDelete) {
    return incoming;
  }
  
  // Para adiciones/actualizaciones: hacer merge para evitar flickering
  // Esto permite que items nuevos se agreguen sin perder items en proceso
  const itemMap = new Map(current.map(item => [item.productoId, item]));
  
  // Actualizar con items nuevos
  incoming.forEach(item => {
    itemMap.set(item.productoId, item);
  });
  
  // Retornar array actualizado
  return Array.from(itemMap.values());
};

// Validar estructura de respuesta del carrito
const validateCartResponse = (data: unknown): BackendCart => {
  if (!data || typeof data !== 'object') {
    throw new Error('Respuesta inválida del servidor');
  }
  
  const cart = data as any;
  
  if (!Array.isArray(cart.items) || typeof cart.total !== 'number' || typeof cart.total_items !== 'number') {
    throw new Error('Estructura de carrito inválida');
  }
  
  return cart as BackendCart;
};

// Fetch con timeout
const fetchWithTimeout = async (url: string, options: RequestInit, timeout = REQUEST_TIMEOUT) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error('Tiempo de conexión agotado');
    }
    throw error;
  }
};

// Retry con backoff exponencial
const fetchWithRetry = async (
  url: string,
  options: RequestInit,
  retries = MAX_RETRIES
): Promise<Response> => {
  try {
    return await fetchWithTimeout(url, options);
  } catch (error) {
    if (retries > 0) {
      await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * (MAX_RETRIES - retries + 1)));
      return fetchWithRetry(url, options, retries - 1);
    }
    throw error;
  }
};

export const useSyncCart = () => {
  const { isAuthenticated, user } = useAuthStore();
  const { setItems, clearCart, getItemByProductId } = useCartStore();

  // ✅ Obtener token desde Zustand (no desde storage)
  const getToken = useCallback(() => {
    const { accessToken } = useAuthStore.getState();
    return accessToken;
  }, []);

  // ═══════════════════════════════════════════════════════════════════════════════
  // 1. OBTENER CARRITO DEL BACKEND (al login)
  // ═══════════════════════════════════════════════════════════════════════════════
  const fetchCartFromBackend = useCallback(async () => {
    if (!isAuthenticated || !user) return;

    // OPTIMIZACIÓN: Si ya se está cargando, esperar a que termine
    if (isCartLoading && cartLoadPromise) {
      await cartLoadPromise;
      return;
    }

    // OPTIMIZACIÓN: Si ya se cargó, no volver a cargar
    if (isCartLoading) {
      return;
    }

    // Marcar como cargando
    isCartLoading = true;

    cartLoadPromise = (async () => {
      try {
        const token = getToken();
        if (!token) return;

        const response = await fetchWithRetry(`${API_BASE_URL}/carrito/`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          if (response.status === 401) {
            console.warn('[useSyncCart] Token inválido o expirado');
            return;
          }
          throw new Error('Error al obtener carrito');
        }

        const data = await response.json();
        const backendCart = validateCartResponse(data);

        // Convertir items del backend al formato local
        const localItems = backendCart.items.map((item) => ({
          itemId: item.id,                    // ID del CartItem en backend
          productoId: item.product.id,        // ID del Producto
          cantidad: item.quantity,            // Cantidad
        }));

        // Establecer items en el store (reemplaza todo)
        setItems(localItems);

        console.debug('[useSyncCart] Carrito sincronizado desde backend:', localItems);
      } catch (error) {
        console.error('[useSyncCart] Error al obtener carrito:', error);
      } finally {
        // Resetear flags después de un tiempo
        setTimeout(() => {
          isCartLoading = false;
          cartLoadPromise = null;
        }, 1000);
      }
    })();

    await cartLoadPromise;
  }, [isAuthenticated, user, getToken, setItems]);

  // ═══════════════════════════════════════════════════════════════════════════════
  // 2. AGREGAR PRODUCTO AL BACKEND
  // ═══════════════════════════════════════════════════════════════════════════════
  const syncAddToBackend = useCallback(async (productId: number, quantity: number = 1) => {
    if (!isAuthenticated || !user) {
      throw new Error('No autenticado');
    }

    const token = getToken();
    if (!token) {
      throw new Error('Token no disponible');
    }

    // Validar entrada
    if (!Number.isInteger(productId) || productId <= 0) {
      throw new Error('ID de producto inválido');
    }
    if (!Number.isInteger(quantity) || quantity <= 0 || quantity > 999) {
      throw new Error('Cantidad inválida');
    }

    try {
      const response = await fetchWithRetry(`${API_BASE_URL}/carrito/agregar/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_id: productId,
          quantity: quantity,
        }),
      });

      if (!response.ok) {
        let errorMessage = 'Error al agregar al carrito';
        
        try {
          const errorData = await response.json();
          // Solo mostrar mensajes de error seguros (del backend)
          if (errorData.error && typeof errorData.error === 'string') {
            errorMessage = errorData.error;
          } else if (errorData.detail && typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          }
        } catch (parseError) {
          // Si no es JSON válido, usar mensaje genérico
          console.error('[useSyncCart] Error parsing response:', parseError);
          if (response.status === 400) {
            errorMessage = 'Solicitud inválida. Por favor, intenta de nuevo.';
          } else if (response.status === 401) {
            errorMessage = 'Tu sesión ha expirado. Por favor, inicia sesión de nuevo.';
          } else if (response.status === 429) {
            errorMessage = 'Demasiadas solicitudes. Por favor, espera un momento.';
          } else if (response.status >= 500) {
            errorMessage = 'Error del servidor. Por favor, intenta más tarde.';
          }
        }
        
        throw new Error(errorMessage);
      }

      const data = await response.json();
      const backendCart = validateCartResponse(data);

      // Actualizar items locales desde la respuesta del backend
      const localItems = backendCart.items.map((item) => ({
        itemId: item.id,                    // CRÍTICO: Guardar itemId del backend
        productoId: item.product.id,
        cantidad: item.quantity,
      }));

      // MERGE FIX: Hacer merge en lugar de reemplazo para evitar flickering
      const currentItems = useCartStore.getState().items;
      const mergedItems = mergeCartItems(currentItems, localItems);
      setItems(mergedItems);

      console.debug('[useSyncCart] Producto agregado al backend. Items:', mergedItems);
    } catch (error) {
      console.error('[useSyncCart] Error al agregar al backend:', error);
      const message = error instanceof Error ? error.message : 'Error al sincronizar carrito';
      toast.error(message, { icon: '❌' });
      // Lanzar la excepción para que useAddToCart pueda manejarla
      throw error;
    }
  }, [isAuthenticated, user, getToken, setItems]);

  // ═══════════════════════════════════════════════════════════════════════════════
  // 3. ACTUALIZAR CANTIDAD EN BACKEND
  // ═══════════════════════════════════════════════════════════════════════════════
  const syncUpdateQuantityBackend = useCallback(async (productoId: number, quantity: number) => {
    if (!isAuthenticated || !user) return;

    try {
      const token = getToken();
      if (!token) return;

      // Validar entrada
      if (!Number.isInteger(quantity) || quantity <= 0 || quantity > 999) {
        throw new Error('Cantidad inválida');
      }

      // Obtener itemId del producto
      const item = getItemByProductId(productoId);
      if (!item || !item.itemId) {
        console.error('[useSyncCart] No se encontró itemId para producto:', productoId);
        return;
      }

      const response = await fetchWithRetry(`${API_BASE_URL}/carrito/items/${item.itemId}/`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ quantity }),
      });

      if (!response.ok) {
        // MANEJO DE 401: Token expirado
        if (response.status === 401) {
          console.warn('[useSyncCart] Token expirado al actualizar cantidad');
          // El error será manejado por el catch
          throw new Error('Tu sesión ha expirado. Por favor, inicia sesión de nuevo.');
        }
        throw new Error('Error al actualizar cantidad');
      }

      const data = await response.json();
      const backendCart = validateCartResponse(data);

      // Actualizar items locales desde la respuesta del backend
      const localItems = backendCart.items.map((item) => ({
        itemId: item.id,
        productoId: item.product.id,
        cantidad: item.quantity,
      }));

      // CRÍTICO: Para actualizaciones de cantidad, usar respuesta del backend directamente
      // NO hacer merge porque el backend tiene el estado correcto
      // El merge causaba flickering (mostrar cantidad anterior brevemente)
      setItems(localItems);

      console.debug('[useSyncCart] Cantidad actualizada en backend');
    } catch (error) {
      console.error('[useSyncCart] Error al actualizar cantidad:', error);
      const message = error instanceof Error ? error.message : 'Error al sincronizar cantidad';
      toast.error(message, { icon: '[ERROR]' });
    }
  }, [isAuthenticated, user, getToken, getItemByProductId, setItems]);

  // ═══════════════════════════════════════════════════════════════════════════════
  // 4. ELIMINAR PRODUCTO DEL BACKEND (CON RACE CONDITION FIX MEJORADO)
  // ═══════════════════════════════════════════════════════════════════════════════
  
  // Función auxiliar para procesar la cola de eliminaciones con concurrencia limitada
  const processDeleteQueue = useCallback(async () => {
    if (pendingDeletes.length === 0) {
      return;
    }

    // Procesar mientras haya items pendientes y no hayamos alcanzado el límite de concurrencia
    while (pendingDeletes.length > 0 && activeDeletes < MAX_CONCURRENT_DELETES) {
      const productoId = pendingDeletes.shift();
      if (!productoId) break;

      activeDeletes++;

      // Procesar en paralelo (no await aquí)
      (async () => {
        try {
          const token = getToken();
          if (!token) {
            activeDeletes--;
            return;
          }

          // VALIDACIÓN: Verificar que el producto existe en el carrito
          const item = getItemByProductId(productoId);
          if (!item || !item.itemId) {
            deleteQueue.delete(productoId);
            activeDeletes--;
            return;
          }

          // VALIDACIÓN: Verificar que itemId es válido
          if (!Number.isInteger(item.itemId) || item.itemId <= 0) {
            deleteQueue.delete(productoId);
            activeDeletes--;
            return;
          }

          const response = await fetchWithRetry(`${API_BASE_URL}/carrito/items/${item.itemId}/`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });

          if (!response.ok) {
            // MANEJO DE 404: Item ya fue eliminado
            if (response.status === 404) {
              // Sincronizar carrito desde backend para obtener estado actual
              await fetchCartFromBackend();
              deleteQueue.delete(productoId);
              activeDeletes--;
              // Procesar siguiente
              await processDeleteQueue();
              return;
            }
            throw new Error('Error al eliminar del carrito');
          }

          const data = await response.json();
          const backendCart = validateCartResponse(data);

          // Actualizar items locales desde la respuesta del backend
          const localItems = backendCart.items.map((item) => ({
            itemId: item.id,
            productoId: item.product.id,
            cantidad: item.quantity,
          }));

          // CRÍTICO: Para eliminaciones, usar respuesta del backend directamente
          setItems(localItems);

          deleteQueue.delete(productoId);
          activeDeletes--;
          
          // Procesar siguiente si hay pendientes
          if (pendingDeletes.length > 0) {
            await processDeleteQueue();
          }
        } catch (error) {
          const message = error instanceof Error ? error.message : 'Error al eliminar producto';
          toast.error(message, { icon: '❌' });
          deleteQueue.delete(productoId);
          activeDeletes--;
          
          // Procesar siguiente si hay pendientes
          if (pendingDeletes.length > 0) {
            await processDeleteQueue();
          }
        }
      })();
    }
  }, [getToken, getItemByProductId, setItems, fetchCartFromBackend]);

  const syncRemoveFromBackend = useCallback(async (productoId: number) => {
    if (!isAuthenticated || !user) return;

    // RACE CONDITION FIX: Agregar a cola en lugar de procesar inmediatamente
    if (deleteQueue.has(productoId)) {
      // Ya está en cola, no hacer nada
      return;
    }

    deleteQueue.add(productoId);
    pendingDeletes.push(productoId);

    // Procesar la cola
    await processDeleteQueue();
  }, [isAuthenticated, user, processDeleteQueue]);

  // ═══════════════════════════════════════════════════════════════════════════════
  // EFECTOS: Sincronización automática
  // ═══════════════════════════════════════════════════════════════════════════════

  // Limpiar carrito cuando el usuario cierra sesión
  useEffect(() => {
    if (!isAuthenticated) {
      clearCart();
      // ✅ Resetear flags globales para evitar carrito fantasma
      cartLoadedForUser.clear();
      isCartLoading = false;
      cartLoadPromise = null;
      console.debug('[useSyncCart] Carrito limpiado al cerrar sesión. Flags reseteados.');
    }
  }, [isAuthenticated, clearCart]);

  // Obtener carrito del backend cuando el usuario inicia sesión
  // OPTIMIZACIÓN: Solo ejecutar UNA VEZ por sesión para evitar N+1 queries
  useEffect(() => {
    if (isAuthenticated && user) {
      // Verificar si ya se cargó el carrito en esta sesión
      // Usar flag en memoria (se reinicia al recargar la página)
      if (cartLoadedForUser.has(user.id)) {
        return; // Ya se cargó, no volver a cargar
      }
      
      // Esperar un poco para asegurar que el token está guardado
      const timer = setTimeout(() => {
        fetchCartFromBackend();
        // Marcar como cargado
        cartLoadedForUser.add(user.id);
      }, 300);

      return () => clearTimeout(timer);
    }
  }, [isAuthenticated, user, fetchCartFromBackend]);

  return {
    fetchCartFromBackend,
    syncAddToBackend,
    syncUpdateQuantityBackend,
    syncRemoveFromBackend,
  };
};
