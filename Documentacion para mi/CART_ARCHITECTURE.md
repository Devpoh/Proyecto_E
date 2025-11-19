# 🛒 ARQUITECTURA PROFESIONAL DE CARRITO POR USUARIO

**Fecha:** 7 de Noviembre, 2025  
**Status:** ✅ **FRONTEND COMPLETADO**

---

## 📋 REQUISITOS IMPLEMENTADOS

### ✅ Frontend - Completado

#### 1. Autenticación Obligatoria
- ✅ `useAddToCart` hook verifica `isAuthenticated`
- ✅ Si NO está logueado → Toast error + Redirige a `/login`
- ✅ Si está logueado → Agrega al carrito
- ✅ Aplicado en: ProductCarousel, CarouselCard, todos los botones "Agregar"

#### 2. Descuentos en CarouselCard
- ✅ Badge rojo con descuento (ej: -15%)
- ✅ Precio actual en grande
- ✅ Precio original tachado abajo
- ✅ Estilos profesionales con gradiente

#### 3. Carrito por Usuario
- ✅ Zustand store con persistencia en localStorage
- ✅ AuthStore con user ID
- ✅ Preparado para sincronizar con backend

---

## 🔐 FLUJO DE AUTENTICACIÓN

### Agregar Producto al Carrito

```
Usuario hace click en "Agregar"
    ↓
useAddToCart() verifica isAuthenticated
    ↓
¿Está logueado?
    ├─ NO → Toast error + Redirige a /login
    └─ SÍ → Agrega al carrito + Toast éxito
```

### Código en useAddToCart.ts

```tsx
const handleAddToCart = (productId: string | number) => {
  // 🔐 VERIFICAR AUTENTICACIÓN
  if (!isAuthenticated) {
    toast.error('Debes iniciar sesión para agregar productos al carrito', {
      icon: '🔒',
      duration: 3000,
    });
    
    // Redirigir a login
    navigate('/login', { replace: true });
    return;
  }

  // Si está logueado, agregar al carrito
  addItem(numericId);
  toast.success('¡Producto agregado al carrito!', { icon: '🛒' });
};
```

---

## 🎨 DESCUENTOS EN CAROUSELCARD

### Visualización

```
┌─────────────────────────────┐
│  Imagen del Producto        │
│  ┌──────────────────────┐   │
│  │  -15%  (Badge Rojo)  │   │
│  └──────────────────────┘   │
├─────────────────────────────┤
│ Categoría                   │
│ Nombre del Producto         │
│ $85.00                      │
│ $100.00 (tachado)           │
├─────────────────────────────┤
│ [Ver detalles] [Agregar]    │
└─────────────────────────────┘
```

### Estilos CSS

```css
.tarjeta-descuento-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-weight: bold;
  font-size: 14px;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
  z-index: 10;
  min-width: 50px;
  text-align: center;
}
```

---

## 🛒 CARRITO POR USUARIO - ARQUITECTURA BACKEND

### ⚠️ IMPORTANTE: IMPLEMENTACIÓN EN BACKEND

El frontend está listo. Ahora necesitas implementar en el backend:

### 1. Modelos de Base de Datos

```python
# Django Models

class Cart(models.Model):
    """Carrito de compras por usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'

class CartItem(models.Model):
    """Items dentro del carrito"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Producto, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_addition = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        unique_together = ('cart', 'product')
```

### 2. API Endpoints

```
POST   /api/carrito/agregar/
       {
         "product_id": 1,
         "quantity": 1
       }
       → Agrega producto al carrito del usuario autenticado

GET    /api/carrito/
       → Obtiene el carrito del usuario autenticado

PUT    /api/carrito/items/{item_id}/
       {
         "quantity": 2
       }
       → Actualiza cantidad de un item

DELETE /api/carrito/items/{item_id}/
       → Elimina un item del carrito

DELETE /api/carrito/
       → Vacía el carrito
```

### 3. Serializers

```python
# serializers.py

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.nombre', read_only=True)
    product_image = serializers.CharField(source='product.imagen_url', read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_image', 'quantity', 'price_at_addition']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total', 'created_at', 'updated_at']
    
    def get_total(self, obj):
        return sum(item.price_at_addition * item.quantity for item in obj.items.all())
```

### 4. Views

```python
# views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    """Obtener carrito del usuario autenticado"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """Agregar producto al carrito"""
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)
    
    try:
        product = Producto.objects.get(id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Crear o actualizar item
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity,
                'price_at_addition': product.precio
            }
        )
        
        if not created:
            item.quantity += quantity
            item.save()
        
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
```

### 5. URLs

```python
# urls.py

urlpatterns = [
    path('carrito/', get_cart, name='get_cart'),
    path('carrito/agregar/', add_to_cart, name='add_to_cart'),
    # ... más endpoints
]
```

---

## 🔄 FLUJO COMPLETO: USUARIO NO LOGUEADO → LOGUEADO

### Paso 1: Usuario No Logueado
```
Usuario navega por la web
    ↓
Intenta agregar producto al carrito
    ↓
useAddToCart verifica: isAuthenticated = false
    ↓
Toast error: "Debes iniciar sesión"
    ↓
Redirige a /login
```

### Paso 2: Usuario Inicia Sesión
```
Usuario completa login
    ↓
AuthStore actualiza: isAuthenticated = true, user = {...}
    ↓
Token guardado en sessionStorage/localStorage
    ↓
Usuario redirigido a página anterior o home
```

### Paso 3: Usuario Agrega Producto
```
Usuario intenta agregar producto
    ↓
useAddToCart verifica: isAuthenticated = true
    ↓
Llama a addItem(productId)
    ↓
Zustand store actualiza items localmente
    ↓
Toast éxito: "¡Producto agregado!"
    ↓
Frontend listo para sincronizar con backend
```

