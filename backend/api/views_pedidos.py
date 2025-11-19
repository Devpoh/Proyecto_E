"""
═══════════════════════════════════════════════════════════════════════════════
📦 VIEWS - Gestión de Pedidos
═══════════════════════════════════════════════════════════════════════════════
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta, datetime
from .models import Pedido, Notificacion
from .serializers_admin import PedidoSerializer, NotificacionSerializer
from .views_admin import IsAdminOrStaff
from .utils.audit import registrar_edicion


class StandardPagination(PageNumberPagination):
    """Paginación estándar para listados"""
    page_size = 20
    page_size_query_param = 'page_size'
    page_size_query_description = 'Número de resultados por página'
    max_page_size = 100


# Estados válidos y transiciones permitidas
ESTADOS_VALIDOS = ['pendiente', 'confirmado', 'en_preparacion', 'en_camino', 'entregado', 'cancelado']
TRANSICIONES_VALIDAS = {
    'pendiente': ['confirmado', 'cancelado'],
    'confirmado': ['en_preparacion', 'cancelado'],
    'en_preparacion': ['en_camino', 'cancelado'],
    'en_camino': ['entregado', 'cancelado'],
    'entregado': [],
    'cancelado': []
}


class PedidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de pedidos
    
    PERMISOS:
    - Admin: Ver todos, editar todos
    - Trabajador: Ver todos, editar todos
    - Mensajero: Ver solo asignados, actualizar estado
    - Cliente: Ver solo propios
    """
    
    queryset = Pedido.objects.all().select_related('usuario', 'mensajero').prefetch_related('detalles__producto')
    serializer_class = PedidoSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        """Filtrar pedidos según rol del usuario"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Obtener rol del usuario
        rol = None
        if hasattr(user, 'profile'):
            rol = user.profile.rol
        
        # Clientes solo ven sus propios pedidos
        if rol == 'cliente':
            queryset = queryset.filter(usuario=user)
        
        # Mensajeros solo ven sus pedidos asignados
        elif rol == 'mensajero':
            queryset = queryset.filter(mensajero=user)
        
        # Admin, trabajador y otros ven todos
        
        # Filtros opcionales
        estado = self.request.query_params.get('estado', None)
        search = self.request.query_params.get('search', '').strip()
        fecha_desde = self.request.query_params.get('fecha_desde', None)
        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        
        if estado:
            queryset = queryset.filter(estado=estado)
        
        if search:
            # Validar longitud de búsqueda (máximo 100 caracteres)
            if len(search) > 100:
                return queryset.none()
            
            queryset = queryset.filter(
                Q(id__icontains=search) |
                Q(usuario__username__icontains=search) |
                Q(telefono__icontains=search)
            )
        
        if fecha_desde:
            queryset = queryset.filter(created_at__gte=fecha_desde)
        
        if fecha_hasta:
            queryset = queryset.filter(created_at__lte=fecha_hasta)
        
        return queryset.order_by('-created_at')
    
    def update(self, request, *args, **kwargs):
        """Actualizar pedido con validaciones"""
        instance = self.get_object()
        user_profile = request.user.profile
        
        # Mensajeros solo pueden actualizar estado
        if user_profile.rol == 'mensajero':
            if 'estado' not in request.data or len(request.data) > 1:
                return Response(
                    {'error': 'Solo puedes actualizar el estado del pedido'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Validar cambio de estado (para todos los roles)
        if 'estado' in request.data:
            nuevo_estado = request.data.get('estado')
            
            # Validar que sea un estado válido
            if nuevo_estado not in ESTADOS_VALIDOS:
                return Response(
                    {'error': f'Estado inválido. Estados válidos: {ESTADOS_VALIDOS}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar transición
            if nuevo_estado not in TRANSICIONES_VALIDAS.get(instance.estado, []):
                return Response(
                    {'error': f'No puedes cambiar de {instance.estado} a {nuevo_estado}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Guardar estado anterior para auditoría
        estado_anterior = instance.estado
        
        response = super().update(request, *args, **kwargs)
        
        # Registrar auditoría si cambió el estado
        if response.status_code == 200 and 'estado' in request.data:
            registrar_edicion(request, 'pedido', instance, {
                'estado': {
                    'anterior': estado_anterior,
                    'nuevo': request.data['estado']
                }
            })
        
        # Crear notificación al cambiar estado
        if 'estado' in request.data and request.data['estado'] != estado_anterior:
            Notificacion.objects.create(
                usuario=instance.usuario,
                tipo='info',
                titulo=f'Pedido #{instance.id} actualizado',
                mensaje=f'Tu pedido ha cambiado a estado: {request.data["estado"]}',
                url=f'/al_pedidos/{instance.id}'
            )
        
        return response
    
    @action(detail=True, methods=['post'])
    def asignar_mensajero(self, request, pk=None):
        """Asignar mensajero a pedido"""
        pedido = self.get_object()
        mensajero_id = request.data.get('mensajero_id')
        
        if not mensajero_id:
            return Response(
                {'error': 'mensajero_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que sea un entero
        try:
            mensajero_id = int(mensajero_id)
        except (ValueError, TypeError):
            return Response(
                {'error': 'mensajero_id debe ser un entero'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            mensajero = User.objects.get(
                id=mensajero_id,
                profile__rol='mensajero',
                is_active=True
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'Mensajero no encontrado o inactivo'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Guardar mensajero anterior para auditoría
        mensajero_anterior = pedido.mensajero
        
        pedido.mensajero = mensajero
        pedido.save()
        
        # Registrar auditoría
        registrar_edicion(request, 'pedido', pedido, {
            'mensajero': {
                'anterior': str(mensajero_anterior) if mensajero_anterior else 'Sin asignar',
                'nuevo': str(mensajero)
            }
        })
        
        # Notificar al mensajero
        Notificacion.objects.create(
            usuario=mensajero,
            tipo='info',
            titulo='Nuevo pedido asignado',
            mensaje=f'Se te ha asignado el pedido #{pedido.id}',
            url=f'/admin/pedidos'
        )
        
        return Response({'message': 'Mensajero asignado correctamente'})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas de pedidos"""
        
        # Total de pedidos
        total_pedidos = Pedido.objects.count()
        
        # Pedidos por estado
        pedidos_por_estado = Pedido.objects.values('estado').annotate(
            count=Count('id')
        )
        
        # Ingresos totales
        ingresos_totales = Pedido.objects.filter(
            estado__in=['confirmado', 'en_preparacion', 'en_camino', 'entregado']
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # Pedidos del mes
        inicio_mes = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        pedidos_mes = Pedido.objects.filter(created_at__gte=inicio_mes).count()
        ingresos_mes = Pedido.objects.filter(
            created_at__gte=inicio_mes,
            estado__in=['confirmado', 'en_preparacion', 'en_camino', 'entregado']
        ).aggregate(total=Sum('total'))['total'] or 0
        
        # Pedidos por día (últimos 7 días)
        hace_7_dias = timezone.now() - timedelta(days=7)
        pedidos_por_dia = []
        for i in range(7):
            dia = hace_7_dias + timedelta(days=i)
            dia_inicio = dia.replace(hour=0, minute=0, second=0, microsecond=0)
            dia_fin = dia_inicio + timedelta(days=1)
            
            count = Pedido.objects.filter(
                created_at__gte=dia_inicio,
                created_at__lt=dia_fin
            ).count()
            
            pedidos_por_dia.append({
                'fecha': dia.strftime('%Y-%m-%d'),
                'count': count
            })
        
        return Response({
            'total_pedidos': total_pedidos,
            'pedidos_por_estado': list(pedidos_por_estado),
            'ingresos_totales': float(ingresos_totales),
            'pedidos_mes': pedidos_mes,
            'ingresos_mes': float(ingresos_mes),
            'pedidos_por_dia': pedidos_por_dia,
        })


class NotificacionViewSet(viewsets.ModelViewSet):
    """ViewSet para notificaciones"""
    
    serializer_class = NotificacionSerializer
    
    def get_queryset(self):
        """Solo notificaciones del usuario actual"""
        return Notificacion.objects.filter(usuario=self.request.user)
    
    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        """Marcar notificación como leída"""
        notificacion = self.get_object()
        notificacion.leida = True
        notificacion.save()
        return Response({'message': 'Notificación marcada como leída'})
    
    @action(detail=False, methods=['post'])
    def marcar_todas_leidas(self, request):
        """Marcar todas las notificaciones como leídas"""
        Notificacion.objects.filter(usuario=request.user, leida=False).update(leida=True)
        return Response({'message': 'Todas las notificaciones marcadas como leídas'})
    
    @action(detail=False, methods=['get'])
    def no_leidas(self, request):
        """Obtener cantidad de notificaciones no leídas"""
        count = Notificacion.objects.filter(usuario=request.user, leida=False).count()
        return Response({'count': count})
