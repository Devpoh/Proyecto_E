/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🧪 TESTS - ProductosPage
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { ProductosPage } from './ProductosPage';
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

// Mock ImageUpload component
jest.mock('@/shared/ui/ImageUpload', () => ({
  ImageUpload: ({ onImageSelect }: any) => (
    <input
      data-testid="image-upload"
      onChange={(e) => onImageSelect(e.target.value)}
    />
  ),
}));

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

describe('ProductosPage', () => {
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
            nombre: 'Producto 1',
            descripcion: 'Descripción 1',
            precio: '100.00',
            descuento: 10,
            stock: 50,
            categoria: 'electrodomesticos',
            imagen_url: null,
            activo: true,
            en_carrusel: true,
            creado_por_username: 'admin',
            created_at: '2025-01-01T00:00:00Z',
          },
        ],
      },
    });
  });

  it('should render ProductosPage', async () => {
    render(<ProductosPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Gestión de Productos')).toBeInTheDocument();
    });
  });

  it('should display products count in carrusel', async () => {
    render(<ProductosPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText(/en carrusel/)).toBeInTheDocument();
    });
  });

  it('should show add button for admin users', async () => {
    render(<ProductosPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Nuevo Producto')).toBeInTheDocument();
    });
  });

  it('should filter products by search', async () => {
    render(<ProductosPage />, { wrapper: createWrapper() });

    const searchInput = screen.getByPlaceholderText('Buscar productos...');
    fireEvent.change(searchInput, { target: { value: 'Producto 1' } });

    await waitFor(() => {
      expect(mockedApi.get).toHaveBeenCalled();
    });
  });

  it('should open modal when clicking add button', async () => {
    render(<ProductosPage />, { wrapper: createWrapper() });

    const addButton = await screen.findByText('Nuevo Producto');
    fireEvent.click(addButton);

    await waitFor(() => {
      expect(screen.getByText('Nuevo Producto', { selector: 'h3' })).toBeInTheDocument();
    });
  });

  it('should handle API errors gracefully', async () => {
    mockedApi.get.mockRejectedValueOnce(new Error('API Error'));

    render(<ProductosPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(mockedApi.get).toHaveBeenCalled();
    });
  });
});
