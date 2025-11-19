# 🧪 CHECKLIST DE PRUEBAS - ANTES DE PRODUCCIÓN

## 📋 **INSTRUCCIONES**

1. Marca cada prueba con ✅ cuando la completes
2. Si algo falla, anota el problema
3. Si todo pasa, estás listo para producción

---

## 🎯 **PRUEBAS PANEL DE ADMINISTRACIÓN**

### **Filtros de Fecha - Dashboard**
- [ ] Accede a `/admin/dashboard`
- [ ] Verifica que hay un selector de "Período de Estadísticas"
- [ ] Cambia a "Hoy" → Las estadísticas se actualizan
- [ ] Cambia a "Última Semana" → Las estadísticas se actualizan
- [ ] Cambia a "Último Mes" → Las estadísticas se actualizan
- [ ] Cambia a "Últimos 3 Meses" → Las estadísticas se actualizan
- [ ] Cambia a "Últimos 6 Meses" → Las estadísticas se actualizan
- [ ] Cambia a "Último Año" → Las estadísticas se actualizan
- [ ] Cambia a "Todo el Tiempo" → Muestra todos los datos

### **Filtros de Fecha - Historial**
- [ ] Accede a `/admin/historial`
- [ ] Verifica que hay un selector de "Período"
- [ ] Cambia a diferentes períodos → El historial se filtra
- [ ] Combina filtro de fecha + búsqueda → Funciona correctamente
- [ ] Combina filtro de fecha + módulo → Funciona correctamente
- [ ] Combina filtro de fecha + acción → Funciona correctamente

### **Botón "Limpiar Todo" - Historial**
- [ ] Verifica que existe el botón rojo "Limpiar Todo"
- [ ] Click en el botón → Aparece modal de confirmación
- [ ] Modal muestra advertencias claras
- [ ] Modal muestra cantidad de registros a eliminar
- [ ] Click en "Cancelar" → Modal se cierra, nada se elimina
- [ ] Click en "Limpiar Todo" → Loading global aparece
- [ ] Después de completar → Historial está vacío
- [ ] Dashboard se actualiza automáticamente

### **Botones PDF/Excel - Historial**
- [ ] Verifica que los botones tienen estilos consistentes
- [ ] Botón PDF tiene color rojo
- [ ] Botón Excel tiene color verde
- [ ] Hover sobre botones → Se elevan suavemente
- [ ] Click en PDF → Se descarga archivo
- [ ] Click en Excel → Se descarga archivo

---

## 🎨 **PRUEBAS DISEÑO LOGIN**

### **Animaciones de Entrada**
- [ ] Recarga la página de login (F5)
- [ ] Verifica que hay animación suave de entrada
- [ ] La tarjeta se desliza hacia arriba
- [ ] El logo tiene animación pulse

### **Interactividad**
- [ ] Hover sobre la tarjeta → Se eleva suavemente
- [ ] Hover sobre inputs → Se elevan + border cambia a primario
- [ ] Focus en inputs → Glow effect visible
- [ ] Hover sobre botón → Se eleva más
- [ ] Active en botón → Scale(0.98)

### **Errores**
- [ ] Intenta enviar vacío → Shake animation en inputs
- [ ] Verifica que los errores aparecen suavemente
- [ ] Corrige el error → El error desaparece

### **Responsive**
- [ ] Abre DevTools (F12)
- [ ] Cambia a Device Toolbar
- [ ] Prueba en iPhone 12 → Se ve bien
- [ ] Prueba en iPad → Se ve bien
- [ ] Prueba en Android → Se ve bien

---

## 🚫 **PRUEBAS PANTALLA DE BLOQUEO**

### **Información Visible**
- [ ] Intenta login 5 veces con credenciales incorrectas
- [ ] Aparece pantalla de bloqueo
- [ ] Título: "Acceso Temporalmente Bloqueado" ✅
- [ ] Subtítulo: "Por tu seguridad..." ✅
- [ ] Alerta: "Demasiados intentos..." ✅
- [ ] Contador regresivo: MM:SS ✅
- [ ] Sección "¿Por qué veo esto?" ✅
- [ ] Sección "Consejos de seguridad" ✅
- [ ] Footer: "El acceso se restablecerá..." ✅

### **Contador Regresivo**
- [ ] Contador comienza en 00:60 (o similar)
- [ ] Cuenta hacia atrás cada segundo
- [ ] Barra de progreso se llena
- [ ] Cuando llega a 00:00 → Se desbloquea automáticamente
- [ ] Puedes intentar login nuevamente

### **Persistencia**
- [ ] Estás en pantalla de bloqueo
- [ ] Navega a otra página (ej: `/`)
- [ ] Vuelve a `/login`
- [ ] Pantalla de bloqueo sigue visible
- [ ] Contador continúa desde donde estaba

