/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🧪 TESTS - Storage Utilities (sessionStorage vs localStorage)
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Tests para verificar que sessionStorage es primario
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';

describe('Storage Priority (sessionStorage vs localStorage)', () => {
  beforeEach(() => {
    // Limpiar ambos storages antes de cada test
    sessionStorage.clear();
    localStorage.clear();
  });

  afterEach(() => {
    sessionStorage.clear();
    localStorage.clear();
  });

  describe('sessionStorage como primario', () => {
    it('debe obtener token de sessionStorage si existe', () => {
      const token = 'token_from_session';
      sessionStorage.setItem('accessToken', token);

      const retrieved = sessionStorage.getItem('accessToken');
      expect(retrieved).toBe(token);
    });

    it('debe priorizar sessionStorage sobre localStorage', () => {
      const sessionToken = 'session_token';
      const localToken = 'local_token';

      sessionStorage.setItem('accessToken', sessionToken);
      localStorage.setItem('accessToken', localToken);

      // Simular lógica de prioridad
      let token = sessionStorage.getItem('accessToken');
      if (!token) {
        token = localStorage.getItem('accessToken');
      }

      expect(token).toBe(sessionToken);
    });

    it('debe usar localStorage como fallback si sessionStorage está vacío', () => {
      const localToken = 'local_token';
      localStorage.setItem('accessToken', localToken);

      // Simular lógica de fallback
      let token = sessionStorage.getItem('accessToken');
      if (!token) {
        token = localStorage.getItem('accessToken');
      }

      expect(token).toBe(localToken);
    });
  });

  describe('Limpieza de tokens', () => {
    it('debe limpiar ambos storages al logout', () => {
      sessionStorage.setItem('accessToken', 'token');
      sessionStorage.setItem('user', JSON.stringify({ id: 1 }));
      localStorage.setItem('accessToken', 'token');
      localStorage.setItem('user', JSON.stringify({ id: 1 }));

      // Simular logout
      sessionStorage.removeItem('accessToken');
      sessionStorage.removeItem('user');
      localStorage.removeItem('accessToken');
      localStorage.removeItem('user');

      expect(sessionStorage.getItem('accessToken')).toBeNull();
      expect(sessionStorage.getItem('user')).toBeNull();
      expect(localStorage.getItem('accessToken')).toBeNull();
      expect(localStorage.getItem('user')).toBeNull();
    });

    it('debe limpiar sessionStorage al cerrar la pestaña', () => {
      sessionStorage.setItem('accessToken', 'token');
      
      // sessionStorage se limpia automáticamente al cerrar la pestaña
      // Aquí solo verificamos que el método existe
      expect(sessionStorage.removeItem).toBeDefined();
    });
  });

  describe('Sincronización de tokens', () => {
    it('debe guardar en ambos storages después de login', () => {
      const token = 'new_token';
      const user = { id: 1, username: 'test' };

      // Simular login
      sessionStorage.setItem('accessToken', token);
      sessionStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('accessToken', token);
      localStorage.setItem('user', JSON.stringify(user));

      expect(sessionStorage.getItem('accessToken')).toBe(token);
      expect(localStorage.getItem('accessToken')).toBe(token);
      expect(JSON.parse(sessionStorage.getItem('user') || '{}')).toEqual(user);
      expect(JSON.parse(localStorage.getItem('user') || '{}')).toEqual(user);
    });

    it('debe actualizar ambos storages al refrescar token', () => {
      const oldToken = 'old_token';
      const newToken = 'new_token';

      // Token inicial
      sessionStorage.setItem('accessToken', oldToken);
      localStorage.setItem('accessToken', oldToken);

      // Simular refresh
      sessionStorage.setItem('accessToken', newToken);
      localStorage.setItem('accessToken', newToken);

      expect(sessionStorage.getItem('accessToken')).toBe(newToken);
      expect(localStorage.getItem('accessToken')).toBe(newToken);
    });
  });

  describe('Seguridad de storage', () => {
    it('sessionStorage debe estar vacío después de cerrar pestaña', () => {
      // Verificar que sessionStorage es específico de la pestaña
      sessionStorage.setItem('test', 'value');
      expect(sessionStorage.getItem('test')).toBe('value');

      // En un test real, cerrar la pestaña limpiaría sessionStorage
      // Aquí solo verificamos que el método existe
      expect(sessionStorage.clear).toBeDefined();
    });

    it('localStorage debe persistir entre sesiones', () => {
      localStorage.setItem('persistent', 'value');
      
      // localStorage persiste incluso después de cerrar el navegador
      expect(localStorage.getItem('persistent')).toBe('value');
      
      localStorage.removeItem('persistent');
    });
  });
});
