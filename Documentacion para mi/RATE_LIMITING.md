# 🚦 Sistema de Rate Limiting - Protección contra Fuerza Bruta

## ✅ Implementación Completada

Se ha implementado un sistema de **rate limiting** para proteger los endpoints de autenticación contra ataques de fuerza bruta y abuso.

---

## 📋 Características

### 1. **Límites Configurados**
- ⏱️ **Ventana de tiempo**: 1 minuto
- 🔢 **Intentos permitidos**: 5 intentos fallidos
- 🔒 **Duración del bloqueo**: 60 segundos
- 📍 **Identificación**: Por dirección IP

### 2. **Endpoints Protegidos**
- ✅ `/api/auth/login/` - Inicio de sesión
- ✅ `/api/auth/register/` - Registro de usuarios

### 3. **Auditoría Completa**
- ✅ Registro de cada intento (exitoso o fallido)
- ✅ Almacenamiento de IP y User-Agent
- ✅ Timestamp de cada intento
- ✅ Limpieza automática de registros antiguos

---

## 🗄️ Modelo de Base de Datos

### Tabla: `login_attempts`

```sql
CREATE TABLE login_attempts (
    id SERIAL PRIMARY KEY,
    ip_address INET NOT NULL,
    username VARCHAR(150),
    attempt_type VARCHAR(20) NOT NULL,  -- 'login' o 'register'
    success BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT NOW(),
    user_agent VARCHAR(500),
    INDEX idx_ip_timestamp (ip_address, timestamp),
    INDEX idx_username_timestamp (username, timestamp)
);
```

### Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `ip_address` | GenericIPAddress | IP del cliente |
| `username` | CharField(150) | Usuario que intentó autenticarse |
| `attempt_type` | CharField(20) | Tipo: 'login' o 'register' |
| `success` | Boolean | Si el intento fue exitoso |
| `timestamp` | DateTime | Fecha y hora del intento |
| `user_agent` | CharField(500) | Navegador/dispositivo |

---

## 🔧 Métodos del Modelo

### `LoginAttempt.registrar_intento()`
Registra un intento de login/registro.

```python
LoginAttempt.registrar_intento(
    ip_address='192.168.1.100',
    username='usuario123',
    attempt_type='login',
    success=False,
    user_agent='Mozilla/5.0...'
)
```

### `LoginAttempt.contar_intentos_fallidos()`
Cuenta intentos fallidos en una ventana de tiempo.

```python
# Contar intentos en el último minuto
count = LoginAttempt.contar_intentos_fallidos(
    ip_address='192.168.1.100',
    attempt_type='login',
    minutos=1
)
```

### `LoginAttempt.esta_bloqueado()`
Verifica si una IP está bloqueada.

```python
bloqueado = LoginAttempt.esta_bloqueado(
    ip_address='192.168.1.100',
    attempt_type='login',
    max_intentos=5,
    minutos=1
)
```

### `LoginAttempt.tiempo_restante_bloqueo()`
Retorna los segundos restantes de bloqueo.

```python
segundos = LoginAttempt.tiempo_restante_bloqueo(
    ip_address='192.168.1.100',
    attempt_type='login',
    minutos=1
)
# Retorna: 45 (segundos restantes)
```

### `LoginAttempt.limpiar_intentos_antiguos()`
Elimina intentos de más de N días.

```python
# Eliminar intentos de más de 7 días
count = LoginAttempt.limpiar_intentos_antiguos(dias=7)
```

---

## 🌐 Respuesta del Backend

### Cuando el usuario está bloqueado (HTTP 429)

```json
{
  "error": "Demasiados intentos de inicio de sesión",
  "bloqueado": true,
  "tiempo_restante": 45,
  "mensaje": "Has excedido el límite de intentos. Intenta de nuevo en 45 segundos."
}
```

### Cuando el intento falla (HTTP 401)

```json
{
  "error": "Credenciales inválidas"
}
```

---

## 🎨 Componente Frontend - RateLimitBlock

### Características

- ⏱️ **Contador regresivo en tiempo real**
- 🎨 **Diseño moderno y profesional**
- 📱 **Responsive**
- ♿ **Accesible**
- 🔄 **Auto-desbloqueo cuando expira el tiempo**

### Uso en Login

```tsx
import { RateLimitBlock } from '@/features/auth/components/RateLimitBlock';

// En el componente
if (rateLimitInfo?.bloqueado) {
  return (
    <RateLimitBlock
      tiempoRestante={rateLimitInfo.tiempo_restante}
      tipo="login"
      onDesbloquear={clearRateLimit}
    />
  );
}
```

### Uso en Register

```tsx
if (rateLimitInfo?.bloqueado) {
  return (
    <RateLimitBlock
      tiempoRestante={rateLimitInfo.tiempo_restante}
      tipo="register"
      onDesbloquear={clearRateLimit}
    />
  );
}
```

---

## 🔄 Flujo Completo

```
1. Usuario intenta login con credenciales incorrectas
   ↓
2. Backend verifica si la IP está bloqueada
   ↓
3. Si NO está bloqueada:
   - Registra el intento fallido
   - Retorna error 401
   ↓
4. Usuario intenta nuevamente (2da, 3ra, 4ta, 5ta vez)
   ↓
5. En el 5to intento fallido:
   - Backend detecta que se alcanzó el límite
   - Retorna error 429 con tiempo_restante
   ↓
6. Frontend detecta error 429
   - Oculta el formulario
   - Muestra componente RateLimitBlock
   - Inicia contador regresivo
   ↓
7. Después de 60 segundos:
   - Componente se auto-desbloquea
   - Muestra el formulario nuevamente
   - Usuario puede intentar de nuevo
```

