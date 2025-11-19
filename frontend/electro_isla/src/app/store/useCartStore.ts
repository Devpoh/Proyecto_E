/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🛒 CART STORE - Estado Global del Carrito (BACKEND AS SOURCE OF TRUTH)
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Maneja el estado del carrito de compras:
 * - items: Array de productos en el carrito (sincronizado con backend)
 * - setItems: Establecer items desde backend
 * - addItem: Agregar producto (solo local, sincronizar con useSyncCart)
 * - removeItem: Eliminar producto (solo local, sincronizar con useSyncCart)
 * - updateQuantity: Actualizar cantidad (solo local, sincronizar con useSyncCart)
 * - clearCart: Vaciar el carrito
 * 
 * CARACTERÍSTICAS:
 * - ✅ Backend es la fuente de verdad
 * - ✅ localStorage backup automático (items + pending)
 * - ✅ Guarda itemId del backend para sincronización
 * - ✅ Validación de cantidades (no negativos)
 * - ✅ Recupera automáticamente del localStorage al iniciar
 * 
 * IMPORTANTE:
 * - Este store es SOLO para estado local
 * - La sincronización con backend se hace en useSyncCart
 * - Siempre usar useSyncCart para cambios
 */

import { create } from 'zustand';
import { useAuthStore } from './useAuthStore';

// Interfaz de un item del carrito (con ID del backend)
interface CartItem {
  itemId?: number;        // ID del CartItem en backend
  productoId: number;     // ID del Producto
  cantidad: number;       // Cantidad
}

// Interfaz del Store
interface CartState {
  items: CartItem[];
  pending: Record<number, number>;  // ← NUEVO: cambios pendientes de sincronizar
  isSyncing: boolean;               // ← NUEVO: estado de sincronización
  retryCount: number;               // ← NUEVO: contador de reintentos
  
  setItems: (items: CartItem[]) => void;
  addItem: (productoId: number, itemId?: number) => void;
  removeItem: (productoId: number) => void;
  updateQuantity: (productoId: number, cantidad: number) => void;
  clearCart: () => void;
  getTotalItems: () => number;
  getItemByProductId: (productoId: number) => CartItem | undefined;
  
  // ← NUEVOS MÉTODOS:
  setPending: (pending: Record<number, number>) => void;
  setSyncing: (syncing: boolean) => void;
  setRetryCount: (count: number) => void;
}

export const useCartStore = create<CartState>((set, get) => {
  // Cargar estado inicial desde localStorage
  const loadFromLocalStorage = () => {
    try {
      const saved = localStorage.getItem('cart-storage');
      if (saved) {
        const parsed = JSON.parse(saved);
        return {
          items: parsed.items || [],
          pending: parsed.pending || {},
        };
      }
    } catch (error) {
      console.error('[useCartStore] Error cargando del localStorage:', error);
    }
    return { items: [], pending: {} };
  };

  const initialState = loadFromLocalStorage();

  return {
    // Estado inicial
    items: initialState.items,
    pending: initialState.pending,
    isSyncing: false,
    retryCount: 0,

    // Establecer items desde backend (sincronización)
    setItems: (items: CartItem[]) => {
      set({ items });
      // ✅ CRÍTICO: Solo guardar en localStorage si está autenticado
      // Evita carrito fantasma cuando se desloguea durante sincronización
      const { isAuthenticated } = useAuthStore.getState();
      if (isAuthenticated) {
        saveToLocalStorage(get());
      }
    },

    // Agregar item al carrito (local)
    addItem: (productoId: number, itemId?: number) => {
      const items = get().items;
      const existingItem = items.find((item) => item.productoId === productoId);

      if (existingItem) {
        // Si ya existe, incrementar cantidad
        set({
          items: items.map((item) =>
            item.productoId === productoId
              ? { ...item, cantidad: item.cantidad + 1 }
              : item
          ),
        });
      } else {
        // Si no existe, agregar nuevo item
        set({ items: [...items, { itemId, productoId, cantidad: 1 }] });
      }
      saveToLocalStorage(get());
    },

    // Eliminar item del carrito (local)
    removeItem: (productoId: number) => {
      set({
        items: get().items.filter((item) => item.productoId !== productoId),
      });
      saveToLocalStorage(get());
    },

    // Actualizar cantidad de un item (local)
    updateQuantity: (productoId: number, cantidad: number) => {
      // Si cantidad es 0 o negativa, eliminar item
      if (cantidad <= 0) {
        get().removeItem(productoId);
        return;
      }

      set({
        items: get().items.map((item) =>
          item.productoId === productoId ? { ...item, cantidad } : item
        ),
      });
      saveToLocalStorage(get());
    },

    // Vaciar carrito
    clearCart: () => {
      set({ items: [], pending: {} });
      // ✅ Limpiar TODOS los localStorage relacionados con el carrito
      localStorage.removeItem('cart-storage');
      localStorage.removeItem('cart-backup');  // Backup de cambios pendientes
    },

    // Obtener cantidad total de items
    getTotalItems: () => {
      return get().items.reduce((total, item) => total + item.cantidad, 0);
    },

    // Obtener item por productoId
    getItemByProductId: (productoId: number) => {
      return get().items.find((item) => item.productoId === productoId);
    },

    // ← NUEVOS MÉTODOS:
    // Establecer cambios pendientes de sincronizar
    setPending: (pending: Record<number, number>) => {
      set({ pending });
      saveToLocalStorage(get());
    },

    // Establecer estado de sincronización
    setSyncing: (syncing: boolean) => {
      set({ isSyncing: syncing });
    },

    // Establecer contador de reintentos
    setRetryCount: (count: number) => {
      set({ retryCount: count });
    },
  };
});

// Helper: Guardar estado en localStorage
const saveToLocalStorage = (state: CartState) => {
  try {
    const toSave = {
      items: state.items,
      pending: state.pending,
    };
    localStorage.setItem('cart-storage', JSON.stringify(toSave));
  } catch (error) {
    console.error('[useCartStore] Error guardando en localStorage:', error);
  }
};
