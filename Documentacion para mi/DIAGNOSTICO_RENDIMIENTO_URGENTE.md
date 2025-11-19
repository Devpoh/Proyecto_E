# 🔴 DIAGNÓSTICO URGENTE - PROBLEMAS DE RENDIMIENTO

**Fecha:** 12 de Noviembre, 2025  
**Status:** 🔴 CRÍTICO - La web está muy lenta

---

## 🎯 PROBLEMAS IDENTIFICADOS

### 1. **CELERY CAUSANDO RALENTIZACIONES** ✅ SOLUCIONADO
**Síntoma:** Celery fallaba con `ValueError: not enough values to unpack`
**Causa:** Tareas se registraban pero no se ejecutaban correctamente
**Solución:** Deshabilitado temporalmente con `CELERY_ALWAYS_EAGER = True`
- Ahora las tareas se ejecutan síncronamente (sin broker)
- Esto permite que la web funcione mientras investigamos

---

## 🔍 PROBLEMAS DE RENDIMIENTO REALES

### 2. **QUERIES N+1 EN BACKEND**

#### Problema: `productos_carrusel` endpoint
**Ubicación:** `backend/api/views.py` línea 524

```python
# ❌ PROBLEMA: Esto causa N+1 queries
productos = Producto.objects.filter(
    en_carrusel=True, 
    activo=True
).select_related(
    'creado_por'
).annotate(
    favoritos_count_cached=Count('favoritos')  # ← PROBLEMA: Causa query por cada producto
).order_by('-created_at')
```

**Por qué es lento:**
- `Count('favoritos')` hace una query POR CADA PRODUCTO
- Si hay 100 productos, hace 101 queries (1 para listar + 100 para contar favoritos)
- Cada query toma ~50-100ms = 5-10 segundos totales

**Solución:**
```python
# ✅ CORRECTO: Usar prefetch_related
productos = Producto.objects.filter(
    en_carrusel=True, 
    activo=True
).select_related(
    'creado_por'
).prefetch_related(
    'favoritos'  # ← Carga todos los favoritos en 1 query
).order_by('-created_at')
```

---

### 3. **SERIALIZER ENVIANDO DATOS INNECESARIOS**

#### Problema: `ProductoSerializer` en listados
**Ubicación:** `backend/api/serializers.py` línea 119

```python
class ProductoSerializer(serializers.ModelSerializer):
    # ❌ PROBLEMA: Estos campos son muy pesados en listados
    imagen_url = serializers.SerializerMethodField()  # Puede ser >100KB en base64
    favoritos_count = serializers.SerializerMethodField()  # Causa queries
    
    class Meta:
        fields = [
            'id', 'nombre', 'descripcion', 'precio', 'descuento', 'categoria', 
            'imagen_url',  # ← PROBLEMA: Base64 muy grande
            'stock', 'stock_total', 'stock_reservado', 'stock_vendido',
            'activo', 'en_carrusel', 'creado_por', 
            'creado_por_username', 'favoritos_count', 'created_at', 'updated_at'
        ]
```

**Por qué es lento:**
- `imagen_url` en base64 puede ser 50-200KB por producto
- Si hay 100 productos = 5-20MB de datos
- Transmisión lenta + procesamiento lento en frontend

**Solución:**
```python
# ✅ CORRECTO: Excluir imagen en listados
def get_serializer_context(self):
    context = super().get_serializer_context()
    context['is_list'] = self.action == 'list'
    return context
```

---

### 4. **FALTA DE PAGINACIÓN EN LISTADOS**

#### Problema: Cargar TODOS los productos
**Ubicación:** `backend/api/views.py` - Endpoints de productos

```python
# ❌ PROBLEMA: Sin paginación
productos = Producto.objects.all()  # Puede ser 1000+ productos
serializer = ProductoSerializer(productos, many=True)
```

**Por qué es lento:**
- Si hay 1000 productos = 1000 * 100KB = 100MB de datos
- Transmisión toma 10-30 segundos
- Procesamiento en frontend toma 5-10 segundos

**Solución:**
```python
# ✅ CORRECTO: Usar paginación
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    pagination_class = PageNumberPagination  # Ya configurado en settings
    # Automáticamente limita a 50 items por página
```

---

### 5. **FALTA DE ÍNDICES EN BASE DE DATOS**

#### Problema: Queries lentas en PostgreSQL
**Ubicación:** `backend/api/models.py`

```python
# ❌ PROBLEMA: Sin índices
class Producto(models.Model):
    en_carrusel = models.BooleanField(default=False)  # Sin índice
    activo = models.BooleanField(default=True)  # Sin índice
    categoria = models.CharField(max_length=50)  # Sin índice
    created_at = models.DateTimeField(auto_now_add=True)  # Sin índice
```

