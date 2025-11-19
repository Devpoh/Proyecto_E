from rest_framework import viewsets, status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.db.models import Q
from django.db import transaction
from .models import Producto, RefreshToken, LoginAttempt, Cart, CartItem, Favorito
from .serializers import UserSerializer, ProductoSerializer, CartSerializer, CartItemSerializer
from .utils import (
    generar_access_token,
    verificar_access_token,
    obtener_info_request,
)
from .cart_utils import check_rate_limit, log_cart_action
from .throttles import CartWriteRateThrottle, CheckoutRateThrottle, AnonLoginRateThrottle  # ✅ Importar throttles
import logging

logger_security = logging.getLogger('security')
logger_auth = logging.getLogger('auth')
logger = logging.getLogger(__name__)  # Logger general para vistas


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_csrf_token(request):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    🛡️ ENDPOINT - Obtener CSRF Token
    ═══════════════════════════════════════════════════════════════════════════════
    
    Obtiene el CSRF token para el cliente.
    El token se envía en la cookie 'csrftoken'.
    
    El frontend debe incluir este token en el header X-CSRFToken
    para todas las peticiones POST/PUT/DELETE/PATCH.
    
    Retorna:
    - 200: CSRF token obtenido exitosamente
    """
    csrf_token = get_token(request)
    return Response({
        'csrfToken': csrf_token,
        'message': 'CSRF token obtenido exitosamente'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def check_email(request):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    🔍 ENDPOINT - Validar Email Duplicado
    ═══════════════════════════════════════════════════════════════════════════════
    
    Valida si un email ya está registrado en la base de datos.
    Usado para validación en tiempo real en el formulario de registro.
    
    Request:
    {
        "email": "usuario@example.com"
    }
    
    Retorna:
    - 200: { "exists": true/false }
    """
    email = request.data.get('email', '').strip().lower()
    
    if not email:
        return Response({
            'exists': False,
            'message': 'Email requerido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validar formato básico
    import re
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return Response({
            'exists': False,
            'message': 'Formato de email inválido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verificar si el email existe
    exists = User.objects.filter(email__iexact=email).exists()
    
    logger_security.debug(f'[EMAIL_CHECK] Email: {email} | Existe: {exists}')
    
    return Response({
        'exists': exists,
        'message': 'Email ya registrado' if exists else 'Email disponible'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """Registro de nuevo usuario con JWT + Refresh Token"""
    # Obtener información del request
    info_request = obtener_info_request(request)
    ip_address = info_request['ip_address']
    
    # Verificar rate limiting (5 intentos en 1 minuto)
    if LoginAttempt.esta_bloqueado(ip_address, attempt_type='register', max_intentos=5, minutos=1):
        tiempo_restante = LoginAttempt.tiempo_restante_bloqueo(ip_address, attempt_type='register', minutos=1)
        return Response({
            'error': 'Demasiados intentos de registro',
            'bloqueado': True,
            'tiempo_restante': tiempo_restante,
            'mensaje': f'Has excedido el límite de intentos. Intenta de nuevo en {tiempo_restante} segundos.'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Registrar intento exitoso
        LoginAttempt.registrar_intento(
            ip_address=ip_address,
            username=user.username,
            attempt_type='register',
            success=True,
            user_agent=info_request['user_agent']
        )
        
        # Generar Access Token (JWT - 15 minutos)
        access_token = generar_access_token(user)
        
        # Generar Refresh Token (30 días)
        refresh_token_plano, refresh_token_obj = RefreshToken.crear_token(
            usuario=user,
            duracion_dias=30,
            user_agent=info_request['user_agent'],
            ip_address=info_request['ip_address']
        )
        
        # Construir nombre completo
        nombre = f"{user.first_name} {user.last_name}".strip() or user.username
        
        # Obtener rol del perfil
        rol = user.profile.rol if hasattr(user, 'profile') else 'cliente'
        
        # Crear respuesta
        response = Response({
            'accessToken': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'nombre': nombre,
                'rol': rol
            },
            'message': 'Usuario registrado exitosamente'
        }, status=status.HTTP_201_CREATED)
        
        # Configurar Refresh Token como HTTP-Only Cookie
        response.set_cookie(
            key='refreshToken',
            value=refresh_token_plano,
            max_age=30 * 24 * 60 * 60,  # 30 días en segundos
            httponly=True,  # No accesible desde JavaScript
            secure=False,  # True en producción (HTTPS)
            samesite='Lax',  # Protección CSRF
            path='/'  # Accesible desde cualquier ruta
        )
        
        return response
    
    # Registrar intento fallido
    LoginAttempt.registrar_intento(
        ip_address=ip_address,
        username=request.data.get('username'),
        attempt_type='register',
        success=False,
        user_agent=info_request['user_agent']
    )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """
    🔐 Login con JWT + Refresh Token
    
    ✅ Throttle: AnonLoginRateThrottle (5 requests/minuto)
    Previene ataques de fuerza bruta
    """
    username_or_email = request.data.get('username')
    password = request.data.get('password')
    
    # Obtener información del request
    info_request = obtener_info_request(request)
    ip_address = info_request['ip_address']
    
    # Verificar rate limiting por IP (5 intentos en 1 minuto)
    if LoginAttempt.esta_bloqueado(ip_address, attempt_type='login', max_intentos=5, minutos=1):
        tiempo_restante = LoginAttempt.tiempo_restante_bloqueo(ip_address, attempt_type='login', minutos=1)
        return Response({
            'error': 'Demasiados intentos de inicio de sesión',
            'bloqueado': True,
            'tiempo_restante': tiempo_restante,
            'mensaje': f'Has excedido el límite de intentos. Intenta de nuevo en {tiempo_restante} segundos.'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    # Verificar rate limiting por usuario (5 intentos en 1 minuto)
    if username_or_email and LoginAttempt.usuario_esta_bloqueado(username_or_email, attempt_type='login', max_intentos=5, minutos=1):
        tiempo_restante = LoginAttempt.tiempo_restante_bloqueo_usuario(username_or_email, attempt_type='login', minutos=1)
        return Response({
            'error': 'Demasiados intentos de inicio de sesión',
            'bloqueado': True,
            'tiempo_restante': tiempo_restante,
            'mensaje': f'Has excedido el límite de intentos. Intenta de nuevo en {tiempo_restante} segundos.'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    if not username_or_email or not password:
        return Response(
            {'error': 'Por favor proporciona usuario/email y contraseña'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Intentar autenticar por username primero
    user = authenticate(username=username_or_email, password=password)
    
    # Si falla, intentar por email
    if not user:
        try:
            user_obj = User.objects.get(email=username_or_email)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass
    
    if user:
        # Registrar intento exitoso
        LoginAttempt.registrar_intento(
            ip_address=ip_address,
            username=username_or_email,
            attempt_type='login',
            success=True,
            user_agent=info_request['user_agent']
        )
        
        # Logging de autenticación exitosa
        logger_auth.info(
            f'[LOGIN_SUCCESS] Usuario: {user.username} | Email: {user.email} | IP: {ip_address} | Rol: {user.profile.rol if hasattr(user, "profile") else "cliente"}'
        )
        
        # Generar Access Token (JWT - 15 minutos)
        access_token = generar_access_token(user)
        
        # Generar Refresh Token (2 horas)
        refresh_token_plano, refresh_token_obj = RefreshToken.crear_token(
            usuario=user,
            duracion_horas=2,
            user_agent=info_request['user_agent'],
            ip_address=info_request['ip_address']
        )
        
        # Construir nombre completo
        nombre = f"{user.first_name} {user.last_name}".strip() or user.username
        
        # Obtener rol del perfil
        rol = user.profile.rol if hasattr(user, 'profile') else 'cliente'
        
        # Crear respuesta
        response = Response({
            'accessToken': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'nombre': nombre,
                'rol': rol
            },
            'message': 'Login exitoso'
        })
        
        # Configurar Refresh Token como HTTP-Only Cookie
        response.set_cookie(
            key='refreshToken',
            value=refresh_token_plano,
            max_age=2 * 60 * 60,  # 2 horas en segundos
            httponly=True,  # No accesible desde JavaScript
            secure=False,  # True en producción (HTTPS)
            samesite='Lax',  # Protección CSRF
            path='/'  # Accesible desde cualquier ruta
        )
        
        return response
    
    # Registrar intento fallido
    LoginAttempt.registrar_intento(
        ip_address=ip_address,
        username=username_or_email,
        attempt_type='login',
        success=False,
        user_agent=info_request['user_agent']
    )
    
    # Logging de intento fallido
    logger_security.warning(
        f'[LOGIN_FAILED] Usuario: {username_or_email} | IP: {ip_address} | Razón: Credenciales inválidas'
    )
    
    return Response(
        {'error': 'Credenciales inválidas'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def refresh_token(request):
    """Refrescar Access Token usando Refresh Token"""
    # Obtener Refresh Token desde cookie
    refresh_token_plano = request.COOKIES.get('refreshToken')
    
    if not refresh_token_plano:
        logger_security.warning('[REFRESH_FAILED] Refresh token no encontrado en cookie')
        return Response(
            {'error': 'Refresh token no encontrado'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Verificar Refresh Token
    refresh_token_obj = RefreshToken.verificar_token(refresh_token_plano)
    
    if not refresh_token_obj:
        logger_security.warning('[REFRESH_FAILED] Refresh token inválido o expirado')
        return Response(
            {'error': 'Refresh token inválido o expirado'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Obtener usuario
    user = refresh_token_obj.usuario
    
    # Obtener información del request
    info_request = obtener_info_request(request)
    
    # Generar nuevo Access Token
    access_token = generar_access_token(user)
    
    # Generar nuevo Refresh Token (rotación de tokens, 2 horas)
    nuevo_refresh_token_plano, nuevo_refresh_token_obj = RefreshToken.crear_token(
        usuario=user,
        duracion_horas=2,
        user_agent=info_request['user_agent'],
        ip_address=info_request['ip_address']
    )
    
    # Revocar el Refresh Token anterior
    refresh_token_obj.revocar()
    
    # Logging de refresh exitoso
    logger_auth.info(
        f'[TOKEN_REFRESH] Usuario: {user.username} | IP: {info_request["ip_address"]}'
    )
    
    # Construir nombre completo
    nombre = f"{user.first_name} {user.last_name}".strip() or user.username
    
    # Obtener rol del perfil
    rol = user.profile.rol if hasattr(user, 'profile') else 'cliente'
    
    # Crear respuesta
    response = Response({
        'accessToken': access_token,
        'user': {
            'id': user.id,
            'email': user.email,
            'nombre': nombre,
            'rol': rol
        },
        'message': 'Token refrescado exitosamente'
    })
    
    # Actualizar Refresh Token en cookie
    from django.conf import settings
    response.set_cookie(
        key='refreshToken',
        value=nuevo_refresh_token_plano,
        max_age=2 * 60 * 60,  # 2 horas en segundos
        httponly=True,
        secure=not settings.DEBUG,  # True en producción (HTTPS), False en desarrollo
        samesite='Lax',
        path='/'  # ← Accesible desde cualquier ruta
    )
    
    return response


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def logout(request):
    """
    Logout - Invalida Access Token en blacklist y revoca Refresh Token
    
    Espera:
    - Token en header Authorization: Bearer <token>
    - Refresh Token en cookie
    
    Retorna:
    - 200: Logout exitoso
    """
    from .models import TokenBlacklist, Cart
    
    # Obtener información del request
    info_request = obtener_info_request(request)
    
    # ✅ CRÍTICO: Limpiar carrito del usuario ANTES de revocar tokens
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                items_count = cart.items.count()
                cart.items.all().delete()
                logger_auth.info(
                    f'[LOGOUT_CART_CLEARED] Usuario: {request.user.username} | Items eliminados: {items_count}'
                )
        except Exception as e:
            logger_security.error(
                f'[LOGOUT_CART_ERROR] Error limpiando carrito: {str(e)} | Usuario: {request.user.username}'
            )
    
    # Obtener Access Token del header
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    access_token = None
    
    if auth_header.startswith('Bearer '):
        access_token = auth_header[7:]
        
        # Agregar Access Token a blacklist
        if access_token and request.user.is_authenticated:
            try:
                TokenBlacklist.agregar_a_blacklist(
                    token=access_token,
                    usuario=request.user,
                    razon='logout'
                )
                logger_auth.info(
                    f'[LOGOUT_SUCCESS] Usuario: {request.user.username} | IP: {info_request["ip_address"]}'
                )
            except Exception as e:
                logger_security.error(
                    f'[LOGOUT_ERROR] Error al agregar token a blacklist: {str(e)} | Usuario: {request.user.username}'
                )
    
    # Obtener Refresh Token desde cookie
    refresh_token_plano = request.COOKIES.get('refreshToken')
    
    if refresh_token_plano:
        # Verificar y revocar el token
        refresh_token_obj = RefreshToken.verificar_token(refresh_token_plano)
        if refresh_token_obj:
            # Revocar todos los tokens del usuario (logout global)
            RefreshToken.revocar_todos_usuario(refresh_token_obj.usuario)
            logger_auth.info(
                f'[REFRESH_TOKENS_REVOKED] Usuario: {refresh_token_obj.usuario.username} | IP: {info_request["ip_address"]}'
            )
    
    # Crear respuesta
    response = Response({'message': 'Logout exitoso'})
    
    # Eliminar cookie de Refresh Token
    response.delete_cookie('refreshToken', path='/api/auth/')
    
    return response


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]
    
    def get_serializer_context(self):
        """Agregar contexto para optimizar serialización"""
        context = super().get_serializer_context()
        # Marcar como listado para no enviar imágenes base64 pesadas
        if self.action == 'list':
            context['is_list'] = True
        return context
    
    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save()
    
    def perform_destroy(self, instance):
        instance.delete()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'message': 'Producto creado exitosamente',
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED,
            headers=headers
        )
    
    def retrieve(self, request, *args, **kwargs):
        """
        Obtener detalles completos de un producto con productos relacionados
        GET /api/productos/{id}/
        """
        producto = self.get_object()
        serializer = self.get_serializer(producto)
        
        # Obtener productos relacionados (misma categoría, máximo 10)
        productos_relacionados = Producto.objects.filter(
            categoria=producto.categoria,
            activo=True
        ).exclude(
            id=producto.id
        ).order_by('-created_at')[:10]
        
        # Optimización: No enviar imágenes base64 en productos relacionados
        productos_relacionados_serializer = ProductoSerializer(
            productos_relacionados,
            many=True,
            context={'is_list': True}
        )
        
        return Response({
            'producto': serializer.data,
            'productos_relacionados': productos_relacionados_serializer.data
        })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def productos_carrusel(request):
    """
    Obtiene todos los productos marcados para mostrar en el carrusel.
    SIN CACHÉ - Los productos aparecen inmediatamente después de crearlos.
    
    OPTIMIZACIONES:
    ✅ select_related('creado_por') - Evita N+1 en usuario
    ✅ prefetch_related('favoritos') - Evita N+1 en favoritos
    ✅ only() - Solo campos necesarios
    ✅ Contexto is_list - Excluye imágenes base64 grandes
    """
    # ✅ OPTIMIZACIÓN: Usar prefetch_related en lugar de annotate(Count())
    # annotate(Count('favoritos')) hace 1 query por producto (N+1)
    # prefetch_related('favoritos') hace 2 queries totales (N+1 evitado)
    productos = Producto.objects.filter(
        en_carrusel=True, 
        activo=True
    ).select_related(
        'creado_por'  # ✅ Evita N+1 en usuario
    ).prefetch_related(
        'favoritos'  # ✅ Evita N+1 en favoritos (carga en 1 query)
    ).only(
        # ✅ Solo campos necesarios (reduce tamaño de datos)
        # ⚠️ IMPORTANTE: Incluir 'imagen' para que el serializer pueda acceder a obj.imagen
        'id', 'nombre', 'descripcion', 'precio', 'descuento', 'categoria',
        'imagen', 'imagen_url', 'stock_total', 'stock_reservado', 'stock_vendido',
        'activo', 'en_carrusel', 'creado_por', 'created_at', 'updated_at'
    ).order_by('-created_at')
    
    # Pasar contexto para optimizar serialización (no enviar base64 pesados)
    # ⚠️ IMPORTANTE: Incluir 'request' para que el serializer construya URLs absolutas
    serializer = ProductoSerializer(productos, many=True, context={'is_list': True, 'request': request})
    
    response_data = {
        'count': len(serializer.data),
        'data': serializer.data
    }
    
    logger.info(f'[CARRUSEL_LOADED] {len(serializer.data)} productos cargados')
    
    return Response(response_data)


# ═══════════════════════════════════════════════════════════════════════════════
# 🛒 CARRITO DE COMPRAS - VIEWS
# ═══════════════════════════════════════════════════════════════════════════════

class CartViewSet(viewsets.ViewSet):
    """
    ViewSet para manejar el carrito de compras
    
    Endpoints:
    - GET    /api/carrito/          → Obtener carrito del usuario
    - POST   /api/carrito/agregar/  → Agregar producto al carrito
    - PUT    /api/carrito/items/{id}/ → Actualizar cantidad
    - DELETE /api/carrito/items/{id}/ → Eliminar item
    - DELETE /api/carrito/vaciar/   → Vaciar carrito
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [CartWriteRateThrottle]  # ✅ Aplicar throttle a escritura en carrito
    
    def get_throttles(self):
        """
        Aplicar throttles específicos según la acción:
        - checkout: CheckoutRateThrottle (más restrictivo)
        - bulk-update: CartWriteRateThrottle (estándar)
        - resto: CartWriteRateThrottle (estándar)
        """
        if self.action == 'checkout':
            return [CheckoutRateThrottle()]
        return super().get_throttles()
    
    def list(self, request):
        """GET /api/carrito/ - Obtener carrito del usuario"""
        # Optimización: prefetch_related para evitar N+1 queries
        cart, _ = Cart.objects.prefetch_related(
            'items__product'
        ).get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    def _get_rate_limit_for_user(self, user):
        """
        Obtener límite de rate limiting según tipo de usuario
        
        - Admin: 1000 por hora (sin restricción práctica)
        - Trabajador: 500 por hora (operaciones bulk)
        - Cliente: 100 por hora (razonable para compra normal)
        """
        if user.is_superuser:
            return 1000
        
        if hasattr(user, 'profile'):
            rol = user.profile.rol
            if rol == 'admin':
                return 1000
            elif rol == 'trabajador':
                return 500
        
        # Cliente por defecto
        return 100
    
    @action(detail=False, methods=['post'], url_path='agregar')
    def agregar(self, request):
        """
        POST /api/carrito/agregar/
        
        Body:
        {
            "product_id": 1,
            "quantity": 1
        }
        
        Returns:
        - 201: Producto agregado exitosamente
        - 400: Validación fallida (stock insuficiente, datos inválidos)
        - 404: Producto no encontrado
        - 429: Rate limit excedido
        """
        # ✅ Rate limiting INTELIGENTE según tipo de usuario
        limit = self._get_rate_limit_for_user(request.user)
        allowed, remaining, reset_time = check_rate_limit(
            request.user.id, 
            'add',
            limit=limit,
            window_minutes=60
        )
        
        if not allowed:
            logger.warning(f"[Rate Limit] Usuario {request.user.username} excedió límite de {limit}/hora")
            return Response(
                {
                    'error': f'Límite de solicitudes excedido ({limit}/hora). Intenta más tarde.',
                    'reset_time': reset_time.isoformat(),
                    'remaining': remaining
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)
        
        # ✅ VALIDACIONES BÁSICAS
        if not product_id:
            return Response(
                {'error': 'product_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not isinstance(quantity, int) or quantity < 1 or quantity > 999:
            return Response(
                {'error': 'La cantidad debe estar entre 1 y 999'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Producto.objects.get(id=product_id)
        except Producto.DoesNotExist:
            return Response(
                {'error': 'Producto no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # ✅ VALIDAR STOCK DISPONIBLE (pero NO reservar)
        # Solo verificamos que haya stock, sin afectar el inventario
        if product.stock_disponible < quantity:
            return Response(
                {
                    'error': f'Stock insuficiente. Disponible: {product.stock_disponible}',
                    'available': product.stock_disponible,
                    'requested': quantity
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ✅ OBTENER O CREAR CARRITO (es solo una lista de deseos)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        # ✅ CREAR O ACTUALIZAR ITEM EN CARRITO
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity,
                'price_at_addition': product.precio
            }
        )
        
        if not created:
            # Si el item ya existe, incrementar cantidad
            new_quantity = item.quantity + quantity
            
            # Validar stock nuevamente
            if product.stock_disponible < new_quantity:
                return Response(
                    {
                        'error': f'Stock insuficiente. Disponible: {product.stock_disponible}',
                        'available': product.stock_disponible,
                        'requested': new_quantity
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            item.quantity = new_quantity
            item.save()
        
        # ✅ REGISTRAR EN AUDITORÍA
        log_cart_action(
            user=request.user,
            action='add',
            product_id=product.id,
            product_name=product.nombre,
            quantity_before=0 if created else item.quantity - quantity,
            quantity_after=item.quantity,
            price=product.precio,
            request=request
        )
        
        # Optimización: Recargar cart con prefetch para evitar N+1 queries
        cart = Cart.objects.prefetch_related(
            'items__product'
        ).get(id=cart.id)
        
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['put'], url_path='items/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        """
        PUT /api/carrito/items/{item_id}/
        
        Body:
        {
            "quantity": 2
        }
        """
        quantity = request.data.get('quantity')
        
        if quantity is None:
            return Response(
                {'error': 'quantity es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if quantity < 1:
            return Response(
                {'error': 'La cantidad debe ser mayor a 0'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validar stock
        if item.product.stock < quantity:
            return Response(
                {'error': f'Stock insuficiente. Disponible: {item.product.stock}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        quantity_before = item.quantity
        item.quantity = quantity
        item.save()
        
        # Registrar en auditoría
        log_cart_action(
            user=request.user,
            action='update',
            product_id=item.product.id,
            product_name=item.product.nombre,
            quantity_before=quantity_before,
            quantity_after=quantity,
            price=item.product.precio,
            request=request
        )
        
        cart = item.cart
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['delete'], url_path='items/(?P<item_id>[^/.]+)')
    def delete_item(self, request, item_id=None):
        """
        DELETE /api/carrito/items/{item_id}/
        Elimina un ítem del carrito con protección contra race conditions
        """
        logger.info(f"[Cart DELETE] Intentando eliminar item_id={item_id} para usuario={request.user.username}")
        
        try:
            # RACE CONDITION FIX: Usar transacción atómica con lock
            with transaction.atomic():
                # select_for_update() previene race conditions
                item = CartItem.objects.select_for_update().get(id=item_id, cart__user=request.user)
                logger.info(f"[Cart DELETE] Item encontrado: id={item.id}, producto={item.product.nombre}, usuario={request.user.username}")
                
                # Registrar en auditoría ANTES de eliminar
                log_cart_action(
                    user=request.user,
                    action='remove',
                    product_id=item.product.id,
                    product_name=item.product.nombre,
                    quantity_before=item.quantity,
                    quantity_after=0,
                    price=item.product.precio,
                    request=request
                )
                
                cart = item.cart
                item.delete()
                
                logger.info(f"[Cart DELETE] Item eliminado exitosamente: id={item_id}, usuario={request.user.username}")
                
                serializer = CartSerializer(cart)
                return Response(serializer.data)
                
        except CartItem.DoesNotExist:
            logger.warning(f"[Cart DELETE] Item NO encontrado: item_id={item_id}, usuario={request.user.username}")
            # Listar todos los items del usuario para depuración
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                items_en_carrito = list(cart.items.values_list('id', flat=True))
                logger.warning(f"[Cart DELETE] Items disponibles en carrito: {items_en_carrito}")
            return Response(
                {'error': 'Item no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['delete'], url_path='vaciar')
    def vaciar(self, request):
        """DELETE /api/carrito/vaciar/ - Vaciar carrito"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        # Registrar en auditoría
        log_cart_action(
            user=request.user,
            action='clear',
            request=request
        )
        
        cart.items.all().delete()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        """
        POST /api/carrito/checkout/
        
        ✅ FASE 2: RESERVAR STOCK PARA CHECKOUT
        
        Este endpoint RESERVA el stock de todos los items del carrito.
        El stock se libera automáticamente si:
        - El pago falla (ROLLBACK)
        - Pasan 15 minutos sin confirmar (TTL expirado)
        
        Respuesta:
        - 200: Reserva exitosa
        - 400: Stock insuficiente o carrito vacío
        - 409: Conflicto (stock cambió mientras se procesaba)
        """
        from .models import StockReservation
        
        # Obtener carrito
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Carrito vacío'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que haya items
        if not cart.items.exists():
            return Response(
                {'error': 'El carrito está vacío'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # ✅ RESERVAR STOCK PARA CADA ITEM
        reservas = []
        errores = []
        
        try:
            for item in cart.items.all():
                producto = item.product
                cantidad = item.quantity
                
                # Verificar stock disponible
                if producto.stock_disponible < cantidad:
                    errores.append({
                        'producto': producto.nombre,
                        'disponible': producto.stock_disponible,
                        'solicitado': cantidad
                    })
                    continue
                
                # Crear reserva
                reserva = StockReservation.crear_reserva(
                    usuario=request.user,
                    producto=producto,
                    cantidad=cantidad,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT'),
                    ttl_minutos=15
                )
                
                # Actualizar stock del producto
                producto.stock_reservado += cantidad
                producto.save()
                
                reservas.append(reserva)
        
        except Exception as e:
            # Si hay error, liberar todas las reservas
            for reserva in reservas:
                producto = reserva.producto
                producto.stock_reservado -= reserva.cantidad
                producto.save()
                reserva.status = 'cancelled'
                reserva.cancelled_at = timezone.now()
                reserva.save()
            
            return Response(
                {'error': f'Error al procesar checkout: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Si hay errores de stock, liberar todo
        if errores:
            for reserva in reservas:
                producto = reserva.producto
                producto.stock_reservado -= reserva.cantidad
                producto.save()
                reserva.status = 'cancelled'
                reserva.cancelled_at = timezone.now()
                reserva.save()
            
            return Response(
                {
                    'error': 'Stock insuficiente para algunos productos',
                    'detalles': errores
                },
                status=status.HTTP_409_CONFLICT
            )
        
        # ✅ ÉXITO: Retornar información de reservas
        return Response(
            {
                'message': 'Stock reservado exitosamente',
                'reservas': [
                    {
                        'id': r.id,
                        'producto': r.producto.nombre,
                        'cantidad': r.cantidad,
                        'expires_at': r.expires_at.isoformat()
                    }
                    for r in reservas
                ],
                'total_items': sum(r.cantidad for r in reservas),
                'ttl_minutos': 15
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='bulk-update')
    def bulk_update(self, request):
        """
        POST /api/carrito/bulk-update/
        
        ✅ ACTUALIZACIÓN MASIVA DE CARRITO
        
        Actualiza múltiples items del carrito en una sola petición.
        Más eficiente que múltiples requests individuales.
        
        Body:
        {
            "updates": {
                "1": 2,      // producto_id: cantidad
                "5": 3,
                "10": 1
            }
        }
        
        Returns:
        - 200: Actualización exitosa
        - 400: Validación fallida
        - 401: No autenticado
        """
        try:
            data = request.data
            updates = data.get('updates', {})
            
            if not updates:
                return Response(
                    {'error': 'updates requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obtener o crear carrito del usuario
            cart, _ = Cart.objects.get_or_create(user=request.user)
            
            # Procesar cada actualización
            for product_id_str, cantidad in updates.items():
                try:
                    product_id = int(product_id_str)
                    cantidad = int(cantidad)
                    
                    # Validar cantidad
                    if cantidad < 0:
                        continue
                    
                    # Si cantidad es 0, eliminar item
                    if cantidad == 0:
                        CartItem.objects.filter(
                            cart=cart,
                            product_id=product_id
                        ).delete()
                        continue
                    
                    # Obtener producto
                    try:
                        product = Producto.objects.get(id=product_id, activo=True)
                    except Producto.DoesNotExist:
                        continue
                    
                    # Validar stock disponible
                    if product.stock_disponible < cantidad:
                        continue
                    
                    # Actualizar o crear item
                    CartItem.objects.update_or_create(
                        cart=cart,
                        product=product,
                        defaults={
                            'quantity': cantidad,
                            'price_at_addition': product.precio
                        }
                    )
                    
                    # Registrar en auditoría
                    log_cart_action(
                        user=request.user,
                        action='bulk_update',
                        product_id=product_id,
                        product_name=product.nombre,
                        quantity_before=0,
                        quantity_after=cantidad,
                        price=product.precio,
                        request=request
                    )
                
                except (ValueError, TypeError):
                    continue
            
            # Retornar carrito actualizado
            cart = Cart.objects.prefetch_related(
                'items__product'
            ).get(id=cart.id)
            
            serializer = CartSerializer(cart)
            return Response(
                {
                    'message': 'Carrito actualizado exitosamente',
                    'cart': serializer.data
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            logger.error(f'[BULK_UPDATE_ERROR] {str(e)} | Usuario: {request.user.username}')
            return Response(
                {'error': f'Error al actualizar carrito: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ═══════════════════════════════════════════════════════════════════════════════
# ❤️ FAVORITOS - ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def agregar_favorito(request, producto_id):
    """
    Agregar un producto a favoritos
    POST /api/favoritos/agregar/{producto_id}/
    """
    try:
        producto = Producto.objects.get(id=producto_id, activo=True)
    except Producto.DoesNotExist:
        return Response(
            {'error': 'Producto no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    favorito, created = Favorito.objects.get_or_create(
        usuario=request.user,
        producto=producto
    )
    
    if created:
        return Response(
            {
                'message': 'Producto agregado a favoritos',
                'favoritos_count': producto.favoritos.count()
            },
            status=status.HTTP_201_CREATED
        )
    else:
        return Response(
            {
                'message': 'El producto ya está en favoritos',
                'favoritos_count': producto.favoritos.count()
            },
            status=status.HTTP_200_OK
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remover_favorito(request, producto_id):
    """
    Remover un producto de favoritos
    DELETE /api/favoritos/remover/{producto_id}/
    """
    try:
        producto = Producto.objects.get(id=producto_id, activo=True)
    except Producto.DoesNotExist:
        return Response(
            {'error': 'Producto no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        favorito = Favorito.objects.get(usuario=request.user, producto=producto)
        favorito.delete()
        return Response(
            {
                'message': 'Producto removido de favoritos',
                'favoritos_count': producto.favoritos.count()
            },
            status=status.HTTP_200_OK
        )
    except Favorito.DoesNotExist:
        return Response(
            {'error': 'El producto no está en favoritos'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def es_favorito(request, producto_id):
    """
    Verificar si un producto es favorito del usuario
    GET /api/favoritos/es-favorito/{producto_id}/
    """
    try:
        producto = Producto.objects.get(id=producto_id, activo=True)
    except Producto.DoesNotExist:
        return Response(
            {'error': 'Producto no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    es_favorito = Favorito.objects.filter(
        usuario=request.user,
        producto=producto
    ).exists()
    
    return Response({
        'es_favorito': es_favorito,
        'favoritos_count': producto.favoritos.count()
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def verificar_favoritos_batch(request):
    """
    Verificar múltiples productos favoritos en una sola petición (optimización N+1)
    GET /api/favoritos/verificar-batch/?ids=1,2,3,4,5
    """
    # Obtener IDs de productos desde query params
    ids_str = request.GET.get('ids', '')
    
    if not ids_str:
        return Response({'favoritos': {}}, status=status.HTTP_200_OK)
    
    try:
        # Convertir string de IDs a lista de enteros
        producto_ids = [int(id.strip()) for id in ids_str.split(',') if id.strip()]
    except ValueError:
        return Response(
            {'error': 'IDs inválidos'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Obtener todos los favoritos del usuario para estos productos en una sola query
    favoritos = Favorito.objects.filter(
        usuario=request.user,
        producto_id__in=producto_ids
    ).values_list('producto_id', flat=True)
    
    # Crear diccionario de respuesta
    resultado = {str(pid): pid in favoritos for pid in producto_ids}
    
    return Response({'favoritos': resultado})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def validar_stock_producto(request, producto_id):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    ✅ ENDPOINT - Validar Stock de Producto (Servidor)
    ═══════════════════════════════════════════════════════════════════════════════
    
    Valida el stock de un producto en el servidor.
    Esto proporciona mayor seguridad que validar solo en frontend.
    
    GET /api/productos/{id}/validar-stock/
    
    Retorna:
    - disponible: bool - Si el producto está disponible
    - stock: int - Stock actual
    - mensaje: str - Mensaje descriptivo
    """
    try:
        producto = Producto.objects.get(id=producto_id)
        disponible = producto.stock > 0
        
        return Response({
            'disponible': disponible,
            'stock': producto.stock,
            'mensaje': 'Producto disponible' if disponible else 'Producto agotado'
        }, status=status.HTTP_200_OK)
    except Producto.DoesNotExist:
        return Response({
            'error': 'Producto no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mis_pedidos(request):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    📦 ENDPOINT - Historial de Pedidos del Usuario
    ═══════════════════════════════════════════════════════════════════════════════
    
    Obtiene todos los pedidos del usuario autenticado con detalles completos.
    
    GET /api/mis-pedidos/
    
    Query params:
    - estado: str - Filtrar por estado (opcional)
    - limit: int - Límite de resultados (default: 50)
    
    Retorna:
    - Lista de pedidos con detalles de productos
    """
    from .serializers_admin import PedidoSerializer
    from .models import Pedido
    
    # Obtener parámetros
    estado = request.query_params.get('estado', None)
    limit = int(request.query_params.get('limit', 50))
    
    # Obtener pedidos del usuario
    pedidos = Pedido.objects.filter(usuario=request.user).select_related(
        'usuario'
    ).prefetch_related('detalles__producto').order_by('-created_at')
    
    # Filtrar por estado si se proporciona
    if estado:
        pedidos = pedidos.filter(estado=estado)
    
    # Aplicar límite
    pedidos = pedidos[:limit]
    
    serializer = PedidoSerializer(pedidos, many=True)
    
    return Response({
        'count': len(pedidos),
        'pedidos': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def mis_favoritos(request):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    ❤️ ENDPOINT - Mis Favoritos del Usuario
    ═══════════════════════════════════════════════════════════════════════════════
    
    Obtiene todos los productos favoritos del usuario autenticado.
    
    GET /api/mis-favoritos/
    
    Query params:
    - limit: int - Límite de resultados (default: 100)
    
    Retorna:
    - Lista de productos favoritos con información completa
    """
    limit = int(request.query_params.get('limit', 100))
    
    # Obtener favoritos del usuario
    favoritos = Favorito.objects.filter(
        usuario=request.user
    ).select_related('producto').order_by('-created_at')[:limit]
    
    # Extraer productos
    productos = [fav.producto for fav in favoritos]
    
    serializer = ProductoSerializer(productos, many=True)
    
    return Response({
        'count': len(productos),
        'favoritos': serializer.data
    }, status=status.HTTP_200_OK)
