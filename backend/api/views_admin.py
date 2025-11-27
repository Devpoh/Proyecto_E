"""
═══════════════════════════════════════════════════════════════════════════════
🔐 VIEWS - Admin Panel
═══════════════════════════════════════════════════════════════════════════════

Vistas para el panel de administración con control de permisos
"""

from rest_framework import viewsets, status, permissions, throttling
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, Producto, AuditLog
from .serializers_admin import (
    UserListSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    ProductoAdminSerializer,
    AuditLogSerializer
)
from .utils.audit import registrar_edicion, registrar_eliminacion, registrar_creacion, registrar_cambio_rol
from .throttles import AdminRateThrottle  # ✅ Importar throttle centralizado


class IsAdminOrStaff(permissions.BasePermission):
    """
    Permiso personalizado: solo admin, trabajador o mensajero
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Verificar si tiene perfil y rol adecuado
        if hasattr(request.user, 'profile'):
            return request.user.profile.has_admin_access
        
        # Fallback: verificar si es staff
        return request.user.is_staff or request.user.is_superuser


class CanManageUsers(permissions.BasePermission):
    """
    Permiso para gestionar usuarios: solo admin y trabajador
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if hasattr(request.user, 'profile'):
            return request.user.profile.rol in ['admin', 'trabajador']
        
        return request.user.is_superuser


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de usuarios
    
    PERMISOS:
    - Admin: Acceso total
    - Trabajador: Puede ver y editar (no puede cambiar roles de admin)
    - Mensajero: Solo lectura
    
    PRIVACIDAD:
    - Emails parcialmente ocultos en listado
    - No expone contraseñas
    - Logs de acciones sensibles
    """
    
    queryset = User.objects.all().select_related('profile').prefetch_related('pedidos')
    permission_classes = [IsAdminOrStaff]
    throttle_classes = [AdminRateThrottle]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserDetailSerializer
    
    def list(self, request, *args, **kwargs):
        """Listar usuarios con validaciones y sanitización"""
        search = request.query_params.get('search', '').strip()
        activo = request.query_params.get('activo')
        rol = request.query_params.get('rol', '').strip()  # ✅ AGREGADO: Validar rol
        
        # Sanitizar búsqueda
        if search:
            # Remover espacios múltiples
            search = ' '.join(search.split())
            # Validar longitud
            if len(search) > 100:
                return Response(
                    {'error': 'Búsqueda muy larga (máximo 100 caracteres)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Validar caracteres válidos (alfanuméricos, espacios, guiones)
            if not all(c.isalnum() or c.isspace() or c in '-_.@' for c in search):
                return Response(
                    {'error': 'Búsqueda contiene caracteres inválidos'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validar activo
        if activo is not None and activo.lower() not in ['true', 'false']:
            return Response(
                {'error': 'activo debe ser "true" o "false"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ✅ AGREGADO: Validar rol
        ROLES_VALIDOS = ['cliente', 'mensajero', 'trabajador', 'admin']
        if rol and rol not in ROLES_VALIDOS:
            return Response(
                {'error': f'Rol inválido. Roles válidos: {ROLES_VALIDOS}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        """
        Filtrar usuarios según el rol del usuario autenticado
        """
        queryset = User.objects.all().select_related('profile').order_by('-date_joined')
        
        # Obtener parámetros
        search = self.request.query_params.get('search', '').strip()
        activo = self.request.query_params.get('activo')
        rol = self.request.query_params.get('rol', '').strip()  # ✅ AGREGADO: Filtro por rol
        
        if activo is not None:
            queryset = queryset.filter(is_active=activo.lower() == 'true')
        
        # ✅ AGREGADO: Filtrar por rol si se proporciona
        if rol:
            queryset = queryset.filter(profile__rol=rol)
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )[:100]  # Limitar resultados
        
        return queryset
    
    def update(self, request, *args, **kwargs):
        """
        Actualizar usuario con validaciones de seguridad
        """
        instance = self.get_object()
        user_profile = request.user.profile
        
        # Roles válidos
        ROLES_VALIDOS = ['cliente', 'mensajero', 'trabajador', 'admin']
        
        # Validación: Validar que el rol sea válido
        if 'rol' in request.data:
            nuevo_rol = request.data['rol']
            
            if nuevo_rol not in ROLES_VALIDOS:
                return Response(
                    {'error': f'Rol inválido. Roles válidos: {ROLES_VALIDOS}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validación: Trabajadores no pueden modificar admins
        if user_profile.rol == 'trabajador':
            if hasattr(instance, 'profile') and instance.profile.rol == 'admin':
                return Response(
                    {'error': 'No tienes permisos para modificar administradores'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Trabajadores no pueden asignar rol admin
            if 'rol' in request.data and request.data['rol'] == 'admin':
                return Response(
                    {'error': 'No tienes permisos para asignar rol de administrador'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Validación: No se puede desactivar a sí mismo
        if instance.id == request.user.id and 'is_active' in request.data:
            if not request.data['is_active']:
                return Response(
                    {'error': 'No puedes desactivar tu propia cuenta'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Guardar estado anterior para auditoría
        rol_anterior = instance.profile.rol if hasattr(instance, 'profile') else None
        estado_anterior = instance.is_active
        
        response = super().update(request, *args, **kwargs)
        
        # Registrar auditoría
        if response.status_code == 200:
            cambios = {}
            
            # Detectar cambio de rol
            if 'rol' in request.data and rol_anterior != request.data['rol']:
                registrar_cambio_rol(request, instance, rol_anterior, request.data['rol'])
                cambios['rol'] = {'anterior': rol_anterior, 'nuevo': request.data['rol']}
            
            # Detectar cambio de estado
            if 'is_active' in request.data and estado_anterior != request.data['is_active']:
                cambios['is_active'] = {'anterior': estado_anterior, 'nuevo': request.data['is_active']}
            
            # Registrar edición general si hay otros cambios
            if cambios or len(request.data) > 0:
                registrar_edicion(request, 'usuario', instance, cambios)
        
        return response
    
    def destroy(self, request, *args, **kwargs):
        """
        Eliminar usuario (solo admin)
        """
        if request.user.profile.rol != 'admin':
            return Response(
                {'error': 'Solo administradores pueden eliminar usuarios'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        instance = self.get_object()
        
        # No se puede eliminar a sí mismo
        if instance.id == request.user.id:
            return Response(
                {'error': 'No puedes eliminar tu propia cuenta'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que no sea el último admin
        if instance.profile.rol == 'admin':
            otros_admins = User.objects.filter(
                profile__rol='admin',
                is_active=True
            ).exclude(id=instance.id).count()
            
            if otros_admins == 0:
                return Response(
                    {'error': 'No puedes eliminar el último administrador'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validar que no tenga pedidos activos
        from .models import Pedido
        pedidos_activos = Pedido.objects.filter(
            usuario=instance,
            estado__in=['pendiente', 'confirmado', 'en_preparacion', 'en_camino']
        ).count()
        
        if pedidos_activos > 0:
            return Response(
                {'error': f'El usuario tiene {pedidos_activos} pedidos activos. No se puede eliminar.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Guardar datos para auditoría antes de eliminar
        usuario_id = instance.id
        usuario_repr = f'{instance.username} ({instance.get_full_name() or "Sin nombre"})'
        datos_eliminados = {
            'username': instance.username,
            'email': instance.email,
            'nombre_completo': instance.get_full_name(),
            'rol': instance.profile.rol if hasattr(instance, 'profile') else 'cliente',
        }
        
        response = super().destroy(request, *args, **kwargs)
        
        # Registrar auditoría
        if response.status_code == 204:
            registrar_eliminacion(request, 'usuario', usuario_id, usuario_repr, datos_eliminados)
        
        return response
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de usuarios"""
        
        total_usuarios = User.objects.count()
        usuarios_activos = User.objects.filter(is_active=True).count()
        
        # Usuarios por rol
        roles_count = UserProfile.objects.values('rol').annotate(
            count=Count('id')
        )
        
        # Nuevos usuarios (últimos 30 días)
        hace_30_dias = timezone.now() - timedelta(days=30)
        nuevos_usuarios = User.objects.filter(
            date_joined__gte=hace_30_dias
        ).count()
        
        return Response({
            'total_usuarios': total_usuarios,
            'usuarios_activos': usuarios_activos,
            'usuarios_inactivos': total_usuarios - usuarios_activos,
            'roles': list(roles_count),
            'nuevos_usuarios_30d': nuevos_usuarios,
        })


class ProductoManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de productos
    
    PERMISOS:
    - Admin y Trabajador: CRUD completo
    - Mensajero: Solo lectura
    """
    
    queryset = Producto.objects.all().select_related('creado_por')
    serializer_class = ProductoAdminSerializer
    permission_classes = [IsAdminOrStaff]
    throttle_classes = [AdminRateThrottle]
    
    def list(self, request, *args, **kwargs):
        """Listar productos con validaciones y sanitización"""
        search = request.query_params.get('search', '').strip()
        
        # Sanitizar búsqueda
        if search:
            # Remover espacios múltiples
            search = ' '.join(search.split())
            # Validar longitud
            if len(search) > 100:
                return Response(
                    {'error': 'Búsqueda muy larga (máximo 100 caracteres)'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # Validar caracteres válidos
            if not all(c.isalnum() or c.isspace() or c in '-_.()' for c in search):
                return Response(
                    {'error': 'Búsqueda contiene caracteres inválidos'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        """Filtrar productos"""
        queryset = super().get_queryset().order_by('-created_at')
        
        categoria = self.request.query_params.get('categoria', None)
        activo = self.request.query_params.get('activo', None)
        search = self.request.query_params.get('search', None)
        
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        
        if search:
            search = search.strip()
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search)
            )[:100]  # Limitar resultados
        
        return queryset
    
    def perform_create(self, serializer):
        """Asignar usuario creador"""
        producto = serializer.save(creado_por=self.request.user)
        
        # Registrar auditoría
        registrar_creacion(self.request, 'producto', producto)
    
    def create(self, request, *args, **kwargs):
        """Crear producto (solo admin y trabajador)"""
        if request.user.profile.rol not in ['admin', 'trabajador']:
            return Response(
                {'error': 'No tienes permisos para crear productos'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al crear producto: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """Actualizar producto (solo admin y trabajador)"""
        if request.user.profile.rol not in ['admin', 'trabajador']:
            return Response(
                {'error': 'No tienes permisos para editar productos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            instance = self.get_object()
            response = super().update(request, *args, **kwargs)
            
            # Registrar auditoría
            if response.status_code == 200:
                cambios = {k: v for k, v in request.data.items()}
                registrar_edicion(request, 'producto', instance, cambios)
            
            return response
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al actualizar producto: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """Eliminar producto (solo admin)"""
        if request.user.profile.rol != 'admin':
            return Response(
                {'error': 'Solo administradores pueden eliminar productos'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Guardar datos para auditoría antes de eliminar
        instance = self.get_object()
        producto_id = instance.id
        producto_repr = instance.nombre
        datos_eliminados = {
            'nombre': instance.nombre,
            'categoria': instance.categoria,
            'precio': str(instance.precio),
            'stock': instance.stock,
        }
        
        response = super().destroy(request, *args, **kwargs)
        
        # Registrar auditoría
        if response.status_code == 204:
            registrar_eliminacion(request, 'producto', producto_id, producto_repr, datos_eliminados)
        
        return response
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de productos"""
        
        total_productos = Producto.objects.count()
        productos_activos = Producto.objects.filter(activo=True).count()
        productos_sin_stock = Producto.objects.filter(stock=0).count()
        
        # Productos por categoría
        categorias_count = Producto.objects.values('categoria').annotate(
            count=Count('id')
        )
        
        # Valor total del inventario
        valor_inventario = Producto.objects.aggregate(
            total=Sum('precio')
        )['total'] or 0
        
        return Response({
            'total_productos': total_productos,
            'productos_activos': productos_activos,
            'productos_inactivos': total_productos - productos_activos,
            'productos_sin_stock': productos_sin_stock,
            'categorias': list(categorias_count),
            'valor_inventario': float(valor_inventario),
        })


