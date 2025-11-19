# 🔐 Feature: Login

## Descripción
Funcionalidad completa de inicio de sesión con validación, manejo de errores y diseño premium.

## Estructura

```
login/
├── api/
│   └── loginApi.ts          # Servicios de API (login, logout)
├── hooks/
│   └── useLogin.ts          # Hook personalizado con React Query
├── ui/
│   ├── LoginForm.tsx        # Componente del formulario
│   └── LoginForm.css        # Estilos premium (Apple/iOS)
├── types.ts                 # Tipos TypeScript
├── index.ts                 # Exports públicos
└── README.md                # Esta documentación
```

## Uso

### En una página:
```tsx
import { LoginForm } from '@/features/auth/login';

export const LoginPage = () => {
  return <LoginForm />;
};
```

### Hook personalizado:
```tsx
import { useLogin } from '@/features/auth/login';

const { login, isLoading, error } = useLogin();

// Usar en un formulario
login({ username: 'user', password: 'pass' });
```

## Características

### ✅ Validación
- Validación en tiempo real
- Mensajes de error claros
- Feedback visual inmediato

### ✅ Seguridad
- No expone contraseñas en logs
- Token guardado en localStorage
- Integración con Zustand para estado global
- Interceptores de Axios para manejo de errores

### ✅ UX Premium
- Animaciones suaves (Apple/iOS)
- Estados de carga con spinner
- Diseño responsive
- Accesibilidad WCAG AA
- Toggle para mostrar/ocultar contraseña

### ✅ Integración
- React Query para manejo de estado
- Zustand para estado global
- React Router para navegación
- Axios para peticiones HTTP

## API Endpoint

**POST** `/api/auth/login/`

### Request:
```json
{
  "username": "usuario",
  "password": "contraseña"
}
```

### Response (Éxito):
```json
{
  "token": "abc123...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "nombre": "Usuario",
    "rol": "cliente"
  },
  "message": "Login exitoso"
}
```

### Response (Error):
```json
{
  "error": "Credenciales inválidas"
}
```

## Flujo de Autenticación

1. Usuario ingresa credenciales
2. Validación frontend (UX)
3. Petición al backend
4. Backend valida (seguridad)
5. Si es exitoso:
   - Token guardado en localStorage
   - Usuario guardado en Zustand
   - Redirección según rol (admin → /admin, cliente → /)
6. Si falla:
   - Mensaje de error mostrado
   - Formulario se mantiene

## Navegación Post-Login

- **Admin**: `/admin`
- **Cliente**: `/` (home)

## Estilos

Los estilos siguen los principios de diseño de Apple/iOS:
- Animaciones suaves (cubic-bezier)
- Espaciado generoso
- Sombras sutiles
- Feedback visual claro
- Responsive design

## Variables CSS Usadas

- `--color-primario`: Color principal
- `--color-peligro`: Errores
- `--transicion-normal`: Animaciones
- `--sombra-2xl`: Elevación de tarjeta
- `--espaciado-*`: Espaciados consistentes

## Testing

```bash
# Ejecutar tests
npm test login

# Coverage
npm run test:coverage
```

## Mejoras Futuras

- [ ] Recordar usuario (checkbox)
- [ ] Recuperación de contraseña
- [ ] Login con redes sociales
- [ ] Autenticación de dos factores (2FA)
- [ ] Rate limiting visual (intentos restantes)