---

## 🧪 Pruebas

### Probar manualmente

1. Intenta hacer login 5 veces con credenciales incorrectas
2. Verifica que aparezca el componente de bloqueo
3. Espera 60 segundos
4. Verifica que se desbloquee automáticamente

### Probar desde código

```python
from api.models import LoginAttempt

# Simular 5 intentos fallidos
for i in range(5):
    LoginAttempt.registrar_intento(
        ip_address='127.0.0.1',
        username='test',
        attempt_type='login',
        success=False
    )

# Verificar si está bloqueado
bloqueado = LoginAttempt.esta_bloqueado('127.0.0.1', 'login')
print(f"Bloqueado: {bloqueado}")  # True

# Ver tiempo restante
tiempo = LoginAttempt.tiempo_restante_bloqueo('127.0.0.1', 'login')
print(f"Tiempo restante: {tiempo} segundos")
```

---

## 🛡️ Seguridad

### Protección Implementada

- ✅ **Fuerza bruta**: Limita intentos por IP
- ✅ **DDoS básico**: Bloqueo temporal por IP
- ✅ **Auditoría**: Registro de todos los intentos
- ✅ **Limpieza automática**: Elimina registros antiguos

### Limitaciones

- ⚠️ **IP compartidas**: Usuarios detrás del mismo NAT comparten límite
- ⚠️ **VPN/Proxy**: Atacantes pueden cambiar de IP
- ⚠️ **Distributed attacks**: No protege contra ataques distribuidos

### Mejoras Futuras

- 🔄 Rate limiting por usuario (además de IP)
- 🌍 Detección de IPs sospechosas (geolocalización)
- 📧 Notificaciones de intentos sospechosos
- 🔐 CAPTCHA después de N intentos
- 🚫 Lista negra de IPs

---

## 📊 Monitoreo

### Ver intentos recientes

```python
from api.models import LoginAttempt
from django.utils import timezone
from datetime import timedelta

# Últimos 10 intentos
intentos = LoginAttempt.objects.all()[:10]
for intento in intentos:
    print(f"{intento.timestamp} - {intento.ip_address} - {intento.username} - {'✓' if intento.success else '✗'}")
```

### Ver IPs bloqueadas actualmente

```python
from django.utils import timezone
from datetime import timedelta

# IPs con 5+ intentos fallidos en el último minuto
desde = timezone.now() - timedelta(minutes=1)
ips_bloqueadas = LoginAttempt.objects.filter(
    success=False,
    timestamp__gte=desde
).values('ip_address').annotate(
    count=models.Count('id')
).filter(count__gte=5)

for ip in ips_bloqueadas:
    print(f"IP bloqueada: {ip['ip_address']} ({ip['count']} intentos)")
```

---

## 🧹 Limpieza Automática

### Comando Manual

```bash
python manage.py limpiar_tokens
```

Este comando limpia:
- ✅ Tokens de refresco expirados
- ✅ Intentos de login de más de 7 días

### Tarea Programada (Automática)

#### Windows

1. Abre PowerShell como Administrador
2. Navega a la carpeta del backend
3. Ejecuta:

```powershell
.\configurar_tarea_programada.ps1
```

Esto creará una tarea que se ejecuta **diariamente a las 3:00 AM**.

#### Linux/Mac (Cron)

Edita el crontab:

```bash
crontab -e
```

Agrega:

```cron
# Limpiar tokens diariamente a las 3:00 AM
0 3 * * * cd /ruta/al/proyecto && python manage.py limpiar_tokens >> logs/limpieza.log 2>&1
```

---

## 📝 Logs

Los logs de limpieza automática se guardan en:

```
backend/logs/limpieza_tokens.log
```

Ejemplo de log:

```
🧹 Iniciando limpieza...
  → Limpiando tokens expirados...
    ✓ Se eliminaron 15 tokens expirados
  → Limpiando intentos de login antiguos...
    ✓ Se eliminaron 342 intentos de login antiguos

✅ Limpieza completada exitosamente
```

---

## ⚙️ Configuración

### Cambiar límites

En `api/views.py`:

```python
# Cambiar a 10 intentos en 5 minutos
if LoginAttempt.esta_bloqueado(ip_address, attempt_type='login', max_intentos=10, minutos=5):
    tiempo_restante = LoginAttempt.tiempo_restante_bloqueo(ip_address, attempt_type='login', minutos=5)
    # ...
```

### Cambiar tiempo de limpieza

En `api/models.py`:

```python
@classmethod
def limpiar_intentos_antiguos(cls, dias=30):  # Cambiar de 7 a 30 días
    fecha_limite = timezone.now() - timedelta(days=dias)
    count, _ = cls.objects.filter(timestamp__lt=fecha_limite).delete()
    return count
```

---

## ✅ Checklist de Seguridad

- [x] Rate limiting implementado en login
- [x] Rate limiting implementado en registro
- [x] Registro de intentos en base de datos
- [x] Bloqueo temporal por IP
- [x] Componente visual de bloqueo en frontend
- [x] Contador regresivo en tiempo real
- [x] Limpieza automática de registros antiguos
- [x] Tarea programada configurada
- [x] Logs de auditoría
- [x] Documentación completa

---

## 🎯 Resumen

El sistema de rate limiting protege tu aplicación contra:

- ✅ **Ataques de fuerza bruta**
- ✅ **Intentos masivos de login**
- ✅ **Spam de registros**
- ✅ **Abuso de endpoints**

Con una experiencia de usuario clara y profesional que informa al usuario exactamente qué está pasando y cuándo podrá intentar nuevamente.
