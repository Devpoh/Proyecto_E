import { useEffect, useState } from 'react';
import { AppRoutes } from '@/routes';
import { GlobalLoading } from '@/shared/ui/GlobalLoading';
import './App.css';

function App() {
  const [isInitialLoading, setIsInitialLoading] = useState(true);

  // Mostrar loading por 1 segundo para que carguen todos los componentes
  // ✅ La inicialización de autenticación se hace en AuthProvider
  useEffect(() => {
    const initializeApp = async () => {
      // Mostrar loading por 1 segundo
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setIsInitialLoading(false);
    };

    initializeApp();
  }, []);

  return (
    <>
      <GlobalLoading 
        isLoading={isInitialLoading} 
        message="Cargando aplicación..." 
      />
      <AppRoutes />
    </>
  );
}

export default App;
