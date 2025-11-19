# ✅ ENDPOINTS DEL CARRITO - CORREGIDOS

**Fecha:** 7 de Noviembre, 2025  
**Status:** ✅ **RUTAS CORREGIDAS CON @action**

---

## 🔧 PROBLEMA SOLUCIONADO

### Error Original
```
404 (Not Found)
SyntaxError: Unexpected token '<', "<!DOCTYPE "... is not valid JSON
```

### Causa
Las rutas personalizadas no estaban registradas correctamente. Usaba `viewsets.ViewSet` sin decoradores `@action`.

### Solución
Agregué decoradores `@action` a cada método para que Django REST Framework genere las rutas correctamente.

---

## 📊 ENDPOINTS FINALES

### 1. Obtener Carrito
```bash
GET /api/carrito/
```

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
```

**Respuesta (200):**
```json
{
  "id": 1,
  "items": [],
  "total": 0.0,
  "total_items": 0,
  "created_at": "2025-11-07T...",
  "updated_at": "2025-11-07T..."
}
```

---

### 2. Agregar Producto al Carrito
```bash
POST /api/carrito/agregar/
```

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Body:**
```json
{
  "product_id": 1,
  "quantity": 2
}
```

**Respuesta (201):**
```json
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "nombre": "Laptop",
        "imagen_url": "...",
        "categoria": "laptops"
      },
      "quantity": 2,
      "price_at_addition": "1000.00",
      "subtotal": 2000.0,
      "created_at": "2025-11-07T...",
      "updated_at": "2025-11-07T..."
    }
  ],
  "total": 2000.0,
  "total_items": 2,
  "created_at": "2025-11-07T...",
  "updated_at": "2025-11-07T..."
}
```

---

### 3. Actualizar Cantidad de Item
```bash
PUT /api/carrito/items/1/
```

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json
```

**Body:**
```json
{
  "quantity": 5
}
```

**Respuesta (200):**
```json
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "product": {...},
      "quantity": 5,
      "price_at_addition": "1000.00",
      "subtotal": 5000.0,
      ...
    }
  ],
  "total": 5000.0,
  "total_items": 5,
  ...
}
```

---

### 4. Eliminar Item del Carrito
```bash
DELETE /api/carrito/items/1/
```

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
```

**Respuesta (200):**
```json
{
  "id": 1,
  "items": [],
  "total": 0.0,
  "total_items": 0,
  ...
}
```

---

### 5. Vaciar Carrito Completo
```bash
DELETE /api/carrito/vaciar/
```

**Headers:**
```
Authorization: Bearer YOUR_TOKEN
```

**Respuesta (200):**
```json
{
  "id": 1,
  "items": [],
  "total": 0.0,
  "total_items": 0,
  ...
}
```

---

## 🧪 PRUEBAS CON CURL

### Paso 1: Obtén Token
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

Guarda el `access_token`.

### Paso 2: Obtén Carrito
```bash
curl -X GET http://localhost:8000/api/carrito/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Paso 3: Agrega Producto
```bash
curl -X POST http://localhost:8000/api/carrito/agregar/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":2}'
```

### Paso 4: Actualiza Cantidad
```bash
curl -X PUT http://localhost:8000/api/carrito/items/1/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity":5}'
```

### Paso 5: Elimina Item
```bash
curl -X DELETE http://localhost:8000/api/carrito/items/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Paso 6: Vacía Carrito
```bash
curl -X DELETE http://localhost:8000/api/carrito/vaciar/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📁 ARCHIVOS MODIFICADOS

- ✅ `backend/api/views.py` - Agregados decoradores `@action`

---

## ✅ VALIDACIONES

✅ Autenticación JWT requerida  
✅ Autorización: Solo su carrito  
✅ Validación de stock  
✅ Validación de cantidad  
✅ Producto debe existir  
✅ Errores descriptivos  

---

## 🚀 LISTO

Todos los endpoints están funcionando correctamente.

¡Adelante! 🎉
