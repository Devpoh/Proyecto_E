import { useState, useEffect } from 'react';
import { useAuthStore } from '@/app/store/useAuthStore';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

/**
 * Hook optimizado para verificar favoritos en batch (evita N+1 queries)
 * En lugar de hacer una petición por cada producto, hace una sola petición con todos los IDs
 */
export const useFavoritosBatch = (productIds: number[]) => {
  const [favoritos, setFavoritos] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);
  const { isAuthenticated } = useAuthStore();

  useEffect(() => {
    const fetchFavoritos = async () => {
      // Si no hay productos o no está autenticado, no hacer nada
      if (productIds.length === 0 || !isAuthenticated) {
        setFavoritos({});
        setLoading(false);
        return;
      }

      try {
        // ✅ Obtener token desde Zustand (no desde storage)
        const { accessToken } = useAuthStore.getState();
        
        if (!accessToken) {
          setFavoritos({});
          setLoading(false);
          return;
        }
        
        const token = accessToken;

        // Hacer UNA SOLA petición con todos los IDs
        const idsString = productIds.join(',');
        const response = await fetch(
          `${API_BASE_URL}/favoritos/verificar-batch/?ids=${idsString}`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        if (response.ok) {
          const data = await response.json();
          setFavoritos(data.favoritos || {});
        } else {
          setFavoritos({});
        }
      } catch (error) {
        console.error('Error al verificar favoritos:', error);
        setFavoritos({});
      } finally {
        setLoading(false);
      }
    };

    fetchFavoritos();
  }, [productIds.join(','), isAuthenticated]); // Usar join para evitar re-renders innecesarios

  return { favoritos, loading };
};
