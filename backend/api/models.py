from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
import secrets
import hashlib


class UserProfile(models.Model):
    """Perfil extendido de usuario con roles personalizados"""
    
    ROLES = [
        ('cliente', 'Cliente'),
        ('mensajero', 'Mensajero'),
        ('trabajador', 'Trabajador'),
        ('admin', 'Administrador'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"
    
    @property
    def has_admin_access(self):
        """Verifica si el usuario tiene acceso al panel de admin"""
        return self.rol in ['admin', 'trabajador', 'mensajero']


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crear perfil automáticamente al crear usuario"""
    if created:
        rol = 'admin' if (instance.is_superuser or instance.is_staff) else 'cliente'
        UserProfile.objects.create(user=instance, rol=rol)
    else:
        # Actualizar rol si cambia a superuser/staff
        if hasattr(instance, 'profile'):
            if instance.is_superuser or instance.is_staff:
                if instance.profile.rol != 'admin':
                    instance.profile.rol = 'admin'
                    instance.profile.save()


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Guardar perfil al guardar usuario"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Producto(models.Model):
    CATEGORIAS = [
        ('electrodomesticos', 'Electrodomésticos'),
        ('energia_tecnologia', 'Energía y Tecnología'),
        ('herramientas', 'Herramientas'),
        ('hogar_entretenimiento', 'Hogar y Entretenimiento'),
        ('otros', 'Otros Artículos'),
    ]
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.IntegerField(default=0, help_text="Porcentaje de descuento (0-100)")
    
    # ✅ SISTEMA DE INVENTARIO SEPARADO
    stock_total = models.IntegerField(default=0, help_text="Stock físico total del almacén")
    stock_reservado = models.IntegerField(default=0, help_text="Stock apartado por clientes en Checkout")
    stock_vendido = models.IntegerField(default=0, help_text="Stock ya vendido/completado")
    
    # Campo legado para compatibilidad (se calcula automáticamente)
    stock = models.IntegerField(default=0, help_text="Stock disponible (total - reservado - vendido)")
    
    categoria = models.CharField(max_length=50, choices=CATEGORIAS, default='otros')
    imagen_url = models.TextField(blank=True, null=True)  # Legado: Base64 (mantener para compatibilidad)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)  # ✅ Nuevo: Archivos reales
    activo = models.BooleanField(default=True)
    en_carrusel = models.BooleanField(default=False, help_text="Mostrar en carrusel principal")
    en_carousel_card = models.BooleanField(default=True, help_text="Mostrar en CarouselCard (tarjetas inferiores)")
    en_all_products = models.BooleanField(default=True, help_text="Mostrar en AllProducts (catálogo completo)")
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'productos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stock']),
            models.Index(fields=['stock_reservado']),
        ]
    
    def __str__(self):
        return self.nombre
    
    @property
    def stock_disponible(self):
        """Calcula el stock disponible (total - reservado - vendido)"""
        return max(0, self.stock_total - self.stock_reservado - self.stock_vendido)
    
    def save(self, *args, **kwargs):
        """
        Actualizar stock automáticamente al guardar.
        Invalida caché de carrusel si el producto está en carrusel o cambió de estado.
        """
        self.stock = self.stock_disponible
        super().save(*args, **kwargs)
        
        # ✅ Invalidar caché si el producto está en carrusel o es activo
        if self.en_carrusel or self.activo:
            cache.delete('productos_carrusel_cache')
    
    def delete(self, *args, **kwargs):
        """
        Al eliminar un producto, invalidar caché de carrusel.
        """
        # Invalidar caché antes de eliminar
        if self.en_carrusel or self.activo:
            cache.delete('productos_carrusel_cache')
        
        super().delete(*args, **kwargs)


class Pedido(models.Model):
    """Modelo de pedidos/órdenes"""
    
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en_preparacion', 'En Preparación'),
        ('en_camino', 'En Camino'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pedidos')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='efectivo')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    direccion_entrega = models.TextField()
    telefono = models.CharField(max_length=20)
    notas = models.TextField(blank=True, null=True)
    
    # Asignación
    mensajero = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='pedidos_asignados',
        limit_choices_to={'profile__rol': 'mensajero'}
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'pedidos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Pedido #{self.id} - {self.usuario.username}'


class DetallePedido(models.Model):
    """Detalle de productos en un pedido"""
    
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'detalles_pedido'
    
    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'
    
    def save(self, *args, **kwargs):
        # Calcular subtotal automáticamente
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)


class Notificacion(models.Model):
    """Sistema de notificaciones"""
    
    TIPOS = [
        ('info', 'Información'),
        ('success', 'Éxito'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    tipo = models.CharField(max_length=20, choices=TIPOS, default='info')
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    url = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notificaciones'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.titulo} - {self.usuario.username}'


class AuditLog(models.Model):
    """
    Registro de auditoría para todas las acciones en el panel de admin.
    Solo visible para administradores.
    """
    
    ACCIONES = [
        ('crear', 'Crear'),
        ('editar', 'Editar'),
        ('eliminar', 'Eliminar'),
        ('activar', 'Activar'),
        ('desactivar', 'Desactivar'),
        ('cambiar_rol', 'Cambiar Rol'),
    ]
    
    MODULOS = [
        ('producto', 'Producto'),
        ('usuario', 'Usuario'),
        ('pedido', 'Pedido'),
        ('notificacion', 'Notificación'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='acciones_realizadas')
    accion = models.CharField(max_length=20, choices=ACCIONES)
    modulo = models.CharField(max_length=20, choices=MODULOS)
    objeto_id = models.IntegerField()
    objeto_repr = models.CharField(max_length=500)  # Representación del objeto
    detalles = models.JSONField(default=dict)  # Datos completos del cambio
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['modulo', '-timestamp']),
            models.Index(fields=['usuario', '-timestamp']),
        ]
    
    def __str__(self):
        usuario_nombre = self.usuario.username if self.usuario else 'Sistema'
        return f'{usuario_nombre} - {self.get_accion_display()} {self.get_modulo_display()} #{self.objeto_id}'


class RefreshToken(models.Model):
    """
    Modelo para almacenar Refresh Tokens de forma segura.
    Los tokens se almacenan hasheados para mayor seguridad.
    """
    
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='refresh_tokens'
    )
    
    # Token hasheado (SHA-256) - nunca almacenamos el token en texto plano
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    
    # Identificador único para el dispositivo/sesión
    jti = models.CharField(max_length=64, unique=True, db_index=True)  # JWT ID
    
    # Información del dispositivo/navegador
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Control de expiración
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    # Control de revocación
    revocado = models.BooleanField(default=False)
    revocado_at = models.DateTimeField(null=True, blank=True)
    
    # Última vez que se usó para refrescar
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'refresh_tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['usuario', '-created_at']),
            models.Index(fields=['token_hash']),
            models.Index(fields=['jti']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f'RefreshToken para {self.usuario.username} - JTI: {self.jti[:8]}...'
    
    @staticmethod
    def hash_token(token):
        """Hashea un token usando SHA-256"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def generate_token():
        """Genera un token seguro de 64 bytes (128 caracteres hex)"""
        return secrets.token_hex(64)
    
    @staticmethod
    def generate_jti():
        """Genera un JWT ID único"""
        return secrets.token_urlsafe(32)
    
    def is_valid(self):
        """Verifica si el token es válido (no expirado y no revocado)"""
        if self.revocado:
            return False
        if timezone.now() > self.expires_at:
            return False
        return True
    
    def revocar(self):
        """Revoca el token"""
        self.revocado = True
        self.revocado_at = timezone.now()
        self.save()
    
    @classmethod
    def crear_token(cls, usuario, duracion_dias=None, duracion_horas=None, user_agent=None, ip_address=None):
        """
        Crea un nuevo refresh token para un usuario.
        Retorna una tupla (token_plano, objeto_refresh_token)
        
        Args:
            duracion_dias: Duración en días (por defecto 30)
            duracion_horas: Duración en horas (si se especifica, tiene prioridad)
        """
        token_plano = cls.generate_token()
        token_hash = cls.hash_token(token_plano)
        jti = cls.generate_jti()
        
        # Calcular fecha de expiración
        if duracion_horas is not None:
            expires_at = timezone.now() + timedelta(hours=duracion_horas)
        elif duracion_dias is not None:
            expires_at = timezone.now() + timedelta(days=duracion_dias)
        else:
            expires_at = timezone.now() + timedelta(days=30)  # Por defecto 30 días
        
        refresh_token = cls.objects.create(
            usuario=usuario,
            token_hash=token_hash,
            jti=jti,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        return token_plano, refresh_token
    
    @classmethod
    def verificar_token(cls, token_plano):
        """
        Verifica un refresh token y retorna el objeto si es válido.
        Retorna None si el token no existe o no es válido.
        """
        token_hash = cls.hash_token(token_plano)
        
        try:
            refresh_token = cls.objects.get(token_hash=token_hash)
            
            if not refresh_token.is_valid():
                return None
            
            # Actualizar última vez usado
            refresh_token.last_used_at = timezone.now()
            refresh_token.save(update_fields=['last_used_at'])
            
            return refresh_token
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def limpiar_tokens_expirados(cls):
        """Elimina tokens expirados de la base de datos"""
        tokens_expirados = cls.objects.filter(expires_at__lt=timezone.now())
        count = tokens_expirados.count()
        tokens_expirados.delete()
        return count
    
    @classmethod
    def revocar_todos_usuario(cls, usuario):
        """Revoca todos los tokens de un usuario (útil para logout global)"""
        tokens = cls.objects.filter(usuario=usuario, revocado=False)
        count = tokens.update(
            revocado=True,
            revocado_at=timezone.now()
        )
        return count


class LoginAttempt(models.Model):
    """
    Modelo para rastrear intentos de login y registro fallidos.
    Usado para implementar rate limiting y prevenir ataques de fuerza bruta.
    """
    ip_address = models.GenericIPAddressField()
    username = models.CharField(max_length=150, blank=True, null=True)
    attempt_type = models.CharField(
        max_length=20,
        choices=[
            ('login', 'Login'),
            ('register', 'Register'),
        ],
        default='login'
    )
    success = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    
    class Meta:
        db_table = 'login_attempts'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['ip_address', 'timestamp']),
            models.Index(fields=['username', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.attempt_type} - {self.ip_address} - {self.timestamp}"
    
    @classmethod
    def registrar_intento(cls, ip_address, username=None, attempt_type='login', success=False, user_agent=None):
        """Registra un intento de login/registro"""
        return cls.objects.create(
            ip_address=ip_address,
            username=username,
            attempt_type=attempt_type,
            success=success,
            user_agent=user_agent
        )
    
    @classmethod
    def contar_intentos_fallidos(cls, ip_address, attempt_type='login', minutos=1):
        """
        Cuenta intentos fallidos en los últimos N minutos para una IP.
        Por defecto: últimos 1 minuto.
        """
        desde = timezone.now() - timedelta(minutes=minutos)
        return cls.objects.filter(
            ip_address=ip_address,
            attempt_type=attempt_type,
            success=False,
            timestamp__gte=desde
        ).count()
    
    @classmethod
    def esta_bloqueado(cls, ip_address, attempt_type='login', max_intentos=5, minutos=1):
        """
        Verifica si una IP está bloqueada por exceder intentos fallidos.
        Por defecto: 5 intentos en 1 minuto.
        """
        intentos = cls.contar_intentos_fallidos(ip_address, attempt_type, minutos)
        return intentos >= max_intentos
    
    @classmethod
    def tiempo_restante_bloqueo(cls, ip_address, attempt_type='login', minutos=1):
        """
        Retorna los segundos restantes de bloqueo.
        Retorna 0 si no está bloqueado.
        """
        desde = timezone.now() - timedelta(minutes=minutos)
        ultimo_intento = cls.objects.filter(
            ip_address=ip_address,
            attempt_type=attempt_type,
            success=False,
            timestamp__gte=desde
        ).order_by('-timestamp').first()
        
        if not ultimo_intento:
            return 0
        
        tiempo_transcurrido = (timezone.now() - ultimo_intento.timestamp).total_seconds()
        tiempo_bloqueo = minutos * 60
        tiempo_restante = max(0, tiempo_bloqueo - tiempo_transcurrido)
        
        return int(tiempo_restante)
    
    @classmethod
    def contar_intentos_fallidos_por_usuario(cls, username, attempt_type='login', minutos=1):
        """
        Cuenta intentos fallidos en los últimos N minutos para un usuario.
        Por defecto: últimos 1 minuto.
        """
        desde = timezone.now() - timedelta(minutes=minutos)
        return cls.objects.filter(
            username=username,
            attempt_type=attempt_type,
            success=False,
            timestamp__gte=desde
        ).count()
    
    @classmethod
    def usuario_esta_bloqueado(cls, username, attempt_type='login', max_intentos=5, minutos=1):
        """
        Verifica si un usuario está bloqueado por exceder intentos fallidos.
        Por defecto: 5 intentos en 1 minuto.
        """
        if not username:
            return False
        intentos = cls.contar_intentos_fallidos_por_usuario(username, attempt_type, minutos)
        return intentos >= max_intentos
    
    @classmethod
    def tiempo_restante_bloqueo_usuario(cls, username, attempt_type='login', minutos=1):
        """
        Retorna los segundos restantes de bloqueo para un usuario.
        Retorna 0 si no está bloqueado.
        """
        if not username:
            return 0
        desde = timezone.now() - timedelta(minutes=minutos)
        ultimo_intento = cls.objects.filter(
            username=username,
            attempt_type=attempt_type,
            success=False,
            timestamp__gte=desde
        ).order_by('-timestamp').first()
        
        if not ultimo_intento:
            return 0
        
        tiempo_transcurrido = (timezone.now() - ultimo_intento.timestamp).total_seconds()
        tiempo_bloqueo = minutos * 60
        tiempo_restante = max(0, tiempo_bloqueo - tiempo_transcurrido)
        
        return int(tiempo_restante)
    
    @classmethod
    def limpiar_intentos_antiguos(cls, dias=7):
        """Elimina intentos de login/registro antiguos"""
        fecha_limite = timezone.now() - timedelta(days=dias)
        count, _ = cls.objects.filter(timestamp__lt=fecha_limite).delete()
        return count


class TokenBlacklist(models.Model):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    🛡️ MODELO - TokenBlacklist
    ═══════════════════════════════════════════════════════════════════════════════
    
    Almacena tokens invalidados (blacklist) para logout y revocación.
    Previene reutilización de tokens después de logout.
    
    CARACTERÍSTICAS:
    - Token único con índice para búsqueda rápida
    - Relación con usuario para auditoría
    - Razón de invalidación (logout, revocado, expirado)
    - Timestamp para limpieza automática
    """
    
    RAZONES = [
        ('logout', 'Logout'),
        ('revoked', 'Revocado'),
        ('expired', 'Expirado'),
        ('security', 'Razón de Seguridad'),
    ]
    
    token = models.TextField(unique=True, db_index=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blacklisted_tokens')
    blacklisted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    razon = models.CharField(
        max_length=50,
        choices=RAZONES,
        default='logout'
    )
    
    class Meta:
        db_table = 'token_blacklist'
        ordering = ['-blacklisted_at']
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['usuario', 'blacklisted_at']),
            models.Index(fields=['blacklisted_at']),
        ]
        verbose_name = 'Token Blacklist'
        verbose_name_plural = 'Tokens Blacklist'
    
    def __str__(self):
        return f"Blacklist: {self.usuario.username} - {self.razon} - {self.blacklisted_at}"
    
    @classmethod
    def esta_en_blacklist(cls, token: str) -> bool:
        """
        Verifica si un token está en la blacklist.
        
        Args:
            token: Token JWT a verificar
        
        Returns:
            bool: True si está en blacklist, False si no
        """
        return cls.objects.filter(token=token).exists()
    
    @classmethod
    def agregar_a_blacklist(cls, token: str, usuario, razon: str = 'logout'):
        """
        Agrega un token a la blacklist.
        
        Args:
            token: Token JWT a invalidar
            usuario: Usuario propietario del token
            razon: Razón de invalidación
        
        Returns:
            TokenBlacklist: Objeto creado
        """
        return cls.objects.create(
            token=token,
            usuario=usuario,
            razon=razon
        )
    
    @classmethod
    def limpiar_expirados(cls, dias: int = 31):
        """
        Elimina tokens de la blacklist más antiguos que X días.
        Ejecutar diariamente para mantener la tabla limpia.
        
        Args:
            dias: Número de días a retener (default: 31)
        
        Returns:
            tuple: (count, dict) de objetos eliminados
        """
        fecha_limite = timezone.now() - timedelta(days=dias)
        return cls.objects.filter(blacklisted_at__lt=fecha_limite).delete()
    
    @classmethod
    def contar_tokens_usuario(cls, usuario) -> int:
        """
        Cuenta tokens invalidados de un usuario.
        Útil para auditoría.
        
        Args:
            usuario: Usuario a contar
        
        Returns:
            int: Número de tokens invalidados
        """
        return cls.objects.filter(usuario=usuario).count()


# ═══════════════════════════════════════════════════════════════════════════════
# 🛒 CARRITO DE COMPRAS - MODELOS
# ═══════════════════════════════════════════════════════════════════════════════

class Cart(models.Model):
    """
    Carrito de compras por usuario
    
    Cada usuario tiene un carrito único.
    El carrito contiene múltiples items.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='cart',
        help_text='Usuario propietario del carrito'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creación del carrito'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Última actualización del carrito'
    )
    
    class Meta:
        db_table = 'carts'
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f'Carrito de {self.user.email}'
    
    def get_total(self):
        """Calcula el total del carrito"""
        return sum(
            item.price_at_addition * item.quantity 
            for item in self.items.all()
        )
    
    def get_total_items(self):
        """Obtiene la cantidad total de items"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """
    Items dentro del carrito
    
    Cada item representa un producto en el carrito.
    Guarda el precio al momento de agregar (para historial).
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        help_text='Carrito al que pertenece este item'
    )
    product = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        help_text='Producto en el carrito'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        help_text='Cantidad del producto'
    )
    price_at_addition = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='Precio del producto al momento de agregar'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de agregación al carrito'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Última actualización del item'
    )
    
    class Meta:
        db_table = 'cart_items'
        verbose_name = 'Item del Carrito'
        verbose_name_plural = 'Items del Carrito'
        unique_together = ('cart', 'product')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cart']),
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f'{self.product.nombre} x {self.quantity}'
    
    def get_subtotal(self):
        """Calcula el subtotal del item"""
        return self.price_at_addition * self.quantity


