"""
═══════════════════════════════════════════════════════════════════════════════
🔐 SERIALIZERS - Admin Panel
═══════════════════════════════════════════════════════════════════════════════

Serializers para el panel de administración con respeto a la privacidad
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Producto, Pedido, DetallePedido, Notificacion, AuditLog


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil de usuario"""
    
    class Meta:
        model = UserProfile
        fields = ['rol', 'telefono', 'direccion', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer para listar usuarios (RESPETANDO PRIVACIDAD)
    
    NO EXPONE:
    - Contraseñas (nunca)
    - Datos sensibles completos
    - Información personal detallada
    """
    
    rol = serializers.CharField(source='profile.rol', read_only=True)
    fecha_registro = serializers.DateTimeField(source='date_joined', read_only=True)
    ultimo_acceso = serializers.DateTimeField(source='last_login', read_only=True)
    
    # Email parcialmente oculto para privacidad
    email_parcial = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email_parcial',  # Email oculto parcialmente
            'first_name',
            'last_name',
            'is_active',
            'rol',
            'fecha_registro',
            'ultimo_acceso',
        ]
    
    def get_email_parcial(self, obj):
        """
        Ocultar parcialmente el email para privacidad
        Ejemplo: j***@ejemplo.com
        """
        if not obj.email:
            return None
        
        parts = obj.email.split('@')
        if len(parts) != 2:
            return obj.email
        
        username = parts[0]
        domain = parts[1]
        
        # Mostrar solo primera letra del username
        hidden_username = username[0] + '*' * (len(username) - 1) if len(username) > 1 else username
        
        return f"{hidden_username}@{domain}"


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer para detalle de usuario (más información, pero controlada)
    """
    
    profile = UserProfileSerializer(read_only=True)
    fecha_registro = serializers.DateTimeField(source='date_joined', read_only=True)
    ultimo_acceso = serializers.DateTimeField(source='last_login', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',  # Email completo solo en detalle
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'profile',
            'fecha_registro',
            'ultimo_acceso',
        ]
        read_only_fields = ['id', 'fecha_registro', 'ultimo_acceso']


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar usuario (solo campos permitidos)
    
    NO PERMITE:
    - Cambiar contraseña (endpoint separado)
    - Cambiar username (inmutable)
    - Modificar fechas del sistema
    """
    
    rol = serializers.ChoiceField(
        choices=UserProfile.ROLES,
        write_only=True,
        required=False
    )
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active', 'rol']
    
    def update(self, instance, validated_data):
        """Actualizar usuario y su perfil"""
        
        # Extraer rol si viene
        rol = validated_data.pop('rol', None)
        
        # Actualizar usuario
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar rol en perfil
        if rol and hasattr(instance, 'profile'):
            instance.profile.rol = rol
            instance.profile.save()
        
        return instance


class ProductoAdminSerializer(serializers.ModelSerializer):
    """Serializer completo de producto para admin con validaciones"""
    
    creado_por_username = serializers.CharField(source='creado_por.username', read_only=True)
    stock = serializers.IntegerField(required=False, allow_null=True)
    imagen = serializers.ImageField(use_url=True, required=False, allow_null=True)
    # ✅ Especificar DecimalField explícitamente para evitar problemas de parsing
    precio = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    # ✅ Método para retornar la imagen correcta (archivo o Base64)
    imagen_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'creado_por', 'stock']
    
    def get_imagen_url(self, obj):
        """
        ✅ RETORNA LA IMAGEN CORRECTA (archivo o Base64)
        
        Prioridad:
        1. imagen (ImageField) - URL de archivo real
        2. imagen_url (TextField) - Base64 legado
        3. None - sin imagen
        """
        # Prioridad 1: Usar imagen (ImageField) si existe
        if obj.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        
        # Prioridad 2: Usar imagen_url (Base64 legado) si existe
        if obj.imagen_url:
            return obj.imagen_url
        
        return None
    
    def validate_precio(self, value):
        """Validar que el precio sea positivo"""
        if value is None:
            raise serializers.ValidationError("El precio es requerido")
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0")
        if value > 999999.99:
            raise serializers.ValidationError("El precio no puede exceder 999999.99")
        return value
    
    def validate_stock(self, value):
        """Validar que el stock sea no negativo"""
        if value is None:
            raise serializers.ValidationError("El stock es requerido")
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo")
        if value > 999999:
            raise serializers.ValidationError("El stock no puede exceder 999999")
        return value
    
    def validate_nombre(self, value):
        """Validar nombre del producto"""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("El nombre es requerido")
        if len(value) > 255:
            raise serializers.ValidationError("El nombre no puede exceder 255 caracteres")
        return value.strip()
    
    def validate_descripcion(self, value):
        """Validar descripción"""
        if value and len(value) > 5000:
            raise serializers.ValidationError("La descripción no puede exceder 5000 caracteres")
        return value
    
    def validate_imagen_url(self, value):
        """Validar que la imagen Base64 no sea demasiado grande"""
        if value and len(value) > 5242880:  # 5MB máximo en base64
            raise serializers.ValidationError("La imagen es demasiado grande. Máximo 5MB")
        return value
    
    def validate_imagen(self, value):
        """Validar que el archivo de imagen no sea demasiado grande"""
        if value and value.size > 5242880:  # 5MB máximo
            raise serializers.ValidationError("La imagen es demasiado grande. Máximo 5MB")
        return value
    
    def validate_categoria(self, value):
        """Validar y normalizar categoría"""
        from .models import Producto
        
        # Limpiar espacios
        if isinstance(value, str):
            value = value.strip()
        
        # Mapeo de labels a valores correctos
        categoria_map = {
            'Electrodomésticos': 'electrodomesticos',
            'Energía y Tecnología': 'energia_tecnologia',
            'Herramientas': 'herramientas',
            'Hogar y Entretenimiento': 'hogar_entretenimiento',
            'Otros Artículos': 'otros',
        }
        
        # Si viene un label, convertir a valor
        if value in categoria_map:
            return categoria_map[value]
        
        # Si ya es un valor válido, retornar
        valid_choices = [choice[0] for choice in Producto.CATEGORIAS]
        if value in valid_choices:
            return value
        
        # Si no es válido, lanzar error
        raise serializers.ValidationError(
            f"Categoría inválida: '{value}'. Opciones válidas: {', '.join(valid_choices)}"
        )
    
    def validate(self, data):
        """Validaciones adicionales"""
        # Validar que no sea descuento negativo
        if 'descuento' in data and data['descuento'] is not None:
            if data['descuento'] < 0 or data['descuento'] > 100:
                raise serializers.ValidationError("El descuento debe estar entre 0 y 100")
        
        # Manejar stock → stock_total
        if 'stock' in data and 'stock_total' not in data:
            data['stock_total'] = data['stock']
        
        return data


class DetallePedidoSerializer(serializers.ModelSerializer):
    """Serializer para detalle de pedido"""
    
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    
    class Meta:
        model = DetallePedido
        fields = ['id', 'producto', 'producto_nombre', 'cantidad', 'precio_unitario', 'subtotal']
        read_only_fields = ['subtotal']


class PedidoSerializer(serializers.ModelSerializer):
    """Serializer para pedidos"""
    
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    mensajero_nombre = serializers.CharField(source='mensajero.get_full_name', read_only=True, allow_null=True)
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Pedido
        fields = [
            'id', 'usuario', 'usuario_nombre', 'usuario_email',
            'estado', 'metodo_pago', 'total', 'direccion_entrega',
            'telefono', 'notas', 'mensajero', 'mensajero_nombre',
            'detalles', 'created_at', 'updated_at', 'fecha_entrega'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones"""
    
    class Meta:
        model = Notificacion
        fields = ['id', 'tipo', 'titulo', 'mensaje', 'leida', 'url', 'created_at']
        read_only_fields = ['id', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer para el historial de auditoría.
    Solo accesible para administradores.
    """
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)
    usuario_nombre_completo = serializers.SerializerMethodField()
    accion_display = serializers.CharField(source='get_accion_display', read_only=True)
    modulo_display = serializers.CharField(source='get_modulo_display', read_only=True)
    detalles = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'usuario',
            'usuario_nombre',
            'usuario_nombre_completo',
            'accion',
            'accion_display',
            'modulo',
            'modulo_display',
            'objeto_id',
            'objeto_repr',
            'detalles',
            'ip_address',
            'user_agent',
            'timestamp',
        ]
        read_only_fields = fields
    
    def get_usuario_nombre_completo(self, obj):
        """Obtener nombre completo del usuario"""
        if obj.usuario:
            nombre_completo = obj.usuario.get_full_name()
            return nombre_completo if nombre_completo else obj.usuario.username
        return 'Sistema'
    
    def get_detalles(self, obj):
        """
        Sanitizar detalles para ocultar imágenes.
        Excluir completamente imagen_url y cualquier dato de imagen.
        """
        if not obj.detalles:
            return {}
        
        detalles_sanitizados = {}
        
        # Filtrar detalles: excluir imagen_url y valores con data:image
        for key, value in obj.detalles.items():
            # Excluir completamente imagen_url
            if key == 'imagen_url':
                continue
            
            # Excluir valores que contengan data:image
            if isinstance(value, str) and value.startswith('data:image'):
                continue
            
            # Incluir el resto de valores
            detalles_sanitizados[key] = value
        
        return detalles_sanitizados
