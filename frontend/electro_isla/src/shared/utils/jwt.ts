/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🔐 JWT UTILITIES - Funciones para Validación y Decodificación de JWT
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Proporciona funciones seguras para:
 * - Decodificar JWT
 * - Validar expiración
 * - Extraer claims
 * - Validar estructura
 */

/**
 * Interfaz para el payload del JWT
 */
export interface JWTPayload {
  exp: number;
  iat: number;
  user_id?: number;
  username?: string;
  email?: string;
  rol?: string;
  [key: string]: any;
}

/**
 * Decodifica un JWT y retorna el payload
 * @param token - Token JWT a decodificar
 * @returns Payload decodificado o null si es inválido
 */
export const decodeJWT = (token: string): JWTPayload | null => {
  try {
    // Validar estructura básica del JWT (3 partes separadas por puntos)
    const parts = token.split('.');
    if (parts.length !== 3) {
      console.error('[JWT] Token inválido: estructura incorrecta');
      return null;
    }

    // Decodificar la segunda parte (payload)
    const payload = parts[1];
    const decoded = JSON.parse(atob(payload));
    
    return decoded as JWTPayload;
  } catch (error) {
    console.error('[JWT] Error al decodificar token:', error);
    return null;
  }
};

/**
 * Verifica si un JWT está expirado
 * @param token - Token JWT a verificar
 * @returns true si está expirado, false si es válido
 */
export const isTokenExpired = (token: string): boolean => {
  try {
    const payload = decodeJWT(token);
    
    if (!payload || !payload.exp) {
      console.warn('[JWT] Token sin claim exp');
      return true;
    }

    // exp está en segundos, convertir a milisegundos
    const expirationTime = payload.exp * 1000;
    const currentTime = Date.now();

    // Considerar expirado si faltan menos de 30 segundos
    const bufferTime = 30 * 1000; // 30 segundos de buffer
    const isExpired = currentTime >= (expirationTime - bufferTime);

    if (isExpired) {
      console.debug(`[JWT] Token expirado. Exp: ${new Date(expirationTime).toISOString()}, Ahora: ${new Date(currentTime).toISOString()}`);
    }

    return isExpired;
  } catch (error) {
    console.error('[JWT] Error al verificar expiración:', error);
    return true; // Considerar expirado si hay error
  }
};

/**
 * Obtiene el tiempo restante de un token en segundos
 * @param token - Token JWT
 * @returns Segundos restantes o -1 si está expirado
 */
export const getTokenTimeRemaining = (token: string): number => {
  try {
    const payload = decodeJWT(token);
    
    if (!payload || !payload.exp) {
      return -1;
    }

    const expirationTime = payload.exp * 1000;
    const currentTime = Date.now();
    const remainingMs = expirationTime - currentTime;

    return Math.max(0, Math.floor(remainingMs / 1000));
  } catch (error) {
    console.error('[JWT] Error al calcular tiempo restante:', error);
    return -1;
  }
};

/**
 * Extrae un claim específico del token
 * @param token - Token JWT
 * @param claimName - Nombre del claim a extraer
 * @returns Valor del claim o null
 */
export const getTokenClaim = (token: string, claimName: string): any => {
  try {
    const payload = decodeJWT(token);
    
    if (!payload) {
      return null;
    }

    return payload[claimName] || null;
  } catch (error) {
    console.error(`[JWT] Error al extraer claim ${claimName}:`, error);
    return null;
  }
};

/**
 * Valida si un token es válido (estructura + expiración)
 * @param token - Token JWT a validar
 * @returns true si es válido, false si no
 */
export const isValidToken = (token: string): boolean => {
  if (!token || typeof token !== 'string') {
    console.warn('[JWT] Token vacío o inválido');
    return false;
  }

  // Verificar estructura
  const payload = decodeJWT(token);
  if (!payload) {
    return false;
  }

  // Verificar expiración
  if (isTokenExpired(token)) {
    return false;
  }

  return true;
};

/**
 * Obtiene el rol del usuario desde el token
 * @param token - Token JWT
 * @returns Rol del usuario o null
 */
export const getTokenRole = (token: string): string | null => {
  return getTokenClaim(token, 'rol') as string | null;
};

/**
 * Verifica si el token tiene un rol específico
 * @param token - Token JWT
 * @param requiredRoles - Array de roles permitidos
 * @returns true si el usuario tiene uno de los roles requeridos
 */
export const hasRole = (token: string, requiredRoles: string[]): boolean => {
  const role = getTokenRole(token);
  
  if (!role) {
    console.warn('[JWT] Token sin rol');
    return false;
  }

  return requiredRoles.includes(role);
};

/**
 * Obtiene el ID del usuario desde el token
 * @param token - Token JWT
 * @returns ID del usuario o null
 */
export const getUserId = (token: string): number | null => {
  return getTokenClaim(token, 'user_id') as number | null;
};

/**
 * Obtiene el username del usuario desde el token
 * @param token - Token JWT
 * @returns Username o null
 */
export const getUsername = (token: string): string | null => {
  return getTokenClaim(token, 'username') as string | null;
};
