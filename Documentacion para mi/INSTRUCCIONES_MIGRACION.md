# 🚀 INSTRUCCIONES - EJECUTAR MIGRACIÓN

**Fecha:** 19 de Noviembre, 2025  
**Problema:** Error 500 en `/api/admin/productos/`  
**Causa:** Nuevos campos no existen en la base de datos  
**Solución:** Ejecutar migración Django

---

## ⚠️ IMPORTANTE

La migración ya está creada en:
```
backend/api/migrations/0028_add_visibility_fields.py
```

---

## 🔧 PASOS PARA EJECUTAR

### Opción 1: Terminal (Recomendado)

1. **Abre una terminal en la carpeta del backend:**
```bash
cd c:\Users\Alejandro\Desktop\Electro-Isla\backend
```

2. **Ejecuta las migraciones:**
```bash
python manage.py migrate
```

3. **Verifica que se ejecutó correctamente:**
```bash
python manage.py showmigrations api
```

Deberías ver `[X] 0028_add_visibility_fields` (con X entre corchetes)

---

### Opción 2: Si tienes Django Shell

```bash
python manage.py shell
```

Luego en el shell:
```python
from django.core.management import call_command
call_command('migrate')
```

---

## ✅ VERIFICACIÓN

Después de ejecutar la migración:

1. **Recarga el frontend:**
   - Presiona `Ctrl+F5` en el navegador

2. **Intenta acceder a `/admin/productos`:**
   - Deberías ver la lista de productos sin errores 500

3. **Crea un nuevo producto:**
   - Deberías ver los 4 checkboxes en grid 2x2:
     - Producto activo
     - Carrusel principal
     - Tarjetas inferiores
     - Catálogo completo

---

## 🐛 SI SIGUE DANDO ERROR 500

1. **Verifica que la migración se ejecutó:**
```bash
python manage.py showmigrations api | grep 0028
```

2. **Si no aparece, ejecuta:**
```bash
python manage.py migrate api 0028_add_visibility_fields
```

3. **Si sigue sin funcionar, revisa los logs:**
```bash
python manage.py migrate --verbosity=3
```

---

## 📊 QUÉ HACE LA MIGRACIÓN

Agrega dos campos a la tabla `productos`:

```sql
ALTER TABLE productos ADD COLUMN en_carousel_card BOOLEAN DEFAULT TRUE;
ALTER TABLE productos ADD COLUMN en_all_products BOOLEAN DEFAULT TRUE;
```

---

## 🎯 RESULTADO ESPERADO

Después de la migración:

✅ Error 500 desaparece  
✅ Lista de productos carga correctamente  
✅ Formulario muestra 4 checkboxes  
✅ Puedes crear/editar productos con control de visibilidad  

---

## ⏱️ TIEMPO ESTIMADO

- Ejecutar migración: < 1 segundo
- Recargar frontend: 2-3 segundos
- Total: ~5 segundos

---

**Una vez ejecutada la migración, todo debería funcionar correctamente.**
