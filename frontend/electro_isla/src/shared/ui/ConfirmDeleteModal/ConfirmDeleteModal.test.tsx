/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🧪 TESTS - ConfirmDeleteModal Component
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { render, screen, fireEvent } from '@testing-library/react';
import { ConfirmDeleteModal } from './ConfirmDeleteModal';

describe('ConfirmDeleteModal', () => {
  const mockOnConfirm = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should not render when isOpen is false', () => {
    render(
      <ConfirmDeleteModal
        isOpen={false}
        itemName="Delete Item"
        description="Are you sure?"
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.queryByText(/Delete Item|Are you sure/)).not.toBeInTheDocument();
  });

  it('should render when isOpen is true', () => {
    render(
      <ConfirmDeleteModal
        isOpen={true}
        itemName="Delete Item"
        description="Are you sure?"
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    expect(screen.getByText('Delete Item')).toBeInTheDocument();
    expect(screen.getByText('Are you sure?')).toBeInTheDocument();
  });

  it('should call onConfirm when confirm button is clicked', () => {
    render(
      <ConfirmDeleteModal
        isOpen={true}
        itemName="Delete Item"
        description="Are you sure?"
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    const confirmButton = screen.getByRole('button', { name: /confirm|eliminar|delete/i });
    fireEvent.click(confirmButton);

    expect(mockOnConfirm).toHaveBeenCalled();
  });

  it('should call onCancel when cancel button is clicked', () => {
    render(
      <ConfirmDeleteModal
        isOpen={true}
        itemName="Delete Item"
        description="Are you sure?"
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    const cancelButton = screen.getByRole('button', { name: /cancel|cancelar/i });
    fireEvent.click(cancelButton);

    expect(mockOnCancel).toHaveBeenCalled();
  });

  it('should display loading state when isLoading is true', () => {
    render(
      <ConfirmDeleteModal
        isOpen={true}
        itemName="Delete Item"
        description="Are you sure?"
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
        isLoading={true}
      />
    );

    const confirmButton = screen.getByRole('button', { name: /eliminando|procesando/i });
    expect(confirmButton).toBeDisabled();
  });

  it('should display warning icon', () => {
    render(
      <ConfirmDeleteModal
        isOpen={true}
        itemName="Delete Item"
        description="Are you sure?"
        onConfirm={mockOnConfirm}
        onCancel={mockOnCancel}
      />
    );

    const icon = document.querySelector('.confirm-delete-icon svg');
    expect(icon).toBeInTheDocument();
  });
});
