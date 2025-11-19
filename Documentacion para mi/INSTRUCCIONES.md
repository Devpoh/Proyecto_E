# 🔌 Electro Isla - Instrucciones de Configuración

## 📋 Requisitos Previos
- Python 3.8+
- Node.js 18+
- WAMP Server instalado y corriendo
- MySQL corriendo en WAMP

---

## 🗄️ Paso 1: Crear la Base de Datos en MySQL

1. Abre WAMP y asegúrate que esté corriendo (ícono verde)
2. Ve a `http://localhost/phpmyadmin`
3. Crea una nueva base de datos llamada `electro_isla`
4. Usa el charset `utf8mb4_general_ci`

---

## 🐍 Paso 2: Configurar y Ejecutar el Backend (Django)

Abre PowerShell o CMD en la carpeta del proyecto y ejecuta:

```powershell
# Navegar a la carpeta backend
cd c:\Users\Alejandro\Desktop\Electro-Isla\backend

# Activar el entorno virtual
venv\Scripts\activate

# Crear las migraciones
python manage.py makemigrations

# Aplicar las migraciones a MySQL
python manage.py migrate

# (Opcional) Crear un superusuario para el admin de Django
python manage.py createsuperuser

# Ejecutar el servidor
python manage.py runserver
```

El backend estará corriendo en: `http://localhost:8000`

---

## ⚛️ Paso 3: Ejecutar el Frontend (React)

Abre otra terminal PowerShell o CMD y ejecuta:

```powershell
# Navegar a la carpeta del frontend
cd c:\Users\Alejandro\Desktop\Electro-Isla\frontend\electro_isla

# Instalar dependencias (solo la primera vez)
npm install

# Ejecutar el servidor de desarrollo
npm run dev
```

El frontend estará corriendo en: `http://localhost:5173`

---

## ✅ Paso 4: Probar la Conexión

1. Abre tu navegador en `http://localhost:5173`
2. Verás un formulario para agregar nombres
3. Ingresa un nombre y haz clic en "Guardar en MySQL"
4. Si todo está bien, verás un mensaje de éxito ✅
5. Haz clic en "Cargar Personas de la BD" para ver los datos guardados

---

## 🔍 Verificar en MySQL

Puedes verificar que los datos se guardaron en MySQL:

1. Ve a `http://localhost/phpmyadmin`
2. Selecciona la base de datos `electro_isla`
3. Abre la tabla `personas`
4. Verás los nombres que agregaste desde el frontend

---

## 🛠️ Panel de Administración de Django

Puedes acceder al panel de administración de Django en:
`http://localhost:8000/admin`

Usa las credenciales del superusuario que creaste.

---

## 📡 Endpoints de la API

- **GET** `http://localhost:8000/api/personas/` - Listar todas las personas
- **POST** `http://localhost:8000/api/personas/` - Crear una nueva persona
- **GET** `http://localhost:8000/api/personas/{id}/` - Obtener una persona
- **PUT** `http://localhost:8000/api/personas/{id}/` - Actualizar una persona
- **DELETE** `http://localhost:8000/api/personas/{id}/` - Eliminar una persona

---

## 🚨 Solución de Problemas

### Error de conexión a MySQL
- Verifica que WAMP esté corriendo
- Verifica que la base de datos `electro_isla` exista
- Revisa las credenciales en el archivo `.env`

### Error de CORS
- Asegúrate que el backend esté corriendo en el puerto 8000
- Verifica que el frontend esté en el puerto 5173

### Error al instalar mysqlclient
Si tienes problemas instalando `mysqlclient`, intenta:
```powershell
pip install mysqlclient==2.2.0
```

Si persiste el error, descarga el wheel desde:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient

---

## 📁 Estructura del Proyecto

```
Electro-Isla/
├── backend/
│   ├── api/                 # App de Django
│   │   ├── models.py       # Modelo Persona
│   │   ├── serializers.py  # Serializer para la API
│   │   ├── views.py        # ViewSet de la API
│   │   └── urls.py         # URLs de la API
│   ├── config/             # Configuración de Django
│   │   ├── settings.py     # Configuración principal
│   │   └── urls.py         # URLs principales
│   ├── .env                # Variables de entorno
│   ├── manage.py           # Script de Django
│   └── requirements.txt    # Dependencias de Python
│
└── frontend/
    └── electro_isla/
        ├── src/
        │   └── App.tsx     # Componente principal con formulario
        └── package.json    # Dependencias de Node
```

---

## 🎉 ¡Listo!

Tu proyecto fullstack está configurado y funcionando:
- ✅ Frontend: React + Vite + TypeScript
- ✅ Backend: Django + Python + REST Framework
- ✅ Base de datos: MySQL en WAMP Server
- ✅ Conexión completa entre frontend y backend
