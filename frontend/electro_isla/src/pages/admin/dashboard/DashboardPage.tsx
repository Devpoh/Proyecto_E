/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📄 PAGE - Admin Dashboard
 * ═══════════════════════════════════════════════════════════════════════════════
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { FiUsers, FiPackage, FiTrendingUp, FiActivity } from 'react-icons/fi';
import api from '@/shared/api/axios';
import { useAuthStore } from '@/app/store/useAuthStore';
import { DateRangeFilter, getDateRange } from '@/shared/ui/DateRangeFilter';
import type { DateRangeOption } from '@/shared/ui/DateRangeFilter';
import './DashboardPage.css';

interface DashboardStats {
  usuarios: {
    total: number;
    activos: number;
    nuevos_7d: number;
  };
  productos: {
    total: number;
    activos: number;
    nuevos_7d: number;
  };
  rol_usuario: string;
}

const fetchDashboardStats = async (dateRange?: { desde: string | null; hasta: string | null }): Promise<DashboardStats> => {
  const params = new URLSearchParams();
  if (dateRange?.desde) params.append('fecha_desde', dateRange.desde);
  if (dateRange?.hasta) params.append('fecha_hasta', dateRange.hasta);
  
  try {
    // ✅ Obtener token desde Zustand (no desde localStorage)
    const { accessToken } = useAuthStore.getState();
    if (!accessToken) {
      throw new Error('No hay token de autenticación disponible');
    }
    
    const response = await api.get(`/admin/dashboard/stats/?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    throw error;
  }
};

export const DashboardPage = () => {
  const [dateRangeOption, setDateRangeOption] = useState<DateRangeOption>('month');
  const dateRange = getDateRange(dateRangeOption);

  const { data: stats, isLoading, isError, error } = useQuery<DashboardStats>({
    queryKey: ['dashboard-stats', dateRangeOption],
    queryFn: () => fetchDashboardStats(dateRange),
    refetchInterval: 3000, // Actualizar cada 3 segundos (más frecuente)
    refetchIntervalInBackground: true, // Actualizar en segundo plano
    refetchOnWindowFocus: true, // Actualizar al volver a la pestaña
    refetchOnMount: 'always', // Siempre actualizar al montar
    refetchOnReconnect: true, // Actualizar al reconectar
    staleTime: 0, // Datos siempre obsoletos (forzar actualización)
    retry: 3, // Reintentar 3 veces si falla
  });

  // Skeleton Loader mientras carga
  if (isLoading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-header">
          <div>
            <h1 className="dashboard-title">Dashboard</h1>
            <p className="dashboard-subtitle">Cargando estadísticas...</p>
          </div>
        </div>
        <div className="dashboard-stats">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="dashboard-card dashboard-card-skeleton">
              <div className="skeleton-header"></div>
              <div className="skeleton-body"></div>
              <div className="skeleton-footer"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-header">
          <div>
            <h1 className="dashboard-title">Dashboard</h1>
            <p className="dashboard-subtitle" style={{ color: 'var(--color-peligro)' }}>
              Error al cargar estadísticas: {error?.message || 'Error desconocido'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  const cards = [
    {
      title: 'Total Usuarios',
      value: stats?.usuarios.total || 0,
      subtitle: `${stats?.usuarios.activos || 0} activos`,
      icon: FiUsers,
      color: 'blue',
      trend: `+${stats?.usuarios.nuevos_7d || 0} esta semana`,
    },
    {
      title: 'Total Productos',
      value: stats?.productos.total || 0,
      subtitle: `${stats?.productos.activos || 0} activos`,
      icon: FiPackage,
      color: 'green',
      trend: `+${stats?.productos.nuevos_7d || 0} esta semana`,
    },
    {
      title: 'Ventas del Mes',
      value: '0',
      subtitle: 'Próximamente',
      icon: FiTrendingUp,
      color: 'yellow',
      trend: 'En desarrollo',
    },
    {
      title: 'Actividad',
      value: '100%',
      subtitle: 'Sistema operativo',
      icon: FiActivity,
      color: 'purple',
      trend: 'Todo funcionando',
    },
  ];

  return (
    <div className="dashboard-page">
      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Dashboard</h1>
          <p className="dashboard-subtitle">
            Bienvenido al panel de administración
          </p>
        </div>
        <DateRangeFilter 
          value={dateRangeOption} 
          onChange={setDateRangeOption}
          label="Período de Estadísticas"
        />
      </div>

      {/* Stats Cards */}
      <div className="dashboard-stats">
        {cards.map((card, index) => (
          <div key={index} className={`dashboard-card dashboard-card-${card.color}`}>
            <div className="dashboard-card-header">
              <div className="dashboard-card-icon-wrapper">
                <card.icon className="dashboard-card-icon" />
              </div>
              <h3 className="dashboard-card-title">{card.title}</h3>
            </div>
            <div className="dashboard-card-body">
              <p className="dashboard-card-value">{card.value}</p>
              <p className="dashboard-card-subtitle">{card.subtitle}</p>
            </div>
            <div className="dashboard-card-footer">
              <span className="dashboard-card-trend">{card.trend}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="dashboard-section">
        <h2 className="dashboard-section-title">Accesos Rápidos</h2>
        <div className="dashboard-quick-actions">
          <Link to="/admin/productos" className="dashboard-quick-action">
            <FiPackage />
            <span>Gestionar Productos</span>
          </Link>
          <Link to="/admin/usuarios" className="dashboard-quick-action">
            <FiUsers />
            <span>Gestionar Usuarios</span>
          </Link>
          <Link to="/admin/pedidos" className="dashboard-quick-action">
            <FiTrendingUp />
            <span>Ver Pedidos</span>
          </Link>
        </div>
      </div>
    </div>
  );
};
