/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🛡️ CSRF UTILITIES - Protección contra ataques CSRF
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Proporciona funciones para:
 * - Obtener CSRF token desde cookies
 * - Obtener CSRF token desde meta tags
 * - Validar presencia de CSRF token
 */

/**
 * Obtiene el CSRF token desde las cookies
 * @returns Token CSRF o null si no existe
 */
export const getCsrfTokenFromCookie = (): string | null => {
  try {
    const name = 'csrftoken';
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    
    if (parts.length === 2) {
      const token = parts.pop()?.split(';').shift();
      if (token) {
        console.debug('[CSRF] Token obtenido desde cookie');
        return token;
      }
    }
    
    console.warn('[CSRF] Token no encontrado en cookies');
    return null;
  } catch (error) {
    console.error('[CSRF] Error al obtener token desde cookie:', error);
    return null;
  }
};

/**
 * Obtiene el CSRF token desde meta tags
 * @returns Token CSRF o null si no existe
 */
export const getCsrfTokenFromMeta = (): string | null => {
  try {
    const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
    
    if (token) {
      console.debug('[CSRF] Token obtenido desde meta tag');
      return token;
    }
    
    return null;
  } catch (error) {
    console.error('[CSRF] Error al obtener token desde meta tag:', error);
    return null;
  }
};

/**
 * Obtiene el CSRF token desde cualquier fuente disponible
 * Intenta primero meta tags, luego cookies
 * @returns Token CSRF o null si no existe
 */
export const getCsrfToken = (): string | null => {
  // Intentar obtener desde meta tag primero (más confiable)
  let token = getCsrfTokenFromMeta();
  
  // Fallback a cookie si no está en meta
  if (!token) {
    token = getCsrfTokenFromCookie();
  }
  
  if (!token) {
    console.warn('[CSRF] No se encontró CSRF token en ninguna fuente');
  }
  
  return token;
};

/**
 * Valida si existe un CSRF token
 * @returns true si existe token, false si no
 */
export const hasCsrfToken = (): boolean => {
  return getCsrfToken() !== null;
};

/**
 * Obtiene los headers con CSRF token para peticiones POST/PUT/DELETE
 * @returns Objeto con headers CSRF
 */
export const getCsrfHeaders = (): Record<string, string> => {
  const token = getCsrfToken();
  
  if (!token) {
    console.warn('[CSRF] No hay token CSRF disponible para headers');
    return {};
  }
  
  return {
    'X-CSRFToken': token,
  };
};
