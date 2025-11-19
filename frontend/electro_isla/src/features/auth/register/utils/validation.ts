/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * ✅ UTILS - Validación de Formulario de Registro
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Validación profesional en tiempo real
 * 
 * REGLAS:
 * - Nombre: 2-50 caracteres, solo letras y espacios
 * - Apellido: 2-50 caracteres, solo letras y espacios
 * - Email: Formato válido RFC 5322
 * - Username: 3-20 caracteres, alfanumérico y guiones
 * - Contraseña: Mínimo 8 caracteres, validación compleja
 * - Confirmación: Debe coincidir
 */

export interface ValidationErrors {
  firstName?: string;
  lastName?: string;
  email?: string;
  username?: string;
  password?: string;
  confirmPassword?: string;
}

/**
 * Valida el nombre
 */
export const validateFirstName = (value: string): string | undefined => {
  if (!value.trim()) {
    return 'El nombre es requerido';
  }
  if (value.trim().length < 2) {
    return 'El nombre debe tener al menos 2 caracteres';
  }
  if (value.trim().length > 50) {
    return 'El nombre no puede exceder 50 caracteres';
  }
  if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(value)) {
    return 'El nombre solo puede contener letras';
  }
  return undefined;
};

/**
 * Valida el apellido
 */
export const validateLastName = (value: string): string | undefined => {
  if (!value.trim()) {
    return 'El apellido es requerido';
  }
  if (value.trim().length < 2) {
    return 'El apellido debe tener al menos 2 caracteres';
  }
  if (value.trim().length > 50) {
    return 'El apellido no puede exceder 50 caracteres';
  }
  if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(value)) {
    return 'El apellido solo puede contener letras';
  }
  return undefined;
};

/**
 * Valida el email (RFC 5322 simplificado)
 */
export const validateEmail = (value: string): string | undefined => {
  if (!value.trim()) {
    return 'El email es requerido';
  }
  
  // Regex RFC 5322 simplificado
  const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
  
  if (!emailRegex.test(value)) {
    return 'Email inválido';
  }
  
  if (value.length > 254) {
    return 'El email es demasiado largo';
  }
  
  // Validar dominio común
  const domain = value.split('@')[1];
  if (domain && domain.split('.').length < 2) {
    return 'El dominio del email parece incorrecto';
  }
  
  return undefined;
};

/**
 * Valida el username
 */
export const validateUsername = (value: string): string | undefined => {
  if (!value.trim()) {
    return 'El usuario es requerido';
  }
  if (value.length < 3) {
    return 'El usuario debe tener al menos 3 caracteres';
  }
  if (value.length > 20) {
    return 'El usuario no puede exceder 20 caracteres';
  }
  if (!/^[a-zA-Z0-9_-]+$/.test(value)) {
    return 'El usuario solo puede contener letras, números, guiones y guiones bajos';
  }
  if (/^[0-9]/.test(value)) {
    return 'El usuario no puede empezar con un número';
  }
  return undefined;
};

/**
 * Valida la contraseña
 */
export const validatePassword = (value: string): string | undefined => {
  if (!value) {
    return 'La contraseña es requerida';
  }
  if (value.length < 8) {
    return 'La contraseña debe tener al menos 8 caracteres';
  }
  if (value.length > 128) {
    return 'La contraseña es demasiado larga';
  }
  
  // Validaciones de complejidad
  const hasUpperCase = /[A-Z]/.test(value);
  const hasLowerCase = /[a-z]/.test(value);
  const hasNumber = /\d/.test(value);
  const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(value);
  
  if (!hasUpperCase) {
    return 'Debe incluir al menos una mayúscula';
  }
  if (!hasLowerCase) {
    return 'Debe incluir al menos una minúscula';
  }
  if (!hasNumber) {
    return 'Debe incluir al menos un número';
  }
  if (!hasSpecialChar) {
    return 'Debe incluir al menos un carácter especial';
  }
  
  return undefined;
};

/**
 * Valida la confirmación de contraseña
 */
export const validateConfirmPassword = (
  password: string,
  confirmPassword: string
): string | undefined => {
  if (!confirmPassword) {
    return 'Confirma tu contraseña';
  }
  if (password !== confirmPassword) {
    return 'Las contraseñas no coinciden';
  }
  return undefined;
};

/**
 * Valida todo el formulario
 */
export const validateRegisterForm = (data: {
  firstName: string;
  lastName: string;
  email: string;
  username: string;
  password: string;
  confirmPassword: string;
}): ValidationErrors => {
  const errors: ValidationErrors = {};

  const firstNameError = validateFirstName(data.firstName);
  if (firstNameError) errors.firstName = firstNameError;

  const lastNameError = validateLastName(data.lastName);
  if (lastNameError) errors.lastName = lastNameError;

  const emailError = validateEmail(data.email);
  if (emailError) errors.email = emailError;

  const usernameError = validateUsername(data.username);
  if (usernameError) errors.username = usernameError;

  const passwordError = validatePassword(data.password);
  if (passwordError) errors.password = passwordError;

  const confirmPasswordError = validateConfirmPassword(
    data.password,
    data.confirmPassword
  );
  if (confirmPasswordError) errors.confirmPassword = confirmPasswordError;

  return errors;
};
