# 🔄 ESTRATEGIA DE CACHÉ ROBUSTA - Electro Isla

## 📋 RESUMEN EJECUTIVO

Se ha implementado una estrategia de caché profesional basada en **Cache-Aside** con **invalidación explícita** para mitigar todos los riesgos identificados:

1. ✅ **Datos Desactualizados (Cache Staleness)**
2. ✅ **Complejidad Adicional**
3. ✅ **Consumo de Recursos**
4. ✅ **Fallos de Caché (Cache Misses)**

---

## 🛡️ RIESGOS MITIGADOS

### 1. Datos Desactualizados (Cache Staleness)

**Problema:** Los datos en caché pueden quedar obsoletos si la BD cambia.

**Solución Implementada:**
- **TTL (Time To Live) Configurable**: Cada tipo de dato tiene un TTL específico
- **Invalidación Explícita**: Se invalida automáticamente cuando hay cambios en BD
- **Señales Django (Signals)**: Detectan cambios y limpian caché

**Configuración TTL:**
```python
TTL_CONFIG = {
    'estadisticas_ventas': 300,        # 5 minutos - datos volátiles
    'estadisticas_usuarios': 600,      # 10 minutos - menos volátiles
    'productos_vendidos': 300,         # 5 minutos - muy volátil
    'metodos_pago': 600,               # 10 minutos
    'perfil_usuario': 3600,            # 1 hora - relativamente estable
    'lista_productos': 300,            # 5 minutos - volátil
}
```

**Ejemplo:**
```python
# Producto se actualiza en BD
producto.precio = 99.99
producto.save()

# Automáticamente se invalida:
# - estadisticas_ventas
# - productos_vendidos
# - lista_productos
```

---

### 2. Complejidad Adicional

**Problema:** Olvidar invalidar caché después de cambios.

**Solución Implementada:**
- **Clase CacheManager**: Centraliza toda la lógica de caché
- **Señales Automáticas**: Django signals invalidan caché automáticamente
- **Patrón Cache-Aside**: Lectura de caché → Escritura en BD + invalidación

**Flujo Implementado:**

```
┌─────────────────────────────────────────────────────────┐
│ LECTURA (GET)                                           │
├─────────────────────────────────────────────────────────┤
│ 1. CacheManager.get(cache_key, fetch_func)             │
│ 2. Intenta obtener del caché                           │
│ 3. Si falla (MISS): ejecuta fetch_func()              │
│ 4. Guarda resultado en caché con TTL                  │
│ 5. Retorna datos                                       │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ ESCRITURA (POST/PUT/DELETE)                            │
├─────────────────────────────────────────────────────────┤
│ 1. Escribir en BD (Django ORM)                         │
│ 2. Signal post_save/post_delete se dispara             │
│ 3. CacheManager.invalidate() limpia caché              │
│ 4. Siguiente lectura obtiene datos frescos             │
└─────────────────────────────────────────────────────────┘
```

---

### 3. Consumo de Recursos

**Problema:** Almacenar datos que no se acceden frecuentemente.

**Solución Implementada:**
- **TTL Agresivo para datos volátiles**: 5 minutos para estadísticas
- **Límites en queries**: `[:10]` para productos más vendidos
- **Monitoreo**: Logging de aciertos/fallos para detectar problemas

**Ejemplo:**
```python
# Estadísticas de ventas: TTL 5 minutos (datos muy volátiles)
CacheManager.get(
    cache_key='estadisticas_ventas',
    fetch_func=fetch_estadisticas_ventas,
    ttl=300  # 5 minutos
)

# Perfil de usuario: TTL 1 hora (datos más estables)
CacheManager.get(
    cache_key=f'user_profile_{user_id}',
    fetch_func=lambda: UserProfile.objects.get(user_id=user_id),
    ttl=3600  # 1 hora
)
```

---

### 4. Fallos de Caché (Cache Misses)

**Problema:** Primeras solicitudes no están en caché.

**Solución Implementada:**
- **Logging detallado**: Detecta patrones de MISS
- **Estadísticas**: Monitoreo de aciertos vs fallos
- **Fallback automático**: Si caché falla, va a BD

**Logs Generados:**
```
✅ Cache HIT: estadisticas_ventas
❌ Cache MISS: estadisticas_ventas
💾 Guardado en caché: estadisticas_ventas (TTL: 300s)
🗑️  Invalidado caché: estadisticas_ventas
```

---

## 🔧 IMPLEMENTACIÓN TÉCNICA

### Archivo: `backend/api/utils/cache_manager.py`

**Clase Principal: CacheManager**

```python
class CacheManager:
    """Gestor de caché con invalidación explícita y TTL configurable"""
    
    @staticmethod
    def get(cache_key, fetch_func=None, ttl=None):
        """Obtener dato del caché o de la fuente original"""
        # Intenta caché → Si falla, va a BD → Guarda en caché
    
    @staticmethod
    def invalidate(cache_keys):
        """Invalidar uno o múltiples registros"""
        # Limpia caché automáticamente
    
    @staticmethod
    def invalidate_pattern(pattern):
        """Invalidar por patrón (requiere Redis)"""
    
    @staticmethod
    def clear_all():
        """Limpiar todo el caché"""
    
    @staticmethod
    def get_stats():
        """Obtener estadísticas de aciertos/fallos"""
```

### Señales Automáticas

