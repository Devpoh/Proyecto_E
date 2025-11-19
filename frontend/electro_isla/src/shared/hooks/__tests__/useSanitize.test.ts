/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🧪 TESTS - useSanitize Hook
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { renderHook } from '@testing-library/react';
import { useSanitize, useSanitizeHTML, sanitizeURL, useSanitizeURL } from '../useSanitize';

describe('useSanitize', () => {
  it('should remove dangerous characters', () => {
    const { result } = renderHook(() => useSanitize('<script>alert("xss")</script>'));
    expect(result.current).not.toContain('<');
    expect(result.current).not.toContain('>');
  });

  it('should trim whitespace', () => {
    const { result } = renderHook(() => useSanitize('  hello world  '));
    expect(result.current).toBe('hello world');
  });

  it('should return empty string for empty input', () => {
    const { result } = renderHook(() => useSanitize(''));
    expect(result.current).toBe('');
  });

  it('should handle normal text', () => {
    const { result } = renderHook(() => useSanitize('Hello World'));
    expect(result.current).toBe('Hello World');
  });
});

describe('useSanitizeHTML', () => {
  it('should sanitize HTML content', () => {
    const { result } = renderHook(() => useSanitizeHTML('<p>Hello</p>'));
    expect(result.current).toBeDefined();
  });

  it('should return empty string for empty input', () => {
    const { result } = renderHook(() => useSanitizeHTML(''));
    expect(result.current).toBe('');
  });
});

describe('sanitizeURL', () => {
  it('should allow http URLs', () => {
    const result = sanitizeURL('http://example.com');
    expect(result).toBe('http://example.com');
  });

  it('should allow https URLs', () => {
    const result = sanitizeURL('https://example.com');
    expect(result).toBe('https://example.com');
  });

  it('should allow data URLs', () => {
    const result = sanitizeURL('data:image/png;base64,iVBORw0KGgo=');
    expect(result).toBe('data:image/png;base64,iVBORw0KGgo=');
  });

  it('should reject javascript URLs', () => {
    const result = sanitizeURL('javascript:alert("xss")');
    expect(result).toBe('');
  });

  it('should reject invalid URLs', () => {
    const result = sanitizeURL('not a url');
    expect(result).toBe('');
  });

  it('should return empty string for empty input', () => {
    const result = sanitizeURL('');
    expect(result).toBe('');
  });
});

describe('useSanitizeURL', () => {
  it('should sanitize URLs', () => {
    const { result } = renderHook(() => useSanitizeURL('https://example.com'));
    expect(result.current).toBe('https://example.com');
  });

  it('should reject dangerous URLs', () => {
    const { result } = renderHook(() => useSanitizeURL('javascript:alert("xss")'));
    expect(result.current).toBe('');
  });
});
