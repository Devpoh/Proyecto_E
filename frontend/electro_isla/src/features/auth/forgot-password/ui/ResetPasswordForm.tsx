/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🎨 UI COMPONENT - ResetPasswordForm
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Formulario para confirmar la recuperación de contraseña con código de 6 dígitos.
 * 
 * CARACTERÍSTICAS:
 * - Validación de contraseña en tiempo real
 * - Indicador de fortaleza de contraseña
 * - Feedback visual de errores
 * - Animaciones suaves
 * - Diseño responsive
 * - Accesibilidad WCAG AA
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiLock, FiCheckCircle, FiAlertCircle, FiX, FiShield } from 'react-icons/fi';
import { confirmPasswordReset } from '../api/forgotPasswordApi';
import { GlobalLoading } from '@/shared/ui/GlobalLoading';
import './ResetPasswordForm.css';

export const ResetPasswordForm = () => {
  const navigate = useNavigate();
  const email = sessionStorage.getItem('recovery_email') || '';

  const [codigo, setCodigo] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showError, setShowError] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  // Validar que exista el email
  useEffect(() => {
    if (!email) {
      setError('Email no encontrado. Por favor solicita recuperación nuevamente.');
      setShowError(true);
      setTimeout(() => navigate('/auth/forgot-password'), 3000);
    }
  }, [email, navigate]);

  const getPasswordStrength = (pwd: string) => {
    if (!pwd) return 0;
    let strength = 0;
    if (pwd.length >= 8) strength++;
    if (pwd.length >= 12) strength++;
    if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength++;
    if (/\d/.test(pwd)) strength++;
    if (/[^a-zA-Z\d]/.test(pwd)) strength++;
    return strength;
  };

  const passwordStrength = getPasswordStrength(password);
  const strengthText = ['Muy débil', 'Débil', 'Regular', 'Fuerte', 'Muy fuerte'];
  const strengthColor = ['#dc3545', '#fd7e14', '#ffc107', '#20c997', '#28a745'];

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setShowError(false);
    setShowSuccess(false);
    setError('');
    setSuccess('');

    // Validaciones
    if (!codigo.trim()) {
      setError('Por favor ingresa el código de 6 dígitos');
      setShowError(true);
      return;
    }

    if (codigo.length !== 6 || !/^\d+$/.test(codigo)) {
      setError('El código debe ser de 6 dígitos');
      setShowError(true);
      return;
    }

    if (!password) {
      setError('Por favor ingresa una contraseña');
      setShowError(true);
      return;
    }

    if (password.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres');
      setShowError(true);
      return;
    }

    if (password !== passwordConfirm) {
      setError('Las contraseñas no coinciden');
      setShowError(true);
      return;
    }

    setIsLoading(true);

    try {
      const response = await confirmPasswordReset(email, codigo, password, passwordConfirm);

      console.log('[ResetPasswordForm] Response recibida:', {
        hasAccessToken: !!response.accessToken,
        hasUser: !!response.user,
        user: response.user
      });

      setSuccess('\u00a1Contraseña actualizada exitosamente!');
      setShowSuccess(true);

      // ✅ NO loguear automáticamente - solo redirigir a login
      // El usuario debe loguear manualmente con su nueva contraseña
      
      // ✅ Guardar mensaje de éxito en sessionStorage para mostrarlo en login
      sessionStorage.setItem('passwordResetSuccess', 'true');
      
      // ✅ Limpiar datos de recuperación DESPUÉS de redirigir
      // para evitar que el useEffect rediriga de vuelta
      setTimeout(() => {
        sessionStorage.removeItem('recovery_email');
        navigate('/login');
      }, 2000);
    } catch (err: any) {
      const errorMsg = err.error || err.detail || 'Error al actualizar contraseña';
      setError(errorMsg);
      setShowError(true);
      setIsLoading(false);
    }
  };

  const handleCloseError = () => {
    setShowError(false);
    setError('');
  };

  const handleCloseSuccess = () => {
    setShowSuccess(false);
    setSuccess('');
  };

  if (!email) {
    return null;
  }

  return (
    <div className="reset-password-page">
      {/* Flecha de regreso */}
      <button
        type="button"
        onClick={() => navigate('/auth/forgot-password')}
        className="reset-password-back-button"
        aria-label="Volver"
      >
        <FiArrowLeft size={20} />
      </button>

      <GlobalLoading isLoading={isLoading} message="Actualizando contraseña..." />
      
      <div className="reset-password-container">
        {/* Wrapper del contenido */}
        <div className="reset-password-wrapper">
          <div className="reset-password-card">
            {/* Título */}
            <div className="reset-password-header">
              <h1 className="reset-password-title">Establece una Nueva Contraseña</h1>
              <p className="reset-password-subtitle">
                Crea una contraseña segura para proteger tu cuenta
              </p>
            </div>

            {/* Formulario */}
            <form onSubmit={handleSubmit} className="reset-password-form">
              {/* Código Input */}
              <div className="reset-password-group">
                <label htmlFor="codigo" className="reset-password-label">
                  Código de Recuperación
                </label>
                <div className="reset-password-input-wrapper">
                  <FiShield className="reset-password-input-icon" />
                  <input
                    id="codigo"
                    type="text"
                    placeholder="Ingresa los 6 dígitos"
                    value={codigo}
                    onChange={(e) => setCodigo(e.target.value.replace(/\D/g, '').slice(0, 6))}
                    disabled={isLoading}
                    className="reset-password-input"
                    maxLength={6}
                    required
                  />
                </div>
                <p className="reset-password-hint">Revisa tu email para obtener el código</p>
              </div>

              {/* Password Input */}
              <div className="reset-password-group">
                <label htmlFor="password" className="reset-password-label">
                  Nueva Contraseña
                </label>
                <div className="reset-password-input-wrapper">
                  <FiLock className="reset-password-input-icon" />
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Mínimo 8 caracteres"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    disabled={isLoading}
                    className="reset-password-input"
                    autoComplete="new-password"
                    required
                  />
                  <input
                    type="checkbox"
                    id="show-password"
                    checked={showPassword}
                    onChange={() => setShowPassword(!showPassword)}
                    className="reset-password-checkbox"
                    aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                  />
                </div>

                {/* Password Strength */}
                {password && (
                  <div className="reset-password-strength">
                    <div className="reset-password-strength-bar">
                      <div
                        className="reset-password-strength-fill"
                        style={{
                          width: `${(passwordStrength / 5) * 100}%`,
                          backgroundColor: strengthColor[passwordStrength - 1],
                        }}
                      ></div>
                    </div>
                    <span
                      className="reset-password-strength-text"
                      style={{ color: strengthColor[passwordStrength - 1] }}
                    >
                      {strengthText[passwordStrength - 1]}
                    </span>
                  </div>
                )}
              </div>

              {/* Password Confirm Input */}
              <div className="reset-password-group">
                <label htmlFor="passwordConfirm" className="reset-password-label">
                  Confirmar Contraseña
                </label>
                <div className="reset-password-input-wrapper">
                  <FiLock className="reset-password-input-icon" />
                  <input
                    id="passwordConfirm"
                    type={showPasswordConfirm ? 'text' : 'password'}
                    placeholder="Repite tu contraseña"
                    value={passwordConfirm}
                    onChange={(e) => setPasswordConfirm(e.target.value)}
                    disabled={isLoading}
                    className="reset-password-input"
                    autoComplete="new-password"
                    required
                  />
                  <input
                    type="checkbox"
                    id="show-password-confirm"
                    checked={showPasswordConfirm}
                    onChange={() => setShowPasswordConfirm(!showPasswordConfirm)}
                    className="reset-password-checkbox"
                    aria-label={showPasswordConfirm ? 'Ocultar contraseña' : 'Mostrar contraseña'}
                  />
                </div>

                {/* Match Indicator */}
                {password && passwordConfirm && (
                  <div
                    className="reset-password-match"
                    style={{
                      color: password === passwordConfirm ? '#28a745' : '#dc3545',
                    }}
                  >
                    {password === passwordConfirm ? '✓ Las contraseñas coinciden' : '✗ Las contraseñas no coinciden'}
                  </div>
                )}
              </div>

              {/* Botón Enviar */}
              <button
                type="submit"
                disabled={isLoading || !codigo || !password || !passwordConfirm || password !== passwordConfirm}
                className="reset-password-button"
              >
                {isLoading ? 'Actualizando...' : 'Actualizar Contraseña'}
              </button>
            </form>

            {/* Mensaje de Error */}
            {showError && error && (
              <div className="reset-password-error">
                <div className="reset-password-error-content">
                  <FiAlertCircle />
                  <span>{error}</span>
                </div>
                <button
                  type="button"
                  onClick={handleCloseError}
                  className="reset-password-close-btn"
                >
                  <FiX />
                </button>
              </div>
            )}

            {/* Mensaje de Éxito */}
            {showSuccess && success && (
              <div className="reset-password-success">
                <div className="reset-password-success-content">
                  <FiCheckCircle />
                  <span>{success}</span>
                </div>
                <button
                  type="button"
                  onClick={handleCloseSuccess}
                  className="reset-password-close-btn"
                >
                  <FiX />
                </button>
              </div>
            )}

            {/* Info */}
            <div className="reset-password-info">
              <p>
                <strong>Consejos de seguridad:</strong>
              </p>
              <ul>
                <li>El código expira en 15 minutos</li>
                <li>Usa al menos 8 caracteres en tu contraseña</li>
                <li>Mezcla mayúsculas, minúsculas y números</li>
                <li>Incluye caracteres especiales (!@#$%)</li>
                <li>No uses información personal</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResetPasswordForm;
