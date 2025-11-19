# 🔍 DIAGNÓSTICO COMPLETO - IMÁGENES NO APARECEN

**Fecha:** 13 de Noviembre, 2025  
**Status:** 🔍 INVESTIGANDO

---

## 📊 FLUJO COMPLETO DE IMÁGENES

### 1️⃣ UPLOAD (Admin Panel)
```
ProductosPage.tsx
  ↓
ImageUpload.tsx (línea 85)
  → reader.readAsDataURL(file)
  → Convierte imagen a Base64
  ↓
onChange(result) 
  → Envía Base64 al formulario
  ↓
createProducto() / updateProducto()
  → POST/PATCH /admin/productos/
  → Envía imagen_url: "data:image/jpeg;base64,..."
```

### 2️⃣ STORAGE (Base de datos)
```
Backend recibe Base64
  ↓
ProductoAdminSerializer.validate_imagen_url()
  → Valida que no sea > 5MB
  ↓
Producto.save()
  → Guarda en imagen_url (TextField)
  → PostgreSQL almacena Base64
```

### 3️⃣ RETRIEVAL (API)
```
GET /api/productos/
  ↓
ProductoViewSet.list()
  ↓
ProductoSerializer.get_imagen_url()
  → ✅ ANTES: Filtraba imágenes grandes → null
  → ✅ AHORA: Retorna todas las imágenes
  ↓
Response JSON
  {
    "id": 1,
    "nombre": "Taladro",
    "imagen_url": "data:image/jpeg;base64,..." ← AQUÍ DEBE ESTAR
  }
```

### 4️⃣ DISPLAY (Frontend)
```
ProductCarousel.tsx (línea 134)
  → <img src={productImage} alt={productName} />
  → productImage = currentProduct.imagen_url
  ↓
Si imagen_url es null → Muestra placeholder "Imagen no disponible"
Si imagen_url es Base64 → Debe mostrar la imagen
```

---

## 🐛 PROBLEMA ACTUAL

**Síntoma:** Todas las imágenes muestran "Imagen no disponible" (📦)

**Posibles causas:**

### Causa 1: El Base64 no se está guardando
```
Verificar:
- ¿La imagen se carga en el admin?
- ¿El formulario envía el Base64?
- ¿La BD recibe el Base64?

Cómo verificar:
1. Abre Django admin
2. Edita un producto
3. Verifica que imagen_url tiene valor (no está vacío)
```

### Causa 2: El serializer sigue filtrando
```
Verificar:
- ¿El serializer retorna null?
- ¿Hay otra lógica filtrando imágenes?

Cómo verificar:
1. Abre DevTools (F12)
2. Network → GET /api/productos/
3. Busca "imagen_url" en la respuesta
4. ¿Tiene valor o es null?
```

### Causa 3: El frontend no recibe el Base64
```
Verificar:
- ¿La API retorna el Base64?
- ¿El frontend lo está procesando?

Cómo verificar:
1. Abre DevTools (F12) → Console
2. Ejecuta: console.log(productos[0].imagen_url)
3. ¿Muestra el Base64 o null?
```

### Causa 4: El navegador no puede renderizar el Base64
```
Verificar:
- ¿El Base64 es válido?
- ¿El formato es correcto?

Cómo verificar:
1. Abre DevTools (F12) → Console
2. Ejecuta: 
   const img = new Image();
   img.src = productos[0].imagen_url;
   console.log(img);
3. ¿Carga la imagen?
```

---

## ✅ SOLUCIONES APLICADAS

### 1. Simplificado get_imagen_url()
**Archivo:** `backend/api/serializers.py` (línea 138-152)

```python
# ✅ ANTES - Filtraba imágenes
def get_imagen_url(self, obj):
    if obj.imagen_url and obj.imagen_url.startswith('data:image'):
        if len(obj.imagen_url) > 100000:
            return None  # ← Problema
    if self.context.get('is_list', False):
        if len(obj.imagen_url) > 5000:
            return None  # ← Problema
    return obj.imagen_url

# ✅ DESPUÉS - Retorna todas
def get_imagen_url(self, obj):
    if not obj.imagen_url:
        return None
    return obj.imagen_url
```

---

## 🚀 VERIFICACIÓN PASO A PASO

### Paso 1: Verifica que el Base64 se guarda
```bash
# En Django shell
python manage.py shell

from api.models import Producto
p = Producto.objects.first()
print(len(p.imagen_url))  # ¿Tiene valor?
print(p.imagen_url[:50])  # ¿Empieza con "data:image"?
```

### Paso 2: Verifica que el API retorna el Base64
```bash
# En terminal
curl http://localhost:8000/api/productos/ | grep imagen_url
```

### Paso 3: Verifica en DevTools
```javascript
// F12 → Console
fetch('http://localhost:8000/api/productos/')
  .then(r => r.json())
  .then(d => {
    console.log('Primer producto:', d.results[0]);
    console.log('Imagen URL:', d.results[0].imagen_url);
  });
```

### Paso 4: Verifica que el navegador puede renderizar
```javascript
// F12 → Console
const img = new Image();
img.src = 'data:image/jpeg;base64,/9j/4AAQSkZJRg...'; // Tu Base64
img.onload = () => console.log('✅ Imagen válida');
img.onerror = () => console.log('❌ Imagen inválida');
```

---

## 📋 CHECKLIST DE VERIFICACIÓN

- [ ] ¿Las imágenes se guardan en la BD?
  - Verificar: `SELECT LENGTH(imagen_url) FROM productos LIMIT 1;`
  
- [ ] ¿El serializer retorna el Base64?
  - Verificar: GET /api/productos/ en DevTools
  
- [ ] ¿El frontend recibe el Base64?
  - Verificar: console.log(productos[0].imagen_url)
  
- [ ] ¿El navegador puede renderizar?
  - Verificar: Crear img element con el Base64
  
- [ ] ¿El componente ProductCarousel recibe la imagen?
  - Verificar: console.log(currentProduct.imagen_url)
  
- [ ] ¿El atributo src de img es correcto?
  - Verificar: Inspeccionar elemento en DevTools

---

## 🎯 PRÓXIMOS PASOS

1. **Ejecuta el checklist** de verificación arriba
2. **Identifica en qué paso falla** el flujo
3. **Reporta el resultado** para aplicar la solución específica

---

## 📝 NOTAS

- Las imágenes se guardan como Base64 en PostgreSQL
- El máximo es 5MB en Base64
- El serializer ahora retorna TODAS las imágenes sin filtrar
- El frontend debe recibir el Base64 y renderizarlo en `<img src={...} />`

