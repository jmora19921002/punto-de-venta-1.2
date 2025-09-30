# 🎯 GUÍA DE USO - SISTEMA PUNTO DE VENTA

## 📋 Índice
1. [Instalación](#instalación)
2. [Primer Uso](#primer-uso)
3. [Funcionalidades Principales](#funcionalidades-principales)
4. [Solución de Problemas](#solución-de-problemas)
5. [Archivos del Sistema](#archivos-del-sistema)

---

## 🚀 Instalación

### Requisitos
- Python 3.x
- Tkinter (incluido con Python)
- SQLite3 (incluido con Python)

### Pasos de Instalación
1. **Descargar** todos los archivos en una carpeta
2. **Ejecutar** el script de inicialización:
   ```bash
   python init_database.py
   ```
3. **Verificar** que se creó el archivo `punto_venta.db`

---

## 🎬 Primer Uso

### 1. Iniciar el Sistema
```bash
python main.py
```

### 2. Verificar Configuración de Fechas
Si tienes problemas con las fechas:
```bash
python configurar_fechas.py
```

### 3. Interfaz Principal
Al abrir el sistema verás:
- 🛒 **Área de productos** (izquierda)
- 🧾 **Área de venta** (centro)
- 💳 **Botones de acción** (derecha)

---

## 🛠️ Funcionalidades Principales

### 🛍️ Realizar una Venta
1. **Buscar producto**: Escribe en la barra de búsqueda o navega por categorías
2. **Agregar al carrito**: Haz clic en el producto deseado
3. **Modificar cantidad**: Cambia la cantidad en el carrito si es necesario
4. **Procesar pago**: Clic en "💳 Cobrar"
5. **Seleccionar método de pago**: Efectivo, tarjeta, transferencia o mixto
6. **Confirmar**: El ticket se generará automáticamente

### 👥 Gestión de Clientes
- **Nuevo cliente**: En la ventana de pago, clic "Nuevo Cliente"
- **Buscar cliente**: Usa la barra de búsqueda en la ventana de pago
- **Ver/editar**: Accede desde el menú "Clientes"

### 📦 Inventario
- **Ver productos**: Menú "Inventario"
- **Agregar producto**: Botón "+" en la ventana de inventario
- **Editar producto**: Doble clic en el producto
- **Stock**: Se actualiza automáticamente con cada venta

### 📊 Reportes y Corte del Día

#### Corte del Día
1. Clic en **"📊 Corte del Día"**
2. Selecciona la fecha:
   - **"Hoy"**: Fecha actual del sistema
   - **"Ayer"**: Fecha de ayer
   - **"Ventas"**: ⭐ Fecha con ventas más recientes (recomendado)
3. Clic **"🔄"** para actualizar datos

#### Información del Corte
- 💰 **Total de ingresos**
- 🧾 **Número de ventas**
- 💳 **Métodos de pago utilizados**
- 📦 **Productos más vendidos**
- 📈 **Estadísticas detalladas**

---

## 🔧 Solución de Problemas

### Problema: "El corte del día muestra 0 ventas"

**Causa**: La fecha del sistema es diferente a la fecha de las ventas registradas.

**Solución**:
1. Ejecuta: `python configurar_fechas.py`
2. En el corte del día, usa el botón **"Ventas"** en lugar de "Hoy"
3. Esto cargará automáticamente la fecha con ventas más recientes

### Problema: "Error de base de datos bloqueada"

**Solución**:
1. Cierra todas las ventanas del sistema
2. Reinicia el programa
3. Si persiste, reinicia el equipo

### Problema: "No aparecen productos"

**Solución**:
1. Verifica que existe `punto_venta.db`
2. Ejecuta: `python init_database.py`
3. Reinicia el sistema

### Problema: "Error al procesar pago"

**Solución**:
1. Verifica que hay productos en el carrito
2. Asegúrate de que el total sea mayor a 0
3. Comprueba que hay stock suficiente

---

## 📁 Archivos del Sistema

### Archivos Principales
- `main.py` - ✅ Sistema principal
- `database.py` - ✅ Gestor de base de datos
- `punto_venta.db` - ✅ Base de datos SQLite

### Ventanas del Sistema
- `pagos_window.py` - ✅ Ventana de pagos
- `inventario_window.py` - ✅ Gestión de inventario
- `clientes_window.py` - ✅ Gestión de clientes
- `reportes_window.py` - ✅ Reportes generales
- `corte_dia_window.py` - ✅ Corte del día

### Scripts de Configuración
- `init_database.py` - ✅ Inicialización de BD
- `configurar_fechas.py` - ✅ Diagnóstico de fechas
- `debug_fechas.py` - ✅ Depuración de fechas
- `test_corte_corregido.py` - ✅ Prueba de corte corregido

### Archivos de Documentación
- `GUIA_DE_USO.md` - 📖 Esta guía
- `README.md` - 📋 Información del proyecto

---

## 🎯 Consejos de Uso

### ✅ Mejores Prácticas
- **Siempre** usa el botón "Ventas" para el corte del día
- **Verifica** el stock antes de grandes ventas
- **Actualiza** regularmente la información de clientes
- **Respalda** el archivo `punto_venta.db` periódicamente

### 🚫 Evitar
- No cierres el sistema durante una venta
- No modifiques manualmente la base de datos
- No elimines archivos del sistema sin respaldar

### 🔄 Mantenimiento Regular
1. **Semanal**: Revisar stock bajo en inventario
2. **Mensual**: Respaldar base de datos
3. **Trimestral**: Limpiar datos innecesarios

---

## 📞 Soporte

### Problemas Técnicos
1. Ejecuta `configurar_fechas.py` para diagnóstico automático
2. Revisa esta guía en la sección "Solución de Problemas"
3. Verifica que todos los archivos estén presentes

### Funciones Avanzadas
- El sistema soporta **descuentos** y **pagos mixtos**
- Puedes **personalizar categorías** de productos
- Los **tickets** se generan automáticamente
- La **búsqueda** funciona por nombre y código de producto

---

**🎉 ¡Sistema listo para usar! El punto de venta está completamente configurado y funcional.**