class CartAuditLog(models.Model):
    """
    Registro de auditoría para cambios en el carrito
    
    Registra todas las operaciones: agregar, actualizar, eliminar
    """
    ACTION_CHOICES = [
        ('add', 'Agregar producto'),
        ('update', 'Actualizar cantidad'),
        ('remove', 'Eliminar producto'),
        ('clear', 'Vaciar carrito'),
        ('bulk_update', 'Actualización masiva'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cart_audit_logs',
        help_text='Usuario que realizó la acción'
    )
    action = models.CharField(
        max_length=20,  # Aumentado de 10 a 20 para soportar 'bulk_update'
        choices=ACTION_CHOICES,
        help_text='Tipo de acción realizada'
    )
    product_id = models.IntegerField(
        null=True,
        blank=True,
        help_text='ID del producto (si aplica)'
    )
    product_name = models.CharField(
        max_length=255,
        blank=True,
        help_text='Nombre del producto (snapshot)'
    )
    quantity_before = models.IntegerField(
        null=True,
        blank=True,
        help_text='Cantidad antes de la acción'
    )
    quantity_after = models.IntegerField(
        null=True,
        blank=True,
        help_text='Cantidad después de la acción'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Precio del producto en el momento'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP del cliente'
    )
    user_agent = models.TextField(
        blank=True,
        help_text='User-Agent del navegador'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha y hora de la acción'
    )
    
    class Meta:
        db_table = 'cart_audit_logs'
        verbose_name = 'Registro de Auditoría del Carrito'
        verbose_name_plural = 'Registros de Auditoría del Carrito'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f'{self.user.email} - {self.get_action_display()} - {self.timestamp}'


class StockReservation(models.Model):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    🛡️ MODELO - StockReservation (Reserva de Stock Temporal)
    ═══════════════════════════════════════════════════════════════════════════════
    
    Gestiona reservas temporales de stock durante el proceso de Checkout.
    
    FLUJO:
    1. Usuario agrega al carrito (SIN reservar)
    2. Usuario va a Checkout → Se RESERVA el stock
    3. Pago exitoso → Stock se mueve a VENDIDO (COMMIT)
    4. Pago falla O TTL expira → Stock se libera (ROLLBACK)
    
    ESTADOS:
    - pending: Reserva activa, esperando confirmación de pago
    - confirmed: Pago confirmado, stock movido a vendido
    - cancelled: Reserva cancelada, stock liberado
    - expired: TTL expiró, stock liberado automáticamente
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('cancelled', 'Cancelado'),
        ('expired', 'Expirado'),
    ]
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stock_reservations',
        help_text='Usuario que realizó la reserva'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='reservations',
        help_text='Producto reservado'
    )
    cantidad = models.PositiveIntegerField(
        help_text='Cantidad reservada'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
        help_text='Estado de la reserva'
    )
    
    # Timestamps críticos
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de creación de la reserva'
    )
    expires_at = models.DateTimeField(
        help_text='Fecha de expiración (TTL: 15 minutos por defecto)'
    )
    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha de confirmación del pago'
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Fecha de cancelación'
    )
    
    # Auditoría
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text='IP del cliente'
    )
    user_agent = models.TextField(
        blank=True,
        null=True,  # Permitir null
        help_text='User-Agent del navegador'
    )
    
    class Meta:
        db_table = 'stock_reservations'
        verbose_name = 'Reserva de Stock'
        verbose_name_plural = 'Reservas de Stock'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['usuario', 'status']),
            models.Index(fields=['producto', 'status']),
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f'{self.usuario.username} - {self.producto.nombre} x{self.cantidad} ({self.status})'
    
    @property
    def is_expired(self):
        """Verifica si la reserva ha expirado"""
        return timezone.now() > self.expires_at and self.status == 'pending'
    
    @classmethod
    def crear_reserva(cls, usuario, producto, cantidad, ip_address=None, user_agent=None, ttl_minutos=15):
        """
        Crea una nueva reserva de stock.
        
        Args:
            usuario: Usuario que realiza la reserva
            producto: Producto a reservar
            cantidad: Cantidad a reservar
            ip_address: IP del cliente
            user_agent: User-Agent del navegador
            ttl_minutos: Tiempo de vida de la reserva en minutos (default: 15)
        
        Returns:
            StockReservation: Objeto creado
        """
        expires_at = timezone.now() + timedelta(minutes=ttl_minutos)
        
        return cls.objects.create(
            usuario=usuario,
            producto=producto,
            cantidad=cantidad,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            status='pending'
        )
    
    @classmethod
    def liberar_reservas_expiradas(cls):
        """
        Libera todas las reservas expiradas (ROLLBACK automático).
        Debe ejecutarse periódicamente (cada 5 minutos).
        
        Returns:
            int: Número de reservas liberadas
        """
        ahora = timezone.now()
        reservas_expiradas = cls.objects.filter(
            status='pending',
            expires_at__lt=ahora
        )
        
        count = 0
        for reserva in reservas_expiradas:
            # Liberar stock
            producto = reserva.producto
            producto.stock_reservado -= reserva.cantidad
            producto.save()
            
            # Marcar como expirada
            reserva.status = 'expired'
            reserva.cancelled_at = ahora
            reserva.save()
            count += 1
        
        return count


