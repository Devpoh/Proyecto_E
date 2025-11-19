# 🧪 PRUEBAS DEL CARRITO - PASO A PASO

**Fecha:** 7 de Noviembre, 2025  
**Status:** ✅ **LISTO PARA PROBAR**

---

## 📋 REQUISITOS

- ✅ Servidor Django corriendo en `http://localhost:8000`
- ✅ Usuario de prueba creado
- ✅ Productos en la base de datos

---

## 🚀 PASO 1: CREAR USUARIO DE PRUEBA

### En PowerShell:

```powershell
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
python manage.py createsuperuser
```

Completa con:
```
Username: testuser
Email: testuser@example.com
Password: testpass123
Password (again): testpass123
```

---

## 🚀 PASO 2: INICIAR SERVIDOR DJANGO

### En PowerShell:

```powershell
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
python manage.py runserver
```

Deberías ver:
```
Starting development server at http://127.0.0.1:8000/
```

---

## 🚀 PASO 3: PROBAR ENDPOINTS

### Opción A: Usar Script PowerShell (Recomendado)

```powershell
# En otra terminal PowerShell
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
.\test_carrito.ps1
```

**Esperado:**
```
[2] PASO 2: Obtener Token
[OK] Token obtenido exitosamente
Token: eyJ0eXAiOiJKV1QiLCJhbGc...

[3] PASO 3: Obtener Carrito Actual
[OK] Carrito obtenido
Items: 0

[4] PASO 4: Agregar Producto al Carrito
[OK] Producto agregado
Items en carrito: 2

[5] PASO 5: Obtener Carrito Nuevamente
[OK] Carrito obtenido
Items: 2
```

---

### Opción B: Usar curl Manualmente

#### 1. Obtén Token

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

**Respuesta:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "testuser@example.com"
  }
}
```

Guarda el `access_token`.

#### 2. Obtén Carrito

```bash
curl -X GET http://localhost:8000/api/carrito/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Respuesta:**
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

#### 3. Agrega Producto

```bash
curl -X POST http://localhost:8000/api/carrito/agregar/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":2}'
```

**Respuesta:**
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

#### 4. Obtén Carrito Nuevamente

```bash
curl -X GET http://localhost:8000/api/carrito/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Deberías ver los 2 items agregados.

---

## 🧪 PRUEBA DE SINCRONIZACIÓN FRONTEND

### Paso 1: Abre el Frontend

```
http://localhost:3000
```

### Paso 2: Inicia Sesión

- Email: `testuser@example.com`
- Password: `testpass123`

### Paso 3: Abre DevTools (F12)

Ve a: **Storage → Local Storage → http://localhost:3000**

### Paso 4: Agrega Producto

- Busca un producto
- Haz clic en "Agregar al Carrito"

### Paso 5: Verifica Sincronización

En DevTools, deberías ver:
- ✅ `cart-storage` actualizado con el producto
- ✅ Carrito en UI actualizado
- ✅ Backend actualizado (verifica con curl)

---

## 🔍 VERIFICAR EN ADMIN

1. Ve a: `http://localhost:8000/admin/`
2. Inicia sesión con superuser
3. Ve a: **Carrito**
4. Deberías ver el carrito de `testuser` con 2 items

---

## ✅ CHECKLIST DE PRUEBAS

- [ ] Usuario creado exitosamente
- [ ] Servidor Django corriendo
- [ ] Script PowerShell ejecutado sin errores
- [ ] Token obtenido
- [ ] Carrito obtenido (vacío)
- [ ] Producto agregado
- [ ] Carrito actualizado
- [ ] Frontend sincronizado
- [ ] Admin muestra carrito

---

## 🐛 TROUBLESHOOTING

### Error: "Credenciales inválidas"
- Verifica que el usuario existe: `python manage.py shell`
- Crea el usuario: `python manage.py createsuperuser`

### Error: "No es posible conectar con el servidor remoto"
- Verifica que Django está corriendo: `python manage.py runserver`
- Verifica que el puerto es 8000

### Error: "Token no proporcionado"
- Verifica que el token es válido
- Verifica que el header es: `Authorization: Bearer TOKEN`

### Error: "Producto no encontrado"
- Verifica que el producto ID 1 existe
- Ve a admin y crea un producto si es necesario

---

## 🎉 ¡LISTO!

Todos los endpoints funcionando correctamente. 🚀

¡Adelante con el checkout! 🎉
