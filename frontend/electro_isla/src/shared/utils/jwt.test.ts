/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🧪 TESTS - JWT Utilities
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Tests para validación de JWT y exp claim
 */

import { describe, it, expect } from '@jest/globals';
import {
  decodeJWT,
  isTokenExpired,
  getTokenTimeRemaining,
  isValidToken,
  getTokenRole,
  hasRole,
  getUserId,
  getUsername,
} from './jwt';

// Mock tokens para testing
const createMockToken = (expiresIn: number = 900): string => {
  const now = Math.floor(Date.now() / 1000);
  const payload = {
    user_id: 1,
    username: 'test_user',
    email: 'test@example.com',
    rol: 'cliente',
    iat: now,
    exp: now + expiresIn,
    type: 'access',
  };

  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const body = btoa(JSON.stringify(payload));
  const signature = 'mock_signature';

  return `${header}.${body}.${signature}`;
};

describe('JWT Utilities', () => {
  describe('decodeJWT', () => {
    it('debe decodificar un JWT válido', () => {
      const token = createMockToken();
      const payload = decodeJWT(token);

      expect(payload).toBeDefined();
      expect(payload?.user_id).toBe(1);
      expect(payload?.username).toBe('test_user');
      expect(payload?.rol).toBe('cliente');
    });

    it('debe retornar null para JWT inválido', () => {
      const invalidToken = 'invalid.token';
      const payload = decodeJWT(invalidToken);

      expect(payload).toBeNull();
    });

    it('debe retornar null para JWT con estructura incorrecta', () => {
      const invalidToken = 'only.two.parts.extra';
      const payload = decodeJWT(invalidToken);

      expect(payload).toBeNull();
    });
  });

  describe('isTokenExpired', () => {
    it('debe retornar false para token válido', () => {
      const token = createMockToken(900); // 15 minutos
      expect(isTokenExpired(token)).toBe(false);
    });

    it('debe retornar true para token expirado', () => {
      const token = createMockToken(-100); // Expirado hace 100 segundos
      expect(isTokenExpired(token)).toBe(true);
    });

    it('debe retornar true si faltan menos de 30 segundos', () => {
      const token = createMockToken(20); // Expira en 20 segundos
      expect(isTokenExpired(token)).toBe(true);
    });

    it('debe retornar true para token sin exp claim', () => {
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const body = btoa(JSON.stringify({ user_id: 1, username: 'test' }));
      const invalidToken = `${header}.${body}.signature`;

      expect(isTokenExpired(invalidToken)).toBe(true);
    });
  });

  describe('getTokenTimeRemaining', () => {
    it('debe retornar segundos restantes correctamente', () => {
      const token = createMockToken(600); // 10 minutos
      const remaining = getTokenTimeRemaining(token);

      expect(remaining).toBeGreaterThan(0);
      expect(remaining).toBeLessThanOrEqual(600);
    });

    it('debe retornar -1 para token sin exp claim', () => {
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const body = btoa(JSON.stringify({ user_id: 1 }));
      const invalidToken = `${header}.${body}.signature`;

      expect(getTokenTimeRemaining(invalidToken)).toBe(-1);
    });

    it('debe retornar 0 para token expirado', () => {
      const token = createMockToken(-100);
      const remaining = getTokenTimeRemaining(token);

      expect(remaining).toBe(0);
    });
  });

  describe('isValidToken', () => {
    it('debe retornar true para token válido', () => {
      const token = createMockToken(900);
      expect(isValidToken(token)).toBe(true);
    });

    it('debe retornar false para token expirado', () => {
      const token = createMockToken(-100);
      expect(isValidToken(token)).toBe(false);
    });

    it('debe retornar false para token vacío', () => {
      expect(isValidToken('')).toBe(false);
    });

    it('debe retornar false para token null', () => {
      expect(isValidToken(null as any)).toBe(false);
    });
  });

  describe('getTokenRole', () => {
    it('debe extraer el rol correctamente', () => {
      const token = createMockToken();
      const role = getTokenRole(token);

      expect(role).toBe('cliente');
    });

    it('debe retornar null si no hay rol', () => {
      const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
      const body = btoa(JSON.stringify({ user_id: 1, username: 'test' }));
      const tokenWithoutRole = `${header}.${body}.signature`;

      expect(getTokenRole(tokenWithoutRole)).toBeNull();
    });
  });

  describe('hasRole', () => {
    it('debe retornar true si el usuario tiene el rol requerido', () => {
      const token = createMockToken();
      expect(hasRole(token, ['cliente'])).toBe(true);
    });

    it('debe retornar true si el usuario tiene uno de los roles requeridos', () => {
      const token = createMockToken();
      expect(hasRole(token, ['admin', 'cliente', 'trabajador'])).toBe(true);
    });

    it('debe retornar false si el usuario no tiene el rol requerido', () => {
      const token = createMockToken();
      expect(hasRole(token, ['admin', 'trabajador'])).toBe(false);
    });
  });

  describe('getUserId', () => {
    it('debe extraer el user_id correctamente', () => {
      const token = createMockToken();
      const userId = getUserId(token);

      expect(userId).toBe(1);
    });
  });

  describe('getUsername', () => {
    it('debe extraer el username correctamente', () => {
      const token = createMockToken();
      const username = getUsername(token);

      expect(username).toBe('test_user');
    });
  });
});