```python
@receiver(post_save, sender=Producto)
def invalidate_producto_cache(sender, instance, created, **kwargs):
    """Invalidar caché cuando se crea/actualiza un Producto"""
    cache_keys_to_invalidate = [
        'estadisticas_ventas',
        'productos_vendidos',
        'lista_productos',
        f'producto_{instance.id}',
    ]
    CacheManager.invalidate(cache_keys_to_invalidate)

@receiver(post_save, sender=Pedido)
def invalidate_pedido_cache(sender, instance, created, **kwargs):
    """Invalidar caché cuando se crea/actualiza un Pedido"""
    cache_keys_to_invalidate = [
        'estadisticas_ventas',
        'metodos_pago',
    ]
    CacheManager.invalidate(cache_keys_to_invalidate)
```

---

## 📊 ENDPOINTS CON CACHÉ

### 1. `/api/admin/estadisticas/ventas/`

**TTL:** 5 minutos (datos muy volátiles)

**Invalidación automática cuando:**
- Se crea un nuevo Pedido
- Se actualiza un Pedido
- Se cambia el estado de un Pedido

**Datos cacheados:**
- Ventas por mes (últimos 12 meses)
- Productos más vendidos
- Métodos de pago
- Ticket promedio

### 2. `/api/admin/estadisticas/usuarios/`

**TTL:** 10 minutos (datos menos volátiles)

**Invalidación automática cuando:**
- Se crea un nuevo Usuario
- Se actualiza el rol de un Usuario

**Datos cacheados:**
- Crecimiento por mes
- Usuarios por rol
- Usuarios más activos
- Tasa de retención

---

## 🚀 USO EN CÓDIGO

### Lectura con Caché

```python
@api_view(['GET'])
@permission_classes([IsAdminOrStaff])
def estadisticas_ventas(request):
    def fetch_estadisticas_ventas():
        # Lógica para obtener datos de BD
        return {
            'ventas_por_mes': [...],
            'productos_mas_vendidos': [...],
        }
    
    # CacheManager maneja todo automáticamente
    data = CacheManager.get(
        cache_key='estadisticas_ventas',
        fetch_func=fetch_estadisticas_ventas,
        ttl=300
    )
    
    return Response(data)
```

### Invalidación Automática

```python
# Cuando se actualiza un Producto:
producto.precio = 99.99
producto.save()  # ← Signal se dispara automáticamente

# Caché se invalida automáticamente:
# - estadisticas_ventas
# - productos_vendidos
# - lista_productos
```

---

## 📈 MONITOREO Y ALERTAS

### Logs Disponibles

```
# Archivo: logs/cache.log

2025-11-09 16:00:00 - cache_manager - INFO - ✅ Cache HIT: estadisticas_ventas
2025-11-09 16:00:05 - cache_manager - WARNING - ❌ Cache MISS: estadisticas_ventas
2025-11-09 16:00:05 - cache_manager - INFO - 💾 Guardado en caché: estadisticas_ventas (TTL: 300s)
2025-11-09 16:01:00 - cache_manager - INFO - 🗑️  Invalidado caché: estadisticas_ventas
```

### Estadísticas

```python
stats = CacheManager.get_stats()
# {
#     'hits': 1250,
#     'misses': 45,
#     'invalidations': 120,
#     'last_updated': '2025-11-09T16:00:00'
# }
```

---

## ⚙️ CONFIGURACIÓN RECOMENDADA

### settings.py

```python
# Backend de caché (Redis recomendado para producción)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'electro_isla',
        'TIMEOUT': 300,  # TTL por defecto: 5 minutos
    }
}

# Logging para monitoreo
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'cache_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/cache.log',
        },
    },
    'loggers': {
        'cache_manager': {
            'handlers': ['cache_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- ✅ Clase `CacheManager` creada
- ✅ TTL configurable por tipo de dato
- ✅ Invalidación explícita implementada
- ✅ Señales Django para auto-invalidación
- ✅ Logging detallado
- ✅ `estadisticas_ventas` con caché
- ✅ `estadisticas_usuarios` con caché
- ✅ Documentación completa

---

## 🎯 BENEFICIOS

| Aspecto | Antes | Después |
|--------|-------|---------|
| **Datos Desactualizados** | Alto riesgo | ✅ Mitigado con TTL + invalidación |
| **Complejidad** | Manual | ✅ Automática con signals |
| **Consumo de RAM** | Descontrolado | ✅ TTL agresivo para datos volátiles |
| **Cache Misses** | No monitoreado | ✅ Logging detallado |
| **Consistencia** | Inconsistente | ✅ Garantizada con invalidación |

---

## 📝 NOTAS IMPORTANTES

1. **Redis vs LocMemCache**: Para desarrollo se usa LocMemCache, pero en producción se recomienda Redis
2. **TTL Ajustable**: Los TTL pueden ajustarse según el comportamiento real del sistema
3. **Monitoreo Continuo**: Revisar logs regularmente para detectar patrones de MISS
4. **Escalabilidad**: Con Redis, la caché es compartida entre múltiples servidores

---

## 🔗 ARCHIVOS RELACIONADOS

- `backend/api/utils/cache_manager.py` - Gestor de caché
- `backend/api/views_estadisticas.py` - Endpoints con caché
- `backend/config/settings.py` - Configuración de caché
- `logs/cache.log` - Logs de caché

---

**Última actualización:** 9 de Noviembre, 2025  
**Status:** ✅ Implementado y Documentado