### Paso 4: Sincronización con Backend (Próximo)
```
Cuando usuario va a checkout:
    ↓
Frontend envía items del carrito al backend
    ↓
Backend valida stock y precios
    ↓
Backend crea/actualiza Cart en BD
    ↓
Procesa el pago
    ↓
Crea Order
```

---

## 📊 ESTADO DEL CARRITO

### Zustand Store (Frontend)

```tsx
interface CartItem {
  productoId: number;
  cantidad: number;
}

interface CartState {
  items: CartItem[];
  addItem: (productoId: number) => void;
  removeItem: (productoId: number) => void;
  updateQuantity: (productoId: number, cantidad: number) => void;
  clearCart: () => void;
  getTotalItems: () => number;
}
```

### Backend (Próximo)

```python
class Cart(models.Model):
    user = models.OneToOneField(User, ...)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, ...)
    product = models.ForeignKey(Producto, ...)
    quantity = models.PositiveIntegerField()
    price_at_addition = models.DecimalField()
```

---

## 🎯 PRÓXIMOS PASOS

### 1. Backend - Modelos
- [ ] Crear modelo `Cart`
- [ ] Crear modelo `CartItem`
- [ ] Crear migraciones

### 2. Backend - API
- [ ] Endpoint GET `/api/carrito/`
- [ ] Endpoint POST `/api/carrito/agregar/`
- [ ] Endpoint PUT `/api/carrito/items/{id}/`
- [ ] Endpoint DELETE `/api/carrito/items/{id}/`
- [ ] Endpoint DELETE `/api/carrito/`

### 3. Backend - Validaciones
- [ ] Validar stock disponible
- [ ] Validar precios actuales
- [ ] Validar autenticación
- [ ] Validar cantidades

### 4. Frontend - Integración
- [ ] Conectar useAddToCart con API
- [ ] Sincronizar carrito local con backend
- [ ] Mostrar carrito del backend en VistaCarrito
- [ ] Implementar checkout

### 5. Caché (Redis)
- [ ] Implementar cache de carritos
- [ ] Invalidar cache al actualizar
- [ ] TTL de 30 días para carritos

---

## 🔐 SEGURIDAD

### Validaciones Obligatorias

1. **Autenticación**
   - ✅ Frontend: Verifica `isAuthenticated`
   - ⏳ Backend: Verifica token JWT en cada request

2. **Autorización**
   - ⏳ Backend: Solo usuario puede acceder a su carrito
   - ⏳ Backend: Validar `request.user == cart.user`

3. **Validación de Datos**
   - ⏳ Backend: Validar product_id existe
   - ⏳ Backend: Validar quantity > 0
   - ⏳ Backend: Validar stock disponible

4. **Precios**
   - ⏳ Backend: Guardar precio al momento de agregar
   - ⏳ Backend: Validar precio en checkout (puede haber cambiado)

---

## 📁 ARCHIVOS MODIFICADOS (FRONTEND)

### ✅ Completados

- `src/shared/hooks/useAddToCart.ts`
  - Agregado: Verificación de autenticación
  - Agregado: Redirección a login
  - Agregado: Toast de error

- `src/widgets/bottom-carousel/CarouselCard.tsx`
  - Agregado: Badge de descuento
  - Agregado: Cálculo de precio original
  - Agregado: Visualización de descuento

- `src/widgets/bottom-carousel/CarouselCard.css`
  - Agregado: Estilos para `.tarjeta-descuento-badge`
  - Agregado: Gradiente rojo
  - Agregado: Sombra y posicionamiento

---

## 🚀 TESTING

### Frontend

```
1. Abre la web sin estar logueado
2. Intenta agregar un producto
3. Deberías ver:
   - Toast rojo: "Debes iniciar sesión"
   - Redirección a /login

4. Inicia sesión
5. Intenta agregar un producto
6. Deberías ver:
   - Toast verde: "¡Producto agregado!"
   - Badge rojo con descuento en CarouselCard
   - Precio original tachado
```

### Backend (Próximo)

```
1. POST /api/carrito/agregar/
   - Sin autenticación → 401 Unauthorized
   - Con autenticación → 201 Created

2. GET /api/carrito/
   - Sin autenticación → 401 Unauthorized
   - Con autenticación → 200 OK + items

3. Validaciones
   - product_id inválido → 404 Not Found
   - quantity negativa → 400 Bad Request
   - stock insuficiente → 400 Bad Request
```

---

## 📚 REFERENCIA

### Archivos Clave

- `src/app/store/useCartStore.ts` - Zustand store del carrito
- `src/app/store/useAuthStore.ts` - Zustand store de autenticación
- `src/shared/hooks/useAddToCart.ts` - Hook para agregar al carrito
- `src/widgets/bottom-carousel/CarouselCard.tsx` - Tarjeta con descuentos
- `src/contexts/AuthContext.tsx` - Provider de autenticación

### Endpoints Necesarios (Backend)

```
GET    /api/carrito/
POST   /api/carrito/agregar/
PUT    /api/carrito/items/{id}/
DELETE /api/carrito/items/{id}/
DELETE /api/carrito/
```

---

## ✨ CONCLUSIÓN

**Frontend completado:**
- ✅ Autenticación obligatoria para agregar al carrito
- ✅ Descuentos visibles en CarouselCard
- ✅ Redirección a login si no está autenticado
- ✅ Estructura lista para sincronizar con backend

**Próximo paso:** Implementar endpoints en backend para persistencia del carrito por usuario.
