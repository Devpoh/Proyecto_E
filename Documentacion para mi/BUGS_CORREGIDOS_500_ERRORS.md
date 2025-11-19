# 🐛 BUGS CORREGIDOS - Errores 500

**Fecha:** 9 de Noviembre, 2025  
**Status:** ✅ **CORREGIDOS**

---

## 📋 RESUMEN

Se identificaron y corrigieron **2 bugs críticos** que causaban errores 500 en:
- ❌ `/api/admin/productos/` - Error 500
- ❌ `/api/admin/historial/` - Error 500

---

## 🔍 BUG #1: ProductoManagementViewSet - prefetch_related inválido

### **Ubicación**
```
Archivo: backend/api/views_admin.py
Línea: 315
```

### **Problema**
```python
# ANTES (❌ INCORRECTO)
queryset = Producto.objects.all().select_related('creado_por').prefetch_related('detalles_pedido')
```

El modelo `Producto` no tiene un relacionado llamado `detalles_pedido`, causando un error 500 cuando se intenta listar productos.

### **Causa Raíz**
- El relacionado `detalles_pedido` no existe en el modelo `Producto`
- Django intenta hacer prefetch de una relación inexistente
- Esto causa una excepción no capturada que resulta en error 500

### **Solución**
```python
# DESPUÉS (✅ CORRECTO)
queryset = Producto.objects.all().select_related('creado_por')
```

Eliminar el `prefetch_related('detalles_pedido')` que no existe.

### **Verificación**
```bash
# Antes
curl http://localhost:8000/api/admin/productos/
# Resultado: 500 Internal Server Error

# Después
curl http://localhost:8000/api/admin/productos/
# Resultado: 200 OK con lista de productos
```

---

## 🔍 BUG #2: AuditLogViewSet - Parsing de fechas ISO inválido

### **Ubicación**
```
Archivo: backend/api/views_admin.py
Línea: 590-592
```

### **Problema**
```python
# ANTES (❌ INCORRECTO)
if fecha_desde:
    queryset = queryset.filter(timestamp__gte=fecha_desde)
if fecha_hasta:
    queryset = queryset.filter(timestamp__lte=fecha_hasta)
```

El filtro intenta comparar directamente strings ISO con timestamps de Django, sin parsear las fechas correctamente.

### **Causa Raíz**
- Las fechas vienen en formato ISO 8601 con zona horaria: `2025-11-09T21:51:07.003Z`
- Django espera objetos `datetime` con zona horaria
- Comparar strings con datetime causa un error 500

### **Solución**
```python
# DESPUÉS (✅ CORRECTO)
def get_queryset(self):
    """Filtrar queryset con optimizaciones"""
    from datetime import datetime
    queryset = super().get_queryset()
    
    # Filtro por fecha
    fecha_desde = self.request.query_params.get('fecha_desde')
    fecha_hasta = self.request.query_params.get('fecha_hasta')
    
    if fecha_desde:
        try:
            fecha_desde_obj = datetime.fromisoformat(fecha_desde.replace('Z', '+00:00'))
            queryset = queryset.filter(timestamp__gte=fecha_desde_obj)
        except (ValueError, AttributeError):
            pass  # Ignorar filtro si la fecha es inválida
    
    if fecha_hasta:
        try:
            fecha_hasta_obj = datetime.fromisoformat(fecha_hasta.replace('Z', '+00:00'))
            queryset = queryset.filter(timestamp__lte=fecha_hasta_obj)
        except (ValueError, AttributeError):
            pass  # Ignorar filtro si la fecha es inválida
    
    return queryset
```

### **Cambios Clave**
1. Importar `datetime` dentro del método
2. Reemplazar `Z` con `+00:00` para compatibilidad con `fromisoformat()`
3. Parsear la fecha con `datetime.fromisoformat()`
4. Agregar manejo de excepciones para fechas inválidas

### **Verificación**
```bash
# Antes
curl "http://localhost:8000/api/admin/historial/?fecha_desde=2025-10-09T20%3A51%3A07.003Z&fecha_hasta=2025-11-09T21%3A51%3A07.003Z"
# Resultado: 500 Internal Server Error

# Después
curl "http://localhost:8000/api/admin/historial/?fecha_desde=2025-10-09T20%3A51%3A07.003Z&fecha_hasta=2025-11-09T21%3A51%3A07.003Z"
# Resultado: 200 OK con historial filtrado
```

---

## 📊 IMPACTO

### **Antes**
```
❌ /api/admin/productos/ - Error 500
❌ /api/admin/historial/ - Error 500
❌ Frontend no puede cargar datos
❌ Admin panel no funciona
```

### **Después**
```
✅ /api/admin/productos/ - 200 OK
✅ /api/admin/historial/ - 200 OK
✅ Frontend carga datos correctamente
✅ Admin panel funciona correctamente
```

---

## 🧪 TESTING

### **Test Manual - Productos**

```bash
# 1. Listar productos
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/admin/productos/

# Resultado esperado: 200 OK
# Respuesta: { "count": X, "next": null, "previous": null, "results": [...] }
```

### **Test Manual - Historial**

```bash
# 1. Listar historial sin filtros
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/admin/historial/

# Resultado esperado: 200 OK

# 2. Listar historial con filtros de fecha
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/admin/historial/?fecha_desde=2025-10-09T20%3A51%3A07.003Z&fecha_hasta=2025-11-09T21%3A51%3A07.003Z"

# Resultado esperado: 200 OK con registros filtrados
```

---

## ✅ CHECKLIST

- [x] Bug #1 identificado
- [x] Bug #1 corregido
- [x] Bug #2 identificado
- [x] Bug #2 corregido
- [x] Cambios verificados
- [x] Documentación creada

---

## 📝 NOTAS

### **Lecciones Aprendidas**

1. **Validar relacionados en modelos**
   - Siempre verificar que los relacionados existan antes de usar `select_related()` o `prefetch_related()`
   - Usar `related_name` en ForeignKey para claridad

2. **Parsear fechas correctamente**
   - Las fechas ISO 8601 con zona horaria requieren conversión
   - Usar `datetime.fromisoformat()` con reemplazo de `Z` por `+00:00`
   - Agregar manejo de excepciones para fechas inválidas

3. **Testing de endpoints**
   - Probar con parámetros de query complejos
   - Verificar que los filtros funcionen correctamente
   - Usar herramientas como curl o Postman para testing

---

## 🚀 PRÓXIMOS PASOS

1. ✅ Verificar que los endpoints funcionan
2. ✅ Probar en el frontend
3. ✅ Verificar que no hay otros errores similares
4. ⏳ Agregar tests unitarios para estos endpoints
5. ⏳ Documentar en guía de desarrollo

---

**Última actualización:** 9 de Noviembre, 2025  
**Status:** ✅ **BUGS CORREGIDOS Y VERIFICADOS**
