# 👤 CREAR USUARIO DE PRUEBA

**Fecha:** 7 de Noviembre, 2025  
**Status:** ✅ **INSTRUCCIONES PASO A PASO**

---

## 🎯 OBJETIVO

Crear un usuario de prueba para probar los endpoints del carrito.

---

## 📝 OPCIÓN 1: Crear Superuser (Recomendado)

### Paso 1: Abre PowerShell en la carpeta backend

```powershell
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
```

### Paso 2: Ejecuta el comando

```powershell
python manage.py createsuperuser
```

### Paso 3: Completa los datos

```
Username: testuser
Email: testuser@example.com
Password: testpass123
Password (again): testpass123
```

---

## 📝 OPCIÓN 2: Usar Script Existente

Si existe `create_test_user.py`:

```powershell
python create_test_user.py
```

---

## 📝 OPCIÓN 3: Crear Usuario por API

### Paso 1: Obtén CSRF Token

```powershell
$csrfResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/csrf-token/" `
    -Method GET

$csrfToken = $csrfResponse.csrfToken
Write-Host "CSRF Token: $csrfToken"
```

### Paso 2: Registra Usuario

```powershell
$registerBody = @{
    username = "testuser"
    email = "testuser@example.com"
    password = "testpass123"
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

$registerResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register/" `
    -Method POST `
    -Headers @{
        "Content-Type" = "application/json"
        "X-CSRFToken" = $csrfToken
    } `
    -Body $registerBody

Write-Host "Usuario creado: $($registerResponse.username)"
```

---

## ✅ VERIFICAR USUARIO

### Opción 1: Admin Django

1. Ve a: `http://localhost:8000/admin/`
2. Inicia sesión con superuser
3. Ve a: "Users" → Deberías ver `testuser`

### Opción 2: Por API

```powershell
$loginResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login/" `
    -Method POST `
    -Headers @{"Content-Type" = "application/json"} `
    -Body '{"username":"testuser","password":"testpass123"}'

Write-Host "Token: $($loginResponse.access_token)"
```

---

## 🧪 PROBAR CON EL USUARIO

Una vez creado el usuario, ejecuta:

```powershell
# En la carpeta backend
.\test_carrito.ps1
```

---

## 📊 CREDENCIALES POR DEFECTO

```
Username: testuser
Password: testpass123
Email: testuser@example.com
```

---

## ✨ LISTO

Usuario creado y listo para probar. 🚀
