# 🔧 Configuración del Panel de Admin

## 📋 Pasos para Configurar

### 1️⃣ Crear Migraciones

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 2️⃣ Asegurar Perfiles de Usuario

Este comando crea perfiles para usuarios existentes y asegura que superusuarios tengan rol admin:

```bash
python manage.py ensure_profiles
```

### 3️⃣ Crear Superusuario (si no existe)

```bash
python manage.py createsuperuser
```

**Datos sugeridos:**
- Username: `admin`
- Email: `admin@electroisla.com`
- Password: (tu contraseña segura)

El superusuario automáticamente tendrá rol **admin**.

### 4️⃣ Verificar en Django Admin

```bash
python manage.py runserver
```

Ir a: `http://localhost:8000/admin`

**Verificar:**
- ✅ User Profiles existe
- ✅ Tu superusuario tiene rol "admin"
- ✅ Modelos: Pedidos, Notificaciones, Productos

### 5️⃣ Iniciar Frontend

```bash
cd frontend/electro_isla
npm run dev
```

### 6️⃣ Acceder al Panel

1. Ir a `http://localhost:5173/login`
2. Iniciar sesión con tu superusuario
3. Click en avatar → "Panel de Administración"
4. O ir directamente a `http://localhost:5173/admin`

---

## 🎯 Endpoints Disponibles

### **Dashboard**
```
GET /api/admin/dashboard/stats/
```

### **Usuarios**
```
GET    /api/admin/users/
POST   /api/admin/users/
GET    /api/admin/users/{id}/
PATCH  /api/admin/users/{id}/
DELETE /api/admin/users/{id}/
GET    /api/admin/users/stats/
```

### **Productos**
```
GET    /api/admin/productos/
POST   /api/admin/productos/
GET    /api/admin/productos/{id}/
PATCH  /api/admin/productos/{id}/
DELETE /api/admin/productos/{id}/
GET    /api/admin/productos/stats/
```

### **Pedidos**
```
GET    /api/admin/pedidos/
POST   /api/admin/pedidos/
GET    /api/admin/pedidos/{id}/
PATCH  /api/admin/pedidos/{id}/
DELETE /api/admin/pedidos/{id}/
GET    /api/admin/pedidos/stats/
POST   /api/admin/pedidos/{id}/asignar_mensajero/
```

### **Notificaciones**
```
GET    /api/notificaciones/
GET    /api/notificaciones/{id}/
POST   /api/notificaciones/{id}/marcar_leida/
POST   /api/notificaciones/marcar_todas_leidas/
GET    /api/notificaciones/no_leidas/
```

### **Estadísticas Avanzadas**
```
GET /api/admin/estadisticas/ventas/
GET /api/admin/estadisticas/usuarios/
GET /api/admin/estadisticas/productos/
GET /api/admin/estadisticas/reporte/
```

---

## 🔐 Roles y Permisos

| Rol | Dashboard | Usuarios | Productos | Pedidos | Estadísticas |
|-----|-----------|----------|-----------|---------|--------------|
| **Admin** | ✅ | ✅ CRUD | ✅ CRUD | ✅ CRUD | ✅ |
| **Trabajador** | ✅ | ✅ Ver/Editar | ✅ CRUD | ✅ Ver/Editar | ✅ |
| **Mensajero** | ✅ | ❌ | ❌ | ✅ Solo asignados | ❌ |
| **Cliente** | ❌ | ❌ | ❌ | ✅ Solo propios | ❌ |

---

## 🚀 Funcionalidades Implementadas

### ✅ Gestión de Usuarios
- Listar con filtros (rol, estado, búsqueda)
- Email parcialmente oculto (privacidad)
- Activar/desactivar usuarios
- Eliminar usuarios (solo admin)
- Estadísticas de usuarios

### ✅ Gestión de Productos
- CRUD completo
- Filtros por categoría, estado
- Upload de imágenes (URL)
- Control de stock
- Estadísticas de productos

### ✅ Gestión de Pedidos
- Ver todos los pedidos
- Filtrar por estado, fecha
- Asignar mensajeros
- Cambiar estado
- Notificaciones automáticas
- Estadísticas de ventas

### ✅ Sistema de Notificaciones
- Notificaciones en tiempo real
- Marcar como leída
- Contador de no leídas
- Tipos: info, success, warning, error

### ✅ Estadísticas Avanzadas
- Ventas por mes (12 meses)
- Productos más vendidos
- Métodos de pago
- Crecimiento de usuarios
- Tasa de retención
- Stock bajo
- Valor del inventario

### ✅ Exportación de Reportes
- Reporte completo en JSON
- Listo para convertir a PDF/Excel

---

## 📊 Próximas Mejoras

- [ ] Gráficos interactivos (Chart.js/Recharts)
- [ ] Exportación a PDF
- [ ] Exportación a Excel
- [ ] Notificaciones push
- [ ] Chat en vivo
- [ ] Sistema de cupones
- [ ] Análisis de comportamiento

---

## 🐛 Solución de Problemas

### Error: "No module named 'api.models'"
```bash
# Asegúrate de estar en el directorio correcto
cd backend
python manage.py migrate
```

### Error: "UserProfile matching query does not exist"
```bash
# Ejecuta el comando para crear perfiles
python manage.py ensure_profiles
```

### El superusuario no tiene rol admin
```bash
# Ejecuta el comando de perfiles
python manage.py ensure_profiles
```

### No aparece el botón "Panel de Administración"
- Verifica que el usuario tenga rol: admin, trabajador o mensajero
- Cierra sesión y vuelve a iniciar
- Revisa la consola del navegador por errores

---

## 📝 Notas Importantes

1. **Seguridad**: Todos los endpoints de admin requieren autenticación
2. **Privacidad**: Los emails están parcialmente ocultos en listados
3. **Permisos**: Cada rol tiene permisos específicos validados en backend
4. **Notificaciones**: Se crean automáticamente al cambiar estado de pedidos
5. **Migraciones**: Ejecutar siempre después de cambios en modelos
