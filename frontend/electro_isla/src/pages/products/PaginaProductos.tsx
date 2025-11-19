/*
 * 📄 PaginaProductos.tsx
 * 🎯 Página de catálogo de productos con filtros avanzados
 * 
 * 🛡️ REGLAS APLICADAS:
 * - Regla 139: Arquitectura FSD - Capa pages
 * - Regla 127: TypeScript First
 * - Regla 147: Nomenclatura en español
 * - Regla 11: HTML Semántico
 * - Regla 158: Paleta de colores oficial
 * - Regla 146: Microinteracciones GPU-optimized
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { FiFilter, FiChevronDown, FiTag, FiChevronRight, FiDollarSign } from 'react-icons/fi';
import { MdElectricBolt, MdBuild, MdChair, MdMoreHoriz, MdKitchen } from 'react-icons/md';
import { Footer } from '@/widgets/footer';
import { CarouselCard } from '@/widgets/bottom-carousel';
import api from '@/shared/api/axios';
import './PaginaProductos.css';

interface PaginaProductosProps {
  categoriaInicial?: string;
  busquedaInicial?: string;
}

export const PaginaProductos: React.FC<PaginaProductosProps> = ({ 
  categoriaInicial = 'Todos los productos',
  busquedaInicial = ''
}) => {
  const [searchParams] = useSearchParams();
  
  // Leer parámetros de URL
  const busquedaURL = searchParams.get('busqueda') || '';
  const categoriaURL = searchParams.get('categoria') || '';
  
  // Estados de filtros
  const [categoriaSeleccionada, setCategoriaSeleccionada] = useState(categoriaURL || categoriaInicial);
  const [precioMin, setPrecioMin] = useState(0);
  const [precioMax, setPrecioMax] = useState(50000);
  const [ordenarPor, setOrdenarPor] = useState('popularidad');
  const [busqueda, setBusqueda] = useState(busquedaURL || busquedaInicial);
  
  // Actualizar búsqueda cuando cambian los parámetros de URL
  useEffect(() => {
    if (busquedaURL) {
      setBusqueda(busquedaURL);
    }
    if (categoriaURL) {
      setCategoriaSeleccionada(categoriaURL);
    }
  }, [busquedaURL, categoriaURL]);

  // Estados de UI
  const [categoriasExpandidas, setCategoriasExpandidas] = useState(true);
  const [preciosExpandidos, setPreciosExpandidos] = useState(true);

  // Fetch productos desde API
  const { data: productosAPI = [], isLoading } = useQuery({
    queryKey: ['productos'],
    queryFn: async () => {
      try {
        const response = await api.get('/productos/');
        // ✅ La respuesta es paginada: { count, next, previous, results }
        // Siempre retornar results (es un array)
        return response.data.results || [];
      } catch (error) {
        console.error('Error fetching productos:', error);
        return [];
      }
    },
    staleTime: 10 * 1000, // ✅ 10 segundos - Balance entre freshness y rendimiento
    gcTime: 1000 * 60 * 5, // Mantener en memoria 5 minutos si no se usa
  });

  /**
   * 🎯 SOLUCIÓN QUIRÚRGICA: Productos ficticios removidos
   * 
   * Se removieron completamente los datos de ejemplo (productosEjemplo).
   * Ahora SOLO se muestran productos del backend.
   * 
   * Ventajas:
   * - No hay confusión entre productos reales y ficticios
   * - El cliente no puede comprar productos que no existen
   * - Mejor rendimiento (menos datos en memoria)
   * - Sincronización perfecta con el dashboard
   */

  const categorias = [
    { nombre: 'Todos los productos', icono: null },
    { nombre: 'Electrodomésticos', icono: <MdKitchen /> },
    { nombre: 'Energía y Tecnología', icono: <MdElectricBolt /> },
    { nombre: 'Herramientas', icono: <MdBuild /> },
    { nombre: 'Hogar y Entretenimiento', icono: <MdChair /> },
    { nombre: 'Otros Artículos', icono: <MdMoreHoriz /> }
  ];

  // SOLO usar productos del API (sin fallback a ejemplos)
  const productos = productosAPI;

  // Filtrar productos
  const productosFiltrados = productos.filter((producto: any) => {
    const coincideCategoria = categoriaSeleccionada === 'Todos los productos' || 
                             producto.categoria === categoriaSeleccionada;
    const precio = parseFloat(producto.precio) || 0;
    const coincidePrecio = precio >= precioMin && 
                          precio <= precioMax;
    
    // Búsqueda mejorada: busca en nombre, descripción, categoría y marca
    const terminoBusqueda = busqueda.toLowerCase().trim();
    const coincideBusqueda = !busqueda || 
                            (producto.nombre && producto.nombre.toLowerCase().includes(terminoBusqueda)) ||
                            (producto.descripcion && producto.descripcion.toLowerCase().includes(terminoBusqueda)) ||
                            (producto.categoria && producto.categoria.toLowerCase().includes(terminoBusqueda)) ||
                            (producto.marca && producto.marca.toLowerCase().includes(terminoBusqueda));
    
    return coincideCategoria && coincidePrecio && coincideBusqueda;
  });

  // Ordenar productos
  const productosOrdenados = [...productosFiltrados].sort((a: any, b: any) => {
    switch (ordenarPor) {
      case 'precio-menor':
        return (parseFloat(a.precio) || 0) - (parseFloat(b.precio) || 0);
      case 'precio-mayor':
        return (parseFloat(b.precio) || 0) - (parseFloat(a.precio) || 0);
      case 'rating':
        return (b.rating || 0) - (a.rating || 0);
      case 'nuevo':
        return (b.id || 0) - (a.id || 0);
      default: // popularidad
        return (b.rating || 0) - (a.rating || 0);
    }
  });

  return (
    <>
      <main className="pagina-productos">
        {/* SECCIÓN DE CATÁLOGO */}
        <section className="catalogo-seccion">
          <div className="container">
            <div className="catalogo-layout">
              
              {/* PANEL DE FILTROS */}
              <aside className="panel-filtros">
                <div className="encabezado-filtros">
                  <h3><FiFilter /> Filtros</h3>
                </div>

                {/* Filtro por Categoría */}
                <div className="grupo-filtro">
                  <div 
                    className="encabezado-filtro-toggle"
                    onClick={() => setCategoriasExpandidas(!categoriasExpandidas)}
                  >
                    <h4><FiTag /> Categoría</h4>
                    {categoriasExpandidas ? <FiChevronDown /> : <FiChevronRight />}
                  </div>
                  <div className={`opciones-filtro ${categoriasExpandidas ? 'expandido' : 'colapsado'}`}>
                    {categorias.map((categoria) => (
                      <label key={categoria.nombre} className="opcion-filtro">
                        <input
                          type="radio"
                          name="categoria"
                          value={categoria.nombre}
                          checked={categoriaSeleccionada === categoria.nombre}
                          onChange={(e) => setCategoriaSeleccionada(e.target.value)}
                        />
                        {categoria.icono && <span className="icono-categoria">{categoria.icono}</span>}
                        <span>{categoria.nombre}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Filtro por Precio */}
                <div className="grupo-filtro">
                  <div 
                    className="encabezado-filtro-toggle"
                    onClick={() => setPreciosExpandidos(!preciosExpandidos)}
                  >
                    <h4><FiDollarSign /> Rango de Precio</h4>
                    {preciosExpandidos ? <FiChevronDown /> : <FiChevronRight />}
                  </div>
                  <div className={`rango-precios ${preciosExpandidos ? 'expandido' : 'colapsado'}`}>
                    <div className="precio-min">
                      <label>Precio mínimo:</label>
                      <input 
                        type="number" 
                        value={precioMin} 
                        onChange={(e) => setPrecioMin(parseInt(e.target.value))}
                      />
                    </div>
                    <div className="precio-max">
                      <label>Precio máximo:</label>
                      <input 
                        type="number" 
                        value={precioMax} 
                        onChange={(e) => setPrecioMax(parseInt(e.target.value))}
                      />
                    </div>
                  </div>
                </div>

              </aside>

              {/* ÁREA DE PRODUCTOS */}
              <main className="area-productos">
                
                {/* BARRA DE HERRAMIENTAS */}
                <div className="barra-herramientas">
                  <div className="info-resultados">
                    <span>Mostrando {productosOrdenados.length} de {productos.length} productos</span>
                    {busqueda && (
                      <span className="indicador-busqueda">
                        • Búsqueda: "{busqueda}"
                        <button 
                          className="boton-limpiar-busqueda"
                          onClick={() => setBusqueda('')}
                          title="Limpiar búsqueda"
                        >
                          ✕
                        </button>
                      </span>
                    )}
                  </div>
                  
                  <div className="controles-barra">
                    <div className="control-ordenamiento">
                      <label>Ordenar por:</label>
                      <select 
                        value={ordenarPor} 
                        onChange={(e) => setOrdenarPor(e.target.value)}
                        className="selector-ordenamiento"
                      >
                        <option value="popularidad">Popularidad</option>
                        <option value="precio-menor">Precio: Menor a Mayor</option>
                        <option value="precio-mayor">Precio: Mayor a Menor</option>
                        <option value="nuevo">Más Nuevos</option>
                        <option value="rating">Mejor Valorados</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* GRID DE PRODUCTOS */}
                {isLoading ? (
                  <div className="grid-productos">
                    {[1, 2, 3, 4, 5, 6].map((i) => (
                      <div key={i} style={{ 
                        height: '340px', 
                        background: '#f0f0f0', 
                        borderRadius: '12px',
                        animation: 'pulse 2s infinite'
                      }} />
                    ))}
                  </div>
                ) : (
                  <div className="grid-productos">
                    {productosOrdenados.map((producto: any) => (
                      <CarouselCard
                        key={producto.id}
                        id={producto.id}
                        nombre={producto.nombre || 'Producto sin nombre'}
                        categoria={producto.categoria || 'Sin categoría'}
                        precio={parseFloat(producto.precio) || 0}
                        descuento={parseFloat(producto.descuento) || 0}
                        imagen_url={producto.imagen_url || producto.imagen || null}
                        stock={producto.stock}
                      />
                    ))}
                  </div>
                )}

                {!isLoading && productosOrdenados.length === 0 && (
                  <div className="sin-productos" style={{ gridColumn: '1 / -1' }}>
                    <p>No se encontraron productos que coincidan con los filtros seleccionados.</p>
                  </div>
                )}
              </main>

            </div>
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
};

export default PaginaProductos;
