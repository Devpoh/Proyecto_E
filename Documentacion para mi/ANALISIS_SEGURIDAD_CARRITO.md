# 🔒 ANÁLISIS DE SEGURIDAD Y OPTIMIZACIÓN - CARRITO

**Fecha:** 7 de Noviembre, 2025  
**Status:** ✅ **ANÁLISIS COMPLETO**

---

## 🔍 ANÁLISIS QUIRÚRGICO

### Frontend - useSyncCart.ts

#### ✅ FORTALEZAS
- Sincronización bidireccional correcta
- Validación de token
- Manejo de errores
- Backend como fuente de verdad
- itemId guardado correctamente

#### ⚠️ PROBLEMAS DE SEGURIDAD

1. **URL hardcodeada** (Línea 62, 106, 158, 206)
   - `'http://localhost:8000/api/carrito/'` está hardcodeada
   - **Riesgo:** Cambios de URL requieren recompilación
   - **Solución:** Usar variable de entorno

2. **Sin validación de respuesta** (Línea 78, 123, 171, 218)
   - No valida estructura de respuesta
   - **Riesgo:** Datos malformados pueden causar errores
   - **Solución:** Validar con Zod o similar

3. **Errores genéricos** (Línea 137, 185, 232)
   - No diferencia tipos de error
   - **Riesgo:** Usuario no sabe qué salió mal
   - **Solución:** Errores específicos

4. **Sin retry logic** 
   - Si falla una sincronización, no reintentar
   - **Riesgo:** Desincronización
   - **Solución:** Agregar retry con backoff exponencial

5. **Timeout no configurado**
   - Fetch sin timeout
   - **Riesgo:** Requests colgadas indefinidamente
   - **Solución:** Agregar AbortController con timeout

### Frontend - useCartStore.ts

#### ✅ FORTALEZAS
- Sin localStorage persist (correcto)
- Métodos simples y claros
- Validación de cantidad

#### ⚠️ PROBLEMAS

1. **Sin validación de entrada**
   - `addItem()` no valida productoId
   - **Riesgo:** IDs negativos o inválidos
   - **Solución:** Validar entrada

2. **Cantidad sin límite**
   - No hay máximo de cantidad
   - **Riesgo:** Usuario agrega 999999 items
   - **Solución:** Validar contra stock

### Frontend - useAddToCart.ts

#### ✅ FORTALEZAS
- Autenticación verificada
- Feedback visual
- Evita múltiples clicks

#### ⚠️ PROBLEMAS

1. **Sin validación de productId**
   - Acepta cualquier string/number
   - **Riesgo:** IDs inválidos
   - **Solución:** Validar formato

### Backend - CartViewSet

#### ✅ FORTALEZAS
- Autenticación requerida
- Validación de stock
- Validación de cantidad
- Filtrado por usuario

#### ⚠️ PROBLEMAS

1. **Sin rate limiting**
   - Usuario puede agregar infinitamente
   - **Riesgo:** Spam/DoS
   - **Solución:** Rate limiting

2. **Sin validación de cantidad máxima**
   - Acepta cualquier cantidad
   - **Riesgo:** Overflow de base de datos
   - **Solución:** Máximo de 999 por item

3. **Sin logging de auditoría**
   - No registra quién agregó/eliminó qué
   - **Riesgo:** No hay trazabilidad
   - **Solución:** Agregar auditoría

4. **Sin validación de precio**
   - Usa precio actual, no el guardado
   - **Riesgo:** Cambios de precio afectan órdenes
   - **Solución:** Usar precio_at_addition siempre

---

## 🔧 MEJORAS A IMPLEMENTAR

### 1. Frontend - Variables de Entorno
```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
```

### 2. Frontend - Timeout y Retry
```typescript
const fetchWithTimeout = (url: string, options: RequestInit, timeout = 5000) => {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  
  return fetch(url, { ...options, signal: controller.signal })
    .finally(() => clearTimeout(id));
};
```

### 3. Frontend - Validación de Respuesta
```typescript
interface ValidatedCart {
  id: number;
  items: Array<{ id: number; product: { id: number; nombre: string }; quantity: number }>;
  total: number;
  total_items: number;
}

const validateCartResponse = (data: unknown): ValidatedCart => {
  // Validar estructura
  if (!data || typeof data !== 'object') throw new Error('Invalid response');
  // ... más validaciones
};
```

### 4. Backend - Rate Limiting
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='user', rate='100/h', method='POST')
def agregar(self, request):
    # ...
```

### 5. Backend - Auditoría
```python
class CartAuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20)  # 'add', 'remove', 'update'
    product_id = models.IntegerField()
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
```

---

## 📊 CÓDIGO MUERTO A ELIMINAR

### Frontend
- ✅ Todos los scripts de prueba excepto `test_perfecto.ps1`
- ✅ Documentos de análisis anteriores (mantener solo este)
- ✅ Archivos markdown duplicados

### Backend
- ✅ Scripts de prueba
- ✅ Documentación duplicada

---

## 🚀 PRIORIDADES

1. **CRÍTICO:** Variables de entorno (API_BASE_URL)
2. **CRÍTICO:** Validación de entrada (frontend y backend)
3. **ALTO:** Timeout y retry (frontend)
4. **ALTO:** Rate limiting (backend)
5. **MEDIO:** Auditoría (backend)
6. **BAJO:** Optimizaciones de rendimiento

---

## ✅ ESTADO ACTUAL

- ✅ Carrito funcional
- ✅ Sincronización correcta
- ✅ Autenticación presente
- ⚠️ Seguridad: 60%
- ⚠️ Optimización: 70%

**Próximo paso:** Implementar mejoras de seguridad
