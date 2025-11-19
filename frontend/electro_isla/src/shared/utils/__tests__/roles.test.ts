/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🧪 TESTS - Roles Utilities
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { getRolLabel, getRolBadgeClass, getRolColor, ROL_CONFIG } from '../roles';

describe('Roles Utilities', () => {
  describe('getRolLabel', () => {
    it('should return correct label for admin role', () => {
      expect(getRolLabel('admin')).toBe('Administrador');
    });

    it('should return correct label for trabajador role', () => {
      expect(getRolLabel('trabajador')).toBe('Trabajador');
    });

    it('should return correct label for mensajero role', () => {
      expect(getRolLabel('mensajero')).toBe('Mensajero');
    });

    it('should return correct label for cliente role', () => {
      expect(getRolLabel('cliente')).toBe('Cliente');
    });

    it('should return default label for unknown role', () => {
      expect(getRolLabel('unknown')).toBe('Cliente');
    });
  });

  describe('getRolBadgeClass', () => {
    it('should return correct badge class for admin role', () => {
      expect(getRolBadgeClass('admin')).toBe('badge-admin');
    });

    it('should return correct badge class for trabajador role', () => {
      expect(getRolBadgeClass('trabajador')).toBe('badge-trabajador');
    });

    it('should return correct badge class for mensajero role', () => {
      expect(getRolBadgeClass('mensajero')).toBe('badge-mensajero');
    });

    it('should return correct badge class for cliente role', () => {
      expect(getRolBadgeClass('cliente')).toBe('badge-cliente');
    });

    it('should return default badge class for unknown role', () => {
      expect(getRolBadgeClass('unknown')).toBe('badge-cliente');
    });
  });

  describe('getRolColor', () => {
    it('should return correct color for admin role', () => {
      expect(getRolColor('admin')).toBe('#ef4444');
    });

    it('should return correct color for trabajador role', () => {
      expect(getRolColor('trabajador')).toBe('#3b82f6');
    });

    it('should return correct color for mensajero role', () => {
      expect(getRolColor('mensajero')).toBe('#f59e0b');
    });

    it('should return correct color for cliente role', () => {
      expect(getRolColor('cliente')).toBe('#10b981');
    });

    it('should return default color for unknown role', () => {
      expect(getRolColor('unknown')).toBe('#10b981');
    });
  });

  describe('ROL_CONFIG', () => {
    it('should have all required roles', () => {
      expect(ROL_CONFIG).toHaveProperty('admin');
      expect(ROL_CONFIG).toHaveProperty('trabajador');
      expect(ROL_CONFIG).toHaveProperty('mensajero');
      expect(ROL_CONFIG).toHaveProperty('cliente');
    });

    it('should have correct structure for each role', () => {
      Object.values(ROL_CONFIG).forEach((role: any) => {
        expect(role).toHaveProperty('label');
        expect(role).toHaveProperty('class');
        expect(role).toHaveProperty('color');
        expect(role).toHaveProperty('icon');
        expect(role).toHaveProperty('description');
        expect(typeof role.label).toBe('string');
        expect(typeof role.class).toBe('string');
        expect(typeof role.color).toBe('string');
        expect(typeof role.icon).toBe('string');
        expect(typeof role.description).toBe('string');
      });
    });
  });
});
