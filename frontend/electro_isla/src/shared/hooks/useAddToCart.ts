/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🪝 HOOK - useAddToCart (Con Autenticación Obligatoria)
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Hook reutilizable para agregar productos al carrito con feedback visual
 * Usado en ProductCarousel, CarouselCard, y otros componentes
 * 
 * 🔐 AUTENTICACIÓN OBLIGATORIA:
 * - ✅ Verifica si el usuario está logueado
 * - ✅ Si NO está logueado → Redirige a /login
 * - ✅ Si está logueado → Agrega al carrito
 * 
 * CARACTERÍSTICAS:
 * - ✅ Agregar producto al carrito (SOLO si está autenticado)
 * - ✅ Delay de 1 segundo
 * - ✅ Botón cambia a "¡AGREGADO!"
 * - ✅ Icono cambia a checkmark
 * - ✅ Notificación toast
 * - ✅ Reutilizable en cualquier componente
 * - ✅ Carrito por usuario (sincronizado con backend)
 * 
 * ⚠️ ORDEN DE HOOKS:
 * - Todos los hooks se llaman en el mismo orden siempre
 * - useState antes de useCallback
 * - No hay condicionales que afecten el orden
 */

import { useState, useCallback, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCartStore } from '@/app/store/useCartStore';
import { useAuthStore } from '@/app/store/useAuthStore';
import { useSyncCart } from './useSyncCart';
import toast from 'react-hot-toast';

interface UseAddToCartReturn {
  addedProductId: string | number | null;
  isAdding: boolean;
  handleAddToCart: (productId: string | number, quantity?: number, stock?: number) => void;
}

// Almacenamiento global para agrupar toasts
let toastTimeout: NodeJS.Timeout | null = null;
let productsAddedCount = 0;
let toastId: string | null = null;

// Almacenamiento global para debounce de requests (evitar spam)
const requestDebounceMap = new Map<number, NodeJS.Timeout>();
const REQUEST_DEBOUNCE_DELAY = 1000; // 1 segundo entre requests del mismo producto

export const useAddToCart = (): UseAddToCartReturn => {
  // 🔴 ORDEN CRÍTICO: Todos los hooks PRIMERO
  const navigate = useNavigate();
  const { addItem } = useCartStore();
  const { isAuthenticated } = useAuthStore();
  const { syncAddToBackend } = useSyncCart();
  const [addedProductId, setAddedProductId] = useState<string | number | null>(null);
  const [isAdding, setIsAdding] = useState(false);
  const addedProductsRef = useRef<Set<number>>(new Set());

  // Limpiar al desmontar
  useEffect(() => {
    return () => {
      if (toastTimeout) clearTimeout(toastTimeout);
    };
  }, []);

  // 🟢 useCallback DESPUÉS de todos los useState
  const handleAddToCart = useCallback(async (productId: string | number, quantity: number = 1, stock: number = 0) => {
    // 🔐 VERIFICAR AUTENTICACIÓN
    if (!isAuthenticated) {
      toast.error('Debes iniciar sesión para agregar productos al carrito', {
        icon: '🔐',
        duration: 3000,
      });
      
      // Redirigir a login
      navigate('/login', { replace: true });
      return;
    }

    // ✅ VALIDAR STOCK DISPONIBLE (no reservado)
    // stock_disponible = stock_total - stock_reservado - stock_vendido
    if (stock <= 0) {
      toast.error('Este producto está agotado', {
        icon: '❌',
        duration: 2000,
      });
      return;
    }

    if (quantity > stock) {
      toast.error(`Solo hay ${stock} unidades disponibles. Otros clientes pueden estar comprando.`, {
        icon: '⚠️',
        duration: 2000,
      });
      return;
    }

    // Convertir a número si es necesario
    const numericId = typeof productId === 'string' ? parseInt(productId, 10) : productId;

    // ✅ DEBOUNCE: Evitar múltiples requests del mismo producto en corto tiempo
    if (requestDebounceMap.has(numericId)) {
      console.warn(`[useAddToCart] Debounce: Producto ${numericId} ya está siendo procesado`);
      toast.error('Por favor espera, procesando...', { duration: 1000 });
      return;
    }

    // Evitar agregar el mismo producto múltiples veces en la misma ráfaga
    if (addedProductsRef.current.has(numericId)) {
      console.warn(`[useAddToCart] Producto ${numericId} ya fue agregado recientemente`);
      return;
    }

    // Verificar si ya está en proceso de agregarse (isAdding)
    if (isAdding) {
      console.warn(`[useAddToCart] Ya hay un producto siendo agregado`);
      return;
    }

    addedProductsRef.current.add(numericId);
    setIsAdding(true);

    // Crear timeout para debounce
    const debounceTimeout = setTimeout(() => {
      requestDebounceMap.delete(numericId);
    }, REQUEST_DEBOUNCE_DELAY);
    requestDebounceMap.set(numericId, debounceTimeout);

    try {
      // Sincronizar con backend PRIMERO para validar stock
      // IMPORTANTE: syncAddToBackend ya actualiza el store local con setItems()
      // NO necesitamos agregar manualmente con addItem()
      await syncAddToBackend(numericId, quantity);

      // Mostrar feedback visual
      setAddedProductId(productId);

      // Agrupar toasts: incrementar contador y resetear timeout
      productsAddedCount += quantity;

      // Limpiar timeout anterior si existe
      if (toastTimeout) {
        clearTimeout(toastTimeout);
        // Descartar el toast anterior
        if (toastId) {
          toast.dismiss(toastId);
        }
      }

      // Mostrar/actualizar notificación agrupada después de 500ms
      toastTimeout = setTimeout(() => {
        const message = productsAddedCount === 1 
          ? '1 producto agregado al carrito!' 
          : `${productsAddedCount} productos agregados al carrito!`;
        
        toastId = toast.success(message, {
          icon: '✅',
          duration: 2000,
        });

        // Resetear contadores
        productsAddedCount = 0;
        addedProductsRef.current.clear();
        toastTimeout = null;
        toastId = null;
      }, 500);

      // Resetear después de 1 segundo
      setTimeout(() => {
        setAddedProductId(null);
        setIsAdding(false);
      }, 1000);
    } catch (error) {
      // Error al sincronizar con backend
      console.error('[useAddToCart] Error al agregar al backend:', error);
      addedProductsRef.current.delete(numericId);
      setIsAdding(false);
      // El error ya fue mostrado por syncAddToBackend
    }
  }, [isAuthenticated, navigate, addItem, syncAddToBackend]);

  return {
    addedProductId,
    isAdding,
    handleAddToCart,
  };
};
