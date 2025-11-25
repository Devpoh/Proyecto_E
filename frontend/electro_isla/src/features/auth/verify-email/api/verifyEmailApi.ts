/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🌐 API - Verify Email Service
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import api from '@/shared/api/axios';

interface VerifyEmailPayload {
  email: string;
  codigo: string;
}

interface VerifyEmailResponse {
  message: string;
  detail: string;
  email: string;
  username: string;
}

interface VerificationStatus {
  email: string;
  is_verified: boolean;
  username: string;
  has_pending_verification: boolean;
  verification_expires_at?: string;
  is_expired?: boolean;
  can_resend?: boolean;
  resend_count?: number;
  max_resends?: number;
  failed_attempts?: number;
  max_attempts?: number;
  resend_available_in_seconds?: number;
}

interface ResendVerificationResponse {
  message: string;
  detail: string;
  expires_in_minutes: number;
}

/**
 * Verificar email con código
 */
export const verifyEmail = async (payload: VerifyEmailPayload): Promise<VerifyEmailResponse> => {
  try {
    const response = await api.post<VerifyEmailResponse>('/auth/verify-email/', payload);
    return response.data;
  } catch (error: any) {
    throw error;
  }
};

/**
 * Obtener estado de verificación
 */
export const getVerificationStatus = async (email: string): Promise<VerificationStatus> => {
  try {
    const response = await api.get<VerificationStatus>('/auth/verification-status/', {
      params: { email }
    });
    return response.data;
  } catch (error: any) {
    throw error;
  }
};

/**
 * Reenviar código de verificación
 */
export const resendVerificationCode = async (email: string): Promise<ResendVerificationResponse> => {
  try {
    const response = await api.post<ResendVerificationResponse>('/auth/resend-verification/', {
      email
    });
    return response.data;
  } catch (error: any) {
    throw error;
  }
};
