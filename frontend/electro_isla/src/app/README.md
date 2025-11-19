# 📱 APP - Configuración Global de la Aplicación

Esta carpeta contiene la configuración global y el punto de entrada de la aplicación.

## 📂 Estructura

```
app/
├── providers/     # Providers globales (QueryClient, Toaster, Router)
├── store/        # Zustand stores (auth, cart, ui)
└── styles/       # Estilos globales adicionales
```

## 🎯 Responsabilidades

- **providers/**: Envolver la app con providers necesarios
- **store/**: Estado global de la aplicación
- **styles/**: CSS global que complementa index.css

## 📖 Ejemplos de Uso

### Providers
```tsx
// app/providers/AppProviders.tsx
import { QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';

export function AppProviders({ children }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster position="top-right" />
    </QueryClientProvider>
  );
}
```

### Store
```tsx
// app/store/useAuthStore.ts
import { create } from 'zustand';

export const useAuthStore = create((set) => ({
  isAuthenticated: false,
  user: null,
  login: (user) => set({ isAuthenticated: true, user }),
  logout: () => set({ isAuthenticated: false, user: null }),
}));
```
