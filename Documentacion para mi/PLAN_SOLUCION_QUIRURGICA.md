# 🎯 PLAN QUIRÚRGICO - SOLUCIÓN IMPECABLE

**Fecha:** 20 de Noviembre, 2025  
**Objetivo:** Solucionar campos `en_carousel_card` y `en_all_products` sin romper nada  
**Estrategia:** Crear archivos separados para no sobrecargar `views.py` (1374 líneas)

---

## 📋 ESTRUCTURA DE SOLUCIÓN

### **Paso 1: Crear `views_catalogo.py` (NUEVO ARCHIVO)**
- Mover lógica de catálogo a archivo separado
- Crear endpoint `/productos-catalogo/`
- Mantener limpieza y organización

### **Paso 2: Crear `urls_catalogo.py` (NUEVO ARCHIVO)**
- Registrar rutas de catálogo
- Mantener `urls.py` limpio

### **Paso 3: Actualizar `serializers.py`**
- Agregar campos a `ProductoSerializer` (cambio mínimo: 1 línea)
- Sin tocar nada más

### **Paso 4: Actualizar `urls.py`**
- Incluir `urls_catalogo.py`
- Sin eliminar nada existente

### **Paso 5: Actualizar Frontend**
- Cambiar endpoint en `carrusel.ts`
- Agregar filtros en componentes
- Cambios mínimos y seguros

---

## 🔧 DETALLES DE CADA PASO

### **PASO 1: Crear `backend/api/views_catalogo.py`**

```python
"""
═══════════════════════════════════════════════════════════════════════════════
📦 VIEWS - Catálogo de Productos
═══════════════════════════════════════════════════════════════════════════════

Endpoints para obtener productos del catálogo completo y tarjetas inferiores.
Separado de views.py para mantener código limpio y organizado.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.response import Response
from django.db.models import Q
from .models import Producto
from .serializers import ProductoSerializer
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def productos_catalogo_completo(request):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    📦 ENDPOINT - Catálogo Completo de Productos
    ═══════════════════════════════════════════════════════════════════════════════
    
    Obtiene TODOS los productos marcados para mostrar en el catálogo completo.
    SIN LÍMITE de productos.
    
    GET /api/catalogo/productos/
    
    Query Parameters:
    - categoria: str (opcional) - Filtrar por categoría
    - search: str (opcional) - Buscar por nombre o descripción
    
    Retorna:
    - count: int - Número total de productos
    - data: array - Lista de productos con información completa
    """
    try:
        # Obtener TODOS los productos con en_all_products=true
        queryset = Producto.objects.filter(
            en_all_products=True,
            activo=True
        ).select_related(
            'creado_por'
        ).only(
            'id', 'nombre', 'descripcion', 'precio', 'descuento', 'categoria',
            'imagen', 'imagen_url', 'stock_total', 'stock_reservado', 'stock_vendido',
            'activo', 'en_all_products', 'en_carousel_card', 'en_carrusel',
            'creado_por', 'created_at', 'updated_at'
        ).order_by('-created_at')
        
        # Filtros opcionales
        categoria = request.query_params.get('categoria', None)
        search = request.query_params.get('search', None)
        
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search)
            )
        
        # Serializar
        serializer = ProductoSerializer(
            queryset,
            many=True,
            context={'is_list': True, 'request': request}
        )
        
        response_data = {
            'count': len(serializer.data),
            'data': serializer.data
        }
        
        logger.info(f'[CATALOGO_COMPLETO] {len(serializer.data)} productos cargados')
        
        return Response(response_data)
    
    except Exception as e:
        logger.error(f'Error al obtener catálogo completo: {str(e)}')
        return Response(
            {'error': 'Error al obtener productos'},
            status=500
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def productos_tarjetas_inferiores(request):
    """
    ═══════════════════════════════════════════════════════════════════════════════
    🎠 ENDPOINT - Tarjetas Inferiores
    ═══════════════════════════════════════════════════════════════════════════════
    
    Obtiene TODOS los productos marcados para mostrar en tarjetas inferiores.
    SIN LÍMITE de productos.
    
    GET /api/catalogo/tarjetas-inferiores/
    
    Retorna:
    - count: int - Número total de productos
    - data: array - Lista de productos
    """
    try:
        # Obtener TODOS los productos con en_carousel_card=true
        queryset = Producto.objects.filter(
            en_carousel_card=True,
            activo=True
        ).select_related(
            'creado_por'
        ).only(
            'id', 'nombre', 'descripcion', 'precio', 'descuento', 'categoria',
            'imagen', 'imagen_url', 'stock_total', 'stock_reservado', 'stock_vendido',
            'activo', 'en_all_products', 'en_carousel_card', 'en_carrusel',
            'creado_por', 'created_at', 'updated_at'
        ).order_by('-created_at')
        
        # Serializar
        serializer = ProductoSerializer(
            queryset,
            many=True,
            context={'is_list': True, 'request': request}
        )
        
        response_data = {
            'count': len(serializer.data),
            'data': serializer.data
        }
        
        logger.info(f'[TARJETAS_INFERIORES] {len(serializer.data)} productos cargados')
        
        return Response(response_data)
    
    except Exception as e:
        logger.error(f'Error al obtener tarjetas inferiores: {str(e)}')
        return Response(
            {'error': 'Error al obtener productos'},
            status=500
        )
```