@api_view(['GET'])
@permission_classes([IsAdminOrStaff])
def dashboard_stats(request):
    """
    Estadísticas generales del dashboard con filtros de fecha opcionales
    """
    from datetime import datetime
    
    # Obtener parámetros de fecha
    fecha_desde = request.query_params.get('fecha_desde')
    fecha_hasta = request.query_params.get('fecha_hasta')
    
    # Validar y parsear fechas
    fecha_desde_obj = None
    fecha_hasta_obj = None
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.fromisoformat(fecha_desde)
        except ValueError:
            return Response(
                {'error': 'Formato de fecha_desde inválido (use ISO format: YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.fromisoformat(fecha_hasta)
        except ValueError:
            return Response(
                {'error': 'Formato de fecha_hasta inválido (use ISO format: YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Validar que fecha_desde < fecha_hasta
    if fecha_desde_obj and fecha_hasta_obj:
        if fecha_desde_obj > fecha_hasta_obj:
            return Response(
                {'error': 'fecha_desde debe ser menor que fecha_hasta'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Filtros de fecha para usuarios
    usuarios_query = User.objects.all()
    if fecha_desde_obj:
        usuarios_query = usuarios_query.filter(date_joined__gte=fecha_desde_obj)
    if fecha_hasta_obj:
        usuarios_query = usuarios_query.filter(date_joined__lte=fecha_hasta_obj)
    
    # Filtros de fecha para productos
    productos_query = Producto.objects.all()
    if fecha_desde_obj:
        productos_query = productos_query.filter(created_at__gte=fecha_desde_obj)
    if fecha_hasta_obj:
        productos_query = productos_query.filter(created_at__lte=fecha_hasta_obj)
    
    # Usuarios
    total_usuarios = usuarios_query.count()
    usuarios_activos = usuarios_query.filter(is_active=True).count()
    
    # Productos
    total_productos = productos_query.count()
    productos_activos = productos_query.filter(activo=True).count()
    
    # Nuevos registros (últimos 7 días)
    hace_7_dias = timezone.now() - timedelta(days=7)
    nuevos_usuarios_7d = User.objects.filter(date_joined__gte=hace_7_dias).count()
    nuevos_productos_7d = Producto.objects.filter(created_at__gte=hace_7_dias).count()
    
    return Response({
        'usuarios': {
            'total': total_usuarios,
            'activos': usuarios_activos,
            'nuevos_7d': nuevos_usuarios_7d,
        },
        'productos': {
            'total': total_productos,
            'activos': productos_activos,
            'nuevos_7d': nuevos_productos_7d,
        },
        'rol_usuario': request.user.profile.rol if hasattr(request.user, 'profile') else 'cliente',
    })


class IsAdmin(permissions.BasePermission):
    """Permiso solo para administradores"""
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if hasattr(request.user, 'profile'):
            return request.user.profile.rol == 'admin'
        
        return request.user.is_superuser


class AuditLogViewSet(viewsets.ModelViewSet):
    """
    ViewSet para el historial de auditoría.
    Permite lectura y eliminación solo para administradores.
    """
    queryset = AuditLog.objects.select_related('usuario').order_by('-timestamp')
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdmin]
    throttle_classes = [AdminRateThrottle]
    http_method_names = ['get', 'delete', 'head', 'options']  # Solo GET y DELETE
    
    def get_queryset(self):
        """Filtrar queryset con optimizaciones"""
        from datetime import datetime
        from django.utils import timezone
        
        queryset = super().get_queryset()
        
        # Filtro por fecha
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        
        if fecha_desde:
            try:
                # Parsear fecha ISO 8601 manualmente
                # Formato: 2025-11-09T22:03:23.130Z
                fecha_desde_str = fecha_desde.replace('Z', '+00:00')
                
                # Intentar con fromisoformat (Python 3.7+)
                try:
                    fecha_desde_obj = datetime.fromisoformat(fecha_desde_str)
                except:
                    # Fallback: parsear manualmente
                    # Remover milisegundos si existen
                    if '.' in fecha_desde_str:
                        fecha_desde_str = fecha_desde_str.split('.')[0] + '+00:00'
                    fecha_desde_obj = datetime.fromisoformat(fecha_desde_str)
                
                # Asegurar que tiene zona horaria
                if fecha_desde_obj.tzinfo is None:
                    fecha_desde_obj = timezone.make_aware(fecha_desde_obj)
                
                queryset = queryset.filter(timestamp__gte=fecha_desde_obj)
            except Exception as e:
                # Log del error para debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'Error parsing fecha_desde: {fecha_desde} - {str(e)}')
                pass
        
        if fecha_hasta:
            try:
                # Parsear fecha ISO 8601 manualmente
                fecha_hasta_str = fecha_hasta.replace('Z', '+00:00')
                
                # Intentar con fromisoformat (Python 3.7+)
                try:
                    fecha_hasta_obj = datetime.fromisoformat(fecha_hasta_str)
                except:
                    # Fallback: parsear manualmente
                    if '.' in fecha_hasta_str:
                        fecha_hasta_str = fecha_hasta_str.split('.')[0] + '+00:00'
                    fecha_hasta_obj = datetime.fromisoformat(fecha_hasta_str)
                
                # Asegurar que tiene zona horaria
                if fecha_hasta_obj.tzinfo is None:
                    fecha_hasta_obj = timezone.make_aware(fecha_hasta_obj)
                
                queryset = queryset.filter(timestamp__lte=fecha_hasta_obj)
            except Exception as e:
                # Log del error para debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'Error parsing fecha_hasta: {fecha_hasta} - {str(e)}')
                pass
        
        # Filtros adicionales (sin django-filter)
        accion = self.request.query_params.get('accion')
        if accion:
            queryset = queryset.filter(accion=accion)
        
        modulo = self.request.query_params.get('modulo')
        if modulo:
            queryset = queryset.filter(modulo=modulo)
        
        usuario = self.request.query_params.get('usuario')
        if usuario:
            queryset = queryset.filter(usuario__id=usuario)
        
        search = self.request.query_params.get('search')
        if search:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(objeto_repr__icontains=search) |
                Q(usuario__username__icontains=search)
            )
        
        return queryset
    
    @action(detail=False, methods=['delete'], url_path='clear_all')
    def clear_all(self, request):
        """
        Elimina TODO el historial de auditoría.
        Solo para administradores.
        Acción destructiva que requiere confirmación en frontend.
        """
        count = AuditLog.objects.count()
        AuditLog.objects.all().delete()
        
        return Response({
            'message': f'Se eliminaron {count} registros del historial',
            'count': count
        }, status=status.HTTP_200_OK)
