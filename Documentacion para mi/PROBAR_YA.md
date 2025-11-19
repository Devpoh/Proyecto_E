# 🚀 PROBAR YA - Sin Complicaciones

---

## 📋 REQUISITOS

- Django corriendo: `python manage.py runserver`
- React corriendo: `npm start`

---

## ⚡ OPCIÓN 1: Script Automático (RECOMENDADO)

```powershell
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
.\setup_y_test.ps1
```

**Esto hace:**
- ✅ Crea usuario `testuser` automáticamente
- ✅ Prueba login
- ✅ Obtiene carrito
- ✅ Agrega un producto
- ✅ Te da instrucciones para probar en navegador

---

## ⚡ OPCIÓN 2: Script Rápido (si ya existe usuario)

```powershell
cd C:\Users\Alejandro\Desktop\Electro-Isla\backend
.\test_rapido.ps1
```

---

## ⚡ OPCIÓN 3: Probar en Navegador (Manual)

1. Ve a `http://localhost:3000`
2. Inicia sesión:
   - Email: `testuser@example.com`
   - Password: `testpass123`
3. Agrega un producto
4. Verifica que aparece en carrito
5. Elimina el producto
6. Verifica que desaparece (NO reaparece)

---

## ✅ ¿QUÉ ESPERAR?

### Si todo funciona:
```
[OK] Usuario listo
[OK] Login exitoso
[OK] Carrito obtenido
[OK] Producto agregado
[OK] SETUP Y TEST COMPLETADO
```

### Si falla:
- Verifica que Django está corriendo
- Verifica que React está corriendo
- Intenta de nuevo

---

## 🎉 ¡LISTO!

Carrito completamente funcional. 🚀
