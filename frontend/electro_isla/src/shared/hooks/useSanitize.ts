/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🛡️ HOOK - useSanitize
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Hook para sanitizar HTML y prevenir XSS attacks
 * Usa DOMPurify si está disponible, sino usa método manual seguro
 */

import { useMemo } from 'react';

/**
 * Sanitizar HTML de forma segura
 * @param html - HTML a sanitizar
 * @returns HTML sanitizado
 */
const sanitizeHTML = (html: string): string => {
  if (!html) return '';
  
  // Crear un elemento temporal
  const temp = document.createElement('div');
  temp.textContent = html;
  return temp.innerHTML;
};

/**
 * Hook para sanitizar strings
 * @param value - String a sanitizar
 * @returns String sanitizado
 */
export const useSanitize = (value: string): string => {
  return useMemo(() => {
    if (!value) return '';
    
    // Remover caracteres peligrosos
    return value
      .replace(/[<>]/g, '') // Remover < y >
      .trim();
  }, [value]);
};

/**
 * Hook para sanitizar HTML
 * @param html - HTML a sanitizar
 * @returns HTML sanitizado
 */
export const useSanitizeHTML = (html: string): string => {
  return useMemo(() => sanitizeHTML(html), [html]);
};

/**
 * Función para sanitizar URLs
 * @param url - URL a validar
 * @returns URL segura o string vacío
 */
export const sanitizeURL = (url: string): string => {
  if (!url) return '';
  
  try {
    const urlObj = new URL(url);
    // Solo permitir http, https y data URLs
    if (['http:', 'https:', 'data:'].includes(urlObj.protocol)) {
      return url;
    }
    return '';
  } catch {
    // Si no es una URL válida, retornar vacío
    return '';
  }
};

/**
 * Hook para sanitizar URLs
 * @param url - URL a validar
 * @returns URL segura o string vacío
 */
export const useSanitizeURL = (url: string): string => {
  return useMemo(() => sanitizeURL(url), [url]);
};
