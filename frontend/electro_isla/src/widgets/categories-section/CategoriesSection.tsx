/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🏷️ WIDGET - Nuestras Categorías
 * ═══════════════════════════════════════════════════════════════════════════════
 * Sección de categorías principales con tarjetas interactivas
 */

import React from 'react';
import { Link } from 'react-router-dom';
import {
  MdElectricBolt,
  MdBuild,
  MdChair,
  MdMoreHoriz,
  MdKitchen,
} from 'react-icons/md';
import { AnimatedTitle } from '@/widgets/bottom-carousel/AnimatedTitle';
import './CategoriesSection.css';

interface Category {
  id: string;
  nombre: string;
  icono: React.ReactNode;
  slug: string;
  imagen: string;
  descripcion: string;
}

const categorias: Category[] = [
  {
    id: '1',
    nombre: 'Electrodomésticos',
    icono: <MdKitchen size={48} />,
    slug: 'electrodomesticos',
    imagen: '/Categorias/Electrodomesticos.png',
    descripcion: 'Electrodomésticos de calidad para tu hogar. Refrigeradores, lavadoras, hornos y más.',
  },
  {
    id: '2',
    nombre: 'Energía y Tecnología',
    icono: <MdElectricBolt size={48} />,
    slug: 'energia_tecnologia',
    imagen: '/Categorias/energia.png',
    descripcion: 'Soluciones de energía renovable y tecnología avanzada para tu negocio.',
  },
  {
    id: '3',
    nombre: 'Herramientas',
    icono: <MdBuild size={48} />,
    slug: 'herramientas',
    imagen: '/Categorias/Herramientas.png',
    descripcion: 'Herramientas profesionales y de calidad para todos tus proyectos.',
  },
  {
    id: '4',
    nombre: 'Hogar y Entretenimiento',
    icono: <MdChair size={48} />,
    slug: 'hogar_entretenimiento',
    imagen: '/Categorias/hogar.png',
    descripcion: 'Muebles elegantes y funcionales para decorar tu hogar con estilo.',
  },
  {
    id: '5',
    nombre: 'Otros Artículos',
    icono: <MdMoreHoriz size={48} />,
    slug: 'otros',
    imagen: '/Categorias/otros.png',
    descripcion: 'Descubre una variedad de productos especiales y únicos.',
  },
];

export const CategoriesSection: React.FC = () => {
  return (
    <section className="categories-section">
      <div className="categories-container">
        {/* Encabezado con línea animada - Usando componente reutilizable */}
        <div className="categories-header">
          <AnimatedTitle text="Nuestras Categorías" />
        </div>

        {/* Grid de categorías - 5 columnas, 1 fila */}
        <div className="categories-grid">
          {categorias.map((categoria) => (
            <Link
              key={categoria.id}
              to={`/productos?categoria=${categoria.slug}`}
              className="categoria-card"
              style={{ backgroundImage: `url(${categoria.imagen})` } as React.CSSProperties}
            >
              {/* Overlay oscuro */}
              <div className="categoria-overlay"></div>

              {/* Contenido - nombre arriba con texto blanco */}
              <div className="categoria-card-contenido">
                <h3 className="categoria-nombre">{categoria.nombre}</h3>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
};
