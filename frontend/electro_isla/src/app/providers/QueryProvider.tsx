/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🔄 REACT QUERY PROVIDER
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Configuración de React Query para:
 * - Data fetching
 * - Caché automático
 * - Revalidación
 * - Estados de carga
 * - Reintentos automáticos
 * 
 * CONFIGURACIÓN:
 * - staleTime: 5 minutos (datos considerados frescos)
 * - retry: 1 intento (evita múltiples peticiones fallidas)
 * - refetchOnWindowFocus: false (no refetch al cambiar de pestaña)
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import type { ReactNode } from 'react';

// Crear instancia de QueryClient con configuración
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutos
      retry: 1, // 1 reintento en caso de error
      refetchOnWindowFocus: false, // No refetch al cambiar de pestaña
    },
    mutations: {
      retry: 0, // No reintentar mutaciones automáticamente
    },
  },
});

interface QueryProviderProps {
  children: ReactNode;
}

export function QueryProvider({ children }: QueryProviderProps) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* DevTools solo en desarrollo */}
      {import.meta.env.VITE_ENV === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}
