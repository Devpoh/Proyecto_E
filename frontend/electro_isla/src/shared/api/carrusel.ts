import React from 'react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export interface ProductoCarrusel {
  id: number;
  nombre: string;
  descripcion: string;
  precio: string;
  descuento: number;
  imagen_url: string;
  categoria: string;
  stock: number;
  activo: boolean;
  en_carrusel: boolean;
}

/**
 * Obtiene todos los productos marcados para mostrar en el carrusel
 */
export const obtenerProductosCarrusel = async (): Promise<ProductoCarrusel[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/carrusel/`);
    return response.data.data || [];
  } catch (error) {
    console.error('Error al obtener productos del carrusel:', error);
    return [];
  }
};

/**
 * Hook para obtener productos del carrusel
 * ✅ Refresca INTELIGENTEMENTE: solo cuando se crea/edita/elimina un producto
 */
export const useProductosCarrusel = () => {
  const [productos, setProductos] = React.useState<ProductoCarrusel[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    const cargarProductos = async () => {
      try {
        setLoading(true);
        const datos = await obtenerProductosCarrusel();
        setProductos(datos);
        setError(null);
      } catch (err) {
        setError('Error al cargar productos del carrusel');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    // ✅ Cargar solo UNA VEZ al montar el componente
    cargarProductos();

    // ✅ Escuchar eventos de cambio en productos
    // Cuando se crea/edita/elimina un producto, se dispara este evento
    const handleProductChange = () => {
      console.log('[CARRUSEL] Producto cambió, refrescando...');
      cargarProductos();
    };

    // Escuchar evento personalizado desde el admin
    window.addEventListener('productChanged', handleProductChange);

    return () => {
      window.removeEventListener('productChanged', handleProductChange);
    };
  }, []); // ✅ Array vacío = ejecutar solo una vez al montar

  return { productos, loading, error };
};
