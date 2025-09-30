import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
from colores import COLOR_BOTON_ACCION, COLOR_BOTON_ACCION_HOVER

class ClientesWindow:
    def __init__(self, parent, database_manager):
        self.parent = parent
        self.db = database_manager
        
        # Crear ventana de clientes
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Gestión de Clientes")
        self.window.geometry("1000x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.cargar_clientes()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Frame principal dividido en dos secciones
        
        # Sección izquierda - Lista de clientes
        self.frame_lista = ctk.CTkFrame(self.window, width=600, height=580)
        self.frame_lista.place(x=10, y=10)
        
        # Sección derecha - Formulario de cliente
        self.frame_formulario = ctk.CTkFrame(self.window, width=370, height=580)
        self.frame_formulario.place(x=620, y=10)
        
        self.setup_lista_clientes()
        self.setup_formulario_cliente()
    
    def setup_lista_clientes(self):
        """Configura la sección de lista de clientes"""
        # Título y búsqueda
        ctk.CTkLabel(
            self.frame_lista, 
            text="Lista de Clientes", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).place(x=10, y=10)
        
        # Búsqueda
        self.entry_buscar = ctk.CTkEntry(
            self.frame_lista, 
            placeholder_text="Buscar cliente...", 
            width=400, height=35
        )
        self.entry_buscar.place(x=10, y=50)
        self.entry_buscar.bind('<KeyRelease>', self.buscar_clientes)
        
        btn_buscar = ctk.CTkButton(
            self.frame_lista, text="🔍", width=50, height=35,
            command=self.buscar_clientes_manual
        )
        btn_buscar.place(x=420, y=50)
        
        btn_refresh = ctk.CTkButton(
            self.frame_lista, text="🔄", width=50, height=35,
            command=self.cargar_clientes
        )
        btn_refresh.place(x=480, y=50)
        
        btn_nuevo = ctk.CTkButton(
            self.frame_lista, text="➕ Nuevo", width=100, height=35,
            command=self.nuevo_cliente,
            fg_color=COLOR_BOTON_ACCION["cobrar"], hover_color=COLOR_BOTON_ACCION_HOVER["cobrar"]
        )
        btn_nuevo.place(x=480, y=95)
        
        # Treeview para clientes
        self.setup_treeview_clientes()
        
        # Botones de acción
        btn_editar = ctk.CTkButton(
            self.frame_lista, text="✏️ Editar", width=100, height=40,
            command=self.editar_cliente_seleccionado
        )
        btn_editar.place(x=10, y=520)
        
        btn_eliminar = ctk.CTkButton(
            self.frame_lista, text="🗑️ Eliminar", width=100, height=40,
            command=self.eliminar_cliente_seleccionado,
            fg_color=COLOR_BOTON_ACCION["quitar"], hover_color=COLOR_BOTON_ACCION_HOVER["quitar"]
        )
        btn_eliminar.place(x=120, y=520)
        
        btn_historial = ctk.CTkButton(
            self.frame_lista, text="📋 Historial", width=100, height=40,
            command=self.ver_historial_cliente
        )
        btn_historial.place(x=240, y=520)
    
    def setup_treeview_clientes(self):
        """Configura el Treeview de clientes"""
        # Frame para treeview
        tree_frame = tk.Frame(self.frame_lista, bg='white')
        tree_frame.place(x=10, y=140, width=570, height=370)
        
        # Treeview
        self.tree_clientes = ttk.Treeview(
            tree_frame,
            columns=("nombre", "apellido", "telefono", "email", "fecha_registro"),
            show="headings",
            height=18
        )
        
        # Configurar encabezados
        headers = {
            "nombre": ("Nombre", 120),
            "apellido": ("Apellido", 120),
            "telefono": ("Teléfono", 100),
            "email": ("Email", 150),
            "fecha_registro": ("Registro", 100)
        }
        
        for col, (text, width) in headers.items():
            self.tree_clientes.heading(col, text=text)
            self.tree_clientes.column(col, width=width, anchor="w")
        
        # Scrollbars
        scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_clientes.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree_clientes.xview)
        self.tree_clientes.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Pack
        self.tree_clientes.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        
        # Eventos
        self.tree_clientes.bind('<<TreeviewSelect>>', self.seleccionar_cliente)
        self.tree_clientes.bind('<Double-1>', self.editar_cliente_seleccionado)
    
    def setup_formulario_cliente(self):
        """Configura el formulario de cliente"""
        ctk.CTkLabel(
            self.frame_formulario, 
            text="Datos del Cliente", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).place(x=10, y=10)
        
        # Campos del formulario
        y_pos = 60
        spacing = 50
        
        # Nombre
        ctk.CTkLabel(self.frame_formulario, text="Nombre:*").place(x=10, y=y_pos)
        self.entry_nombre = ctk.CTkEntry(self.frame_formulario, width=300, height=35)
        self.entry_nombre.place(x=10, y=y_pos + 25)
        
        # Apellido
        y_pos += spacing
        ctk.CTkLabel(self.frame_formulario, text="Apellido:").place(x=10, y=y_pos)
        self.entry_apellido = ctk.CTkEntry(self.frame_formulario, width=300, height=35)
        self.entry_apellido.place(x=10, y=y_pos + 25)
        
        # Teléfono
        y_pos += spacing
        ctk.CTkLabel(self.frame_formulario, text="Teléfono:").place(x=10, y=y_pos)
        self.entry_telefono = ctk.CTkEntry(self.frame_formulario, width=300, height=35)
        self.entry_telefono.place(x=10, y=y_pos + 25)
        
        # Email
        y_pos += spacing
        ctk.CTkLabel(self.frame_formulario, text="Email:").place(x=10, y=y_pos)
        self.entry_email = ctk.CTkEntry(self.frame_formulario, width=300, height=35)
        self.entry_email.place(x=10, y=y_pos + 25)
        
        # Dirección
        y_pos += spacing
        ctk.CTkLabel(self.frame_formulario, text="Dirección:").place(x=10, y=y_pos)
        self.text_direccion = ctk.CTkTextbox(self.frame_formulario, width=300, height=80)
        self.text_direccion.place(x=10, y=y_pos + 25)
        
        # Botones del formulario
        y_pos += 120
        
        self.btn_guardar = ctk.CTkButton(
            self.frame_formulario, text="💾 Guardar", width=140, height=50,
            command=self.guardar_cliente,
            fg_color=COLOR_BOTON_ACCION["guardar"], hover_color=COLOR_BOTON_ACCION_HOVER["guardar"],
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.btn_guardar.place(x=10, y=y_pos)
        
        self.btn_cancelar = ctk.CTkButton(
            self.frame_formulario, text="❌ Cancelar", width=140, height=50,
            command=self.limpiar_formulario,
            fg_color=COLOR_BOTON_ACCION["limpiar"], hover_color=COLOR_BOTON_ACCION_HOVER["limpiar"]
        )
        self.btn_cancelar.place(x=160, y=y_pos)
        
        self.btn_actualizar = ctk.CTkButton(
            self.frame_formulario, text="🔄 Actualizar", width=140, height=50,
            command=self.actualizar_cliente,
            fg_color=COLOR_BOTON_ACCION["guardar"], hover_color=COLOR_BOTON_ACCION_HOVER["guardar"]
        )
        self.btn_actualizar.place(x=160, y=y_pos)
        self.btn_actualizar.place_forget()  # Ocultar inicialmente
        
        # Variables de estado
        self.cliente_editando = None
    
    def cargar_clientes(self, clientes=None):
        """Carga los clientes en el treeview"""
        # Limpiar treeview
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        
        if clientes is None:
            # Obtener clientes desde la base de datos
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nombre, apellido, telefono, email, 
                       DATE(fecha_registro) as fecha_registro
                FROM clientes 
                WHERE activo = 1 
                ORDER BY nombre, apellido
            """)
            clientes_data = cursor.fetchall()
            conn.close()
            
            clientes = [dict(zip([col[0] for col in cursor.description], row)) for row in clientes_data]
        
        # Insertar clientes
        for cliente in clientes:
            self.tree_clientes.insert('', 'end', values=(
                cliente['nombre'],
                cliente.get('apellido', ''),
                cliente.get('telefono', ''),
                cliente.get('email', ''),
                cliente.get('fecha_registro', '')
            ))
    
    def buscar_clientes(self, event=None):
        """Busca clientes en tiempo real"""
        termino = self.entry_buscar.get()
        if len(termino) >= 2:
            clientes = self.db.buscar_cliente(termino)
            # Convertir a formato esperado
            clientes_formatted = []
            for cliente in clientes:
                clientes_formatted.append({
                    'nombre': cliente['nombre'],
                    'apellido': cliente.get('apellido', ''),
                    'telefono': cliente.get('telefono', ''),
                    'email': cliente.get('email', ''),
                    'fecha_registro': ''  # Agregar fecha si es necesario
                })
            self.cargar_clientes(clientes_formatted)
        elif len(termino) == 0:
            self.cargar_clientes()
    
    def buscar_clientes_manual(self):
        """Busca clientes manualmente"""
        termino = self.entry_buscar.get()
        if termino:
            clientes = self.db.buscar_cliente(termino)
            clientes_formatted = []
            for cliente in clientes:
                clientes_formatted.append({
                    'nombre': cliente['nombre'],
                    'apellido': cliente.get('apellido', ''),
                    'telefono': cliente.get('telefono', ''),
                    'email': cliente.get('email', ''),
                    'fecha_registro': ''
                })
            self.cargar_clientes(clientes_formatted)
        else:
            self.cargar_clientes()
    
    def seleccionar_cliente(self, event=None):
        """Maneja la selección de un cliente en el treeview"""
        selection = self.tree_clientes.selection()
        if not selection:
            return
        
        # Obtener datos del cliente seleccionado
        item = self.tree_clientes.item(selection[0])
        valores = item['values']
        
        # Buscar el cliente completo en la base de datos
        nombre = valores[0]
        apellido = valores[1] if len(valores) > 1 else ""
        
        # Buscar cliente por nombre y apellido
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM clientes 
            WHERE nombre = ? AND apellido = ? AND activo = 1
        """, (nombre, apellido))
        cliente_data = cursor.fetchone()
        conn.close()
        
        if cliente_data:
            cliente = dict(zip([col[0] for col in cursor.description], cliente_data))
            self.cargar_cliente_en_formulario(cliente)
    
    def cargar_cliente_en_formulario(self, cliente):
        """Carga los datos de un cliente en el formulario"""
        # Limpiar formulario
        self.limpiar_formulario()
        
        # Cargar datos
        self.entry_nombre.insert(0, cliente['nombre'])
        self.entry_apellido.insert(0, cliente.get('apellido', ''))
        self.entry_telefono.insert(0, cliente.get('telefono', ''))
        self.entry_email.insert(0, cliente.get('email', ''))
        
        if cliente.get('direccion'):
            self.text_direccion.insert('1.0', cliente['direccion'])
        
        # Cambiar a modo edición
        self.cliente_editando = cliente
        self.btn_guardar.place_forget()
        self.btn_actualizar.place(x=160, y=460)
    
    def nuevo_cliente(self):
        """Prepara el formulario para un nuevo cliente"""
        self.limpiar_formulario()
        self.cliente_editando = None
        self.btn_actualizar.place_forget()
        self.btn_guardar.place(x=10, y=460)
        
        # Enfocar en el primer campo
        self.entry_nombre.focus()
    
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        self.entry_nombre.delete(0, 'end')
        self.entry_apellido.delete(0, 'end')
        self.entry_telefono.delete(0, 'end')
        self.entry_email.delete(0, 'end')
        self.text_direccion.delete('1.0', 'end')
        
        self.cliente_editando = None
        self.btn_actualizar.place_forget()
        self.btn_guardar.place(x=10, y=460)
    
    def validar_formulario(self):
        """Valida los datos del formulario"""
        errores = []
        
        if not self.entry_nombre.get().strip():
            errores.append("El nombre es requerido")
        
        # Validar email si se proporciona
        email = self.entry_email.get().strip()
        if email and '@' not in email:
            errores.append("El email no tiene un formato válido")
        
        # Validar teléfono si se proporciona
        telefono = self.entry_telefono.get().strip()
        if telefono and not telefono.replace('-', '').replace(' ', '').replace('(', '').replace(')', '').isdigit():
            errores.append("El teléfono debe contener solo números")
        
        if errores:
            messagebox.showerror("Errores de validación", "\\n".join(errores))
            return False
        
        return True
    
    def guardar_cliente(self):
        """Guarda un nuevo cliente"""
        if not self.validar_formulario():
            return
        
        try:
            cliente_id = self.db.agregar_cliente(
                nombre=self.entry_nombre.get().strip(),
                apellido=self.entry_apellido.get().strip(),
                telefono=self.entry_telefono.get().strip(),
                email=self.entry_email.get().strip(),
                direccion=self.text_direccion.get('1.0', 'end').strip()
            )
            
            messagebox.showinfo("Éxito", "Cliente guardado correctamente")
            self.limpiar_formulario()
            self.cargar_clientes()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar cliente: {str(e)}")
    
    def actualizar_cliente(self):
        """Actualiza un cliente existente"""
        if not self.cliente_editando:
            return
        
        if not self.validar_formulario():
            return
        
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE clientes 
                SET nombre = ?, apellido = ?, telefono = ?, email = ?, direccion = ?
                WHERE id = ?
            """, (
                self.entry_nombre.get().strip(),
                self.entry_apellido.get().strip(),
                self.entry_telefono.get().strip(),
                self.entry_email.get().strip(),
                self.text_direccion.get('1.0', 'end').strip(),
                self.cliente_editando['id']
            ))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Éxito", "Cliente actualizado correctamente")
            self.limpiar_formulario()
            self.cargar_clientes()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar cliente: {str(e)}")
    
    def editar_cliente_seleccionado(self, event=None):
        """Edita el cliente seleccionado"""
        selection = self.tree_clientes.selection()
        if not selection:
            messagebox.showinfo("Información", "Seleccione un cliente para editar")
            return
        
        # El cliente ya se carga automáticamente al seleccionar
        pass
    
    def eliminar_cliente_seleccionado(self):
        """Elimina el cliente seleccionado"""
        selection = self.tree_clientes.selection()
        if not selection:
            messagebox.showinfo("Información", "Seleccione un cliente para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este cliente?"):
            try:
                if self.cliente_editando:
                    # Eliminar cliente (marcar como inactivo)
                    conn = self.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("UPDATE clientes SET activo = 0 WHERE id = ?", (self.cliente_editando['id'],))
                    conn.commit()
                    conn.close()
                    
                    messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                    self.cargar_clientes()
                    self.limpiar_formulario()
                else:
                    messagebox.showwarning("Advertencia", "No hay cliente seleccionado")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar cliente: {str(e)}")
    
    def ver_historial_cliente(self):
        """Muestra el historial de compras del cliente seleccionado"""
        if not self.cliente_editando:
            messagebox.showinfo("Información", "Seleccione un cliente para ver su historial")
            return
        
        # Crear ventana de historial
        ventana_historial = ctk.CTkToplevel(self.window)
        ventana_historial.title(f"Historial - {self.cliente_editando['nombre']}")
        ventana_historial.geometry("800x500")
        ventana_historial.transient(self.window)
        
        # Obtener historial de compras
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.fecha_venta, v.total, v.metodo_pago, 
                   COUNT(dv.id) as items_comprados
            FROM ventas v
            LEFT JOIN detalle_ventas dv ON v.id = dv.venta_id
            WHERE v.cliente_id = ?
            GROUP BY v.id
            ORDER BY v.fecha_venta DESC
        """, (self.cliente_editando['id'],))
        
        historial = cursor.fetchall()
        conn.close()
        
        # Información del cliente
        info_frame = ctk.CTkFrame(ventana_historial, width=780, height=100)
        info_frame.place(x=10, y=10)
        
        cliente_info = f"""Cliente: {self.cliente_editando['nombre']} {self.cliente_editando.get('apellido', '')}
Teléfono: {self.cliente_editando.get('telefono', 'No registrado')}
Email: {self.cliente_editando.get('email', 'No registrado')}
Total de compras: {len(historial)}"""
        
        ctk.CTkLabel(info_frame, text=cliente_info, justify="left").place(x=10, y=10)
        
        # Lista de compras
        ctk.CTkLabel(
            ventana_historial, 
            text="Historial de Compras", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).place(x=10, y=120)
        
        # Treeview para historial
        tree_frame = tk.Frame(ventana_historial, bg='white')
        tree_frame.place(x=10, y=150, width=780, height=340)
        
        tree_historial = ttk.Treeview(
            tree_frame,
            columns=("fecha", "total", "metodo_pago", "items"),
            show="headings"
        )
        
        tree_historial.heading("fecha", text="Fecha")
        tree_historial.heading("total", text="Total")
        tree_historial.heading("metodo_pago", text="Método Pago")
        tree_historial.heading("items", text="Items")
        
        tree_historial.column("fecha", width=200)
        tree_historial.column("total", width=150)
        tree_historial.column("metodo_pago", width=150)
        tree_historial.column("items", width=100)
        
        # Insertar datos del historial
        total_gastado = 0
        for compra in historial:
            tree_historial.insert('', 'end', values=(
                compra[0][:16],  # Fecha sin microsegundos
                f"${compra[1]:.2f}",
                compra[2].title(),
                compra[3]
            ))
            total_gastado += compra[1]
        
        scrollbar_hist = ttk.Scrollbar(tree_frame, orient="vertical", command=tree_historial.yview)
        tree_historial.configure(yscrollcommand=scrollbar_hist.set)
        
        tree_historial.pack(side="left", fill="both", expand=True)
        scrollbar_hist.pack(side="right", fill="y")
        
        # Resumen
        ctk.CTkLabel(
            ventana_historial, 
            text=f"Total gastado: ${total_gastado:.2f}", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).place(x=10, y=500)
