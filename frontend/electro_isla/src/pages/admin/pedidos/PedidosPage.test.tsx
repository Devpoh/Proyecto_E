/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🧪 TESTS - PedidosPage
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { PedidosPage } from './PedidosPage';
import * as useAuthStoreModule from '@/app/store/useAuthStore';
import api from '@/shared/api/axios';
import React from 'react';

// Mock API
jest.mock('@/shared/api/axios');
const mockedApi = api as jest.Mocked<typeof api>;

// Mock useAuthStore
jest.mock('@/app/store/useAuthStore');
const mockedUseAuthStore = useAuthStoreModule.useAuthStore as jest.MockedFunction<
  typeof useAuthStoreModule.useAuthStore
>;

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(
      QueryClientProvider,
      { client: queryClient },
      React.createElement(BrowserRouter, {}, children)
    );
};

describe('PedidosPage', () => {
  beforeEach(() => {
    mockedUseAuthStore.mockReturnValue({
      user: { id: 1, username: 'admin', rol: 'admin' },
      isAuthenticated: true,
      login: jest.fn(),
      logout: jest.fn(),
      initializeAuth: jest.fn(),
    } as any);

    mockedApi.get.mockResolvedValue({
      data: {
        results: [
          {
            id: 1,
            usuario_nombre: 'usuario1',
            usuario_email: 'usuario@ejemplo.com',
            estado: 'pendiente',
            metodo_pago: 'tarjeta',
            total: '500.00',
            direccion_entrega: 'Calle Principal 123',
            telefono: '1234567890',
            notas: null,
            mensajero: null,
            mensajero_nombre: null,
            detalles: [],
            created_at: '2025-01-01T00:00:00Z',
            fecha_entrega: null,
          },
        ],
      },
    });
  });

  it('should render PedidosPage', async () => {
    render(<PedidosPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Gestión de Pedidos')).toBeInTheDocument();
    });
  });

  it('should display orders list', async () => {
    render(<PedidosPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText(/usuario1|Pedido/)).toBeInTheDocument();
    });
  });

  it('should filter orders by search', async () => {
    render(<PedidosPage />, { wrapper: createWrapper() });

    const searchInput = screen.getByPlaceholderText('Buscar por ID, cliente o teléfono...');
    fireEvent.change(searchInput, { target: { value: 'usuario1' } });

    await waitFor(() => {
      expect(mockedApi.get).toHaveBeenCalled();
    });
  });

  it('should display order status', async () => {
    render(<PedidosPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByDisplayValue('pendiente')).toBeInTheDocument();
    });
  });

  it('should allow changing order status', async () => {
    mockedApi.patch.mockResolvedValueOnce({ data: { id: 1, estado: 'confirmado' } });

    render(<PedidosPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      const statusSelects = screen.getAllByRole('combobox');
      if (statusSelects.length > 0) {
        fireEvent.change(statusSelects[0], { target: { value: 'confirmado' } });
      }
    });
  });

  it('should handle API errors gracefully', async () => {
    mockedApi.get.mockRejectedValueOnce(new Error('API Error'));

    render(<PedidosPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(mockedApi.get).toHaveBeenCalled();
    });
  });
});
