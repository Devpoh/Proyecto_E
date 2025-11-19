# ⚡ Electro Isla - E-commerce de Electrónica

> Plataforma de comercio electrónico completa con panel de administración profesional

[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue.svg)](https://www.typescriptlang.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8-orange.svg)](https://www.mysql.com/)

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Tecnologías](#-tecnologías)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [API Endpoints](#-api-endpoints)
- [Roles y Permisos](#-roles-y-permisos)
- [Capturas de Pantalla](#-capturas-de-pantalla)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## ✨ Características

### **🛒 E-commerce**
- Catálogo de productos con categorías
- Búsqueda y filtros avanzados
- Carrito de compras
- Proceso de checkout
- Historial de pedidos

### **👥 Gestión de Usuarios**
- Registro y autenticación (JWT)
- Perfiles de usuario
- Sistema de roles (Admin, Trabajador, Mensajero, Cliente)
- Privacidad de datos (emails parcialmente ocultos)

### **📦 Gestión de Productos**
- CRUD completo
- Control de stock
- Categorías: Laptops, Smartphones, Accesorios, Gaming
- Imágenes de productos
- Activar/desactivar productos

### **🚚 Gestión de Pedidos**
- Estados: Pendiente, Confirmado, En Preparación, En Camino, Entregado, Cancelado
- Asignación de mensajeros
- Métodos de pago: Efectivo, Tarjeta, Transferencia
- Notificaciones automáticas

### **🔔 Sistema de Notificaciones**
- Notificaciones en tiempo real
- Tipos: Info, Success, Warning, Error
- Marcar como leída
- Contador de no leídas

### **📊 Estadísticas Avanzadas**
- Ventas por mes (12 meses)
- Productos más vendidos
- Crecimiento de usuarios
- Tasa de retención
- Stock bajo
- Valor del inventario

### **📄 Exportación de Reportes**
- Reporte completo en JSON
- Listo para PDF/Excel

---

## 🛠️ Tecnologías

### **Backend**
- **Django 4.2** - Framework web
- **Django REST Framework** - API REST
- **MySQL 8** - Base de datos
- **JWT** - Autenticación
- **Python 3.11** - Lenguaje

### **Frontend**
- **React 18** - Biblioteca UI
- **TypeScript 5** - Tipado estático
- **Vite** - Build tool
- **React Query** - Gestión de estado servidor
- **Zustand** - Gestión de estado global
- **Axios** - Cliente HTTP
- **React Router** - Enrutamiento

### **Diseño**
- **CSS Modules** - Estilos encapsulados
- **Diseño Apple/iOS** - Principios de diseño
- **Responsive** - Mobile-first
- **Animaciones suaves** - 60fps

---

## 🚀 Instalación

### **Requisitos Previos**
- Python 3.11+
- Node.js 18+
- MySQL 8+
- Git

### **1. Clonar Repositorio**
```bash
git clone https://github.com/tu-usuario/electro-isla.git
cd electro-isla
```

### **2. Configurar Backend**

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos en .env
# Copiar .env.example a .env y configurar

# Crear migraciones
python manage.py makemigrations
python manage.py migrate

# Asegurar perfiles de usuario
python manage.py ensure_profiles

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

### **3. Configurar Frontend**

```bash
cd frontend/electro_isla

# Instalar dependencias
npm install

# Iniciar desarrollo
npm run dev
```

### **4. Acceder a la Aplicación**

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000/api
- **Django Admin:** http://localhost:8000/admin

---

## 📖 Uso

### **Crear Superusuario Admin**

```bash
cd backend
python manage.py createsuperuser
```

**Datos sugeridos:**
- Username: `admin`
- Email: `admin@electroisla.com`
- Password: (tu contraseña segura)

El superusuario automáticamente tendrá rol **admin**.

### **Asegurar Perfiles**

```bash
python manage.py ensure_profiles
```

Este comando crea perfiles para usuarios existentes y asegura que superusuarios tengan rol admin.

### **Acceder al Panel de Admin**

1. Ir a http://localhost:5173/login
2. Iniciar sesión con tu superusuario
3. Click en el avatar (primera letra de tu nombre)
4. Click en "Panel de Administración"

---

## 📁 Estructura del Proyecto

```
electro-isla/
├── backend/                    # Backend Django
│   ├── api/                   # App principal
│   │   ├── models.py         # Modelos (UserProfile, Producto, Pedido, etc.)
│   │   ├── serializers_admin.py  # Serializers con privacidad
│   │   ├── views_admin.py    # Vistas de admin
│   │   ├── views_pedidos.py  # Vistas de pedidos
│   │   ├── views_estadisticas.py  # Estadísticas
│   │   ├── urls.py           # Rutas
│   │   └── management/       # Comandos personalizados
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/                   # Frontend React
│   └── electro_isla/
│       └── src/
│           ├── app/           # Configuración
│           ├── pages/         # Páginas
│           │   ├── admin/    # Panel de admin
│           │   └── auth/     # Autenticación
│           ├── widgets/       # Componentes complejos
│           ├── features/      # Funcionalidades
│           ├── entities/      # Entidades
│           └── shared/        # Código compartido
│
├── RESUMEN_COMPLETO.md        # Documentación completa
├── SETUP_ADMIN.md             # Guía de configuración
└── README.md                  # Este archivo
```

---

## 🔌 API Endpoints

### **Autenticación**
```
POST   /api/auth/register/     # Registrar usuario
POST   /api/auth/login/        # Iniciar sesión
POST   /api/auth/logout/       # Cerrar sesión
```

### **Usuarios (Admin)**
```
GET    /api/admin/users/              # Listar usuarios
GET    /api/admin/users/{id}/         # Detalle de usuario
PATCH  /api/admin/users/{id}/         # Actualizar usuario
DELETE /api/admin/users/{id}/         # Eliminar usuario
GET    /api/admin/users/stats/        # Estadísticas
```

### **Productos (Admin)**
```
GET    /api/admin/productos/          # Listar productos
POST   /api/admin/productos/          # Crear producto
GET    /api/admin/productos/{id}/     # Detalle de producto
PATCH  /api/admin/productos/{id}/     # Actualizar producto
DELETE /api/admin/productos/{id}/     # Eliminar producto
GET    /api/admin/productos/stats/    # Estadísticas
```

### **Pedidos (Admin)**
```
GET    /api/admin/pedidos/                      # Listar pedidos
POST   /api/admin/pedidos/                      # Crear pedido
GET    /api/admin/pedidos/{id}/                 # Detalle de pedido
PATCH  /api/admin/pedidos/{id}/                 # Actualizar pedido
DELETE /api/admin/pedidos/{id}/                 # Eliminar pedido
POST   /api/admin/pedidos/{id}/asignar_mensajero/  # Asignar mensajero
GET    /api/admin/pedidos/stats/                # Estadísticas
```

### **Notificaciones**
```
GET    /api/notificaciones/                    # Listar notificaciones
GET    /api/notificaciones/{id}/               # Detalle
POST   /api/notificaciones/{id}/marcar_leida/  # Marcar como leída
POST   /api/notificaciones/marcar_todas_leidas/  # Marcar todas
GET    /api/notificaciones/no_leidas/          # Contador
```

### **Estadísticas (Admin)**
```
GET /api/admin/dashboard/stats/           # Dashboard general
GET /api/admin/estadisticas/ventas/       # Estadísticas de ventas
GET /api/admin/estadisticas/usuarios/     # Estadísticas de usuarios
GET /api/admin/estadisticas/productos/    # Estadísticas de productos
GET /api/admin/estadisticas/reporte/      # Reporte completo
```

---

## 🔐 Roles y Permisos

| Funcionalidad | Admin | Trabajador | Mensajero | Cliente |
|--------------|-------|------------|-----------|---------|
| **Dashboard** | ✅ | ✅ | ✅ | ❌ |
| **Ver Usuarios** | ✅ | ✅ | ❌ | ❌ |
| **Editar Usuarios** | ✅ | ✅ (no admins) | ❌ | ❌ |
| **Eliminar Usuarios** | ✅ | ❌ | ❌ | ❌ |
| **Ver Productos** | ✅ | ✅ | ✅ | ✅ |
| **Crear Productos** | ✅ | ✅ | ❌ | ❌ |
| **Editar Productos** | ✅ | ✅ | ❌ | ❌ |
| **Eliminar Productos** | ✅ | ❌ | ❌ | ❌ |
| **Ver Pedidos** | ✅ Todos | ✅ Todos | ✅ Asignados | ✅ Propios |
| **Editar Pedidos** | ✅ | ✅ | ✅ Estado | ❌ |
| **Asignar Mensajeros** | ✅ | ✅ | ❌ | ❌ |
| **Estadísticas** | ✅ | ✅ | ❌ | ❌ |
| **Exportar Reportes** | ✅ | ✅ | ❌ | ❌ |

---

## 🔒 Seguridad

### **Implementado:**
- ✅ JWT con expiración (15 minutos)
- ✅ Refresh tokens (7 días)
- ✅ Hashing de contraseñas (PBKDF2)
- ✅ Validación OWASP (12 caracteres mínimo)
- ✅ Rate limiting (5 intentos/minuto)
- ✅ CORS estricto
- ✅ Permisos por rol
- ✅ Emails parcialmente ocultos
- ✅ Validación en backend
- ✅ Protección XSS
- ✅ Protección CSRF

---

## 📸 Capturas de Pantalla

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Gestión de Usuarios
![Usuarios](docs/screenshots/usuarios.png)

### Gestión de Productos
![Productos](docs/screenshots/productos.png)

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más información.

---

## 👨‍💻 Autor

**Alejandro**
- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- Email: admin@electroisla.com

---

## 🙏 Agradecimientos

- Django REST Framework
- React Team
- Comunidad de código abierto

---

## 📚 Documentación Adicional

- [RESUMEN_COMPLETO.md](RESUMEN_COMPLETO.md) - Documentación completa del proyecto
- [SETUP_ADMIN.md](backend/SETUP_ADMIN.md) - Guía de configuración del panel de admin

---

**⚡ Electro Isla - Tu tienda de electrónica de confianza**
