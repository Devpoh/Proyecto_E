# 🔐 Configuración de Variables de Entorno

## ⚠️ IMPORTANTE: Solucionar Warning de Clave de Encriptación

Si ves este warning en la consola:
```
⚠️ [secure-storage] VITE_STORAGE_ENCRYPTION_KEY no definida. Usando clave temporal.
```

Significa que necesitas crear tu archivo `.env` con la clave de encriptación.

---

## 📋 Pasos para Configurar

### 1️⃣ Crear el archivo `.env`

En la carpeta `Frontend/`, crea un archivo llamado `.env` (sin extensión adicional).

**Ubicación exacta:**
```
Electronica-isla-App/
└── Frontend/
    ├── .env.example  ← Este es el ejemplo
    └── .env          ← Crea este archivo
```

### 2️⃣ Copiar el contenido

Copia **TODO** el contenido del archivo `.env.example` al nuevo archivo `.env`:

```bash
# En Windows (PowerShell):
Copy-Item .env.example .env

# En Linux/Mac:
cp .env.example .env
```

### 3️⃣ Verificar la clave de encriptación

Abre el archivo `.env` y verifica que tenga esta línea:

```env
VITE_STORAGE_ENCRYPTION_KEY=8K7mN2pQ5rT9vX3wZ6yB4cF1gH8jL0nM5oP2sU7vY9aD3eG6hJ1kN4qR7tW0xZ3
```

### 4️⃣ (Opcional) Generar tu propia clave

Para mayor seguridad, puedes generar tu propia clave única:

**Opción A - Usando OpenSSL (recomendado):**
```bash
openssl rand -base64 32
```

**Opción B - Usando Node.js:**
```bash
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

**Opción C - Generador online:**
- Ve a: https://www.random.org/strings/
- Configura: 64 caracteres, alfanumérico
- Copia el resultado

Luego reemplaza el valor en tu `.env`:
```env
VITE_STORAGE_ENCRYPTION_KEY=TU_CLAVE_GENERADA_AQUI
```

### 5️⃣ Reiniciar el servidor de desarrollo

**IMPORTANTE:** Después de crear o modificar el `.env`, debes reiniciar Vite:

```bash
# Detén el servidor (Ctrl+C)
# Luego inicia nuevamente:
npm run dev
```

---

## ✅ Verificar que Funciona

Después de reiniciar, el warning **NO** debería aparecer más en la consola.

Si aún aparece, verifica:
1. ✅ El archivo se llama exactamente `.env` (no `.env.txt` ni otro nombre)
2. ✅ Está en la carpeta `Frontend/` (al mismo nivel que `package.json`)
3. ✅ La variable empieza con `VITE_` (obligatorio para Vite)
4. ✅ Reiniciaste el servidor de desarrollo

---

## 🔒 Seguridad

- ✅ El archivo `.env` está en `.gitignore` - **NO se subirá a Git**
- ✅ La clave es para encriptar datos en localStorage (temporal)
- ⚠️ En producción, cambiar a cookies HttpOnly (más seguro)
- ⚠️ Las variables `VITE_*` son públicas en el bundle final

---

## 📝 Otras Variables Importantes

Tu archivo `.env` también debe incluir:

```env
# API Backend
VITE_API_URL=http://localhost:8080/api

# OAuth (opcional - solo si usas login social)
VITE_GOOGLE_CLIENT_ID=TU_GOOGLE_CLIENT_ID_AQUI
VITE_FACEBOOK_APP_ID=TU_FACEBOOK_APP_ID_AQUI

# Modo desarrollo
VITE_DEV_MODE=true
```

---

## 🆘 Problemas Comunes

### El warning sigue apareciendo
- Asegúrate de haber **reiniciado** el servidor de desarrollo
- Verifica que el archivo se llame `.env` (sin espacios ni extensiones)
- En Windows, asegúrate de ver las extensiones de archivo

### No puedo crear un archivo que empiece con punto
- **Windows:** Usa el terminal (PowerShell o CMD) con `echo. > .env`
- **VS Code:** Crea el archivo directamente desde el explorador
- **Notepad++:** Guarda como "Todos los archivos" y escribe `.env`

### La clave no se está leyendo
- Verifica que la variable empiece con `VITE_` (obligatorio)
- Asegúrate de no tener espacios alrededor del `=`
- Reinicia el servidor de desarrollo

---

## 📚 Más Información

- [Documentación de Vite sobre Variables de Entorno](https://vitejs.dev/guide/env-and-mode.html)
- Ver archivo `.env.example` para todas las variables disponibles
