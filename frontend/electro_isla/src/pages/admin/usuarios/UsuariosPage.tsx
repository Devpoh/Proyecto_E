/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📄 PAGE - Gestión de Usuarios (CON PRIVACIDAD)
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * POLÍTICAS DE PRIVACIDAD IMPLEMENTADAS:
 * - Emails parcialmente ocultos en listado (j***@ejemplo.com)
 * - No se exponen contraseñas (nunca)
 * - Solo admin y trabajador pueden acceder
 * - Trabajadores no pueden modificar admins
 * - Logs de acciones sensibles
 * - Confirmación para acciones destructivas
 */

import { useState, useCallback } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { FiSearch, FiEdit2, FiX } from 'react-icons/fi';
import api from '@/shared/api/axios';
import { useAuthStore } from '@/app/store/useAuthStore';
import { GlobalLoading } from '@/shared/ui/GlobalLoading';
import { useInvalidateAdminQueries } from '@/shared/hooks/useInvalidateAdminQueries';
import './UsuariosPage.css';

interface User {
  id: number;
  username: string;
  email_parcial: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  rol: 'cliente' | 'mensajero' | 'trabajador' | 'admin';
  fecha_registro: string;
  ultimo_acceso: string | null;
}

interface UserDetail extends Omit<User, 'email_parcial'> {
  email: string;
  profile: {
    rol: string;
    telefono: string | null;
    direccion: string | null;
  };
}

const fetchUsers = async (filters: { search?: string; rol?: string; activo?: string }): Promise<User[]> => {
  const params = new URLSearchParams();
  if (filters.search) params.append('search', filters.search);
  if (filters.rol) params.append('rol', filters.rol);
  if (filters.activo) params.append('activo', filters.activo);
  
  const response = await api.get(`/admin/users/?${params.toString()}`);
  // DRF retorna objeto paginado, extraer results
  return response.data.results || response.data;
};

const updateUser = async (data: { id: number; updates: Partial<UserDetail> }) => {
  const response = await api.patch(`/admin/users/${data.id}/`, data.updates);
  return response.data;
};

const deleteUser = async (id: number) => {
  await api.delete(`/admin/users/${id}/`);
};

