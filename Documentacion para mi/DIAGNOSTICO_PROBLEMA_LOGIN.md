# 🔍 DIAGNÓSTICO - Problema de Login Después de Reset de Contraseña

## 📋 Síntomas Reportados

- ✅ Backend: Contraseña se cambia correctamente
- ✅ Backend: Login funciona con nueva contraseña en test
- ❌ Frontend: Usuario no puede loguear con nueva contraseña
- ❌ Frontend: "Dice que está bien pero no me deja loguearme"

---

## 🔎 Análisis de Posibles Causas

### **Causa 1: Token no se está guardando en Zustand**

**Síntoma:** El usuario ve el mensaje de éxito pero no está autenticado.

**Verificación:**
```typescript
// En ResetPasswordForm.tsx línea 113
if (response.accessToken && response.user) {
  setAuthState(response.user, response.accessToken);
}
```

**Solución:**
Agregar console.log para verificar que se está guardando:
```typescript
console.log('[ResetPasswordForm] Guardando autenticación:', {
  user: response.user,
  token: response.accessToken ? 'presente' : 'ausente'
});
setAuthState(response.user, response.accessToken);
```

---

### **Causa 2: El token no se está enviando en las solicitudes posteriores**

**Síntoma:** El token se guarda pero no se envía al backend.

**Verificación:**
En `useAuthStore`, verificar que `accessToken` está disponible:
```typescript
const { accessToken } = useAuthStore();
console.log('[API] Token disponible:', accessToken ? 'sí' : 'no');
```

**Solución:**
Verificar que el interceptor de Axios está incluyendo el token:
```typescript
// En la configuración de Axios
axios.interceptors.request.use((config) => {
  const { accessToken } = useAuthStore.getState();
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});
```

---

### **Causa 3: El backend no está validando el token correctamente**

**Síntoma:** El token se envía pero el backend lo rechaza.

**Verificación:**
Revisar logs del backend para ver si el token llega:
```bash
# En Django logs
[AUTH] Token recibido: ...
[AUTH] Token válido: sí/no
```

**Solución:**
Verificar que el middleware de autenticación está configurado correctamente.

---

### **Causa 4: El usuario está siendo redirigido a login en lugar del dashboard**

**Síntoma:** Después del reset, el usuario es redirigido a login.

**Verificación:**
En ResetPasswordForm línea 120-126:
```typescript
setTimeout(() => {
  if (response.user?.rol === 'admin') {
    navigate('/admin');
  } else {
    navigate('/');
  }
}, 2000);
```

**Problema posible:**
- `response.user?.rol` podría ser `undefined`
- El usuario podría ser redirigido a `/` pero luego redirigido a `/auth/login` por protección de rutas

**Solución:**
Verificar que el rol se está retornando correctamente del backend.

---

### **Causa 5: Problema de sincronización de estado**

**Síntoma:** El estado se guarda pero no se refleja en la UI.

**Verificación:**
Verificar que el componente se está re-renderizando después de `setAuthState`:
```typescript
const { isAuthenticated, user } = useAuthStore();
console.log('[ResetPasswordForm] Estado de autenticación:', {
  isAuthenticated,
  user: user?.username
});
```

---

## 🧪 PLAN DE DIAGNÓSTICO PASO A PASO

### Paso 1: Verificar que el backend retorna los datos correctos

```bash
# Ejecutar test E2E
python test_e2e_reset_password.py
```

**Esperado:** ✅ Todas las etapas completadas exitosamente

---

### Paso 2: Verificar que el frontend está guardando el token

**Agregar console.log en ResetPasswordForm.tsx:**

```typescript
try {
  const response = await confirmPasswordReset(email, codigo, password, passwordConfirm);

  console.log('[ResetPasswordForm] Response:', response);
  
  setSuccess('¡Contraseña actualizada exitosamente!');
  setShowSuccess(true);

  // ✅ Guardar autenticación en Zustand (memoria) - SEGURO
  if (response.accessToken && response.user) {
    console.log('[ResetPasswordForm] Guardando autenticación:', {
      userId: response.user.id,
      username: response.user.email,
      token: response.accessToken.substring(0, 20) + '...'
    });
    setAuthState(response.user, response.accessToken);
    
    // Verificar que se guardó
    const state = useAuthStore.getState();
    console.log('[ResetPasswordForm] Estado después de guardar:', {
      isAuthenticated: state.isAuthenticated,
      user: state.user?.email,
      token: state.accessToken ? 'presente' : 'ausente'
    });
  }
  
  // ... resto del código
}
```

**Verificar en consola del navegador:**
- ¿Se ve el console.log con los datos?
- ¿El estado se actualiza correctamente?

---

### Paso 3: Verificar que el usuario está autenticado después del reset

**Agregar verificación en el dashboard:**

```typescript
// En el componente del dashboard
useEffect(() => {
  const { isAuthenticated, user, accessToken } = useAuthStore();
  console.log('[Dashboard] Estado de autenticación:', {
    isAuthenticated,
    user: user?.email,
    token: accessToken ? 'presente' : 'ausente'
  });
}, []);
```

**Verificar en consola:**
- ¿`isAuthenticated` es `true`?
- ¿`user` tiene datos?
- ¿`accessToken` está presente?

---

### Paso 4: Verificar que el token se está enviando en las solicitudes

**En las herramientas de desarrollo del navegador (Network tab):**

1. Ir a la pestaña "Network"
2. Hacer una solicitud a la API
3. Verificar que el header `Authorization` está presente:
   ```
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

---

### Paso 5: Verificar que el backend está validando el token

**Agregar logs en el backend:**

En `backend/api/views.py` o middleware de autenticación:

```python
@api_view(['GET'])
def test_auth(request):
    """Endpoint para probar autenticación"""
    print(f"[AUTH_TEST] Headers: {request.headers}")
    print(f"[AUTH_TEST] User: {request.user}")
    print(f"[AUTH_TEST] Is authenticated: {request.user.is_authenticated}")
    
    if request.user.is_authenticated:
        return Response({
            'message': 'Autenticado',
            'user': request.user.username
        })
    else:
        return Response({
            'error': 'No autenticado'
        }, status=401)
```

---

## 📝 CHECKLIST DE VERIFICACIÓN

- [ ] Backend retorna token y usuario correctamente (test E2E)
- [ ] Frontend recibe la respuesta correctamente
- [ ] Frontend guarda el token en Zustand
- [ ] Frontend redirige al dashboard (no a login)
- [ ] Dashboard muestra que el usuario está autenticado
- [ ] Token se envía en el header `Authorization`
- [ ] Backend valida el token correctamente
- [ ] Usuario puede acceder a endpoints protegidos

---

## 🚀 PRÓXIMOS PASOS

1. **Ejecutar test E2E** para confirmar que el backend funciona
2. **Agregar console.log** en el frontend para ver qué está pasando
3. **Revisar Network tab** para verificar que el token se está enviando
4. **Revisar logs del backend** para ver si el token llega y es válido
5. **Reportar hallazgos** para identificar exactamente dónde está el problema

---

## 📞 INFORMACIÓN PARA REPORTAR

Cuando reportes el problema, incluye:

1. **Consola del navegador:** Captura de los console.log
2. **Network tab:** Captura de las solicitudes HTTP
3. **Logs del backend:** Captura de los logs relevantes
4. **Pasos exactos para reproducir:** Qué hiciste exactamente

---

**Última actualización:** 25 de Noviembre de 2025
