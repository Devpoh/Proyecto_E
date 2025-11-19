/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🧪 TESTS - useInvalidateAdminQueries Hook
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useInvalidateAdminQueries } from '../useInvalidateAdminQueries';
import React from 'react';

// Mock QueryClient
const createWrapper = () => {
  const queryClient = new QueryClient();
  return ({ children }: { children: React.ReactNode }) =>
    React.createElement(QueryClientProvider, { client: queryClient }, children);
};

describe('useInvalidateAdminQueries', () => {
  it('should return a function', () => {
    const { result } = renderHook(() => useInvalidateAdminQueries(), {
      wrapper: createWrapper(),
    });

    expect(typeof result.current).toBe('function');
  });

  it('should invalidate default queries when called without arguments', () => {
    const { result } = renderHook(() => useInvalidateAdminQueries(), {
      wrapper: createWrapper(),
    });

    expect(() => result.current()).not.toThrow();
  });

  it('should invalidate additional keys when provided', () => {
    const { result } = renderHook(
      () => useInvalidateAdminQueries({ additionalKeys: ['admin-productos'] }),
      { wrapper: createWrapper() }
    );

    expect(() => result.current()).not.toThrow();
  });

  it('should invalidate custom keys when provided to the function', () => {
    const { result } = renderHook(() => useInvalidateAdminQueries(), {
      wrapper: createWrapper(),
    });

    expect(() => result.current(['custom-key'])).not.toThrow();
  });

  it('should not invalidate default keys when includeDefaults is false', () => {
    const { result } = renderHook(
      () => useInvalidateAdminQueries({ includeDefaults: false, additionalKeys: ['admin-usuarios'] }),
      { wrapper: createWrapper() }
    );

    expect(() => result.current()).not.toThrow();
  });
});
