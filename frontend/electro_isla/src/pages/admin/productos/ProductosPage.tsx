/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📄 PAGE - Gestión de Productos
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { useState, useMemo, useCallback } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { FiSearch, FiPlus, FiEdit2, FiTrash2, FiEye, FiEyeOff } from 'react-icons/fi';
import api from '@/shared/api/axios';
import { useAuthStore } from '@/app/store/useAuthStore';
import { ImageUpload } from '@/shared/ui/ImageUpload';
import { GlobalLoading } from '@/shared/ui/GlobalLoading';
import { useInvalidateAdminQueries } from '@/shared/hooks/useInvalidateAdminQueries';
import './ProductosPage.css';

interface Producto {
  id: number;
  nombre: string;
  descripcion: string;
  precio: string;
  descuento: number;
  stock: number;
  categoria: string;
  imagen_url: string | null;
  imagen?: string | null;  // URL de archivo
  activo: boolean;
  en_carrusel: boolean;
  en_carousel_card: boolean;
  en_all_products: boolean;
  creado_por_username: string;
  created_at: string;
}

interface ProductoForm {
  nombre: string;
  descripcion: string;
  precio: string;
  descuento: string | number;
  stock: string | number;
  categoria: string;
  imagen_url?: string;
  imagen?: File | string | null;
  activo: boolean;
  en_carrusel: boolean;
  en_carousel_card: boolean;
  en_all_products: boolean;
}

const CATEGORIAS = [
  { value: 'electrodomesticos', label: 'Electrodomésticos' },
  { value: 'energia_tecnologia', label: 'Energía y Tecnología' },
  { value: 'herramientas', label: 'Herramientas' },
  { value: 'hogar_entretenimiento', label: 'Hogar y Entretenimiento' },
  { value: 'otros', label: 'Otros Artículos' },
];

const fetchProductos = async (filters: { search?: string; categoria?: string; activo?: string }): Promise<Producto[]> => {
  const params = new URLSearchParams();
  if (filters.search) params.append('search', filters.search);
  if (filters.categoria) params.append('categoria', filters.categoria);
  if (filters.activo) params.append('activo', filters.activo);
  
  const response = await api.get(`/admin/productos/?${params.toString()}`);
  // DRF retorna objeto paginado, extraer results
  return response.data.results || response.data;
};

