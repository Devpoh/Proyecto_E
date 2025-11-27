/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎨 UI COMPONENT - ForgotPasswordForm
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Formulario para solicitar recuperación de contraseña.
 * 
 * CARACTERÍSTICAS:
 * - Validación de email en tiempo real
 * - Feedback visual de errores
 * - Diseño responsive
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiMail, FiCheckCircle, FiAlertCircle, FiX } from 'react-icons/fi';
import { GlobalLoading } from '@/shared/ui/GlobalLoading';
import { useForgotPassword } from '../hooks/useForgotPassword';
import './ForgotPasswordForm.css';

export const ForgotPasswordForm = () => {
  const navigate = useNavigate();
  const { email, setEmail, isLoading, error, success, requestReset, clearMessages } =
    useForgotPassword();
  const [showError, setShowError] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setShowError(false);
    setShowSuccess(false);

    await requestReset();

    if (error) {
      setShowError(true);
      setTimeout(() => setShowError(false), 5000);
    }
    if (success) {
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 5000);
    }
  };

  const handleCloseError = () => {
    setShowError(false);
    clearMessages();
  };

  const handleCloseSuccess = () => {
    setShowSuccess(false);
    clearMessages();
  };

  return (
    <div className="forgot-password-page">
      <GlobalLoading isLoading={isLoading} message="Enviando código..." />

      {/* Flecha de regreso */}
      <button
        type="button"
        onClick={() => navigate('/auth/login')}
        className="forgot-password-back-button"
        aria-label="Volver al login"
      >
        <FiArrowLeft size={20} />
      </button>

      <div className="forgot-password-container">
        {/* Fondo decorativo */}
        <div className="forgot-password-background" aria-hidden="true">
          <div className="forgot-password-background-gradient"></div>
        </div>

        {/* Wrapper del contenido */}
        <div className="forgot-password-wrapper">
          <div className="forgot-password-card">
            {/* Título */}
            <div className="forgot-password-header">
              <h1 className="forgot-password-title">Recupera tu Contraseña</h1>
              <p className="forgot-password-subtitle">
                Ingresa tu email y te enviaremos un código para restablecer tu contraseña
              </p>
            </div>

            {/* Formulario */}
            <form onSubmit={handleSubmit} className="forgot-password-form">
              {/* Email Input */}
              <div className="forgot-password-group">
                <label htmlFor="email" className="forgot-password-label">
                  Email
                </label>
                <div className="forgot-password-input-wrapper">
                  <FiMail className="forgot-password-input-icon" />
                  <input
                    id="email"
                    type="email"
                    placeholder="tu@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    disabled={isLoading}
                    className="forgot-password-input"
                    autoComplete="email"
                    required
                  />
                </div>
              </div>

              {/* Botón Enviar */}
              <button
                type="submit"
                disabled={isLoading || !email.trim()}
                className="forgot-password-button reset-password-button"
              >
                {isLoading ? 'Enviando...' : 'Recuperar Contraseña'}
              </button>
            </form>

            {/* Mensaje de Error */}
            {showError && error && (
              <div className="forgot-password-error">
                <div className="forgot-password-error-content">
                  <FiAlertCircle />
                  <span>{error}</span>
                </div>
                <button
                  type="button"
                  onClick={handleCloseError}
                  className="forgot-password-close-btn"
                >
                  <FiX />
                </button>
              </div>
            )}

            {/* Mensaje de Éxito */}
            {showSuccess && success && (
              <div className="forgot-password-success">
                <div className="forgot-password-success-content">
                  <FiCheckCircle />
                  <span>{success}</span>
                </div>
                <button
                  type="button"
                  onClick={handleCloseSuccess}
                  className="forgot-password-close-btn"
                >
                  <FiX />
                </button>
              </div>
            )}

            {/* Links */}
            <div className="forgot-password-links">
              <p>
                ¿Recuerdas tu contraseña?{' '}
                <button
                  type="button"
                  onClick={() => navigate('/auth/login')}
                  className="forgot-password-link-plain"
                >
                  Volver al Login
                </button>
              </p>
              <p>
                ¿No tienes cuenta?{' '}
                <button
                  type="button"
                  onClick={() => navigate('/auth/register')}
                  className="forgot-password-link-plain"
                >
                  Registrate aquí
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordForm;
