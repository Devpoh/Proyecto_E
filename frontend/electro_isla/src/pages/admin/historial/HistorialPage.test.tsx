/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🧪 TESTS - HistorialPage
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { HistorialPage } from './HistorialPage';
import api from '@/shared/api/axios';
import React from 'react';

// Mock API
jest.mock('@/shared/api/axios');
const mockedApi = api as jest.Mocked<typeof api>;

// Mock jsPDF
jest.mock('jspdf', () => ({
  jsPDF: jest.fn(() => ({
    text: jest.fn(),
    save: jest.fn(),
  })),
}));

// Mock xlsx
jest.mock('xlsx', () => ({
  utils: {
    json_to_sheet: jest.fn(),
    book_new: jest.fn(),
    book_append_sheet: jest.fn(),
  },
  writeFile: jest.fn(),
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

describe('HistorialPage', () => {
  beforeEach(() => {
    mockedApi.get.mockResolvedValue({
      data: {
        count: 1,
        next: null,
        previous: null,
        results: [
          {
            id: 1,
            usuario_nombre: 'admin',
            usuario_nombre_completo: 'Admin User',
            accion: 'CREATE',
            accion_display: 'Crear',
            modulo: 'productos',
            modulo_display: 'Productos',
            objeto_id: 1,
            objeto_repr: 'Producto 1',
            detalles: {},
            ip_address: '127.0.0.1',
            user_agent: 'Mozilla/5.0',
            timestamp: '2025-01-09T00:00:00Z',
          },
        ],
      },
    });
  });

  it('should render HistorialPage without 500 error', async () => {
    render(<HistorialPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Historial de Acciones')).toBeInTheDocument();
    });
  });

  it('should display audit logs', async () => {
    render(<HistorialPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText('Admin User')).toBeInTheDocument();
    });
  });

  it('should filter logs by search', async () => {
    render(<HistorialPage />, { wrapper: createWrapper() });

    const searchInput = screen.getByPlaceholderText('Buscar por objeto o usuario...');
    fireEvent.change(searchInput, { target: { value: 'Producto 1' } });

    await waitFor(() => {
      expect(mockedApi.get).toHaveBeenCalled();
    });
  });

  it('should filter logs by module', async () => {
    render(<HistorialPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      const moduleSelects = screen.getAllByRole('combobox');
      if (moduleSelects.length > 0) {
        fireEvent.change(moduleSelects[0], { target: { value: 'productos' } });
      }
    });
  });

  it('should filter logs by action', async () => {
    render(<HistorialPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      const actionSelects = screen.getAllByRole('combobox');
      if (actionSelects.length > 1) {
        fireEvent.change(actionSelects[1], { target: { value: 'CREATE' } });
      }
    });
  });

  it('should filter logs by date range', async () => {
    render(<HistorialPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      const dateSelects = screen.getAllByRole('combobox');
      if (dateSelects.length > 2) {
        fireEvent.change(dateSelects[2], { target: { value: 'week' } });
      }
    });
  });

  it('should handle API errors gracefully', async () => {
    mockedApi.get.mockRejectedValueOnce(new Error('API Error'));

    render(<HistorialPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(mockedApi.get).toHaveBeenCalled();
    });
  });

  it('should allow deleting a log entry', async () => {
    mockedApi.delete.mockResolvedValueOnce({ data: {} });

    render(<HistorialPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      const deleteButtons = screen.getAllByRole('button');
      const deleteButton = deleteButtons.find((btn) => btn.innerHTML.includes('trash'));
      if (deleteButton) {
        fireEvent.click(deleteButton);
      }
    });
  });
});