const createProducto = async (data: ProductoForm) => {
  // ✅ Usar FormData para enviar archivo
  const formData = new FormData();
  formData.append('nombre', data.nombre);
  formData.append('descripcion', data.descripcion);
  formData.append('precio', data.precio);
  formData.append('descuento', String(data.descuento));
  formData.append('stock', String(data.stock));
  formData.append('stock_total', String(data.stock));
  formData.append('categoria', data.categoria);
  formData.append('activo', String(data.activo));
  formData.append('en_carrusel', String(data.en_carrusel));
  formData.append('en_carousel_card', String(data.en_carousel_card));
  formData.append('en_all_products', String(data.en_all_products));
  
  // Agregar imagen si es un File
  if (data.imagen instanceof File) {
    formData.append('imagen', data.imagen);
  }
  
  const response = await api.post('/admin/productos/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

const updateProducto = async (data: { id: number; updates: Partial<ProductoForm> }) => {
  // ✅ Usar FormData para enviar archivo
  const formData = new FormData();
  
  if (data.updates.nombre) formData.append('nombre', data.updates.nombre);
  if (data.updates.descripcion) formData.append('descripcion', data.updates.descripcion);
  if (data.updates.precio) formData.append('precio', data.updates.precio);
  if (data.updates.descuento !== undefined) formData.append('descuento', String(data.updates.descuento));
  if (data.updates.stock !== undefined) {
    formData.append('stock', String(data.updates.stock));
    formData.append('stock_total', String(data.updates.stock));
  }
  if (data.updates.categoria) formData.append('categoria', data.updates.categoria);
  if (data.updates.activo !== undefined) formData.append('activo', String(data.updates.activo));
  if (data.updates.en_carrusel !== undefined) formData.append('en_carrusel', String(data.updates.en_carrusel));
  if (data.updates.en_carousel_card !== undefined) formData.append('en_carousel_card', String(data.updates.en_carousel_card));
  if (data.updates.en_all_products !== undefined) formData.append('en_all_products', String(data.updates.en_all_products));
  
  // Agregar imagen si es un File
  if (data.updates.imagen instanceof File) {
    formData.append('imagen', data.updates.imagen);
  }
  
  const response = await api.patch(`/admin/productos/${data.id}/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

const deleteProducto = async (id: number) => {
  await api.delete(`/admin/productos/${id}/`);
};

export const ProductosPage = () => {
  const { user } = useAuthStore();
  const invalidateQueries = useInvalidateAdminQueries({ additionalKeys: ['admin-productos'] });
  
  const [search, setSearch] = useState('');
  const [categoriaFilter, setCategoriaFilter] = useState('');
  const [activoFilter, setActivoFilter] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingProducto, setEditingProducto] = useState<Producto | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [selectedProducto, setSelectedProducto] = useState<Producto | null>(null);
  const [showCarouselLimitModal, setShowCarouselLimitModal] = useState(false);

  const [formData, setFormData] = useState<ProductoForm>({
    nombre: '',
    descripcion: '',
    precio: '',
    descuento: '',
    stock: '',
    categoria: 'otros',
    imagen_url: '',
    imagen: null,
    activo: true,
    en_carrusel: false,
    en_carousel_card: true,
    en_all_products: true,
  });

  // Query productos
  const { data: productos = [], isLoading } = useQuery({
    queryKey: ['admin-productos', search, categoriaFilter, activoFilter],
    queryFn: () => fetchProductos({ search, categoria: categoriaFilter, activo: activoFilter }),
    staleTime: 10 * 1000, // ✅ 10 segundos - Balance entre freshness y rendimiento
    gcTime: 1000 * 60 * 5, // Mantener en memoria 5 minutos si no se usa
  });

  // Memoizar cálculo de productos en carrusel
  const productosEnCarruselCount = useMemo(
    () => productos.filter((p) => p.en_carrusel).length,
    [productos]
  );

  // Mutations
  const createMutation = useMutation({
    mutationFn: createProducto,
    onSuccess: () => {
      invalidateQueries();
      handleCloseModal();
      // ✅ Disparar evento para refrescar carrusel
      window.dispatchEvent(new Event('productChanged'));
    },
  });

  const updateMutation = useMutation({
    mutationFn: updateProducto,
    onSuccess: () => {
      invalidateQueries();
      handleCloseModal();
      // ✅ Disparar evento para refrescar carrusel
      window.dispatchEvent(new Event('productChanged'));
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteProducto,
    onSuccess: () => {
      invalidateQueries();
      setShowDeleteConfirm(false);
      setSelectedProducto(null);
      // ✅ Disparar evento para refrescar carrusel
      window.dispatchEvent(new Event('productChanged'));
    },
  });

  const handleOpenModal = useCallback((producto?: Producto) => {
    if (producto) {
      setEditingProducto(producto);
      setFormData({
        nombre: producto.nombre,
        descripcion: producto.descripcion,
        precio: producto.precio,
        descuento: producto.descuento ? String(producto.descuento) : '',
        stock: String(producto.stock),
        categoria: producto.categoria,
        imagen_url: producto.imagen_url || '',
        // Mostrar imagen actual (prioridad: imagen > imagen_url)
        imagen: (producto.imagen || producto.imagen_url) as any,
        activo: producto.activo,
        en_carrusel: producto.en_carrusel || false,
        en_carousel_card: producto.en_carousel_card,
        en_all_products: producto.en_all_products,
      });
    } else {
      setEditingProducto(null);
      setFormData({
        nombre: '',
        descripcion: '',
        precio: '',
        descuento: '',
        stock: '',
        categoria: 'otros',
        imagen_url: '',
        imagen: null,
        activo: false,
        en_carrusel: false,
        en_carousel_card: true,
        en_all_products: true,
      });
    }
    setShowModal(true);
  }, []);

  const handleCloseModal = useCallback(() => {
    setShowModal(false);
    setEditingProducto(null);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validar límite de 5 productos en carrusel
    if (formData.en_carrusel) {
      const productosEnCarrusel = productos.filter((p) => p.en_carrusel && p.id !== editingProducto?.id).length;
      
      if (productosEnCarrusel >= 5) {
        setShowCarouselLimitModal(true);
        return;
      }
    }
    
    if (editingProducto) {
      updateMutation.mutate({
        id: editingProducto.id,
        updates: formData,
      });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleToggleActive = (producto: Producto) => {
    updateMutation.mutate({
      id: producto.id,
      updates: { activo: !producto.activo },
    });
  };

  const handleDelete = () => {
    if (selectedProducto) {
      deleteMutation.mutate(selectedProducto.id);
    }
  };

  const canEdit = user?.rol === 'admin' || user?.rol === 'trabajador';
  const canDelete = user?.rol === 'admin';

  return (
    <div className="productos-page">
      {/* Header */}
      <div className="productos-header">
        <div>
          <h1 className="productos-title">Gestión de Productos</h1>
          <p className="productos-subtitle">
            Administra el catálogo de productos ({productosEnCarruselCount} en carrusel)
          </p>
        </div>
        {canEdit && (
          <button
            className="productos-btn-add"
            onClick={() => handleOpenModal()}
          >
            <FiPlus />
            <span>Nuevo Producto</span>
          </button>
        )}
      </div>

      {/* Filtros */}
      <div className="productos-filters">
        <div className="productos-search">
          <FiSearch className="productos-search-icon" />
          <input
            type="text"
            placeholder="Buscar productos..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="productos-search-input"
          />
        </div>

        <select
          value={categoriaFilter}
          onChange={(e) => setCategoriaFilter(e.target.value)}
          className="productos-filter-select"
        >
          <option value="">Todas las categorías</option>
          {CATEGORIAS.map((cat) => (
            <option key={cat.value} value={cat.value}>
              {cat.label}
            </option>
          ))}
        </select>

        <select
          value={activoFilter}
          onChange={(e) => setActivoFilter(e.target.value)}
          className="productos-filter-select"
        >
          <option value="">Todos los estados</option>
          <option value="true">Activos</option>
          <option value="false">Inactivos</option>
        </select>
      </div>

      {/* Grid de productos */}
      {isLoading ? (
        <div className="productos-loading">
          <div className="productos-spinner"></div>
          <p>Cargando productos...</p>
        </div>
      ) : (
        <div className="productos-grid">
          {productos.map((producto) => (
            <div key={producto.id} className="producto-card">
              <div className="producto-card-image">
                {producto.imagen_url ? (
                  <img src={producto.imagen_url} alt={producto.nombre} />
                ) : (
                  <div className="producto-card-no-image">Sin imagen</div>
                )}
                <div className="producto-card-badge">
                  {CATEGORIAS.find((c) => c.value === producto.categoria)?.label}
                </div>
              </div>

              <div className="producto-card-content">
                <h3 className="producto-card-title">{producto.nombre}</h3>
                <p className="producto-card-description">
                  {producto.descripcion.length > 100
                    ? `${producto.descripcion.substring(0, 100)}...`
                    : producto.descripcion}
                </p>

                <div className="producto-card-info">
                  <div className="producto-card-price">${producto.precio}</div>
                  <div className="producto-card-stock">
                    Stock: <strong>{producto.stock}</strong>
                  </div>
                </div>

                <div className="producto-card-details">
                  {producto.descuento > 0 && (
                    <span className="producto-card-discount">
                      Desc: {producto.descuento}%
                    </span>
                  )}
                  {producto.en_carrusel && (
                    <span className="producto-card-carousel">
                      En Carrusel
                    </span>
                  )}
                </div>

                <div className="producto-card-meta">
                  <span className={`producto-card-status ${producto.activo ? 'active' : 'inactive'}`}>
                    {producto.activo ? 'Activo' : 'Inactivo'}
                  </span>
                  <span className="producto-card-author">
                    Por: {producto.creado_por_username}
                  </span>
                </div>
              </div>

              <div className="producto-card-actions">
                {canEdit && (
                  <>
                    <button
                      className="producto-action-btn producto-action-edit"
                      onClick={() => handleOpenModal(producto)}
                      title="Editar"
                    >
                      <FiEdit2 />
                    </button>
                    <button
                      className="producto-action-btn producto-action-toggle"
                      onClick={() => handleToggleActive(producto)}
                      title={producto.activo ? 'Desactivar' : 'Activar'}
                    >
                      {producto.activo ? <FiEyeOff /> : <FiEye />}
                    </button>
                  </>
                )}
                {canDelete && (
                  <button
                    className="producto-action-btn producto-action-delete"
                    onClick={() => {
                      setSelectedProducto(producto);
                      setShowDeleteConfirm(true);
                    }}
                    title="Eliminar"
                  >
                    <FiTrash2 />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {productos.length === 0 && !isLoading && (
        <div className="productos-empty">
          <p>No se encontraron productos</p>
        </div>
      )}

      {/* Modal de formulario */}
      {showModal && (
        <div className="productos-modal-overlay">
          <div className="productos-modal">
            <h3 className="productos-modal-title">
              {editingProducto ? 'Editar Producto' : 'Nuevo Producto'}
            </h3>

            <form onSubmit={handleSubmit} className="productos-form">
              <div className="productos-form-field">
                <label>Nombre *</label>
                <input
                  type="text"
                  value={formData.nombre}
                  onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                  required
                />
              </div>

              <div className="productos-form-field">
                <label>Descripción *</label>
                <textarea
                  value={formData.descripcion}
                  onChange={(e) => setFormData({ ...formData, descripcion: e.target.value })}
                  rows={4}
                  required
                />
              </div>

              <div className="productos-form-row">
                <div className="productos-form-field">
                  <label>Precio *</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    value={formData.precio}
                    onChange={(e) => {
                      // ✅ NO redondear - dejar que el backend valide
                      setFormData({ ...formData, precio: e.target.value });
                    }}
                    required
                  />
                </div>

                <div className="productos-form-field">
                  <label>Descuento (%)</label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={formData.descuento}
                    onChange={(e) => setFormData({ ...formData, descuento: e.target.value })}
                  />
                </div>

                <div className="productos-form-field">
                  <label>Stock *</label>
                  <input
                    type="number"
                    value={formData.stock}
                    onChange={(e) => setFormData({ ...formData, stock: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className="productos-form-field">
                <label>Categoría *</label>
                <select
                  value={formData.categoria}
                  onChange={(e) => setFormData({ ...formData, categoria: e.target.value })}
                  required
                >
                  {CATEGORIAS.map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="productos-form-field">
                <label>Imagen del Producto</label>
                <ImageUpload
                  value={formData.imagen || formData.imagen_url || null}
                  onChange={(file) => setFormData({ ...formData, imagen: file })}
                />
              </div>

              {/* Grid de 2x2 para checkboxes */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: 'var(--espaciado-md)',
                marginBottom: 'var(--espaciado-lg)'
              }}>
                <div className="productos-form-field productos-form-checkbox">
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.activo}
                      onChange={(e) => setFormData({ ...formData, activo: e.target.checked })}
                    />
                    <span>Producto activo</span>
                  </label>
                </div>

                <div className="productos-form-field productos-form-checkbox">
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.en_carrusel}
                      onChange={(e) => setFormData({ ...formData, en_carrusel: e.target.checked })}
                    />
                    <span>Carrusel principal</span>
                  </label>
                </div>

                <div className="productos-form-field productos-form-checkbox">
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.en_carousel_card}
                      onChange={(e) => setFormData({ ...formData, en_carousel_card: e.target.checked })}
                    />
                    <span>Tarjetas inferiores</span>
                  </label>
                </div>

                <div className="productos-form-field productos-form-checkbox">
                  <label>
                    <input
                      type="checkbox"
                      checked={formData.en_all_products}
                      onChange={(e) => setFormData({ ...formData, en_all_products: e.target.checked })}
                    />
                    <span>Catálogo completo</span>
                  </label>
                </div>
              </div>

              <div className="productos-form-actions">
                <button
                  type="button"
                  className="productos-form-btn productos-form-btn-cancel"
                  onClick={handleCloseModal}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="productos-form-btn productos-form-btn-submit"
                  disabled={createMutation.isPending || updateMutation.isPending}
                >
                  {createMutation.isPending || updateMutation.isPending
                    ? 'Guardando...'
                    : editingProducto
                    ? 'Actualizar'
                    : 'Crear'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal de confirmación de eliminación */}
      {showDeleteConfirm && selectedProducto && (
        <div className="productos-modal-overlay">
          <div className="productos-modal">
            <h3 className="productos-modal-title">Confirmar Eliminación</h3>
            <p className="productos-modal-text">
              ¿Estás seguro de que deseas eliminar el producto <strong>{selectedProducto.nombre}</strong>?
              Esta acción no se puede deshacer.
            </p>
            <div className="productos-modal-actions">
              <button
                className="productos-modal-btn productos-modal-btn-cancel"
                onClick={() => setShowDeleteConfirm(false)}
              >
                Cancelar
              </button>
              <button
                className="productos-modal-btn productos-modal-btn-confirm"
                onClick={handleDelete}
                disabled={deleteMutation.isPending}
              >
                {deleteMutation.isPending ? 'Eliminando...' : 'Eliminar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de límite de carrusel */}
      {showCarouselLimitModal && (
        <div className="productos-modal-overlay">
          <div className="productos-modal">
            <h3 className="productos-modal-title">⚠️ Límite de Carrusel Alcanzado</h3>
            <p className="productos-modal-text">
              El carrusel principal ya tiene <strong>5 productos</strong>. 
              No puedes agregar más productos al carrusel en este momento.
            </p>
            <p className="productos-modal-text" style={{ fontSize: '14px', color: '#64748b', marginTop: '12px' }}>
              Para agregar un nuevo producto al carrusel, primero debes remover uno de los productos existentes.
            </p>
            <div className="productos-modal-actions">
              <button
                className="productos-modal-btn productos-modal-btn-confirm"
                onClick={() => setShowCarouselLimitModal(false)}
              >
                Entendido
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Loading Global */}
      <GlobalLoading 
        isLoading={createMutation.isPending || updateMutation.isPending || deleteMutation.isPending} 
        message={
          createMutation.isPending ? 'Creando producto...' :
          updateMutation.isPending ? 'Actualizando producto...' :
          'Eliminando producto...'
        } 
      />
    </div>
  );
};
