/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎨 UI COMPONENT - LoginForm
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Formulario de inicio de sesión con validación y diseño premium
 * 
 * CARACTERÍSTICAS:
 * - Validación en tiempo real
 * - Feedback visual de errores
 * - Animaciones suaves (Apple/iOS)
 * - Diseño responsive
 * - Accesibilidad WCAG AA
 */

import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiArrowLeft } from 'react-icons/fi';
import { LogoBrand } from '@/shared/ui/LogoBrand';
import { RateLimitAlert } from '@/shared/components';
import { useLogin } from '../hooks/useLogin';
import { RateLimitBlock } from '../../components/RateLimitBlock';
import './LoginForm.css';

export const LoginForm = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [validationErrors, setValidationErrors] = useState<{
    username?: string;
    password?: string;
  }>({});

  const { login, isLoading, error, rateLimitInfo, clearRateLimit } = useLogin();

  // Validación del formulario
  const validateForm = (): boolean => {
    const errors: { username?: string; password?: string } = {};

    if (!username.trim()) {
      errors.username = 'El usuario es requerido';
    }

    if (!password) {
      errors.password = 'La contraseña es requerida';
    } else if (password.length < 4) {
      errors.password = 'La contraseña debe tener al menos 4 caracteres';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Manejar envío del formulario
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    login({ username, password });
  };

  // Si hay rate limit, mostrar componente de bloqueo
  if (rateLimitInfo?.bloqueado) {
    return (
      <div className="login-form-container">
        <RateLimitBlock
          tiempoRestante={rateLimitInfo.tiempo_restante}
          tipo="login"
          onDesbloquear={clearRateLimit}
        />
      </div>
    );
  }

  return (
    <div className="login-form-container">
      {/* Fondo decorativo */}
      <div className="login-form-background" aria-hidden="true">
        <div className="login-form-background-gradient"></div>
      </div>

      {/* Flecha de regreso */}
      <button
        type="button"
        onClick={() => navigate('/')}
        className="login-form-back-button"
        aria-label="Volver al inicio"
      >
        <FiArrowLeft size={20} />
      </button>

      {/* Wrapper del contenido */}
      <div className="login-form-wrapper">
        <div className="login-form-card">
        {/* Logo y título */}
        <div className="login-form-header">
          <LogoBrand variant="login" className="login-form-branding" />
          <p className="login-form-subtitle">
            Inicia sesión en tu cuenta
          </p>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="login-form" noValidate>
          {/* Alerta de Rate Limiting */}
          {rateLimitInfo?.bloqueado && (
            <RateLimitAlert
              visible={true}
              tiempoRestante={rateLimitInfo.tiempo_restante}
              mensaje={rateLimitInfo.mensaje}
              onExpire={clearRateLimit}
            />
          )}

          {/* Error general del servidor */}
          {error && (
            <div className="login-form-error-banner" role="alert">
              <span className="login-form-error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}

          {/* Campo de usuario o email */}
          <div className="login-form-field">
            <label htmlFor="username" className="login-form-label">
              Email o Usuario
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => {
                setUsername(e.target.value);
                if (validationErrors.username) {
                  setValidationErrors((prev) => ({ ...prev, username: undefined }));
                }
              }}
              className={`login-form-input ${
                validationErrors.username ? 'login-form-input-error' : ''
              }`}
              placeholder="ejemplo@gmail.com o Usuario"
              disabled={isLoading}
              autoComplete="username"
              aria-invalid={!!validationErrors.username}
              aria-describedby={validationErrors.username ? 'username-error' : undefined}
            />
            {validationErrors.username && (
              <span id="username-error" className="login-form-field-error">
                {validationErrors.username}
              </span>
            )}
          </div>

          {/* Campo de contraseña */}
          <div className="login-form-field">
            <label htmlFor="password" className="login-form-label">
              Contraseña
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (validationErrors.password) {
                  setValidationErrors((prev) => ({ ...prev, password: undefined }));
                }
              }}
              className={`login-form-input ${
                validationErrors.password ? 'login-form-input-error' : ''
              }`}
              placeholder="Password"
              disabled={isLoading}
              autoComplete="current-password"
              aria-invalid={!!validationErrors.password}
              aria-describedby={validationErrors.password ? 'password-error' : undefined}
            />
            {validationErrors.password && (
              <span id="password-error" className="login-form-field-error">
                {validationErrors.password}
              </span>
            )}
          </div>

          {/* Recordarme y Olvidaste contraseña */}
          <div className="login-form-options">
            <label className="login-form-checkbox">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                disabled={isLoading}
              />
              <span>Recordarme</span>
            </label>
            <Link to="/forgot-password" className="login-form-forgot-password">
              ¿Olvidaste tu contraseña?
            </Link>
          </div>

          {/* Botón de envío */}
          <button
            type="submit"
            className="login-form-submit"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <span className="login-form-spinner"></span>
                <span>Iniciando sesión...</span>
              </>
            ) : (
              'Iniciar Sesión'
            )}
          </button>

          {/* Divider */}
          <div className="login-form-divider">
            <span>O continúa con</span>
          </div>

          {/* Botón de Google */}
          <button
            type="button"
            className="login-form-google"
            disabled={isLoading}
            aria-label="Iniciar sesión con Google"
          >
            <svg className="login-form-google-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            <span>Iniciar con Google</span>
          </button>

          {/* Link a registro */}
          <div className="login-form-footer">
            <p className="login-form-footer-text">
              ¿No tienes una cuenta?{' '}
              <Link to="/register" className="login-form-footer-link">
                Regístrate aquí
              </Link>
            </p>
          </div>
        </form>
        </div>
      </div>
    </div>
  );
};
