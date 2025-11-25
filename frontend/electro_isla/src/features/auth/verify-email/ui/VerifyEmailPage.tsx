/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📧 PÁGINA - Verificación de Email
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Página para verificar el email con código de 6 dígitos.
 * 
 * Características:
 * - Input para código de 6 dígitos
 * - Temporizador de cuenta regresiva (5 minutos)
 * - Botón "Reenviar Código" con cooldown (60 segundos)
 * - Contador de reenvíos restantes (máximo 3)
 * - Mensajes de error para códigos inválidos/expirados
 * - Redirección a login después de verificación exitosa
 */

import { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FiMail, FiRefreshCw, FiCheckCircle, FiAlertCircle, FiClock, FiX, FiArrowLeft } from 'react-icons/fi';
import { verifyEmail, getVerificationStatus, resendVerificationCode } from '../api/verifyEmailApi';
import './VerifyEmailPage.css';

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

const VerifyEmailPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Obtener email de URL params o state
  const searchParams = new URLSearchParams(location.search);
  const emailFromUrl = searchParams.get('email');
  const email = emailFromUrl || location.state?.email || '';

  // Estados
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [status, setStatus] = useState<VerificationStatus | null>(null);
  const [timeLeft, setTimeLeft] = useState(300); // 5 minutos en segundos
  const [resendCooldown, setResendCooldown] = useState(0);

  // Referencias para los inputs
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Cargar estado de verificación
  useEffect(() => {
    if (email) {
      // Verificar si ya se alcanzó el límite de reenvíos
      const limitReached = localStorage.getItem(`resend_limit_reached_${email}`);
      if (limitReached === 'true') {
        setError('Has alcanzado el límite de reenvíos. Por favor, registrate de nuevo.');
        setTimeout(() => setError(''), 15000);
        return;
      }
      
      // Intentar cargar estado desde localStorage primero
      const savedStatus = localStorage.getItem(`verification_status_${email}`);
      if (savedStatus) {
        try {
          setStatus(JSON.parse(savedStatus));
        } catch (e) {
          console.error('Error al parsear estado guardado:', e);
        }
      }
      
      fetchVerificationStatus();
    } else {
      navigate('/auth/register');
    }
  }, [email]);

  // Temporizador de expiración
  useEffect(() => {
    if (status?.verification_expires_at) {
      const expiresAt = new Date(status.verification_expires_at).getTime();
      const now = Date.now();
      const secondsLeft = Math.max(0, Math.floor((expiresAt - now) / 1000));
      setTimeLeft(secondsLeft);

      const timer = setInterval(() => {
        const now = Date.now();
        const secondsLeft = Math.max(0, Math.floor((expiresAt - now) / 1000));
        setTimeLeft(secondsLeft);

        if (secondsLeft === 0) {
          clearInterval(timer);
          setError('El código ha expirado. Solicita uno nuevo.');
        }
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [status?.verification_expires_at]);

  // Temporizador de cooldown de reenvío
  useEffect(() => {
    if (status?.resend_available_in_seconds && status.resend_available_in_seconds > 0) {
      setResendCooldown(status.resend_available_in_seconds);

      const timer = setInterval(() => {
        setResendCooldown((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [status?.resend_available_in_seconds]);

  // Obtener estado de verificación
  const fetchVerificationStatus = async () => {
    try {
      const data = await getVerificationStatus(email);
      setStatus(data);
      
      // Guardar estado en localStorage
      if (email) {
        localStorage.setItem(`verification_status_${email}`, JSON.stringify(data));
      }

      if (data.is_verified) {
        setSuccess('Email ya verificado. Redirigiendo...');
        setTimeout(() => navigate('/auth/login'), 2000);
      }
      
      // Si se alcanzó el límite de reenvíos, bloquear permanentemente
      if (data.resend_count && data.resend_count >= 3) {
        if (email) {
          localStorage.setItem(`resend_limit_reached_${email}`, 'true');
        }
      }
    } catch (err) {
      console.error('Error al obtener estado:', err);
    }
  };

  // Manejar cambio en input
  const handleChange = (index: number, value: string) => {
    // Solo permitir números
    if (value && !/^\d$/.test(value)) return;

    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);
    setError('');

    // Auto-focus al siguiente input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    // Auto-submit cuando se completen los 6 dígitos
    if (newCode.every((digit) => digit !== '') && index === 5) {
      handleVerify(newCode.join(''));
    }
  };

  // Manejar tecla presionada
  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !code[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  // Manejar paste
  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').slice(0, 6);
    
    if (/^\d+$/.test(pastedData)) {
      const newCode = pastedData.split('').concat(Array(6 - pastedData.length).fill(''));
      setCode(newCode);
      
      // Focus al último input con valor
      const lastIndex = Math.min(pastedData.length, 5);
      inputRefs.current[lastIndex]?.focus();

      // Auto-submit si se pegaron 6 dígitos
      if (pastedData.length === 6) {
        handleVerify(pastedData);
      }
    }
  };

  // Verificar código
  const handleVerify = async (codeToVerify?: string) => {
    const verificationCode = codeToVerify || code.join('');

    if (verificationCode.length !== 6) {
      setError('Por favor ingresa los 6 dígitos del código');
      // Auto-limpiar error después de 15 segundos
      setTimeout(() => setError(''), 15000);
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await verifyEmail({
        email,
        codigo: verificationCode,
      });

      // ✅ NO guardar tokens aquí - el usuario debe hacer login manualmente
      setSuccess('¡Email verificado exitosamente! Redirigiendo a login...');
      setTimeout(() => navigate('/auth/login'), 2000);
    } catch (err: any) {
      const errorMessage = err.response?.data?.error || 'Código inválido o expirado';
      setError(errorMessage);
      setCode(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
      
      // Auto-limpiar error después de 15 segundos
      setTimeout(() => setError(''), 15000);
      
      // Actualizar estado
      fetchVerificationStatus();
    } finally {
      setLoading(false);
    }
  };

  // Reenviar código
  const handleResend = async () => {
    if (resendCooldown > 0) return;
    if (status && status.resend_count && status.resend_count >= 3) {
      setError('Has alcanzado el límite de reenvíos. Contacta con soporte.');
      // Auto-limpiar error después de 15 segundos
      setTimeout(() => setError(''), 15000);
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await resendVerificationCode(email);

      setSuccess('Código reenviado exitosamente. Revisa tu email.');
      setCode(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
      
      // Auto-limpiar success después de 15 segundos
      setTimeout(() => setSuccess(''), 15000);
      
      // Actualizar estado inmediatamente
      await fetchVerificationStatus();
    } catch (err: any) {
      let errorMessage = 'Error al reenviar el código';
      
      // Manejar errores específicos
      if (err.response?.status === 429) {
        errorMessage = 'Demasiados intentos. Por favor, espera antes de intentar de nuevo.';
      } else if (err.response?.status === 401) {
        errorMessage = 'No autorizado. Por favor, registrate de nuevo.';
      } else {
        errorMessage = err.response?.data?.error || errorMessage;
      }
      
      setError(errorMessage);
      // Auto-limpiar error después de 15 segundos
      setTimeout(() => setError(''), 15000);
      
      // Actualizar estado para reflejar cambios en el backend
      await fetchVerificationStatus();
    } finally {
      setLoading(false);
    }
  };

  // Formatear tiempo
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="verify-email-page">
      {/* Flecha de regreso */}
      <button
        type="button"
        onClick={() => navigate('/auth/register')}
        className="verify-email-back-button"
        aria-label="Volver al registro"
      >
        <FiArrowLeft size={20} />
      </button>

      <div className="verify-email-container">
        {/* Header */}
        <div className="verify-email-header">
          <div className="verify-email-icon">
            <FiMail />
          </div>
          <h1 className="verify-email-title">Verifica tu Email</h1>
          <p className="verify-email-subtitle">
            Hemos enviado un código de 6 dígitos a
          </p>
          <p className="verify-email-email">{email}</p>
        </div>

        {/* Código Input */}
        <div className="verify-email-code">
          <label className="verify-email-label">Ingresa el código</label>
          <div className="verify-email-inputs" onPaste={handlePaste}>
            {code.map((digit, index) => (
              <input
                key={index}
                ref={(el) => {
                  if (el) inputRefs.current[index] = el;
                }}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={digit}
                onChange={(e) => handleChange(index, e.target.value)}
                onKeyDown={(e) => handleKeyDown(index, e)}
                className="verify-email-input"
                disabled={loading}
                autoFocus={index === 0}
              />
            ))}
          </div>
        </div>

        {/* Temporizador */}
        {timeLeft > 0 && (
          <div className="verify-email-timer">
            <FiClock />
            <span>El código expira en {formatTime(timeLeft)}</span>
          </div>
        )}

        {/* Mensajes */}
        {error && (
          <div className="verify-email-error">
            <FiAlertCircle />
            <span>{error}</span>
            <button 
              className="verify-email-close-btn"
              onClick={() => setError('')}
              aria-label="Cerrar mensaje"
            >
              <FiX />
            </button>
          </div>
        )}

        {success && (
          <div className="verify-email-success">
            <FiCheckCircle />
            <span>{success}</span>
            <button 
              className="verify-email-close-btn"
              onClick={() => setSuccess('')}
              aria-label="Cerrar mensaje"
            >
              <FiX />
            </button>
          </div>
        )}

        {/* Botón Verificar */}
        <button
          onClick={() => handleVerify()}
          disabled={loading || code.some((d) => !d)}
          className="verify-email-button"
        >
          {loading ? 'Verificando...' : 'Verificar Email'}
        </button>

        {/* Reenviar Código */}
        <div className="verify-email-resend">
          <p>¿No recibiste el código?</p>
          {localStorage.getItem(`resend_limit_reached_${email}`) === 'true' ? (
            <button
              disabled={true}
              className="verify-email-resend-button"
              title="Límite de reenvíos alcanzado. Debes registrarte de nuevo."
            >
              <FiRefreshCw />
              Límite alcanzado
            </button>
          ) : (
            <button
              onClick={handleResend}
              disabled={loading || resendCooldown > 0 || (status?.resend_count ?? 0) >= 3}
              className="verify-email-resend-button"
            >
              <FiRefreshCw className={loading ? 'spinning' : ''} />
              {resendCooldown > 0
                ? `Reenviar en ${resendCooldown}s`
                : 'Reenviar Código'}
            </button>
          )}
          
          {/* Contador de reenvíos */}
          {status && status.resend_count !== undefined && (
            <p className="verify-email-resend-count">
              Reenvíos: {status.resend_count} / {status.max_resends || 3}
            </p>
          )}
        </div>

        {/* Intentos restantes */}
        {status && status.failed_attempts !== undefined && status.failed_attempts > 0 && (
          <div className="verify-email-attempts">
            <FiAlertCircle />
            <span>
              Intentos fallidos: {status.failed_attempts} / {status.max_attempts || 5}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default VerifyEmailPage;
