/**
 * ═══════════════════════════════════════════════════════════════════════════════
 * 🛣️ ROUTES - Configuración de Rutas
 * ═══════════════════════════════════════════════════════════════════════════════
 * 
 * Sistema de rutas de la aplicación
 * 
 * ESTRUCTURA:
 * - Rutas públicas (login, register, home)
 * - Rutas protegidas (admin, checkout)
 * - Rutas con layout (header + footer)
 * - Rutas standalone (sin layout)
 */

import { Routes, Route, Navigate } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { GlobalLoading } from '@/shared/ui/GlobalLoading';

// Lazy load de páginas públicas
const LoginPage = lazy(() => import('@/pages/auth/login').then(m => ({ default: m.LoginPage })));
const RegisterPage = lazy(() => import('@/pages/auth/register').then(m => ({ default: m.RegisterPage })));
const VerifyEmailPage = lazy(() => import('@/features/auth/verify-email').then(m => ({ default: m.VerifyEmailPage })));
const HomePage = lazy(() => import('@/pages/home').then(m => ({ default: m.HomePage })));
const PaginaSobreNosotros = lazy(() => import('@/pages/about').then(m => ({ default: m.PaginaSobreNosotros })));
const PaginaProductos = lazy(() => import('@/pages/products').then(m => ({ default: m.PaginaProductos })));
const ProductDetail = lazy(() => import('@/pages/ProductDetail').then(m => ({ default: m.ProductDetail })));
const VistaCarrito = lazy(() => import('@/pages/VistaCarrito'));
const OrderHistory = lazy(() => import('@/pages/order-history').then(m => ({ default: m.OrderHistory })));

// Lazy load de páginas admin
const AdminLayout = lazy(() => import('@/pages/admin').then(m => ({ default: m.AdminLayout })));
const DashboardPage = lazy(() => import('@/pages/admin').then(m => ({ default: m.DashboardPage })));
const UsuariosPage = lazy(() => import('@/pages/admin').then(m => ({ default: m.UsuariosPage })));
const ProductosPage = lazy(() => import('@/pages/admin').then(m => ({ default: m.ProductosPage })));
const PedidosPage = lazy(() => import('@/pages/admin').then(m => ({ default: m.PedidosPage })));
const EstadisticasPage = lazy(() => import('@/pages/admin').then(m => ({ default: m.EstadisticasPage })));
const HistorialPage = lazy(() => import('@/pages/admin').then(m => ({ default: m.HistorialPage })));

// Importar componentes que no necesitan lazy load
import { MainLayout } from '@/app/layouts/MainLayout';
import { ProtectedRoute } from '@/shared/components';

// Componente de fallback para Suspense
const RouteLoadingFallback = () => (
  <GlobalLoading 
    isLoading={true} 
    message="Cargando página..." 
  />
);

export const AppRoutes = () => {
  return (
    <Suspense fallback={<RouteLoadingFallback />}>
      <Routes>
        {/* Rutas sin layout (standalone) */}
        <Route path="/login" element={<Suspense fallback={<RouteLoadingFallback />}><LoginPage /></Suspense>} />
        <Route path="/register" element={<Suspense fallback={<RouteLoadingFallback />}><RegisterPage /></Suspense>} />
        <Route path="/auth/verify-email" element={<Suspense fallback={<RouteLoadingFallback />}><VerifyEmailPage /></Suspense>} />
        
        {/* Rutas de admin - Protegidas por rol */}
        <Route 
          path="/admin" 
          element={
            <ProtectedRoute requiredRoles={['admin', 'trabajador', 'mensajero']}>
              <Suspense fallback={<RouteLoadingFallback />}>
                <AdminLayout />
              </Suspense>
            </ProtectedRoute>
          }
        >
          <Route index element={<Suspense fallback={<RouteLoadingFallback />}><DashboardPage /></Suspense>} />
          <Route path="usuarios" element={<Suspense fallback={<RouteLoadingFallback />}><UsuariosPage /></Suspense>} />
          <Route path="productos" element={<Suspense fallback={<RouteLoadingFallback />}><ProductosPage /></Suspense>} />
          <Route path="pedidos" element={<Suspense fallback={<RouteLoadingFallback />}><PedidosPage /></Suspense>} />
          <Route path="estadisticas" element={<Suspense fallback={<RouteLoadingFallback />}><EstadisticasPage /></Suspense>} />
          <Route path="historial" element={<Suspense fallback={<RouteLoadingFallback />}><HistorialPage /></Suspense>} />
        </Route>
        
        {/* Rutas con layout principal */}
        <Route element={<MainLayout />}>
          <Route path="/" element={<Suspense fallback={<RouteLoadingFallback />}><HomePage /></Suspense>} />
          <Route path="/nosotros" element={<Suspense fallback={<RouteLoadingFallback />}><PaginaSobreNosotros /></Suspense>} />
          <Route path="/productos" element={<Suspense fallback={<RouteLoadingFallback />}><PaginaProductos /></Suspense>} />
          <Route path="/producto/:id" element={<Suspense fallback={<RouteLoadingFallback />}><ProductDetail /></Suspense>} />
          <Route path="/carrito" element={<Suspense fallback={<RouteLoadingFallback />}><VistaCarrito /></Suspense>} />
          <Route 
            path="/historial-pedidos" 
            element={
              <ProtectedRoute>
                <Suspense fallback={<RouteLoadingFallback />}>
                  <OrderHistory />
                </Suspense>
              </ProtectedRoute>
            } 
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </Suspense>
  );
};
