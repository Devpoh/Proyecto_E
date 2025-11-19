/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🧪 TESTS - AdminModal Component
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { AdminModal } from './AdminModal';

describe('AdminModal', () => {
  const mockOnClose = jest.fn();
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should not render when isOpen is false', () => {
    render(
      <AdminModal
        isOpen={false}
        title="Test Modal"
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
      >
        <div>Modal Content</div>
      </AdminModal>
    );

    expect(screen.queryByText('Test Modal')).not.toBeInTheDocument();
  });

  it('should render when isOpen is true', () => {
    render(
      <AdminModal
        isOpen={true}
        title="Test Modal"
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
      >
        <div>Modal Content</div>
      </AdminModal>
    );

    expect(screen.getByText('Test Modal')).toBeInTheDocument();
    expect(screen.getByText('Modal Content')).toBeInTheDocument();
  });

  it('should call onClose when close button is clicked', () => {
    render(
      <AdminModal
        isOpen={true}
        title="Test Modal"
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
      >
        <div>Modal Content</div>
      </AdminModal>
    );

    const closeButton = screen.getByRole('button', { name: /close|cerrar/i });
    fireEvent.click(closeButton);

    expect(mockOnClose).toHaveBeenCalled();
  });

  it('should call onSubmit when submit button is clicked', () => {
    render(
      <AdminModal
        isOpen={true}
        title="Test Modal"
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
      >
        <div>Modal Content</div>
      </AdminModal>
    );

    const submitButton = screen.getByRole('button', { name: /submit|guardar/i });
    fireEvent.click(submitButton);

    expect(mockOnSubmit).toHaveBeenCalled();
  });

  it('should display loading state when isLoading is true', () => {
    render(
      <AdminModal
        isOpen={true}
        title="Test Modal"
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
        isLoading={true}
      >
        <div>Modal Content</div>
      </AdminModal>
    );

    const submitButton = screen.getByRole('button', { name: /procesando|guardando/i });
    expect(submitButton).toBeDisabled();
  });

  it('should display custom submit button label', () => {
    render(
      <AdminModal
        isOpen={true}
        title="Test Modal"
        onClose={mockOnClose}
        onSubmit={mockOnSubmit}
        submitLabel="Crear"
      >
        <div>Modal Content</div>
      </AdminModal>
    );

    expect(screen.getByText('Crear')).toBeInTheDocument();
  });
});
