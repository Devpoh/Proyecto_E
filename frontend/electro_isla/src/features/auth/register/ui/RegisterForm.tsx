/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎨 UI COMPONENT - RegisterForm
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Formulario de registro con validación brutal en tiempo real
 */

import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FiArrowLeft } from 'react-icons/fi';
import { LogoBrand } from '@/shared/ui/LogoBrand';
import { useRegister } from '../hooks/useRegister';
import { useEmailValidation } from '../hooks/useEmailValidation';
import { RateLimitBlock } from '../../components/RateLimitBlock';
import { PasswordStrengthMeter } from './PasswordStrengthMeter';
import { calculatePasswordStrength } from '../utils/passwordStrength';
import {
  validateFirstName,
  validateLastName,
  validateEmail,
  validateUsername,
  validatePassword,
  validateConfirmPassword,
  validateRegisterForm,
} from '../utils/validation';
import type { ValidationErrors } from '../utils/validation';
import './RegisterForm.css';

export const RegisterForm = () => {
  const navigate = useNavigate();
  
  // Estados del formulario
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Errores de validación
  const [errors, setErrors] = useState<ValidationErrors>({});

  // Touched fields (para validación en tiempo real)
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  // Hook de registro
  const { register, isLoading, error: serverError, rateLimitInfo, clearRateLimit } = useRegister();

  // Validación de email en tiempo real
  const emailValidation = useEmailValidation(email);

  // Fortaleza de contraseña
  const passwordStrength = calculatePasswordStrength(password);

  // Validación en tiempo real
  useEffect(() => {
    if (touched.firstName) {
      const error = validateFirstName(firstName);
      setErrors((prev) => ({ ...prev, firstName: error }));
    }
  }, [firstName, touched.firstName]);

  useEffect(() => {
    if (touched.lastName) {
      const error = validateLastName(lastName);
      setErrors((prev) => ({ ...prev, lastName: error }));
    }
  }, [lastName, touched.lastName]);

  useEffect(() => {
    if (touched.email) {
      const error = validateEmail(email);
      setErrors((prev) => ({ ...prev, email: error }));
    }
  }, [email, touched.email]);

  useEffect(() => {
    if (touched.username) {
      const error = validateUsername(username);
      setErrors((prev) => ({ ...prev, username: error }));
    }
  }, [username, touched.username]);

  useEffect(() => {
    if (touched.password) {
      const error = validatePassword(password);
      setErrors((prev) => ({ ...prev, password: error }));
    }
  }, [password, touched.password]);

  useEffect(() => {
    if (touched.confirmPassword) {
      const error = validateConfirmPassword(password, confirmPassword);
      setErrors((prev) => ({ ...prev, confirmPassword: error }));
    }
  }, [password, confirmPassword, touched.confirmPassword]);

  // Manejar blur (campo tocado)
  const handleBlur = (field: string) => {
    setTouched((prev) => ({ ...prev, [field]: true }));
  };

  // Deshabilitar copiar/pegar en campos de contraseña
  const handlePasswordPaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
  };

  const handlePasswordCopy = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
  };

  // Manejar envío
  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    // Validar todo el formulario
    const validationErrors = validateRegisterForm({
      firstName,
      lastName,
      email,
      username,
      password,
      confirmPassword,
    });

    setErrors(validationErrors);
    setTouched({
      firstName: true,
      lastName: true,
      email: true,
      username: true,
      password: true,
      confirmPassword: true,
    });

    // Si hay errores, no enviar
    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    // Enviar registro
    register({
      firstName,
      lastName,
      email,
      username,
      password,
    });
  };

  // Si hay rate limit, mostrar componente de bloqueo
  if (rateLimitInfo?.bloqueado) {
    return (
      <div className="register-form-container">
        <RateLimitBlock
          tiempoRestante={rateLimitInfo.tiempo_restante}
          tipo="register"
          onDesbloquear={clearRateLimit}
        />
      </div>
    );
  }

  return (
    <div className="register-form-container">
      {/* Flecha de regreso */}
      <button
        type="button"
        onClick={() => navigate('/')}
        className="register-form-back-button"
        aria-label="Volver al inicio"
      >
        <FiArrowLeft size={20} />
      </button>

      <div className="register-form-card">
        {/* Header */}
        <div className="register-form-header">
          <LogoBrand variant="login" className="register-form-branding" />
          <h1 className="register-form-title">Crear Cuenta</h1>
          <p className="register-form-subtitle">
            Únete a Electrónica Isla
          </p>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="register-form" noValidate>
          {/* Error del servidor */}
          {serverError && (
            <div className="register-form-error-banner" role="alert">
              <span className="register-form-error-icon">⚠️</span>
              <span>{serverError}</span>
            </div>
          )}

          {/* Nombre y Apellido (Grid) */}
          <div className="register-form-row">
            {/* Nombre */}
            <div className="register-form-field">
              <label htmlFor="firstName" className="register-form-label">
                Nombre <span className="register-form-required">*</span>
              </label>
              <input
                id="firstName"
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                onBlur={() => handleBlur('firstName')}
                className={`register-form-input ${
                  errors.firstName && touched.firstName ? 'register-form-input-error' : ''
                }`}
                placeholder="Nombre"
                disabled={isLoading}
                autoComplete="given-name"
              />
              {errors.firstName && touched.firstName && (
                <span className="register-form-field-error">{errors.firstName}</span>
              )}
            </div>

            {/* Apellido */}
            <div className="register-form-field">
              <label htmlFor="lastName" className="register-form-label">
                Apellido <span className="register-form-required">*</span>
              </label>
              <input
                id="lastName"
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                onBlur={() => handleBlur('lastName')}
                className={`register-form-input ${
                  errors.lastName && touched.lastName ? 'register-form-input-error' : ''
                }`}
                placeholder="Apellido"
                disabled={isLoading}
                autoComplete="family-name"
              />
              {errors.lastName && touched.lastName && (
                <span className="register-form-field-error">{errors.lastName}</span>
              )}
            </div>
          </div>

          {/* Email */}
          <div className="register-form-field">
            <label htmlFor="email" className="register-form-label">
              Email <span className="register-form-required">*</span>
            </label>
            <div className="register-form-email-wrapper">
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onBlur={() => handleBlur('email')}
                className={`register-form-input ${
                  (errors.email && touched.email) || emailValidation.isDuplicate ? 'register-form-input-error' : ''
                }`}
                placeholder="ejemplo@gmail.com"
                disabled={isLoading}
                autoComplete="email"
              />
              {emailValidation.isChecking && (
                <span className="register-form-email-checking">Verificando...</span>
              )}
              {!emailValidation.isChecking && !emailValidation.isDuplicate && emailValidation.isValid && (
                <span className="register-form-email-duplicate">✓ Email disponible</span>
              )}
            </div>
            {(errors.email && touched.email) || emailValidation.error ? (
              <span className="register-form-field-error">
                {emailValidation.error || errors.email}
              </span>
            ) : null}
          </div>

          {/* Username */}
          <div className="register-form-field">
            <label htmlFor="username" className="register-form-label">
              Usuario <span className="register-form-required">*</span>
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onBlur={() => handleBlur('username')}
              className={`register-form-input ${
                errors.username && touched.username ? 'register-form-input-error' : ''
              }`}
              placeholder="Usuario"
              disabled={isLoading}
              autoComplete="username"
            />
            {errors.username && touched.username && (
              <span className="register-form-field-error">{errors.username}</span>
            )}
          </div>

          {/* Contraseña */}
          <div className="register-form-field">
            <label htmlFor="password" className="register-form-label">
              Contraseña <span className="register-form-required">*</span>
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onBlur={() => handleBlur('password')}
              onPaste={handlePasswordPaste}
              onCopy={handlePasswordCopy}
              className={`register-form-input ${
                errors.password && touched.password ? 'register-form-input-error' : ''
              }`}
              placeholder="Password"
              disabled={isLoading}
              autoComplete="new-password"
            />
            {errors.password && touched.password && (
              <span className="register-form-field-error">{errors.password}</span>
            )}
            
            {/* Medidor de fortaleza */}
            <PasswordStrengthMeter
              strength={passwordStrength}
              show={password.length > 0}
            />
          </div>

          {/* Confirmar Contraseña */}
          <div className="register-form-field">
            <label htmlFor="confirmPassword" className="register-form-label">
              Confirmar Contraseña <span className="register-form-required">*</span>
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              onBlur={() => handleBlur('confirmPassword')}
              onPaste={handlePasswordPaste}
              onCopy={handlePasswordCopy}
              className={`register-form-input ${
                errors.confirmPassword && touched.confirmPassword
                  ? 'register-form-input-error'
                  : ''
              }`}
              placeholder="Confirm Password"
              disabled={isLoading}
              autoComplete="new-password"
            />
            {errors.confirmPassword && touched.confirmPassword && (
              <span className="register-form-field-error">{errors.confirmPassword}</span>
            )}
            
            {/* Medidor de fortaleza para confirmación */}
            <PasswordStrengthMeter
              strength={calculatePasswordStrength(confirmPassword)}
              show={confirmPassword.length > 0}
            />
          </div>

          {/* Botón de envío */}
          <button type="submit" className="register-form-submit" disabled={isLoading}>
            {isLoading ? (
              <>
                <span className="register-form-spinner"></span>
                <span>Creando cuenta...</span>
              </>
            ) : (
              'Crear Cuenta'
            )}
          </button>

          {/* Link a login */}
          <div className="register-form-footer">
            <p className="register-form-footer-text">
              ¿Ya tienes una cuenta?{' '}
              <Link to="/login" className="register-form-footer-link">
                Inicia sesión aquí
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};
