/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 📊 PAGE - Estadísticas Avanzadas con Gráficos
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * NOTA: Requiere instalar dependencias:
 * npm install chart.js react-chartjs-2 jspdf jspdf-autotable xlsx
 */

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FiDownload, FiTrendingUp, FiUsers, FiPackage, FiDollarSign } from 'react-icons/fi';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import * as XLSX from 'xlsx';
import api from '@/shared/api/axios';
import './EstadisticasPage.css';

// Registrar componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface EstadisticasVentas {
  ventas_por_mes: Array<{ mes: string; total: number; pedidos: number }>;
  productos_mas_vendidos: Array<{ producto__nombre: string; cantidad_vendida: number; ingresos: number }>;
  metodos_pago: Array<{ metodo_pago: string; count: number; total: number }>;
  ticket_promedio: number;
}

interface EstadisticasUsuarios {
  usuarios_por_mes: Array<{ mes: string; nuevos: number }>;
  usuarios_por_rol: Array<{ rol: string; count: number }>;
  usuarios_mas_activos: Array<{ username: string; pedidos_count: number }>;
  tasa_retencion: number;
}

interface EstadisticasProductos {
  productos_por_categoria: Array<{ categoria: string; count: number; stock_total: number }>;
  stock_bajo: Array<{ nombre: string; stock: number }>;
  productos_sin_stock: number;
  valor_inventario: number;
}

const fetchEstadisticasVentas = async (): Promise<EstadisticasVentas> => {
  const response = await api.get('/admin/estadisticas/ventas/');
  return response.data;
};

const fetchEstadisticasUsuarios = async (): Promise<EstadisticasUsuarios> => {
  const response = await api.get('/admin/estadisticas/usuarios/');
  return response.data;
};

const fetchEstadisticasProductos = async (): Promise<EstadisticasProductos> => {
  const response = await api.get('/admin/estadisticas/productos/');
  return response.data;
};

const fetchReporteCompleto = async () => {
  const response = await api.get('/admin/estadisticas/reporte/');
  return response.data;
};

