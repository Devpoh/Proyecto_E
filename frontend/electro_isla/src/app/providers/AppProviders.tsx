/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎁 APP PROVIDERS - Wrapper de Todos los Providers
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Envuelve la aplicación con todos los providers necesarios:
 * - QueryProvider: React Query para data fetching
 * - Toaster: Notificaciones toast
 * 
 * CONFIGURACIÓN DE TOAST:
 * - Posición: top-right
 * - Duración: 3 segundos
 * - Estilos: Usando variables CSS de la paleta oficial
 * - Colores: success (verde), error (rojo)
 */

import type { ReactNode } from 'react';
import { QueryProvider } from './QueryProvider';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from '@/contexts/AuthContext';
import { CartProvider } from '@/contexts/CartContext';

interface AppProvidersProps {
  children: ReactNode;
}

export function AppProviders({ children }: AppProvidersProps) {
  return (
    <QueryProvider>
      <AuthProvider>
        <CartProvider>
          {children}
          
          {/* Toast Notifications */}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 3000,
              style: {
                background: 'var(--color-fondo)',
                color: 'var(--color-texto-principal)',
                borderRadius: 'var(--radio-borde-lg)',
                boxShadow: 'var(--sombra-lg)',
                padding: 'var(--espaciado-md)',
                fontSize: 'var(--texto-base)',
                fontWeight: 'var(--peso-medio)',
              },
              success: {
                iconTheme: {
                  primary: 'var(--color-exito)',
                  secondary: 'white',
                },
              },
              error: {
                iconTheme: {
                  primary: 'var(--color-peligro)',
                  secondary: 'white',
                },
              },
            }}
          />
        </CartProvider>
      </AuthProvider>
    </QueryProvider>
  );
}
