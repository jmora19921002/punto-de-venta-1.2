import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk

class InventarioWindow:
    def __init__(self, parent, database_manager):
        self.parent = parent
        self.db = database_manager
        
        # Crear ventana de inventario
        self.window = ctk.CTkToplevel(parent, fg_color="#FFFFFF")
        self.window.title("Gestión de Inventario")
        self.window.geometry("1200x700")
        self.window.transient(parent)
        self.window.grab_set()
        self.setup_ui()
        self.cargar_productos()
        self.cargar_categorias()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal dividido en dos secciones
        
        # Sección izquierda - Lista de productos
        self.frame_lista = ctk.CTkFrame(self.window, width=700, height=680, fg_color="#e3f0ff")
        self.frame_lista.place(x=10, y=10)
        
        # Sección derecha - Formulario de producto
        self.frame_formulario = ctk.CTkFrame(self.window, width=470, height=680, fg_color="#e3f0ff")
        self.frame_formulario.place(x=720, y=10)
        
        self.setup_lista_productos()
        self.setup_formulario_producto()
    
    def setup_lista_productos(self):
        """Configura la sección de lista de productos"""
        # Título y búsqueda
        ctk.CTkLabel(
            self.frame_lista, 
            text="Inventario de Productos", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).place(x=10, y=10)
        
        # Búsqueda
        self.entry_buscar = ctk.CTkEntry(
            self.frame_lista, 
            placeholder_text="Buscar producto...", 
            width=500, height=35
        )
        self.entry_buscar.place(x=10, y=50)
        self.entry_buscar.bind('<KeyRelease>', self.buscar_productos)
        
        btn_buscar = ctk.CTkButton(
            self.frame_lista, text="🔍", width=50, height=35,
            command=self.buscar_productos_manual
        )
        btn_buscar.place(x=520, y=50)
        
        btn_refresh = ctk.CTkButton(
            self.frame_lista, text="🔄", width=50, height=35,
            command=self.cargar_productos
        )
        btn_refresh.place(x=580, y=50)
        
        btn_nuevo = ctk.CTkButton(
            self.frame_lista, text="➕ Nuevo", width=100, height=35,
            command=self.nuevo_producto,
            fg_color="green", hover_color="darkgreen"
        )
        btn_nuevo.place(x=580, y=95)
        
        # Treeview para productos
        self.setup_treeview_productos()
        
        # Botones de acción
        btn_editar = ctk.CTkButton(
            self.frame_lista, text="✏️ Editar", width=100, height=40,
            command=self.editar_producto_seleccionado
        )
        btn_editar.place(x=10, y=620)
        
        btn_eliminar = ctk.CTkButton(
            self.frame_lista, text="🗑️ Eliminar", width=100, height=40,
            command=self.eliminar_producto_seleccionado,
            fg_color="red", hover_color="darkred"
        )
        btn_eliminar.place(x=120, y=620)
        
        btn_ajuste_stock = ctk.CTkButton(
            self.frame_lista, text="📦 Ajustar Stock", width=120, height=40,
            command=self.ajustar_stock_dialog
        )
        btn_ajuste_stock.place(x=240, y=620)
    
    def setup_treeview_productos(self):
        """Configura el Treeview de productos"""
        # Frame para treeview
        tree_frame = tk.Frame(self.frame_lista, bg='white')
        tree_frame.place(x=10, y=140, width=670, height=470)
        
        # Treeview
        self.tree_productos = ttk.Treeview(
            tree_frame,
            columns=("codigo", "nombre", "categoria", "precio_venta", "precio_compra", "stock", "stock_min"),
            show="headings",
            height=20
        )
        
        # Configurar encabezados
        headers = {
            "codigo": ("Código", 100),
            "nombre": ("Nombre", 200),
            "categoria": ("Categoría", 100),
            "precio_venta": ("P. Venta USD", 90),
            "precio_compra": ("P. Compra USD", 90),
            "stock": ("Stock", 60),
            "stock_min": ("Stock Mín", 80)
        }
        
        for col, (text, width) in headers.items():
            self.tree_productos.heading(col, text=text)
            self.tree_productos.column(col, width=width, anchor="center" if col in ["stock", "stock_min"] else "w")
        
        # Configurar fuente reducida para treeview
        style = ttk.Style()
        style.configure("Treeview", font=('Arial', 9))  # Reducido en 3 puntos desde 12
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_productos.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree_productos.xview)
        self.tree_productos.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Pack
        self.tree_productos.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        
        # Eventos
        self.tree_productos.bind('<<TreeviewSelect>>', self.seleccionar_producto)
        self.tree_productos.bind('<Double-1>', self.editar_producto_seleccionado)
    
    def setup_formulario_producto(self):
        """Configura el formulario de producto"""
        ctk.CTkLabel(
            self.frame_formulario, 
            text="Datos del Producto", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).place(x=10, y=10)
        
        # Campos del formulario
        y_pos = 60
        spacing = 45
        
        # Código de barras
        ctk.CTkLabel(self.frame_formulario, text="Código de Barras:").place(x=10, y=y_pos)
        self.entry_codigo = ctk.CTkEntry(self.frame_formulario, width=300, height=35)
        self.entry_codigo.place(x=150, y=y_pos)
        
        # Nombre
        y_pos += spacing
        ctk.CTkLabel(self.frame_formulario, text="Nombre:").place(x=10, y=y_pos)
        self.entry_nombre = ctk.CTkEntry(self.frame_formulario, width=300, height=35)
        self.entry_nombre.place(x=150, y=y_pos)
        
        # Descripción
        y_pos += spacing
        ctk.CTkLabel(self.frame_formulario, text="Descripción:").place(x=10, y=y_pos)
        self.text_descripcion = ctk.CTkTextbox(self.frame_formulario, width=300, height=80)
        self.text_descripcion.place(x=150, y=y_pos)
        
        # Categoría
        y_pos += 90
        ctk.CTkLabel(self.frame_formulario, text="Categoría:").place(x=10, y=y_pos)
        self.combo_categoria = ctk.CTkComboBox(self.frame_formulario, width=300, height=35)
        self.combo_categoria.place(x=150, y=y_pos)
        
        # Precio de venta en USD
        y_pos += spacing
        ctk.CTkLabel(self.frame_formulario, text="Precio Venta (USD):").place(x=10, y=y_pos)
        self.entry_precio_venta = ctk.CTkEntry(self.frame_formulario, width=140, height=35)
        self.entry_precio_venta.place(x=150, y=y_pos)
        
        # Preview del precio en VES
        self.label_precio_ves = ctk.CTkLabel(self.frame_formulario, text="", text_color="gray")
        self.label_precio_ves.place(x=300, y=y_pos)
        self.entry_precio_venta.bind('<KeyRelease>', self.actualizar_preview_precio)
        
        # Precio de compra en USD
        y_pos += 30
        ctk.CTkLabel(self.frame_formulario, text="Precio Compra (USD):").place(x=10, y=y_pos)
        self.entry_precio_compra = ctk.CTkEntry(self.frame_formulario, width=140, height=35)
        self.entry_precio_compra.place(x=150, y=y_pos)
        
        # Stock actual
        y_pos += spacing * 2
        ctk.CTkLabel(self.frame_formulario, text="Stock Actual:").place(x=10, y=y_pos)
        self.entry_stock_actual = ctk.CTkEntry(self.frame_formulario, width=140, height=35)
        self.entry_stock_actual.place(x=150, y=y_pos)
        
        # Stock mínimo
        ctk.CTkLabel(self.frame_formulario, text="Stock Mínimo:").place(x=300, y=y_pos)
        self.entry_stock_minimo = ctk.CTkEntry(self.frame_formulario, width=140, height=35)
        self.entry_stock_minimo.place(x=310, y=y_pos + 30)
        
        # Venta al mayor
        y_pos += 80
        self.chk_vende_mayor_var = tk.IntVar(value=0)
        self.chk_vende_mayor = ctk.CTkCheckBox(self.frame_formulario, text="Se vende al mayor (por bulto)", variable=self.chk_vende_mayor_var)
        self.chk_vende_mayor.place(x=10, y=y_pos)
        
        ctk.CTkLabel(self.frame_formulario, text="Unidades por bulto:").place(x=300, y=y_pos)
        self.entry_unidades_bulto = ctk.CTkEntry(self.frame_formulario, width=140, height=35)
        self.entry_unidades_bulto.place(x=310, y=y_pos + 25)
        
        # Botones del formulario
        y_pos += 80
        
        self.btn_guardar = ctk.CTkButton(
            self.frame_formulario, text="💾 Guardar", width=140, height=50,
            command=self.guardar_producto,
            fg_color="green", hover_color="darkgreen",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_guardar.place(x=10, y=y_pos)
        
        self.btn_cancelar = ctk.CTkButton(
            self.frame_formulario, text="❌ Cancelar", width=140, height=50,
            command=self.limpiar_formulario,
            fg_color="gray", hover_color="darkgray"
        )
        self.btn_cancelar.place(x=160, y=y_pos)
        
        self.btn_actualizar = ctk.CTkButton(
            self.frame_formulario, text="🔄 Actualizar", width=140, height=50,
            command=self.actualizar_producto,
            fg_color="orange", hover_color="darkorange"
        )
        self.btn_actualizar.place(x=310, y=y_pos)
        self.btn_actualizar.place_forget()  # Ocultar inicialmente
        
        # Variables de estado
        self.producto_editando = None
    
    def cargar_categorias(self):
        """Carga las categorías en el combobox"""
        categorias = self.db.get_categorias()
        nombres_categorias = [cat['nombre'] for cat in categorias]
        self.combo_categoria.configure(values=nombres_categorias)
        self.categorias_dict = {cat['nombre']: cat['id'] for cat in categorias}
    
    def cargar_productos(self, productos=None):
        """Carga los productos en el treeview"""
        # Limpiar treeview
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        if productos is None:
            productos = self.db.get_productos()
        
        # Insertar productos
        for producto in productos:
            # Determinar color según stock
            tags = ()
            if producto['stock_actual'] <= 0:
                tags = ('sin_stock',)
            elif producto['stock_actual'] <= 5:  # Asumiendo stock mínimo bajo
                tags = ('stock_bajo',)
            
            # Mostrar precios USD en el treeview
            precio_venta_usd = producto.get('precio_venta_usd', 0) or 0
            precio_compra_usd = producto.get('precio_compra_usd', 0) or 0
            
            self.tree_productos.insert('', 'end', values=(
                producto['codigo_barras'] or '',
                producto['nombre'],
                producto['categoria'] or 'Sin categoría',
                f"${precio_venta_usd:.2f}",
                f"${precio_compra_usd:.2f}",
                producto['stock_actual'],
                producto.get('stock_minimo', 0)
            ), tags=tags)
        
        # Configurar colores para las etiquetas
        self.tree_productos.tag_configure('sin_stock', background='#ffcccc')
        self.tree_productos.tag_configure('stock_bajo', background='#ffffcc')
    
    def buscar_productos(self, event=None):
        """Busca productos en tiempo real"""
        termino = self.entry_buscar.get()
        if len(termino) >= 2:
            productos = self.db.buscar_productos(termino)
            self.cargar_productos(productos)
        elif len(termino) == 0:
            self.cargar_productos()
    
    def buscar_productos_manual(self):
        """Busca productos manualmente"""
        termino = self.entry_buscar.get()
        if termino:
            productos = self.db.buscar_productos(termino)
            self.cargar_productos(productos)
        else:
            self.cargar_productos()
    
    def seleccionar_producto(self, event=None):
        """Maneja la selección de un producto en el treeview"""
        selection = self.tree_productos.selection()
        if not selection:
            return
        
        # Obtener datos del producto seleccionado
        item = self.tree_productos.item(selection[0])
        valores = item['values']
        
        # Buscar el producto completo en la base de datos
        codigo_barras = valores[0]
        if codigo_barras:
            productos = self.db.buscar_productos(codigo_barras)
            if productos:
                producto = productos[0]
                self.cargar_producto_en_formulario(producto)
    
    def cargar_producto_en_formulario(self, producto):
        """Carga los datos de un producto en el formulario"""
        # Limpiar formulario
        self.limpiar_formulario()
        
        # Cargar datos
        self.entry_codigo.insert(0, producto.get('codigo_barras', ''))
        self.entry_nombre.insert(0, producto['nombre'])
        self.text_descripcion.insert('1.0', producto.get('descripcion', ''))
        
        # Seleccionar categoría
        categoria_nombre = producto.get('categoria', '')
        if categoria_nombre:
            self.combo_categoria.set(categoria_nombre)
        
        # Cargar precios USD en el formulario
        precio_venta_usd = producto.get('precio_venta_usd', 0) or 0
        precio_compra_usd = producto.get('precio_compra_usd', 0) or 0
        
        self.entry_precio_venta.insert(0, str(precio_venta_usd))
        self.entry_precio_compra.insert(0, str(precio_compra_usd))
        
        # Actualizar preview
        self.actualizar_preview_precio()
        self.entry_stock_actual.insert(0, str(producto['stock_actual']))
        self.entry_stock_minimo.insert(0, str(producto.get('stock_minimo', 0)))
        
        # Cargar venta al mayor
        vende_mayor = int(producto.get('vende_al_mayor', 0) or 0)
        self.chk_vende_mayor_var.set(vende_mayor)
        self.entry_unidades_bulto.delete(0, 'end')
        if vende_mayor == 1:
            self.entry_unidades_bulto.insert(0, str(producto.get('unidades_por_bulto', 0) or 0))
        
        # Cambiar a modo edición
        self.producto_editando = producto
        self.btn_guardar.place_forget()
        self.btn_actualizar.place(x=310, y=520)
    
    def nuevo_producto(self):
        """Prepara el formulario para un nuevo producto"""
        self.limpiar_formulario()
        self.producto_editando = None
        self.btn_actualizar.place_forget()
        self.btn_guardar.place(x=10, y=520)
        
        # Enfocar en el primer campo
        self.entry_codigo.focus()
    
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        self.entry_codigo.delete(0, 'end')
        self.entry_nombre.delete(0, 'end')
        self.text_descripcion.delete('1.0', 'end')
        self.combo_categoria.set('')
        self.entry_precio_venta.delete(0, 'end')
        self.entry_precio_compra.delete(0, 'end')
        self.entry_stock_actual.delete(0, 'end')
        self.entry_stock_minimo.delete(0, 'end')
        if hasattr(self, 'chk_vende_mayor_var'):
            self.chk_vende_mayor_var.set(0)
        if hasattr(self, 'entry_unidades_bulto'):
            self.entry_unidades_bulto.delete(0, 'end')
        
        self.producto_editando = None
        self.btn_actualizar.place_forget()
        self.btn_guardar.place(x=10, y=520)
    
    def validar_formulario(self):
        """Valida los datos del formulario"""
        errores = []
        
        if not self.entry_nombre.get().strip():
            errores.append("El nombre es requerido")
        
        try:
            precio_venta = float(self.entry_precio_venta.get())
            if precio_venta <= 0:
                errores.append("El precio de venta debe ser mayor a 0")
        except ValueError:
            errores.append("El precio de venta debe ser un número válido")
        
        try:
            precio_compra = float(self.entry_precio_compra.get() or 0)
            if precio_compra < 0:
                errores.append("El precio de compra no puede ser negativo")
        except ValueError:
            errores.append("El precio de compra debe ser un número válido")
        
        try:
            stock_actual = int(self.entry_stock_actual.get() or 0)
            if stock_actual < 0:
                errores.append("El stock actual no puede ser negativo")
        except ValueError:
            errores.append("El stock actual debe ser un número entero")
        
        try:
            stock_minimo = int(self.entry_stock_minimo.get() or 0)
            if stock_minimo < 0:
                errores.append("El stock mínimo no puede ser negativo")
        except ValueError:
            errores.append("El stock mínimo debe ser un número entero")
        
        if errores:
            messagebox.showerror("Errores de validación", "\\n".join(errores))
            return False
        
        # Validación venta al mayor
        if self.chk_vende_mayor_var.get() == 1:
            try:
                unidades_bulto = int(self.entry_unidades_bulto.get() or 0)
                if unidades_bulto <= 0:
                    messagebox.showerror("Error", "Unidades por bulto debe ser un entero mayor a 0")
                    return False
            except ValueError:
                messagebox.showerror("Error", "Unidades por bulto debe ser un número entero")
                return False
        
        return True
    
    def actualizar_preview_precio(self, event=None):
        """Actualiza el texto de preview mostrando el precio VES calculado"""
        try:
            tasa = self.db.get_tasa_cambio()
            precio_usd = float(self.entry_precio_venta.get() or 0)
            bs = precio_usd * tasa
            self.label_precio_ves.configure(text=f"≈ Bs {bs:.2f}")
        except Exception:
            self.label_precio_ves.configure(text="")
    
    def guardar_producto(self):
        """Guarda un nuevo producto (precios en USD, se convierten a VES automáticamente)"""
        if not self.validar_formulario():
            return
        
        try:
            # Obtener categoria_id
            categoria_nombre = self.combo_categoria.get()
            categoria_id = self.categorias_dict.get(categoria_nombre) if categoria_nombre else None
            
            # Tomar precios en USD del formulario
            precio_venta_usd = float(self.entry_precio_venta.get())
            precio_compra_usd = float(self.entry_precio_compra.get() or 0)
            
            # Calcular precios VES usando la tasa actual
            tasa = self.db.get_tasa_cambio()
            precio_venta_ves = round(precio_venta_usd * tasa, 2)
            precio_compra_ves = round(precio_compra_usd * tasa, 2)
            
            # Crear producto (guardamos VES y USD)
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO productos (
                    codigo_barras, nombre, descripcion, categoria_id,
                    precio_venta, precio_compra, precio_venta_usd, precio_compra_usd,
                    stock_actual, stock_minimo, vende_al_mayor, unidades_por_bulto
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.entry_codigo.get().strip() or None,
                self.entry_nombre.get().strip(),
                self.text_descripcion.get('1.0', 'end').strip(),
                categoria_id,
                precio_venta_ves,
                precio_compra_ves,
                precio_venta_usd,
                precio_compra_usd,
                int(self.entry_stock_actual.get() or 0),
                int(self.entry_stock_minimo.get() or 0),
                int(self.chk_vende_mayor_var.get() or 0),
                int(self.entry_unidades_bulto.get() or 0) if int(self.chk_vende_mayor_var.get() or 0) == 1 else None
            ))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Éxito", "Producto guardado correctamente (precios convertidos por tasa)")
            self.limpiar_formulario()
            self.cargar_productos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar producto: {str(e)}")
    
    def actualizar_producto(self):
        """Actualiza un producto existente (precios en USD, convierte a VES)"""
        if not self.producto_editando:
            return
        
        if not self.validar_formulario():
            return
        
        try:
            # Por simplicidad, vamos a usar una consulta SQL directa
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            categoria_nombre = self.combo_categoria.get()
            categoria_id = self.categorias_dict.get(categoria_nombre) if categoria_nombre else None
            
            # Tomar precios USD y convertir a VES
            precio_venta_usd = float(self.entry_precio_venta.get())
            precio_compra_usd = float(self.entry_precio_compra.get() or 0)
            tasa = self.db.get_tasa_cambio()
            precio_venta_ves = round(precio_venta_usd * tasa, 2)
            precio_compra_ves = round(precio_compra_usd * tasa, 2)
            
            cursor.execute("""
                UPDATE productos 
                SET codigo_barras = ?, nombre = ?, descripcion = ?, categoria_id = ?,
                    precio_venta = ?, precio_compra = ?, precio_venta_usd = ?, precio_compra_usd = ?,
                    stock_actual = ?, stock_minimo = ?, vende_al_mayor = ?, unidades_por_bulto = ?,
                    fecha_modificacion = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                self.entry_codigo.get().strip() or None,
                self.entry_nombre.get().strip(),
                self.text_descripcion.get('1.0', 'end').strip(),
                categoria_id,
                precio_venta_ves,
                precio_compra_ves,
                precio_venta_usd,
                precio_compra_usd,
                int(self.entry_stock_actual.get() or 0),
                int(self.entry_stock_minimo.get() or 0),
                int(self.chk_vende_mayor_var.get() or 0),
                int(self.entry_unidades_bulto.get() or 0) if int(self.chk_vende_mayor_var.get() or 0) == 1 else None,
                self.producto_editando['id']
            ))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Éxito", "Producto actualizado correctamente (precios convertidos por tasa)")
            self.limpiar_formulario()
            self.cargar_productos()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar producto: {str(e)}")
    
    def editar_producto_seleccionado(self, event=None):
        """Edita el producto seleccionado"""
        selection = self.tree_productos.selection()
        if not selection:
            messagebox.showinfo("Información", "Seleccione un producto para editar")
            return
        
        # El producto ya se carga automáticamente al seleccionar
        pass
    
    def eliminar_producto_seleccionado(self):
        """Elimina el producto seleccionado"""
        selection = self.tree_productos.selection()
        if not selection:
            messagebox.showinfo("Información", "Seleccione un producto para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este producto?"):
            try:
                # Obtener el código de barras del producto seleccionado
                item = self.tree_productos.item(selection[0])
                codigo_barras = item['values'][0]
                
                # Buscar el producto para obtener su ID
                productos = self.db.buscar_productos(codigo_barras)
                if productos:
                    producto = productos[0]
                    
                    # Eliminar producto (marcar como inactivo)
                    conn = self.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE productos SET activo = 0 WHERE id = ?", (producto['id'],))
                    conn.commit()
                    conn.close()
                    
                    messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                    self.cargar_productos()
                    self.limpiar_formulario()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar producto: {str(e)}")
    
    def ajustar_stock_dialog(self):
        """Abre un diálogo para ajustar el stock de un producto"""
        selection = self.tree_productos.selection()
        if not selection:
            messagebox.showinfo("Información", "Seleccione un producto para ajustar stock")
            return
        
        # Obtener producto
        item = self.tree_productos.item(selection[0])
        codigo_barras = item['values'][0]
        productos = self.db.buscar_productos(codigo_barras)
        
        if not productos:
            return
        
        producto = productos[0]
        
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Ajustar Stock")
        dialog.geometry("400x300")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Información del producto
        ctk.CTkLabel(
            dialog, 
            text=f"Producto: {producto['nombre']}", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        ctk.CTkLabel(
            dialog, 
            text=f"Stock actual: {producto['stock_actual']}"
        ).pack(pady=5)
        
        # Tipo de ajuste
        ctk.CTkLabel(dialog, text="Tipo de movimiento:").pack(pady=(20, 5))
        combo_tipo = ctk.CTkComboBox(
            dialog, 
            values=["Entrada (Suma)", "Salida (Resta)", "Ajuste (Establece valor exacto)"],
            width=300
        )
        combo_tipo.pack(pady=5)
        combo_tipo.set("Entrada (Suma)")
        
        # Cantidad
        ctk.CTkLabel(dialog, text="Cantidad:").pack(pady=(10, 5))
        entry_cantidad = ctk.CTkEntry(dialog, width=200)
        entry_cantidad.pack(pady=5)
        
        # Motivo
        ctk.CTkLabel(dialog, text="Motivo:").pack(pady=(10, 5))
        entry_motivo = ctk.CTkEntry(dialog, width=300, placeholder_text="Motivo del ajuste...")
        entry_motivo.pack(pady=5)
        
        def procesar_ajuste():
            try:
                cantidad = int(entry_cantidad.get())
                tipo_seleccionado = combo_tipo.get()
                motivo = entry_motivo.get() or "Ajuste manual"
                
                # Calcular nuevo stock
                stock_anterior = producto['stock_actual']
                
                if "Entrada" in tipo_seleccionado:
                    nuevo_stock = stock_anterior + cantidad
                    tipo_movimiento = 'entrada'
                elif "Salida" in tipo_seleccionado:
                    nuevo_stock = max(0, stock_anterior - cantidad)
                    tipo_movimiento = 'salida'
                else:  # Ajuste
                    nuevo_stock = cantidad
                    tipo_movimiento = 'ajuste'
                    cantidad = nuevo_stock - stock_anterior
                
                # Actualizar en la base de datos
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute(
                    "UPDATE productos SET stock_actual = ? WHERE id = ?",
                    (nuevo_stock, producto['id'])
                )
                
                # Registrar movimiento
                self.db.registrar_movimiento_inventario(
                    producto['id'], tipo_movimiento, abs(cantidad),
                    stock_anterior, nuevo_stock, motivo, 'Manual'
                )
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Éxito", "Stock ajustado correctamente")
                dialog.destroy()
                self.cargar_productos()
                
            except ValueError:
                messagebox.showerror("Error", "Ingrese una cantidad válida")
            except Exception as e:
                messagebox.showerror("Error", f"Error al ajustar stock: {str(e)}")
        
        # Botones
        frame_botones = ctk.CTkFrame(dialog)
        frame_botones.pack(pady=20)
        
        ctk.CTkButton(
            frame_botones, text="Aplicar", 
            command=procesar_ajuste,
            fg_color="green", hover_color="darkgreen"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            frame_botones, text="Cancelar", 
            command=dialog.destroy,
            fg_color="gray", hover_color="darkgray"
        ).pack(side="right", padx=10)
