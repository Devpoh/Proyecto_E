from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
import logging
from .models import Producto, Cart, CartItem, Favorito

logger = logging.getLogger('security')


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y validar usuarios con sanitización de entrada.
    """
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']
        read_only_fields = ['id']
    
    def validate_username(self, value):
        """
        Validar username:
        - Solo alfanuméricos, guiones y guiones bajos
        - Entre 3 y 150 caracteres
        - No puede existir otro usuario con el mismo username (case-insensitive)
        """
        # Sanitizar: trim y lowercase
        value = value.strip().lower()
        
        # Validar formato
        if not re.match(r'^[a-z0-9_-]{3,150}$', value):
            raise ValidationError(
                'Username debe contener solo letras minúsculas, números, guiones y guiones bajos (3-150 caracteres)'
            )
        
        # Validar que no exista otro usuario
        if User.objects.filter(username__iexact=value).exists():
            raise ValidationError('Este usuario ya existe')
        
        logger.info(f'[VALIDATION] Username validado: {value}')
        return value
    
    def validate_email(self, value):
        """
        Validar email:
        - Debe ser un email válido
        - No puede existir otro usuario con el mismo email
        """
        # Sanitizar: trim y lowercase
        value = value.strip().lower()
        
        # Validar que no exista otro usuario
        if User.objects.filter(email__iexact=value).exists():
            raise ValidationError('Este email ya está registrado')
        
        logger.info(f'[VALIDATION] Email validado: {value}')
        return value
    
    def validate_password(self, value):
        """
        Validar contraseña:
        - Mínimo 8 caracteres
        - Máximo 128 caracteres
        - No puede ser solo números
        - No puede ser solo letras
        """
        # Validar longitud
        if len(value) < 8:
            raise ValidationError('La contraseña debe tener al menos 8 caracteres')
        
        if len(value) > 128:
            raise ValidationError('La contraseña no puede exceder 128 caracteres')
        
        # Validar que no sea solo números
        if value.isdigit():
            raise ValidationError('La contraseña no puede ser solo números')
        
        # Validar que no sea solo letras
        if value.isalpha():
            raise ValidationError('La contraseña debe contener números y letras')
        
        logger.info('[VALIDATION] Contraseña validada')
        return value
    
    def validate_first_name(self, value):
        """Sanitizar first_name"""
        if value:
            value = value.strip()
            # Permitir solo letras, espacios y algunos caracteres especiales
            if not re.match(r'^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s\-\']{1,150}$', value):
                raise ValidationError('Nombre contiene caracteres inválidos')
        return value
    
    def validate_last_name(self, value):
        """Sanitizar last_name"""
        if value:
            value = value.strip()
            # Permitir solo letras, espacios y algunos caracteres especiales
            if not re.match(r'^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s\-\']{1,150}$', value):
                raise ValidationError('Apellido contiene caracteres inválidos')
        return value
    
    def create(self, validated_data):
        """Crear usuario con contraseña hasheada"""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', '').strip(),
            last_name=validated_data.get('last_name', '').strip()
        )
        
        logger.info(f'[USER_CREATED] Usuario creado: {user.username} | Email: {user.email}')
        return user


class ProductoSerializer(serializers.ModelSerializer):
    creado_por_username = serializers.CharField(source='creado_por.username', read_only=True)
    favoritos_count = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    imagen_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'descripcion', 'precio', 'descuento', 'categoria', 
            'imagen_url', 'stock', 'stock_total', 'stock_reservado', 'stock_vendido',
            'activo', 'en_carrusel', 'creado_por', 
            'creado_por_username', 'favoritos_count', 'created_at', 'updated_at',
            'en_carousel_card', 'en_all_products'
        ]
        read_only_fields = [
            'id', 'creado_por', 'created_at', 'updated_at', 'favoritos_count',
            'stock', 'stock_reservado', 'stock_vendido', 'en_carousel_card', 'en_all_products'
        ]
    
    def get_imagen_url(self, obj):
        """
        RETORNA LA IMAGEN CORRECTA (archivo o Base64)
        
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
    
    def get_favoritos_count(self, obj):
        """Obtiene la cantidad de favoritos del producto"""
        # Usar valor anotado si existe (optimización)
        if hasattr(obj, 'favoritos_count_cached'):
            return obj.favoritos_count_cached
        return obj.favoritos.count()
    
    def get_stock(self, obj):
        """Retorna stock_disponible como 'stock' para compatibilidad con frontend"""
        return max(0, obj.stock_total - obj.stock_reservado - obj.stock_vendido)
    
    def create(self, validated_data):
        """Al crear, si viene 'stock_total', usarlo; si no, asumimos que es stock"""
        # Si no viene stock_total pero viene stock en los datos originales, usarlo
        if 'stock_total' not in validated_data and hasattr(self, 'initial_data'):
            stock_value = self.initial_data.get('stock')
            if stock_value:
                validated_data['stock_total'] = int(stock_value)
        
        # Asegurar que stock_total tenga un valor
        if 'stock_total' not in validated_data:
            validated_data['stock_total'] = 0
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Al actualizar, si viene 'stock_total', usarlo; si no, asumimos que es stock"""
        if 'stock_total' not in validated_data and hasattr(self, 'initial_data'):
            stock_value = self.initial_data.get('stock')
            if stock_value:
                validated_data['stock_total'] = int(stock_value)
        
        return super().update(instance, validated_data)
    
    def validate_categoria(self, value):
        """Validar que la categoría sea válida"""
        # Mapeo de labels y variantes a valores correctos
        categoria_map = {
            # Labels
            'Electrodomésticos': 'electrodomesticos',
            'Energía y Tecnología': 'energia_tecnologia',
            'Herramientas': 'herramientas',
            'Hogar y Entretenimiento': 'hogar_entretenimiento',
            'Otros Artículos': 'otros',
            # Variantes con guiones (frontend)
            'energia-tecnologia': 'energia_tecnologia',
            'hogar-entretenimiento': 'hogar_entretenimiento',
            'otros-articulos': 'otros',
        }
        
        # Si viene un label o variante, convertir a valor
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


# ═══════════════════════════════════════════════════════════════════════════════
# 🛒 CARRITO DE COMPRAS - SERIALIZERS
# ═══════════════════════════════════════════════════════════════════════════════

class ProductoSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para productos en el carrito"""
    
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'categoria']


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer para items del carrito"""
    product = ProductoSimpleSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id',
            'product',
            'product_id',
            'quantity',
            'price_at_addition',
            'subtotal',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'price_at_addition']
    
    def get_subtotal(self, obj):
        """Calcula el subtotal del item"""
        return float(obj.get_subtotal())
    
    def validate_quantity(self, value):
        """Valida que la cantidad sea positiva"""
        if value < 1:
            raise serializers.ValidationError('La cantidad debe ser mayor a 0')
        return value


class CartSerializer(serializers.ModelSerializer):
    """Serializer para el carrito completo"""
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id',
            'items',
            'total',
            'total_items',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total(self, obj):
        """Calcula el total del carrito"""
        return float(obj.get_total())
    
    def get_total_items(self, obj):
        """Obtiene la cantidad total de items"""
        return obj.get_total_items()
