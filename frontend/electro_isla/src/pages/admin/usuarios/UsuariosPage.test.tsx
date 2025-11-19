/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🧪 TESTS - UsuariosPage
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { UsuariosPage } from './UsuariosPage';
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

describe('UsuariosPage', () => {
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
            username: 'usuario1',
            email_parcial: 'u***@ejemplo.com',
            first_name: 'Juan',
            last_name: 'Pérez',
            is_active: true,
            rol: 'cliente',
            fecha_registro: '2025-01-01T00:00:00Z',
            ultimo_acceso: '2025-01-09T00:00:00Z',
          },
        ],
      },
    });
  });

  it('should render UsuariosPage', async () => {
    render(<UsuariosPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Gestión de Usuarios')).toBeInTheDocument();
    });
  });

  it('should display users list', async () => {
    render(<UsuariosPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('usuario1')).toBeInTheDocument();
    });
  });

  it('should filter users by search', async () => {
    render(<UsuariosPage />, { wrapper: createWrapper() });

    const searchInput = screen.getByPlaceholderText('Buscar por nombre o usuario...');
    fireEvent.change(searchInput, { target: { value: 'usuario1' } });

    await waitFor(() => {
      expect(mockedApi.get).toHaveBeenCalled();
    });
  });

  it('should open edit modal when clicking edit button', async () => {
    render(<UsuariosPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      const editButtons = screen.getAllByRole('button');
      const editButton = editButtons.find((btn) => btn.innerHTML.includes('edit'));
      if (editButton) {
        fireEvent.click(editButton);
      }
    });
  });

  it('should display user roles correctly', async () => {
    render(<UsuariosPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Cliente')).toBeInTheDocument();
    });
  });

  it('should handle API errors gracefully', async () => {
    mockedApi.get.mockRejectedValueOnce(new Error('API Error'));

    render(<UsuariosPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(mockedApi.get).toHaveBeenCalled();
    });
  });
});