export const EstadisticasPage = () => {
  const [activeTab, setActiveTab] = useState<'ventas' | 'usuarios' | 'productos'>('ventas');

  // Queries
  const { data: ventas, isLoading: loadingVentas } = useQuery({
    queryKey: ['estadisticas-ventas'],
    queryFn: fetchEstadisticasVentas,
  });

  const { data: usuarios, isLoading: loadingUsuarios } = useQuery({
    queryKey: ['estadisticas-usuarios'],
    queryFn: fetchEstadisticasUsuarios,
  });

  const { data: productos, isLoading: loadingProductos } = useQuery({
    queryKey: ['estadisticas-productos'],
    queryFn: fetchEstadisticasProductos,
    staleTime: 10 * 1000, // ✅ 10 segundos - Balance entre freshness y rendimiento
    gcTime: 1000 * 60 * 5, // Mantener en memoria 5 minutos si no se usa
  });

  const { data: reporte } = useQuery({
    queryKey: ['reporte-completo'],
    queryFn: fetchReporteCompleto,
    staleTime: 10 * 1000, // ✅ 10 segundos - Balance entre freshness y rendimiento
    gcTime: 1000 * 60 * 5, // Mantener en memoria 5 minutos si no se usa
  });

  // Exportar a PDF
  const exportarPDF = async () => {
    const doc = new jsPDF();
    
    // Título
    doc.setFontSize(20);
    doc.text('Reporte de Estadísticas - Electro Isla', 14, 20);
    
    doc.setFontSize(10);
    doc.text(`Fecha: ${new Date().toLocaleDateString('es-ES')}`, 14, 30);

    // Resumen
    if (reporte) {
      doc.setFontSize(14);
      doc.text('Resumen General', 14, 45);
      
      autoTable(doc, {
        startY: 50,
        head: [['Métrica', 'Valor']],
        body: [
          ['Total Usuarios', reporte.resumen.total_usuarios],
          ['Total Productos', reporte.resumen.total_productos],
          ['Total Pedidos', reporte.resumen.total_pedidos],
          ['Ingresos Totales', `$${reporte.resumen.ingresos_totales}`],
          ['Pedidos del Mes', reporte.resumen.pedidos_mes],
          ['Ingresos del Mes', `$${reporte.resumen.ingresos_mes}`],
        ],
      });
    }

    // Productos más vendidos
    if (ventas?.productos_mas_vendidos) {
      doc.addPage();
      doc.setFontSize(14);
      doc.text('Productos Más Vendidos', 14, 20);
      
      autoTable(doc, {
        startY: 25,
        head: [['Producto', 'Cantidad', 'Ingresos']],
        body: ventas.productos_mas_vendidos.map(p => [
          p.producto__nombre,
          p.cantidad_vendida,
          `$${p.ingresos}`
        ]),
      });
    }

    doc.save('estadisticas-electro-isla.pdf');
  };

  // Exportar a Excel
  const exportarExcel = () => {
    const wb = XLSX.utils.book_new();

    // Hoja de resumen
    if (reporte) {
      const wsResumen = XLSX.utils.json_to_sheet([reporte.resumen]);
      XLSX.utils.book_append_sheet(wb, wsResumen, 'Resumen');
    }

    // Hoja de ventas por mes
    if (ventas?.ventas_por_mes) {
      const wsVentas = XLSX.utils.json_to_sheet(ventas.ventas_por_mes);
      XLSX.utils.book_append_sheet(wb, wsVentas, 'Ventas por Mes');
    }

    // Hoja de productos más vendidos
    if (ventas?.productos_mas_vendidos) {
      const wsProductos = XLSX.utils.json_to_sheet(ventas.productos_mas_vendidos);
      XLSX.utils.book_append_sheet(wb, wsProductos, 'Productos');
    }

    // Hoja de usuarios por mes
    if (usuarios?.usuarios_por_mes) {
      const wsUsuarios = XLSX.utils.json_to_sheet(usuarios.usuarios_por_mes);
      XLSX.utils.book_append_sheet(wb, wsUsuarios, 'Usuarios por Mes');
    }

    XLSX.writeFile(wb, 'estadisticas-electro-isla.xlsx');
  };

  // Configuración de gráficos
  const ventasPorMesData = {
    labels: ventas?.ventas_por_mes.map(v => v.mes) || [],
    datasets: [
      {
        label: 'Ingresos ($)',
        data: ventas?.ventas_por_mes.map(v => v.total) || [],
        borderColor: '#ffbb00',
        backgroundColor: 'rgba(255, 187, 0, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const productosMasVendidosData = {
    labels: ventas?.productos_mas_vendidos.slice(0, 5).map(p => p.producto__nombre) || [],
    datasets: [
      {
        label: 'Cantidad Vendida',
        data: ventas?.productos_mas_vendidos.slice(0, 5).map(p => p.cantidad_vendida) || [],
        backgroundColor: [
          '#ffbb00',
          '#ff9500',
          '#10b981',
          '#3b82f6',
          '#8b5cf6',
        ],
      },
    ],
  };

  const usuariosPorRolData = {
    labels: usuarios?.usuarios_por_rol.map(u => u.rol) || [],
    datasets: [
      {
        label: 'Usuarios',
        data: usuarios?.usuarios_por_rol.map(u => u.count) || [],
        backgroundColor: [
          '#ef4444',
          '#3b82f6',
          '#8b5cf6',
          '#6b7280',
        ],
      },
    ],
  };

  const productosPorCategoriaData = {
    labels: productos?.productos_por_categoria.map(p => p.categoria) || [],
    datasets: [
      {
        label: 'Cantidad de Productos',
        data: productos?.productos_por_categoria.map(p => p.count) || [],
        backgroundColor: '#ffbb00',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
  };

  const isLoading = loadingVentas || loadingUsuarios || loadingProductos;

  return (
    <div className="estadisticas-page">
      {/* Header */}
      <div className="estadisticas-header">
        <div>
          <h1 className="estadisticas-title">Estadísticas Avanzadas</h1>
          <p className="estadisticas-subtitle">
            Análisis detallado del negocio con gráficos interactivos
          </p>
        </div>
        <div className="estadisticas-actions">
          <button className="estadisticas-btn estadisticas-btn-pdf" onClick={exportarPDF}>
            <FiDownload />
            <span>Exportar PDF</span>
          </button>
          <button className="estadisticas-btn estadisticas-btn-excel" onClick={exportarExcel}>
            <FiDownload />
            <span>Exportar Excel</span>
          </button>
        </div>
      </div>

      {/* Resumen rápido */}
      {reporte && (
        <div className="estadisticas-resumen">
          <div className="estadisticas-card">
            <div className="estadisticas-card-icon" style={{ background: 'rgba(59, 130, 246, 0.1)' }}>
              <FiUsers style={{ color: '#3b82f6' }} />
            </div>
            <div className="estadisticas-card-content">
              <span className="estadisticas-card-label">Total Usuarios</span>
              <span className="estadisticas-card-value">{reporte.resumen.total_usuarios}</span>
            </div>
          </div>

          <div className="estadisticas-card">
            <div className="estadisticas-card-icon" style={{ background: 'rgba(255, 187, 0, 0.1)' }}>
              <FiPackage style={{ color: '#ffbb00' }} />
            </div>
            <div className="estadisticas-card-content">
              <span className="estadisticas-card-label">Total Productos</span>
              <span className="estadisticas-card-value">{reporte.resumen.total_productos}</span>
            </div>
          </div>

          <div className="estadisticas-card">
            <div className="estadisticas-card-icon" style={{ background: 'rgba(16, 185, 129, 0.1)' }}>
              <FiTrendingUp style={{ color: '#10b981' }} />
            </div>
            <div className="estadisticas-card-content">
              <span className="estadisticas-card-label">Pedidos del Mes</span>
              <span className="estadisticas-card-value">{reporte.resumen.pedidos_mes}</span>
            </div>
          </div>

          <div className="estadisticas-card">
            <div className="estadisticas-card-icon" style={{ background: 'rgba(16, 185, 129, 0.1)' }}>
              <FiDollarSign style={{ color: '#10b981' }} />
            </div>
            <div className="estadisticas-card-content">
              <span className="estadisticas-card-label">Ingresos del Mes</span>
              <span className="estadisticas-card-value">${reporte.resumen.ingresos_mes}</span>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="estadisticas-tabs">
        <button
          className={`estadisticas-tab ${activeTab === 'ventas' ? 'active' : ''}`}
          onClick={() => setActiveTab('ventas')}
        >
          Ventas
        </button>
        <button
          className={`estadisticas-tab ${activeTab === 'usuarios' ? 'active' : ''}`}
          onClick={() => setActiveTab('usuarios')}
        >
          Usuarios
        </button>
        <button
          className={`estadisticas-tab ${activeTab === 'productos' ? 'active' : ''}`}
          onClick={() => setActiveTab('productos')}
        >
          Productos
        </button>
      </div>

      {/* Contenido de tabs */}
      {isLoading ? (
        <div className="estadisticas-loading">
          <div className="estadisticas-spinner"></div>
          <p>Cargando estadísticas...</p>
        </div>
      ) : (
        <div className="estadisticas-content">
          {/* Tab de Ventas */}
          {activeTab === 'ventas' && ventas && (
            <div className="estadisticas-grid">
              <div className="estadisticas-chart-container">
                <h3>Ventas por Mes (Últimos 12 meses)</h3>
                <div className="estadisticas-chart">
                  <Line data={ventasPorMesData} options={chartOptions} />
                </div>
              </div>

              <div className="estadisticas-chart-container">
                <h3>Top 5 Productos Más Vendidos</h3>
                <div className="estadisticas-chart">
                  <Doughnut data={productosMasVendidosData} options={chartOptions} />
                </div>
              </div>

              <div className="estadisticas-info-card">
                <h3>Ticket Promedio</h3>
                <div className="estadisticas-big-number">${ventas.ticket_promedio.toFixed(2)}</div>
              </div>

              <div className="estadisticas-info-card">
                <h3>Métodos de Pago</h3>
                <div className="estadisticas-list">
                  {ventas.metodos_pago.map((metodo, index) => (
                    <div key={index} className="estadisticas-list-item">
                      <span>{metodo.metodo_pago}</span>
                      <strong>{metodo.count} pedidos</strong>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Tab de Usuarios */}
          {activeTab === 'usuarios' && usuarios && (
            <div className="estadisticas-grid">
              <div className="estadisticas-chart-container">
                <h3>Crecimiento de Usuarios (Últimos 12 meses)</h3>
                <div className="estadisticas-chart">
                  <Bar
                    data={{
                      labels: usuarios.usuarios_por_mes.map(u => u.mes),
                      datasets: [{
                        label: 'Nuevos Usuarios',
                        data: usuarios.usuarios_por_mes.map(u => u.nuevos),
                        backgroundColor: '#3b82f6',
                      }],
                    }}
                    options={chartOptions}
                  />
                </div>
              </div>

              <div className="estadisticas-chart-container">
                <h3>Usuarios por Rol</h3>
                <div className="estadisticas-chart">
                  <Doughnut data={usuariosPorRolData} options={chartOptions} />
                </div>
              </div>

              <div className="estadisticas-info-card">
                <h3>Tasa de Retención</h3>
                <div className="estadisticas-big-number">{usuarios.tasa_retencion}%</div>
                <p className="estadisticas-info-text">Usuarios con más de 1 pedido</p>
              </div>

              <div className="estadisticas-info-card">
                <h3>Usuarios Más Activos</h3>
                <div className="estadisticas-list">
                  {usuarios.usuarios_mas_activos.slice(0, 5).map((usuario, index) => (
                    <div key={index} className="estadisticas-list-item">
                      <span>{usuario.username}</span>
                      <strong>{usuario.pedidos_count} pedidos</strong>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Tab de Productos */}
          {activeTab === 'productos' && productos && (
            <div className="estadisticas-grid">
              <div className="estadisticas-chart-container">
                <h3>Productos por Categoría</h3>
                <div className="estadisticas-chart">
                  <Bar data={productosPorCategoriaData} options={chartOptions} />
                </div>
              </div>

              <div className="estadisticas-info-card">
                <h3>Valor del Inventario</h3>
                <div className="estadisticas-big-number">${productos.valor_inventario.toFixed(2)}</div>
              </div>

              <div className="estadisticas-info-card">
                <h3>Productos Sin Stock</h3>
                <div className="estadisticas-big-number">{productos.productos_sin_stock}</div>
                <p className="estadisticas-info-text">Requieren reabastecimiento</p>
              </div>

              <div className="estadisticas-info-card">
                <h3>Stock Bajo (menos de 10)</h3>
                <div className="estadisticas-list">
                  {productos.stock_bajo.slice(0, 5).map((producto, index) => (
                    <div key={index} className="estadisticas-list-item">
                      <span>{producto.nombre}</span>
                      <strong className="estadisticas-stock-bajo">{producto.stock} unidades</strong>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