---

### **PASO 2: Crear `backend/api/urls_catalogo.py`**

```python
"""
═══════════════════════════════════════════════════════════════════════════════
🔗 URLS - Catálogo de Productos
═══════════════════════════════════════════════════════════════════════════════

Rutas para endpoints de catálogo.
Separado de urls.py para mantener código limpio y organizado.
"""

from django.urls import path
from .views_catalogo import (
    productos_catalogo_completo,
    productos_tarjetas_inferiores,
)

urlpatterns = [
    path('productos/', productos_catalogo_completo, name='catalogo-productos'),
    path('tarjetas-inferiores/', productos_tarjetas_inferiores, name='tarjetas-inferiores'),
]
```

---

### **PASO 3: Actualizar `backend/api/serializers.py`**

**Cambio mínimo - Línea 130:**

```python
# ANTES:
fields = [
    'id', 'nombre', 'descripcion', 'precio', 'descuento', 'categoria', 
    'imagen_url', 'stock', 'stock_total', 'stock_reservado', 'stock_vendido',
    'activo', 'en_carrusel', 'creado_por', 
    'creado_por_username', 'favoritos_count', 'created_at', 'updated_at'
]

# DESPUÉS:
fields = [
    'id', 'nombre', 'descripcion', 'precio', 'descuento', 'categoria', 
    'imagen_url', 'stock', 'stock_total', 'stock_reservado', 'stock_vendido',
    'activo', 'en_carrusel', 'en_carousel_card', 'en_all_products', 'creado_por', 
    'creado_por_username', 'favoritos_count', 'created_at', 'updated_at'
]
```

---

### **PASO 4: Actualizar `backend/api/urls.py`**

**Agregar al inicio (después de otros imports):**

```python
from .urls_catalogo import urlpatterns as catalogo_urls
```

**Agregar en urlpatterns (después de rutas públicas):**

```python
# Rutas de catálogo
path('catalogo/', include(catalogo_urls)),
```

---

### **PASO 5: Actualizar Frontend**

#### **5.1 Actualizar `carrusel.ts`**

```typescript
// CAMBIAR línea 147 de:
const response = await axios.get(`${API_BASE_URL}/carrusel/`);

// A:
const response = await axios.get(`${API_BASE_URL}/catalogo/productos/`);
```

#### **5.2 Actualizar `BottomCarousel.tsx`**

```typescript
// CAMBIAR línea 31 de:
const displayProducts = productos && productos.length > 0 ? productos : [];

// A:
const displayProducts = productos?.filter(p => p.en_carousel_card !== false) || [];
```

#### **5.3 Actualizar `AllProducts.tsx`**

```typescript
// CAMBIAR línea 41 de:
setDisplayedProducts(products.slice(0, initialCount));

// A:
const filteredProducts = products.filter(p => p.en_all_products !== false);
const initialCount = Math.min(PRODUCTS_PER_PAGE, filteredProducts.length);
setDisplayedProducts(filteredProducts.slice(0, initialCount));
```

---

## ✅ VENTAJAS DE ESTE PLAN

1. **Sin romper nada**: No tocamos `views.py` directamente
2. **Código limpio**: Separamos responsabilidades
3. **Mantenible**: Cada archivo tiene un propósito claro
4. **Escalable**: Fácil agregar más endpoints de catálogo
5. **Seguro**: Cambios mínimos y quirúrgicos
6. **Funcional**: Todo sigue funcionando

---

## 📊 CAMBIOS POR ARCHIVO

| Archivo | Tipo | Cambios | Riesgo |
|---------|------|---------|--------|
| `views_catalogo.py` | NUEVO | +150 líneas | ✅ Bajo |
| `urls_catalogo.py` | NUEVO | +20 líneas | ✅ Bajo |
| `serializers.py` | MODIFICAR | +2 campos en 1 línea | ✅ Muy bajo |
| `urls.py` | MODIFICAR | +2 líneas | ✅ Muy bajo |
| `carrusel.ts` | MODIFICAR | 1 línea | ✅ Muy bajo |
| `BottomCarousel.tsx` | MODIFICAR | 1 línea | ✅ Muy bajo |
| `AllProducts.tsx` | MODIFICAR | 3 líneas | ✅ Muy bajo |

---

## 🚀 ORDEN DE EJECUCIÓN

1. ✅ Crear `views_catalogo.py`
2. ✅ Crear `urls_catalogo.py`
3. ✅ Actualizar `serializers.py`
4. ✅ Actualizar `urls.py`
5. ✅ Actualizar `carrusel.ts`
6. ✅ Actualizar `BottomCarousel.tsx`
7. ✅ Actualizar `AllProducts.tsx`
8. ✅ Pruebas exhaustivas

---

## ⚠️ PRECAUCIONES

- ✅ No tocar `views.py` directamente
- ✅ Cambios mínimos en cada archivo
- ✅ Mantener compatibilidad hacia atrás
- ✅ Probar después de cada cambio
- ✅ Verificar que `/carrusel/` sigue funcionando

---

**ESTADO:** Listo para proceder paso a paso sin errores.
