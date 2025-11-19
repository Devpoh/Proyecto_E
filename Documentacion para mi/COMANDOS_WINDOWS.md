# 🪟 Comandos para Windows PowerShell

## Problema
En Windows PowerShell, `curl` es un alias de `Invoke-WebRequest`, que tiene sintaxis diferente a bash.

---

## Solución 1: Usar PowerShell Nativo (Recomendado)

### Obtener CSRF Token
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/auth/csrf-token/" -Method GET
```

### Login
```powershell
$body = @{
    username = "admin"
    password = "tu-contraseña"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/api/auth/login/" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body
```

### Logout
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/auth/logout/" `
  -Method POST `
  -Headers @{
    "Authorization"="Bearer <tu-token-aqui>"
    "Content-Type"="application/json"
  }
```

---

## Solución 2: Instalar curl Real (Mejor)

### Opción A: Usar Git Bash (Si tienes Git instalado)
```powershell
# Abre Git Bash en lugar de PowerShell
# Luego usa los comandos curl normales
```

### Opción B: Instalar curl con Chocolatey
```powershell
# Si tienes Chocolatey instalado
choco install curl

# Luego reinicia PowerShell y usa curl normalmente
```

### Opción C: Instalar curl Manualmente
1. Descarga curl desde: https://curl.se/download.html
2. Extrae el archivo
3. Agrega la ruta a la variable PATH de Windows

---

## Solución 3: Usar Python (Más Fácil)

### Crear archivo `test_api.py`
```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

# 1. Obtener CSRF Token
print("1. Obteniendo CSRF Token...")
response = requests.get(f"{BASE_URL}/auth/csrf-token/")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")

# 2. Login
print("2. Haciendo Login...")
login_data = {
    "username": "admin",
    "password": "tu-contraseña"
}
response = requests.post(
    f"{BASE_URL}/auth/login/",
    json=login_data,
    headers={"Content-Type": "application/json"}
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}\n")

if response.status_code == 200:
    access_token = response.json()["accessToken"]
    
    # 3. Logout
    print("3. Haciendo Logout...")
    response = requests.post(
        f"{BASE_URL}/auth/logout/",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")
```

### Ejecutar Script
```powershell
python test_api.py
```

---

## Solución 4: Usar Postman (Interfaz Gráfica)

1. Descarga Postman: https://www.postman.com/downloads/
2. Crea una nueva colección
3. Agrega requests:
   - GET `http://localhost:8000/api/auth/csrf-token/`
   - POST `http://localhost:8000/api/auth/login/`
   - POST `http://localhost:8000/api/auth/logout/`

---

## Acceder a Admin Panel

### Opción 1: Abrir en Navegador
```powershell
# Simplemente abre tu navegador y ve a:
# http://localhost:8000/admin/
```

### Opción 2: Desde PowerShell
```powershell
# Abrir en navegador por defecto
Start-Process "http://localhost:8000/admin/"
```

---

## Migraciones en Windows

### Crear Migraciones
```powershell
python manage.py makemigrations
```

### Ejecutar Migraciones
```powershell
python manage.py migrate
```

### Ver Estado de Migraciones
```powershell
python manage.py showmigrations
```

---

## Crear Carpeta de Logs

```powershell
# Crear carpeta
New-Item -ItemType Directory -Force -Path "logs"

# Verificar que se creó
Get-Item logs
```

---

## Comandos Útiles en PowerShell

### Cambiar Directorio
```powershell
cd backend
```

### Activar Entorno Virtual
```powershell
venv\Scripts\Activate.ps1

# Si da error de permisos, ejecuta:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Luego intenta de nuevo
```

### Ejecutar Servidor Django
```powershell
python manage.py runserver
```

### Ver Logs en Tiempo Real
```powershell
# Security log
Get-Content -Path "logs/security.log" -Wait

# Auth log
Get-Content -Path "logs/auth.log" -Wait

# Presiona Ctrl+C para salir
```

### Buscar en Logs
```powershell
# Buscar LOGIN_FAILED
Select-String -Path "logs/security.log" -Pattern "LOGIN_FAILED"

# Buscar LOGOUT_SUCCESS
Select-String -Path "logs/auth.log" -Pattern "LOGOUT_SUCCESS"
```

---

## Recomendación Final

**Usa Python para probar la API** - Es más fácil y funciona igual en Windows, macOS y Linux:

```powershell
# 1. Crea el archivo test_api.py (ver arriba)
# 2. Ejecuta:
python test_api.py

# 3. Verás la salida clara y formateada
```

O **instala Git Bash** para usar comandos curl normales.
