/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🪝 HOOK - useValidateStock
 * ═══════════════════════════════════════════════════════════════════════════════
 * Hook para validar stock de productos en el servidor
 * Proporciona mayor seguridad que validar solo en frontend
 */

import { useState } from 'react';
import { useAuthStore } from '@/app/store/useAuthStore';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000/api';

interface StockValidation {
  disponible: boolean;
  stock: number;
  mensaje: string;
}

export const useValidateStock = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const validarStock = async (productoId: number): Promise<StockValidation | null> => {
    setLoading(true);
    setError(null);

    try {
      // ✅ Obtener token desde Zustand (no desde storage)
      const { accessToken } = useAuthStore.getState();
      
      const response = await fetch(`${API_BASE_URL}/productos/${productoId}/validar-stock/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(accessToken && { 'Authorization': `Bearer ${accessToken}` }),
        },
      });

      if (!response.ok) {
        throw new Error('Error al validar stock');
      }

      const data: StockValidation = await response.json();
      return data;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Error desconocido';
      setError(errorMsg);
      return null;
    } finally {
      setLoading(false);
    }
  };

  return {
    validarStock,
    loading,
    error,
  };
};
