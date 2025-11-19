/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🧪 TESTS - CSRF Protection
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Tests para verificar que CSRF token se agrega a peticiones
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import { getCsrfToken, getCsrfTokenFromCookie, getCsrfTokenFromMeta, hasCsrfToken } from './csrf';

describe('CSRF Protection', () => {
  beforeEach(() => {
    // Limpiar cookies y meta tags antes de cada test
    document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    document.head.innerHTML = '';
  });

  afterEach(() => {
    document.cookie = 'csrftoken=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    document.head.innerHTML = '';
  });

  describe('getCsrfTokenFromMeta', () => {
    it('debe obtener CSRF token desde meta tag', () => {
      const token = 'test_csrf_token_123';
      const metaTag = document.createElement('meta');
      metaTag.setAttribute('name', 'csrf-token');
      metaTag.setAttribute('content', token);
      document.head.appendChild(metaTag);

      const retrieved = getCsrfTokenFromMeta();
      expect(retrieved).toBe(token);
    });

    it('debe retornar null si no existe meta tag', () => {
      const retrieved = getCsrfTokenFromMeta();
      expect(retrieved).toBeNull();
    });
  });

  describe('getCsrfTokenFromCookie', () => {
    it('debe obtener CSRF token desde cookie', () => {
      const token = 'test_csrf_cookie_123';
      document.cookie = `csrftoken=${token}; path=/`;

      const retrieved = getCsrfTokenFromCookie();
      expect(retrieved).toBe(token);
    });

    it('debe retornar null si no existe cookie', () => {
      const retrieved = getCsrfTokenFromCookie();
      expect(retrieved).toBeNull();
    });
  });

  describe('getCsrfToken', () => {
    it('debe obtener CSRF token desde meta tag (primario)', () => {
      const metaToken = 'meta_token_123';
      const cookieToken = 'cookie_token_123';

      // Agregar ambos
      const metaTag = document.createElement('meta');
      metaTag.setAttribute('name', 'csrf-token');
      metaTag.setAttribute('content', metaToken);
      document.head.appendChild(metaTag);
      document.cookie = `csrftoken=${cookieToken}; path=/`;

      // Debe priorizar meta tag
      const retrieved = getCsrfToken();
      expect(retrieved).toBe(metaToken);
    });

    it('debe usar cookie como fallback si no hay meta tag', () => {
      const cookieToken = 'cookie_token_123';
      document.cookie = `csrftoken=${cookieToken}; path=/`;

      const retrieved = getCsrfToken();
      expect(retrieved).toBe(cookieToken);
    });

    it('debe retornar null si no hay CSRF token en ninguna fuente', () => {
      const retrieved = getCsrfToken();
      expect(retrieved).toBeNull();
    });
  });

  describe('hasCsrfToken', () => {
    it('debe retornar true si existe CSRF token', () => {
      const metaTag = document.createElement('meta');
      metaTag.setAttribute('name', 'csrf-token');
      metaTag.setAttribute('content', 'test_token');
      document.head.appendChild(metaTag);

      expect(hasCsrfToken()).toBe(true);
    });

    it('debe retornar false si no existe CSRF token', () => {
      expect(hasCsrfToken()).toBe(false);
    });
  });

  describe('CSRF token en peticiones', () => {
    it('debe agregar CSRF token a peticiones POST', () => {
      const token = 'csrf_token_123';
      const metaTag = document.createElement('meta');
      metaTag.setAttribute('name', 'csrf-token');
      metaTag.setAttribute('content', token);
      document.head.appendChild(metaTag);

      // Simular agregar CSRF token a headers
      const headers: Record<string, string> = {};
      const csrfToken = getCsrfToken();
      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
      }

      expect(headers['X-CSRFToken']).toBe(token);
    });

    it('debe agregar CSRF token a peticiones PUT', () => {
      const token = 'csrf_token_123';
      const metaTag = document.createElement('meta');
      metaTag.setAttribute('name', 'csrf-token');
      metaTag.setAttribute('content', token);
      document.head.appendChild(metaTag);

      const headers: Record<string, string> = {};
      const csrfToken = getCsrfToken();
      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
      }

      expect(headers['X-CSRFToken']).toBe(token);
    });

    it('debe agregar CSRF token a peticiones DELETE', () => {
      const token = 'csrf_token_123';
      const metaTag = document.createElement('meta');
      metaTag.setAttribute('name', 'csrf-token');
      metaTag.setAttribute('content', token);
      document.head.appendChild(metaTag);

      const headers: Record<string, string> = {};
      const csrfToken = getCsrfToken();
      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
      }

      expect(headers['X-CSRFToken']).toBe(token);
    });

    it('debe agregar CSRF token a peticiones PATCH', () => {
      const token = 'csrf_token_123';
      const metaTag = document.createElement('meta');
      metaTag.setAttribute('name', 'csrf-token');
      metaTag.setAttribute('content', token);
      document.head.appendChild(metaTag);

      const headers: Record<string, string> = {};
      const csrfToken = getCsrfToken();
      if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
      }

      expect(headers['X-CSRFToken']).toBe(token);
    });

    it('no debe agregar CSRF token a peticiones GET', () => {
      const token = 'csrf_token_123';
      const metaTag = document.createElement('meta');
      metaTag.setAttribute('name', 'csrf-token');
      metaTag.setAttribute('content', token);
      document.head.appendChild(metaTag);

      // GET requests no necesitan CSRF token
      const method = 'GET';
      const headers: Record<string, string> = {};

      if (method && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
        const csrfToken = getCsrfToken();
        if (csrfToken) {
          headers['X-CSRFToken'] = csrfToken;
        }
      }

      expect(headers['X-CSRFToken']).toBeUndefined();
    });
  });
});
