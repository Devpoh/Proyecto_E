/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🧪 TESTS - usePermissions Hook
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { renderHook } from '@testing-library/react';
import { usePermissions } from '../usePermissions';
import * as useAuthStoreModule from '@/app/store/useAuthStore';

// Mock useAuthStore
jest.mock('@/app/store/useAuthStore');
const mockedUseAuthStore = useAuthStoreModule.useAuthStore as jest.MockedFunction<
  typeof useAuthStoreModule.useAuthStore
>;

describe('usePermissions', () => {
  it('should return false for all permissions when user is not authenticated', () => {
    mockedUseAuthStore.mockReturnValue({
      user: null,
      isAuthenticated: false,
    } as any);

    const { result } = renderHook(() => usePermissions());

    expect(result.current.canEdit).toBe(false);
    expect(result.current.canDelete).toBe(false);
    expect(result.current.isAdmin).toBe(false);
  });

  it('should return correct permissions for admin user', () => {
    mockedUseAuthStore.mockReturnValue({
      user: { id: 1, username: 'admin', rol: 'admin' },
      isAuthenticated: true,
    } as any);

    const { result } = renderHook(() => usePermissions());

    expect(result.current.canEdit).toBe(true);
    expect(result.current.canDelete).toBe(true);
    expect(result.current.isAdmin).toBe(true);
  });

  it('should return correct permissions for trabajador user', () => {
    mockedUseAuthStore.mockReturnValue({
      user: { id: 2, username: 'trabajador', rol: 'trabajador' },
      isAuthenticated: true,
    } as any);

    const { result } = renderHook(() => usePermissions());

    expect(result.current.canEdit).toBe(true);
    expect(result.current.canDelete).toBe(false);
    expect(result.current.isAdmin).toBe(false);
  });

  it('should return correct permissions for mensajero user', () => {
    mockedUseAuthStore.mockReturnValue({
      user: { id: 3, username: 'mensajero', rol: 'mensajero' },
      isAuthenticated: true,
    } as any);

    const { result } = renderHook(() => usePermissions());

    expect(result.current.canEdit).toBe(false);
    expect(result.current.canDelete).toBe(false);
    expect(result.current.isAdmin).toBe(false);
  });

  it('should return correct permissions for cliente user', () => {
    mockedUseAuthStore.mockReturnValue({
      user: { id: 4, username: 'cliente', rol: 'cliente' },
      isAuthenticated: true,
    } as any);

    const { result } = renderHook(() => usePermissions());

    expect(result.current.canEdit).toBe(false);
    expect(result.current.canDelete).toBe(false);
    expect(result.current.isAdmin).toBe(false);
  });
});
