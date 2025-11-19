# 🚀 Setup Backend - Electro Isla

## Requisitos Previos

- Python 3.8+
- PostgreSQL 12+ (o MySQL 8+)
- pip (gestor de paquetes de Python)
- virtualenv (entorno virtual)

---

## 1. Instalación

### Paso 1: Crear Entorno Virtual
```bash
cd backend
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

### Paso 2: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 3: Crear Archivo .env
```bash
cp .env.example .env
```

Editar `.env` con tus configuraciones:
```env
# Django
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=electro_isla
DB_USER=postgres
DB_PASSWORD=tu-contraseña
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# JWT
JWT_SECRET_KEY=tu-clave-jwt-aqui
JWT_ALGORITHM=HS256
```

### Paso 4: Crear Migraciones
```bash
python manage.py makemigrations
```

### Paso 5: Ejecutar Migraciones
```bash
python manage.py migrate
```

### Paso 6: Crear Carpeta de Logs
```bash
mkdir -p logs
```

### Paso 7: Crear Superusuario
```bash
python manage.py createsuperuser
```

Ingresa:
- Username: `admin`
- Email: `admin@example.com`
- Password: `tu-contraseña-segura`

---

## 2. Ejecutar Servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://localhost:8000`

Panel de admin: `http://localhost:8000/admin/`

---

## 3. Verificar Instalación

### Probar Endpoints

**Obtener CSRF Token:**
```bash
curl -X GET http://localhost:8000/api/auth/csrf-token/
```

**Registro:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "TestPassword123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "TestPassword123"
  }'
```

---

## 4. Migraciones de Seguridad

### Crear Migraciones para TokenBlacklist

```bash
python manage.py makemigrations api
```

Verifica que se cree una migración para `TokenBlacklist`:
```
Migrations for 'api':
  api/migrations/XXXX_auto_YYYYMMDD_HHMM.py
    - Create model TokenBlacklist
```

### Ejecutar Migraciones

```bash
python manage.py migrate
```

Verifica que se ejecute correctamente:
```
Running migrations:
  ...
  api.XXXX_auto_YYYYMMDD_HHMM ... OK
```

---

## 5. Verificar Admin Panel

1. Acceder a: `http://localhost:8000/admin/`
2. Ingresar con superusuario (admin)
3. Verificar que aparezca "Token Blacklists" en la sección "API"

---

## 6. Verificar Logs

### Crear Logs de Prueba

```bash
# Login exitoso
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"tu-contraseña"}'

# Ver logs
tail -f logs/auth.log
tail -f logs/security.log
```

---

## 7. Limpiar Tokens Expirados

### Ejecutar Comando Manualmente

```bash
python manage.py limpiar_tokens
```

### Programar Ejecución Diaria (Cron)

En Linux/macOS:
```bash
# Editar crontab
crontab -e

# Agregar línea (ejecutar a las 2 AM diariamente)
0 2 * * * cd /ruta/backend && /ruta/venv/bin/python manage.py limpiar_tokens
```

En Windows (Programador de Tareas):
```
Crear tarea programada:
- Programa: C:\ruta\venv\Scripts\python.exe
- Argumentos: C:\ruta\backend\manage.py limpiar_tokens
- Horario: 2:00 AM diariamente
```

---

## 8. Configuración de Producción

### Variables de Entorno

```env
# Django
SECRET_KEY=clave-secreta-muy-larga-y-aleatoria
DEBUG=False
ALLOWED_HOSTS=electro-isla.com,www.electro-isla.com

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=electro_isla_prod
DB_USER=postgres
DB_PASSWORD=contraseña-muy-segura
DB_HOST=db.electro-isla.com
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=https://electro-isla.com,https://www.electro-isla.com

# HTTPS
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

### Recolectar Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### Ejecutar con Gunicorn

```bash
pip install gunicorn

gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 9. Troubleshooting

### Error: "No module named 'django'"
```bash
# Asegúrate de que el entorno virtual esté activado
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstala dependencias
pip install -r requirements.txt
```

### Error: "Database connection refused"
```bash
# Verifica que PostgreSQL esté corriendo
# macOS:
brew services start postgresql

# Linux:
sudo systemctl start postgresql

# Windows:
# Iniciar PostgreSQL desde Servicios
```

### Error: "CSRF token missing"
```bash
# Obtener CSRF token
curl -X GET http://localhost:8000/api/auth/csrf-token/

# Incluir en header X-CSRFToken
```

### Error: "Token expirado"
```bash
# Refrescar token automáticamente
POST /api/auth/refresh/

# O hacer login nuevamente
```

---

## 10. Documentación

- **Autenticación:** Ver `docs/AUTHENTICATION.md`
- **API Endpoints:** Ver `docs/` (próximamente)
- **Modelos:** Ver `api/models.py`
- **Serializers:** Ver `api/serializers.py`

---

## 11. Comandos Útiles

```bash
# Crear superusuario
python manage.py createsuperuser

# Crear usuario regular
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.create_user('username', 'email@example.com', 'password')

# Limpiar tokens expirados
python manage.py limpiar_tokens --dias 31

# Ver migraciones
python manage.py showmigrations

# Ejecutar migraciones específicas
python manage.py migrate api 0001

# Revertir migraciones
python manage.py migrate api zero

# Crear dump de base de datos
python manage.py dumpdata > backup.json

# Cargar dump de base de datos
python manage.py loaddata backup.json

# Shell interactivo
python manage.py shell

# Ejecutar tests
python manage.py test

# Verificar configuración
python manage.py check
```

---

## 12. Monitoreo

### Ver Logs en Tiempo Real

```bash
# Security log
tail -f logs/security.log

# Auth log
tail -f logs/auth.log

# Ambos
tail -f logs/*.log
```

### Buscar Eventos Específicos

```bash
# Intentos de login fallidos
grep "LOGIN_FAILED" logs/security.log

# Logout exitosos
grep "LOGOUT_SUCCESS" logs/auth.log

# Tokens invalidados
grep "BLACKLIST" logs/security.log

# Errores
grep "ERROR" logs/*.log
```

---

## 13. Seguridad

### Cambiar SECRET_KEY

```bash
# Generar nueva clave
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Actualizar en .env
SECRET_KEY=nueva-clave-aqui
```

### Cambiar Contraseña de Superusuario

```bash
python manage.py changepassword admin
```

### Verificar Configuración de Seguridad

```bash
python manage.py check --deploy
```

---

## 14. Soporte

Para reportar problemas o sugerencias, contactar al equipo de desarrollo.