export const UsuariosPage = () => {
  const { user: currentUser } = useAuthStore();
  const invalidateQueries = useInvalidateAdminQueries({ additionalKeys: ['admin-users'] });
  
  const [search, setSearch] = useState('');
  const [rolFilter, setRolFilter] = useState('');
  const [activoFilter, setActivoFilter] = useState('');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editForm, setEditForm] = useState<{ rol: 'cliente' | 'mensajero' | 'trabajador' | 'admin'; is_active: boolean }>({ rol: 'cliente', is_active: true });

  // Query usuarios
  const { data: usuarios = [], isLoading } = useQuery({
    queryKey: ['admin-users', search, rolFilter, activoFilter],
    queryFn: () => fetchUsers({ search, rol: rolFilter, activo: activoFilter }),
  });

  // Mutation actualizar
  const updateMutation = useMutation({
    mutationFn: updateUser,
    onSuccess: () => {
      invalidateQueries();
      setSelectedUser(null);
      setShowEditModal(false);
    },
  });

  // Mutation eliminar
  const deleteMutation = useMutation({
    mutationFn: deleteUser,
    onSuccess: () => {
      invalidateQueries();
      setShowDeleteConfirm(false);
      setSelectedUser(null);
    },
  });

  const handleOpenEdit = useCallback((user: User) => {
    setSelectedUser(user);
    setEditForm({ rol: user.rol, is_active: user.is_active });
    setShowEditModal(true);
  }, []);

  const handleSaveEdit = useCallback(() => {
    if (selectedUser) {
      updateMutation.mutate({
        id: selectedUser.id,
        updates: editForm,
      });
    }
  }, [selectedUser, editForm, updateMutation]);

  const handleDelete = useCallback(() => {
    if (selectedUser) {
      deleteMutation.mutate(selectedUser.id);
    }
  }, [selectedUser, deleteMutation]);

  const getRolBadgeClass = (rol: string) => {
    switch (rol) {
      case 'admin': return 'badge-admin';
      case 'trabajador': return 'badge-trabajador';
      case 'mensajero': return 'badge-mensajero';
      default: return 'badge-cliente';
    }
  };

  const getRolLabel = (rol: string) => {
    switch (rol) {
      case 'admin': return 'Administrador';
      case 'trabajador': return 'Trabajador';
      case 'mensajero': return 'Repartidor';
      default: return 'Cliente';
    }
  };

  // Verificar permisos (solo admin puede editar usuarios)
  const canEdit = currentUser?.rol === 'admin';

  return (
    <div className="usuarios-page">
      {/* Header */}
      <div className="usuarios-header">
        <div>
          <h1 className="usuarios-title">Gestión de Usuarios</h1>
          <p className="usuarios-subtitle">
            Administra usuarios respetando su privacidad
          </p>
        </div>
      </div>

      {/* Filtros */}
      <div className="usuarios-filters">
        <div className="usuarios-search">
          <FiSearch className="usuarios-search-icon" />
          <input
            type="text"
            placeholder="Buscar por nombre o usuario..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="usuarios-search-input"
          />
        </div>

        <select
          value={rolFilter}
          onChange={(e) => setRolFilter(e.target.value)}
          className="usuarios-filter-select"
        >
          <option value="">Todos los roles</option>
          <option value="admin">Administrador</option>
          <option value="trabajador">Trabajador</option>
          <option value="mensajero">Mensajero</option>
          <option value="cliente">Cliente</option>
        </select>

        <select
          value={activoFilter}
          onChange={(e) => setActivoFilter(e.target.value)}
          className="usuarios-filter-select"
        >
          <option value="">Todos los estados</option>
          <option value="true">Activos</option>
          <option value="false">Inactivos</option>
        </select>
      </div>

      {/* Tabla */}
      {isLoading ? (
        <div className="usuarios-loading">
          <div className="usuarios-spinner"></div>
          <p>Cargando usuarios...</p>
        </div>
      ) : (
        <div className="usuarios-table-container">
          <table className="usuarios-table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Email</th>
                <th>Nombre</th>
                <th>Rol</th>
                <th>Estado</th>
                <th>Registro</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map((user) => (
                <tr key={user.id}>
                  <td className="usuarios-table-username">{user.username}</td>
                  <td className="usuarios-table-email">
                    {user.email_parcial}
                    <span className="usuarios-privacy-badge">Privado</span>
                  </td>
                  <td>{`${user.first_name} ${user.last_name}`.trim() || '-'}</td>
                  <td>
                    <span className={`usuarios-badge ${getRolBadgeClass(user.rol)}`}>
                      {getRolLabel(user.rol)}
                    </span>
                  </td>
                  <td>
                    <span className={`usuarios-status ${user.is_active ? 'active' : 'inactive'}`}>
                      {user.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </td>
                  <td className="usuarios-table-date">
                    {new Date(user.fecha_registro).toLocaleDateString('es-ES')}
                  </td>
                  <td>
                    <div className="usuarios-actions">
                      {canEdit && (
                        <button
                          className="usuarios-action-btn usuarios-action-edit"
                          onClick={() => handleOpenEdit(user)}
                          title="Editar usuario"
                          disabled={user.id === currentUser?.id}
                        >
                          <FiEdit2 />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {usuarios.length === 0 && (
            <div className="usuarios-empty">
              <p>No se encontraron usuarios</p>
            </div>
          )}
        </div>
      )}

      {/* Modal de edición */}
      {showEditModal && selectedUser && (
        <div className="usuarios-modal-overlay">
          <div className="usuarios-modal usuarios-modal-edit">
            <div className="usuarios-modal-header">
              <h3 className="usuarios-modal-title">Editar Usuario</h3>
              <button
                className="usuarios-modal-close"
                onClick={() => setShowEditModal(false)}
              >
                <FiX />
              </button>
            </div>
            
            <div className="usuarios-modal-body">
              <div className="usuarios-form-group">
                <label className="usuarios-form-label">Usuario</label>
                <input
                  type="text"
                  value={selectedUser.username}
                  disabled
                  className="usuarios-form-input usuarios-form-input-disabled"
                />
              </div>

              <div className="usuarios-form-group">
                <label className="usuarios-form-label">Nombre Completo</label>
                <input
                  type="text"
                  value={`${selectedUser.first_name} ${selectedUser.last_name}`.trim() || 'Sin nombre'}
                  disabled
                  className="usuarios-form-input usuarios-form-input-disabled"
                />
              </div>

              <div className="usuarios-form-group">
                <label className="usuarios-form-label">Rol</label>
                <select
                  value={editForm.rol}
                  onChange={(e) => setEditForm({ ...editForm, rol: e.target.value as 'cliente' | 'mensajero' | 'trabajador' | 'admin' })}
                  className="usuarios-form-select"
                >
                  <option value="cliente">Cliente</option>
                  <option value="mensajero">Mensajero</option>
                  <option value="trabajador">Trabajador</option>
                  {currentUser?.rol === 'admin' && (
                    <option value="admin">Administrador</option>
                  )}
                </select>
                <p className="usuarios-form-hint">
                  Cambiar el rol modificará los permisos del usuario
                </p>
              </div>

              <div className="usuarios-form-group">
                <label className="usuarios-form-label">Estado</label>
                <div className="usuarios-form-toggle">
                  <label className="usuarios-toggle">
                    <input
                      type="checkbox"
                      checked={editForm.is_active}
                      onChange={(e) => setEditForm({ ...editForm, is_active: e.target.checked })}
                    />
                    <span className="usuarios-toggle-slider"></span>
                  </label>
                  <span className="usuarios-toggle-label">
                    {editForm.is_active ? 'Usuario Activo' : 'Usuario Inactivo'}
                  </span>
                </div>
                <p className="usuarios-form-hint">
                  Los usuarios inactivos no podrán iniciar sesión
                </p>
              </div>
            </div>

            <div className="usuarios-modal-actions">
              <button
                className="usuarios-modal-btn usuarios-modal-btn-cancel"
                onClick={() => setShowEditModal(false)}
              >
                Cancelar
              </button>
              <button
                className="usuarios-modal-btn usuarios-modal-btn-confirm"
                onClick={handleSaveEdit}
                disabled={updateMutation.isPending}
              >
                {updateMutation.isPending ? 'Guardando...' : 'Guardar Cambios'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de confirmación de eliminación */}
      {showDeleteConfirm && selectedUser && (
        <div className="usuarios-modal-overlay">
          <div className="usuarios-modal">
            <h3 className="usuarios-modal-title">Confirmar Eliminación</h3>
            <p className="usuarios-modal-text">
              ¿Estás seguro de que deseas eliminar al usuario <strong>{selectedUser.username}</strong>?
              Esta acción no se puede deshacer.
            </p>
            <div className="usuarios-modal-actions">
              <button
                className="usuarios-modal-btn usuarios-modal-btn-cancel"
                onClick={() => setShowDeleteConfirm(false)}
              >
                Cancelar
              </button>
              <button
                className="usuarios-modal-btn usuarios-modal-btn-confirm"
                onClick={handleDelete}
                disabled={deleteMutation.isPending}
              >
                {deleteMutation.isPending ? 'Eliminando...' : 'Eliminar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Loading Global */}
      <GlobalLoading 
        isLoading={updateMutation.isPending || deleteMutation.isPending} 
        message={
          updateMutation.isPending ? 'Actualizando usuario...' :
          'Eliminando usuario...'
        } 
      />
    </div>
  );
};