class Favorito(models.Model):
    """
    Modelo para guardar productos favoritos de los usuarios
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favoritos',
        help_text='Usuario que marcó como favorito'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='favoritos',
        help_text='Producto marcado como favorito'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de agregación a favoritos'
    )
    
    class Meta:
        db_table = 'favoritos'
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'
        unique_together = ('usuario', 'producto')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['usuario', '-created_at']),
            models.Index(fields=['producto']),
        ]
    
    def __str__(self):
        return f'{self.usuario.username} - {self.producto.nombre}'


class EmailVerification(models.Model):
    """
    Modelo para verificación de email con código de 6 dígitos.
    Incluye protección contra fuerza bruta y límite de reenvíos.
    """
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_verifications'
    )
    
    # Código de verificación de 6 dígitos
    codigo = models.CharField(max_length=6, db_index=True)
    
    # Control de tiempo
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    # Estado de verificación
    verificado = models.BooleanField(default=False)
    verificado_at = models.DateTimeField(null=True, blank=True)
    
    # Protección contra fuerza bruta
    intentos_fallidos = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Control de reenvíos
    ultimo_reenvio = models.DateTimeField(null=True, blank=True)
    contador_reenvios = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'email_verifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['usuario', '-created_at']),
            models.Index(fields=['codigo', 'expires_at']),
        ]
    
    def __str__(self):
        status = 'Verificado' if self.verificado else 'Pendiente'
        return f'EmailVerification para {self.usuario.username} - {status}'
    
    @staticmethod
    def generar_codigo():
        """Genera un código de 6 dígitos aleatorio"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    
    def is_valid(self):
        """Verifica si el código es válido (no expirado y no verificado)"""
        if self.verificado:
            return False
        if timezone.now() > self.expires_at:
            return False
        return True
    
    def marcar_verificado(self):
        """Marca el código como verificado"""
        self.verificado = True
        self.verificado_at = timezone.now()
        self.save()
    
    def incrementar_intentos(self):
        """Incrementa el contador de intentos fallidos"""
        self.intentos_fallidos += 1
        self.save(update_fields=['intentos_fallidos'])
    
    def puede_reenviar(self, minutos_espera=2):
        """
        Verifica si se puede reenviar un nuevo código.
        Por defecto requiere esperar 2 minutos entre reenvíos.
        """
        if self.ultimo_reenvio is None:
            return True
        
        tiempo_transcurrido = timezone.now() - self.ultimo_reenvio
        return tiempo_transcurrido.total_seconds() >= (minutos_espera * 60)
    
    def marcar_reenvio(self):
        """Marca que se ha reenviado un código"""
        self.ultimo_reenvio = timezone.now()
        self.contador_reenvios += 1
        self.save(update_fields=['ultimo_reenvio', 'contador_reenvios'])
    
    @classmethod
    def crear_codigo(cls, usuario, duracion_minutos=15, ip_address=None):
        """
        Crea un nuevo código de verificación para un usuario.
        Retorna el objeto EmailVerification creado.
        
        Args:
            usuario: Usuario para el cual crear el código
            duracion_minutos: Duración del código en minutos (por defecto 15)
            ip_address: Dirección IP del usuario
        """
        codigo = cls.generar_codigo()
        expires_at = timezone.now() + timedelta(minutes=duracion_minutos)
        
        verificacion = cls.objects.create(
            usuario=usuario,
            codigo=codigo,
            expires_at=expires_at,
            ip_address=ip_address
        )
        
        return verificacion
    
    @classmethod
    def verificar_codigo(cls, usuario, codigo):
        """
        Verifica un código de verificación.
        Retorna el objeto EmailVerification si es válido, None si no.
        """
        try:
            verificacion = cls.objects.filter(
                usuario=usuario,
                codigo=codigo,
                verificado=False
            ).order_by('-created_at').first()
            
            if verificacion is None:
                return None
            
            if not verificacion.is_valid():
                return None
            
            return verificacion
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def limpiar_codigos_expirados(cls):
        """Elimina códigos expirados de la base de datos"""
        codigos_expirados = cls.objects.filter(
            expires_at__lt=timezone.now(),
            verificado=False
        )
        count = codigos_expirados.count()
        codigos_expirados.delete()
        return count
    
    @classmethod
    def invalidar_codigos_usuario(cls, usuario):
        """Invalida todos los códigos pendientes de un usuario"""
        codigos = cls.objects.filter(usuario=usuario, verificado=False)
        count = codigos.update(
            verificado=True,
            verificado_at=timezone.now()
        )
        return count