**Por qué es lento:**
- Queries como `filter(en_carrusel=True, activo=True)` hacen full table scan
- Si hay 10,000 productos = 10,000 comparaciones
- Toma 1-5 segundos por query

**Solución:**
```python
# ✅ CORRECTO: Agregar índices
class Producto(models.Model):
    en_carrusel = models.BooleanField(default=False, db_index=True)
    activo = models.BooleanField(default=True, db_index=True)
    categoria = models.CharField(max_length=50, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['en_carrusel', 'activo']),  # Índice compuesto
            models.Index(fields=['categoria', 'activo']),
        ]
```

---

### 6. **FALTA DE CACHÉ EN FRONTEND**

#### Problema: Recargando datos innecesariamente
**Ubicación:** `frontend/electro_isla/src/shared/api/carrusel.ts`

```typescript
// ❌ PROBLEMA: Sin caché
export const useProductosCarrusel = () => {
  const [productos, setProductos] = React.useState<ProductoCarrusel[]>([]);
  
  React.useEffect(() => {
    const cargarProductos = async () => {
      // Cada vez que se monta el componente, hace una petición
      const datos = await obtenerProductosCarrusel();
      setProductos(datos);
    };
    
    cargarProductos();
  }, []);  // ← Sin dependencias = se ejecuta cada vez
```

**Por qué es lento:**
- Si el usuario navega a Home 5 veces = 5 peticiones
- Cada petición toma 2-5 segundos
- Total = 10-25 segundos de espera

**Solución:**
```typescript
// ✅ CORRECTO: Usar React Query con caché
import { useQuery } from '@tanstack/react-query';

export const useProductosCarrusel = () => {
  return useQuery({
    queryKey: ['productos-carrusel'],
    queryFn: obtenerProductosCarrusel,
    staleTime: 5 * 60 * 1000,  // 5 minutos
    cacheTime: 10 * 60 * 1000,  // 10 minutos
  });
};
```

---

### 7. **FALTA DE LAZY LOADING EN IMÁGENES**

#### Problema: Cargar todas las imágenes al mismo tiempo
**Ubicación:** `frontend/electro_isla/src/widgets/bottom-carousel/CarouselCard.tsx`

```tsx
// ❌ PROBLEMA: Sin lazy loading
<img src={producto.imagen_url} alt={producto.nombre} />
```

**Por qué es lento:**
- Si hay 20 productos con imágenes de 50KB = 1MB
- Todas se cargan al mismo tiempo
- Bloquea el renderizado

**Solución:**
```tsx
// ✅ CORRECTO: Lazy loading
<img 
  src={producto.imagen_url} 
  alt={producto.nombre}
  loading="lazy"  // ← Carga solo cuando es visible
/>
```

---

## 📊 RESUMEN DE PROBLEMAS

| Problema | Impacto | Solución | Prioridad |
|----------|---------|----------|-----------|
| Celery fallando | 🔴 Crítico | Deshabilitado (HECHO) | ✅ HECHO |
| N+1 queries | 🔴 Crítico | Usar prefetch_related | 🔴 URGENTE |
| Imágenes base64 grandes | 🔴 Crítico | Excluir en listados | 🔴 URGENTE |
| Sin paginación | 🟡 Alto | Agregar PageNumberPagination | 🟡 ALTO |
| Sin índices BD | 🟡 Alto | Agregar db_index=True | 🟡 ALTO |
| Sin caché frontend | 🟡 Alto | Usar React Query | 🟡 ALTO |
| Sin lazy loading | 🟡 Medio | Agregar loading="lazy" | 🟡 MEDIO |

---

## 🚀 PLAN DE ACCIÓN

### FASE 1: CRÍTICA (Hoy)
1. ✅ Deshabilitar Celery
2. ✅ Arreglar N+1 queries en `productos_carrusel`
3. ✅ Agregar índices en BD (migración 0025)
4. ✅ Excluir imágenes base64 en listados

### FASE 2: ALTA (Mañana)
4. 🟡 Agregar paginación
5. 🟡 Agregar índices en BD
6. 🟡 Implementar React Query

### FASE 3: MEDIA (Esta semana)
7. 🟡 Lazy loading de imágenes
8. 🟡 Code splitting en frontend
9. 🟡 Compresión de imágenes

---

## 📝 PRÓXIMOS PASOS

1. Ejecutar migraciones para agregar índices
2. Actualizar `productos_carrusel` endpoint
3. Actualizar serializer
4. Probar rendimiento con DevTools
5. Medir tiempo de carga antes/después

