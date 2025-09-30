import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
import tkinter as tk
from icon_manager import icon_manager
from colores import COLOR_BOTON_ACCION, COLOR_BOTON_ACCION_HOVER

class ComprasWindow:
    def __init__(self, master, db):
        self.db = db
        self.proveedor_seleccionado_id = None
        self.window = ctk.CTkToplevel(master, fg_color="#e3f0ff")
        self.window.title("Registrar Compras")
        self.window.geometry("1200x700")
        self.window.transient(master)
        self.window.grab_set()
        self.window.lift()
        self.window.focus_force()

        # Aplicar iconos
        icon_manager.apply_to_window(self.window)

        # Encabezado
        encabezado = ctk.CTkFrame(self.window, width=1150, height=80, fg_color="#f0f6ff")
        encabezado.place(x=20, y=10)

        # Entry de proveedor con botón de búsqueda
        self.entry_proveedor = ctk.CTkEntry(encabezado, placeholder_text="Proveedor (obligatorio)", width=200, height=35)
        self.entry_proveedor.place(x=20, y=20)

        # Botón para buscar proveedor
        btn_buscar_proveedor = ctk.CTkButton(
            encabezado,
            text="🔍",
            width=40,
            height=35,
            command=self.buscar_proveedor_dialog,
            fg_color=COLOR_BOTON_ACCION["manual"],
            hover_color=COLOR_BOTON_ACCION_HOVER["manual"]
        )
        btn_buscar_proveedor.place(x=230, y=20)

        self.entry_documento = ctk.CTkEntry(encabezado, placeholder_text="Documento (obligatorio)", width=250, height=35)
        self.entry_documento.place(x=290, y=20)
        # Selector de fecha
        import datetime
        from tkinter import StringVar
        self.fecha_var = StringVar()
        from tkcalendar import DateEntry
        hoy = datetime.date.today()
        self.entry_fecha = DateEntry(encabezado, textvariable=self.fecha_var, width=18, date_pattern='yyyy-mm-dd', year=hoy.year, month=hoy.month, day=hoy.day)
        self.entry_fecha.place(x=560, y=20)

        # Parte izquierda: productos
        self.parte1 = ctk.CTkFrame(self.window, width=570, height=500, fg_color="#f0f6ff")
        self.parte1.place(x=20, y=110)
        self.entry_producto = ctk.CTkEntry(self.parte1, placeholder_text="Producto", width=250, height=35)
        self.entry_producto.place(x=20, y=20)
        ctk.CTkButton(self.parte1, text="Buscar", width=90, height=35, fg_color=COLOR_BOTON_ACCION["cobrar"]).place(x=290, y=20)

        self.productos_tree = ttk.Treeview(self.parte1, columns=("Producto", "PrecioCompraUSD", "Stock"), show="headings", height=15)
        self.productos_tree.column("Producto", anchor="center", width=220)
        self.productos_tree.column("PrecioCompraUSD", anchor="center", width=130)
        self.productos_tree.column("Stock", anchor="center", width=80)
        self.productos_tree.heading("Producto", text="Producto")
        self.productos_tree.heading("PrecioCompraUSD", text="P. Compra USD")
        self.productos_tree.heading("Stock", text="Stock")
        self.productos_tree.place(x=20, y=80, width=520, height=390)

        self.productos_tree.bind('<Double-1>', self.agregar_producto_a_compra)

        self.cargar_productos()

        # Carrito/resumen de compra
        self.carrito = []

        # Parte derecha: resumen
        self.parte2 = ctk.CTkFrame(self.window, width=570, height=500, fg_color="#f0f6ff")
        self.parte2.place(x=610, y=110)
        ctk.CTkLabel(self.parte2, text="Resumen de la Compra", font=ctk.CTkFont(size=18, weight="bold")).place(x=20, y=20)
        self.carrito_tree = ttk.Treeview(self.parte2, columns=("Producto", "Cantidad", "Precio", "Total"), show="headings", height=10)
        self.carrito_tree.column("Producto", anchor="center", width=180)
        self.carrito_tree.column("Cantidad", anchor="center", width=80)
        self.carrito_tree.column("Precio", anchor="center", width=80)
        self.carrito_tree.column("Total", anchor="center", width=80)
        self.carrito_tree.heading("Producto", text="Producto")
        self.carrito_tree.heading("Cantidad", text="Cantidad")
        self.carrito_tree.heading("Precio", text="Precio")
        self.carrito_tree.heading("Total", text="Total")
        self.carrito_tree.place(x=20, y=60, width=520, height=320)
        ctk.CTkLabel(self.parte2, text="Total:", font=("arial", 17, "bold")).place(x=350, y=400)
        self.label_total = ctk.CTkLabel(self.parte2, text="$0.00", font=("arial", 17, "bold"))
        self.label_total.place(x=420, y=400)

        ctk.CTkButton(self.parte2, text="Registrar Compra", width=180, height=40, font=("arial", 15, "bold"), command=self.registrar_compra).place(x=20, y=450)
        ctk.CTkButton(self.parte2, text="Vaciar", width=180, height=40, font=("arial", 15, "bold"), fg_color=COLOR_BOTON_ACCION["quitar"], command=self.vaciar_carrito).place(x=220, y=450)

        self.pie = ctk.CTkFrame(self.window, width=1150, height=80)
        self.pie.place(x=20, y=630)
        botones_pie = ["Proveedores", "Cuentas por pagar", "Agregar Producto", "Categorías"]
        acciones_pie = [
            self.abrir_proveedor_formulario,
            self.abrir_cuentas_por_pagar,
            self.abrir_inventario,
            None
        ]
        for i, texto in enumerate(botones_pie):
            boton = ctk.CTkButton(
                self.pie, text=texto, width=200, height=60, font=("arial", 15, "bold"),
                command=acciones_pie[i] if acciones_pie[i] else None
            )
            boton.place(x=20 + i * 270, y=10)

    def abrir_inventario(self):
        try:
            from inventario_window import InventarioWindow
            InventarioWindow(self.window, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Inventario: {e}")

    def abrir_proveedor_formulario(self):
        """Abre la ventana completa de gestión de proveedores"""
        try:
            from proveedores_window import ProveedoresWindow
            ProveedoresWindow(self.window, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Proveedores: {e}")

    def abrir_cuentas_por_pagar(self):
        """Abre la ventana de cuentas por pagar"""
        try:
            from cuentas_por_pagar_window import CuentasPorPagarWindow
            CuentasPorPagarWindow(self.window, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Cuentas por pagar: {e}")
    
    def buscar_proveedor_dialog(self):
        """Abre diálogo para buscar y seleccionar un proveedor"""
        # Crear ventana de búsqueda
        search_window = ctk.CTkToplevel(self.window)
        search_window.title("Seleccionar Proveedor")
        search_window.geometry("800x600")
        search_window.transient(self.window)
        search_window.grab_set()
        search_window.lift()
        search_window.focus_force()
        
        # Centrar ventana
        search_window.update_idletasks()
        x = (search_window.winfo_screenwidth() - 800) // 2
        y = (search_window.winfo_screenheight() - 600) // 2
        search_window.geometry(f"800x600+{x}+{y}")
        
        # Título
        title_frame = ctk.CTkFrame(search_window)
        title_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            title_frame, 
            text="🔍 Seleccionar Proveedor", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=15)
        
        # Búsqueda
        search_frame = ctk.CTkFrame(search_window)
        search_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            search_frame,
            text="Buscar:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(15, 5), pady=15)
        
        entry_busqueda = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar por nombre, contacto, teléfono o RIF...",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        entry_busqueda.pack(side="left", fill="x", expand=True, padx=5, pady=15)
        
        # Lista de proveedores
        list_frame = ctk.CTkFrame(search_window)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ("nombre", "contacto", "telefono", "email")
        tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            height=15
        )
        
        # Configurar encabezados
        tree.heading("nombre", text="Nombre Empresa")
        tree.heading("contacto", text="Contacto")
        tree.heading("telefono", text="Teléfono")
        tree.heading("email", text="Email")
        
        # Configurar anchos
        tree.column("nombre", width=250, anchor="w")
        tree.column("contacto", width=180, anchor="w")
        tree.column("telefono", width=120, anchor="center")
        tree.column("email", width=200, anchor="w")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        scrollbar.pack(side="right", fill="y", pady=15)
        
        # Funciones internas
        def cargar_proveedores():
            """Carga la lista de proveedores"""
            for item in tree.get_children():
                tree.delete(item)
            
            try:
                proveedores = self.db.get_proveedores()
                for proveedor in proveedores:
                    tree.insert("", "end", values=(
                        proveedor['nombre'],
                        proveedor['contacto'] or '',
                        proveedor['telefono'] or '',
                        proveedor['email'] or ''
                    ), tags=(proveedor['id'], proveedor['nombre']))
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar proveedores: {e}")
        
        def buscar_proveedores(event=None):
            """Busca proveedores por término"""
            termino = entry_busqueda.get().strip()
            
            for item in tree.get_children():
                tree.delete(item)
            
            try:
                if termino:
                    proveedores = self.db.buscar_proveedores(termino)
                else:
                    proveedores = self.db.get_proveedores()
                
                for proveedor in proveedores:
                    tree.insert("", "end", values=(
                        proveedor['nombre'],
                        proveedor['contacto'] or '',
                        proveedor['telefono'] or '',
                        proveedor['email'] or ''
                    ), tags=(proveedor['id'], proveedor['nombre']))
            except Exception as e:
                messagebox.showerror("Error", f"Error en búsqueda: {e}")
        
        def seleccionar_proveedor():
            """Selecciona el proveedor y cierra la ventana"""
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("Aviso", "Seleccione un proveedor")
                return
            
            item = tree.item(selection[0])
            proveedor_id = int(item['tags'][0])
            proveedor_nombre = item['tags'][1]
            
            # Establecer el nombre en el entry de proveedor y guardar id
            self.entry_proveedor.delete(0, tk.END if hasattr(tk, 'END') else 'end')
            self.entry_proveedor.insert(0, proveedor_nombre)
            self.proveedor_seleccionado_id = proveedor_id
            
            search_window.destroy()
        
        # Bind para búsqueda en tiempo real
        entry_busqueda.bind('<KeyRelease>', buscar_proveedores)
        
        # Bind para doble clic
        tree.bind('<Double-1>', lambda e: seleccionar_proveedor())
        
        # Botones
        buttons_frame = ctk.CTkFrame(search_window)
        buttons_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(
            buttons_frame,
            text="✅ Seleccionar",
            command=seleccionar_proveedor,
            fg_color="#2fa572",
            hover_color="#106A43",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            buttons_frame,
            text="🆕 Nuevo Proveedor",
            command=lambda: self.nuevo_proveedor_desde_busqueda(search_window),
            fg_color="#ff8c00",
            hover_color="#cc7000",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            buttons_frame,
            text="❌ Cancelar",
            command=search_window.destroy,
            fg_color="#6c757d",
            hover_color="#545b62",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="right", padx=10, pady=10)
        
        # Cargar datos iniciales
        cargar_proveedores()
        
        # Focus en búsqueda
        entry_busqueda.focus()
    
    def nuevo_proveedor_desde_busqueda(self, parent_window):
        """Abre ventana para crear nuevo proveedor desde la búsqueda"""
        try:
            from proveedores_window import ProveedoresWindow
            
            def callback_actualizar():
                """Callback que se ejecuta al cerrar la ventana de proveedores"""
                # Cerrar la ventana de búsqueda actual
                parent_window.destroy()
                # Reabrir la búsqueda para mostrar el nuevo proveedor
                self.buscar_proveedor_dialog()
            
            ProveedoresWindow(parent_window, self.db, callback_actualizar)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Proveedores: {e}")
    def mostrar_dialogo_modo_compra(self, nombre_producto, unidades_por_bulto):
        """Muestra un diálogo con botones para elegir Unidad o Bulto en compras"""
        dialog = ctk.CTkToplevel(self.window)
        dialog.title("Modo de compra")
        dialog.geometry("360x160")
        dialog.transient(self.window)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text=f"¿Cómo desea comprar {nombre_producto}?\nCada bulto contiene {unidades_por_bulto} unidades.",
            font=ctk.CTkFont(size=14, weight="bold")
        ).place(x=10, y=10)
        
        resultado = {'bulto': False}
        
        def elegir_bulto():
            resultado['bulto'] = True
            dialog.destroy()

        def elegir_unidad():
            resultado['bulto'] = False
            dialog.destroy()

        btn_bulto = ctk.CTkButton(dialog, text="🧱 Bulto", width=120, height=45, command=elegir_bulto, fg_color=COLOR_BOTON_ACCION["manual"], hover_color=COLOR_BOTON_ACCION_HOVER["manual"])
        btn_unidad = ctk.CTkButton(dialog, text="🧩 Unidad", width=120, height=45, command=elegir_unidad, fg_color=COLOR_BOTON_ACCION["cobrar"], hover_color=COLOR_BOTON_ACCION_HOVER["cobrar"])

        btn_bulto.place(x=40, y=90)
        btn_unidad.place(x=190, y=90)
        
        self.window.wait_window(dialog)
        return resultado['bulto']

    def cargar_productos(self):
        """Carga todos los productos en la parte 1"""
        self.productos_tree.delete(*self.productos_tree.get_children())
        productos = self.db.get_productos()
        for prod in productos:
            precio_compra_usd = prod.get('precio_compra_usd', 0) or 0
            self.productos_tree.insert('', 'end', values=(prod['nombre'], f"{precio_compra_usd:.2f}", prod['stock_actual']), tags=(prod['id'],))

    def agregar_producto_a_compra(self, event):
        """Agrega el producto seleccionado al resumen de compra (parte 2)"""
        selected = self.productos_tree.selection()
        if not selected:
            return
        item = self.productos_tree.item(selected[0])
        nombre = item['values'][0]
        # precio mostrado es string, convertir
        try:
            precio_compra_usd = float(item['values'][1])
        except Exception:
            precio_compra_usd = 0.0
        stock = item['values'][2]
        prod_id = item['tags'][0]
        
        # Obtener información completa del producto para verificar si vende por bulto
        productos = self.db.get_productos()
        producto_completo = None
        for p in productos:
            if p['id'] == prod_id:
                producto_completo = p
                break
        
        if not producto_completo:
            messagebox.showerror("Error", "No se pudo obtener información del producto")
            return
        
        # Verificar si el producto se vende por bulto
        modo_bulto = False
        unidades_por_bulto = int(producto_completo.get('unidades_por_bulto', 0) or 0)
        
        if int(producto_completo.get('vende_al_mayor', 0) or 0) == 1 and unidades_por_bulto > 0:
            modo_bulto = self.mostrar_dialogo_modo_compra(nombre, unidades_por_bulto)

        # Solicitar cantidad según el modo
        if modo_bulto:
            cantidad_dialog = ctk.CTkInputDialog(
                text=f"Cantidad de BULTOS a comprar para {nombre}:\n(Cada bulto = {unidades_por_bulto} unidades)",
                title="Cantidad de Bultos"
            )
            cantidad_input = cantidad_dialog.get_input()
            try:
                cantidad_bultos = float(cantidad_input)
                if cantidad_bultos <= 0:
                    messagebox.showwarning("Cantidad inválida", "Ingrese una cantidad mayor a cero")
                    return
                # Convertir bultos a unidades para el inventario
                cantidad = cantidad_bultos * unidades_por_bulto
            except Exception:
                messagebox.showerror("Error", "Ingrese un número válido.")
                return
        else:
            cantidad_dialog = ctk.CTkInputDialog(
                text=f"Cantidad de UNIDADES a comprar para {nombre}:",
                title="Cantidad de Unidades"
            )
            cantidad_input = cantidad_dialog.get_input()
            try:
                cantidad = float(cantidad_input)
                if cantidad <= 0:
                    messagebox.showwarning("Cantidad inválida", "Ingrese una cantidad mayor a cero")
                    return
            except Exception:
                messagebox.showerror("Error", "Ingrese un número válido.")
                return
        
        # Solicitar precio de compra USD (editable)
        precio_dialog = ctk.CTkInputDialog(
            text=f"Precio de compra USD para {nombre} (actual: {precio_compra_usd:.2f}):",
            title="Precio Compra USD"
        )
        precio_input = precio_dialog.get_input()
        try:
            nuevo_precio_usd = float(precio_input) if precio_input not in (None, "",) else precio_compra_usd
            if nuevo_precio_usd < 0:
                messagebox.showwarning("Precio inválido", "El precio no puede ser negativo")
                return
        except Exception:
            messagebox.showerror("Error", "Ingrese un precio válido.")
            return
        
        # Si el producto ya está en el carrito, acumular cantidades y actualizar precio
        for c in self.carrito:
            if c['id'] == prod_id:
                c['cantidad'] += cantidad
                c['precio_usd'] = nuevo_precio_usd
                self.actualizar_carrito_tree()
                return
        
        # Agregar nuevo producto al carrito
        self.carrito.append({
            'id': prod_id,
            'nombre': nombre,
            'precio_usd': nuevo_precio_usd,
            'cantidad': cantidad,
            'stock': stock
        })
        self.actualizar_carrito_tree()

    def actualizar_carrito_tree(self):
        """Actualiza la tabla de resumen de compra y el total"""
        self.carrito_tree.delete(*self.carrito_tree.get_children())
        total = 0
        for idx, item in enumerate(self.carrito):
            precio_usd = float(item.get('precio_usd', 0))
            subtotal = precio_usd * float(item['cantidad'])
            total += subtotal
            self.carrito_tree.insert('', 'end', iid=idx, values=(item['nombre'], item['cantidad'], f"{precio_usd:.2f}", f"{subtotal:.2f}"))
        self.label_total.configure(text=f"${total:.2f}")
        # Permitir editar cantidad con doble clic
        self.carrito_tree.bind('<Double-1>', self.editar_cantidad_carrito)

    def editar_cantidad_carrito(self, event):
        """Permite editar la cantidad o el precio de un producto en el carrito"""
        selected = self.carrito_tree.selection()
        if not selected:
            return
        idx = int(selected[0])
        item = self.carrito[idx]
        # Preguntar si editar cantidad o precio
        opcion = ctk.CTkInputDialog(text=f"Editar para {item['nombre']}:\nEscriba 'c' para Cantidad, 'p' para Precio USD", title="Editar Item").get_input()
        if not opcion:
            return
        opcion = str(opcion).strip().lower()
        if opcion == 'c':
            cantidad = ctk.CTkInputDialog(text=f"Nueva cantidad (Stock: {item['stock']})", title="Editar Cantidad").get_input()
            if cantidad:
                try:
                    cantidad = float(cantidad)
                    if cantidad <= 0:
                        self.carrito.pop(idx)
                    else:
                        item['cantidad'] = cantidad
                    self.actualizar_carrito_tree()
                except ValueError:
                    messagebox.showerror("Error", "Ingrese un número válido.")
        elif opcion == 'p':
            precio = ctk.CTkInputDialog(text=f"Nuevo precio USD (actual: {item.get('precio_usd',0):.2f})", title="Editar Precio").get_input()
            if precio:
                try:
                    precio = float(precio)
                    if precio < 0:
                        messagebox.showwarning("Precio inválido", "El precio no puede ser negativo")
                        return
                    item['precio_usd'] = precio
                    self.actualizar_carrito_tree()
                except ValueError:
                    messagebox.showerror("Error", "Ingrese un número válido.")

    def registrar_compra(self):
        """Registra la compra (con precios y tasa) y suma cantidades a existencia"""
        proveedor = self.entry_proveedor.get().strip()
        documento = self.entry_documento.get().strip()
        fecha = self.fecha_var.get().strip() if hasattr(self, 'fecha_var') else self.entry_fecha.get().strip()
        if not proveedor or not self.proveedor_seleccionado_id:
            messagebox.showerror("Error", "El proveedor es obligatorio. Use el botón de búsqueda y seleccione uno.")
            return
        if not documento:
            messagebox.showerror("Error", "El documento es obligatorio.")
            return
        if not fecha:
            messagebox.showerror("Error", "La fecha es obligatoria.")
            return
        if not self.carrito:
            messagebox.showinfo("Información", "No hay productos en el resumen de compra.")
            return
        
        # Preparar items para la BD
        items_bd = []
        for item in self.carrito:
            items_bd.append({
                'producto_id': int(item['id']),
                'cantidad': float(item['cantidad']),
                'precio_unitario_usd': float(item.get('precio_usd', 0))
            })
        try:
            tasa = self.db.get_tasa_cambio()
            compra_id = self.db.crear_compra(
                proveedor_id=self.proveedor_seleccionado_id,
                documento=documento,
                fecha_compra=fecha,
                tasa_cambio=tasa,
                items=items_bd
            )
            messagebox.showinfo("Compra registrada", f"Compra #{compra_id} registrada y el inventario actualizado.")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar la compra: {e}")

    def vaciar_carrito(self):
        """Vacía el resumen de compra"""
        self.carrito.clear()
        self.actualizar_carrito_tree()