### **Animaciones**
- [ ] Icono principal tiene animación bounce
- [ ] Contador tiene animación pulse
- [ ] Barra de progreso tiene shimmer
- [ ] Alerta tiene shake suave
- [ ] Todas las animaciones son suaves (60fps)

### **Responsive**
- [ ] Pantalla de bloqueo se ve bien en desktop
- [ ] Pantalla de bloqueo se ve bien en tablet
- [ ] Pantalla de bloqueo se ve bien en móvil
- [ ] Texto es legible en todos los tamaños

---

## ♿ **PRUEBAS ACCESIBILIDAD**

### **Keyboard Navigation**
- [ ] Presiona Tab → Navega por los elementos
- [ ] Presiona Shift+Tab → Navega hacia atrás
- [ ] Presiona Enter en botones → Se activan
- [ ] Presiona Space en checkboxes → Se marcan/desmarcan

### **Screen Reader**
- [ ] Abre NVDA o JAWS
- [ ] Lee la página de login
- [ ] Verifica que los labels están presentes
- [ ] Verifica que los errores se anuncian

### **Contraste**
- [ ] Abre DevTools (F12)
- [ ] Lighthouse → Accessibility
- [ ] Score debe ser > 90
- [ ] No hay warnings de contraste

### **Reduced Motion**
- [ ] Abre DevTools (F12)
- [ ] Emula `prefers-reduced-motion: reduce`
- [ ] Recarga la página
- [ ] Las animaciones deben ser mínimas o inexistentes

---

## 🔒 **PRUEBAS SEGURIDAD**

### **Rate Limiting**
- [ ] Intenta login 5 veces fallido → Se bloquea
- [ ] Espera a que se desbloquee → Puedes intentar de nuevo
- [ ] Intenta 5 veces más → Se bloquea nuevamente

### **Permisos Backend**
- [ ] Intenta acceder a `/admin/dashboard` sin autenticación → Redirige a login
- [ ] Intenta acceder a `/admin/historial` sin autenticación → Redirige a login
- [ ] Intenta eliminar historial sin ser admin → Error 403

### **Validación**
- [ ] Intenta enviar formulario vacío → Errores de validación
- [ ] Intenta inyectar HTML → No se ejecuta
- [ ] Intenta inyectar JavaScript → No se ejecuta

---

## 📊 **PRUEBAS RENDIMIENTO**

### **Lighthouse**
- [ ] Abre DevTools (F12)
- [ ] Lighthouse → Generate report
- [ ] Performance score > 90
- [ ] Accessibility score > 90
- [ ] Best Practices score > 90
- [ ] SEO score > 90

### **Carga de Página**
- [ ] Mide tiempo de carga inicial
- [ ] Debe ser < 3 segundos
- [ ] No hay layout shifts
- [ ] Animaciones son suaves

### **Bundle Size**
- [ ] Verifica que no hay duplicación de CSS
- [ ] Verifica que no hay imports innecesarios
- [ ] Bundle debe ser < 200KB (gzipped)

---

## 🔄 **PRUEBAS FUNCIONALIDAD**

### **Actualización en Tiempo Real**
- [ ] Abre dashboard en 2 pestañas
- [ ] En una pestaña, crea un nuevo producto
- [ ] En la otra pestaña, verifica que se actualiza automáticamente
- [ ] Mismo con usuarios y historial

### **Modales**
- [ ] Abre modal de confirmación
- [ ] Click fuera del modal → NO se cierra
- [ ] Click en botón X → Se cierra
- [ ] Click en Cancelar → Se cierra

### **Formularios**
- [ ] Completa un formulario
- [ ] Verifica que la validación funciona
- [ ] Verifica que los errores se muestran
- [ ] Verifica que se pueden corregir

---

## 📱 **PRUEBAS DISPOSITIVOS REALES**

### **iPhone**
- [ ] Prueba en iPhone 12/13/14
- [ ] Verifica que se ve bien
- [ ] Verifica que los botones son accesibles
- [ ] Verifica que las animaciones funcionan

### **Android**
- [ ] Prueba en Samsung/Pixel
- [ ] Verifica que se ve bien
- [ ] Verifica que los botones son accesibles
- [ ] Verifica que las animaciones funcionan

### **Desktop**
- [ ] Prueba en Chrome
- [ ] Prueba en Firefox
- [ ] Prueba en Safari
- [ ] Prueba en Edge

---

## 🎉 **RESULTADO FINAL**

### **Si todas las pruebas pasan:**
```
✅ LISTO PARA PRODUCCIÓN
```

### **Si alguna prueba falla:**
```
❌ REVISAR Y CORREGIR ANTES DE PRODUCCIÓN
```

---

## 📝 **NOTAS**

Usa este espacio para anotar cualquier problema encontrado:

```
Problema 1: _______________________________________________
Solución: __________________________________________________

Problema 2: _______________________________________________
Solución: __________________________________________________

Problema 3: _______________________________________________
Solución: __________________________________________________
```

---

**¡BUENA SUERTE CON LAS PRUEBAS!** 🚀
