"""
Ventana de gestión de proveedores
Permite registrar, editar, eliminar y buscar proveedores
"""

import customtkinter as ctk
from tkinter import messagebox, ttk
from colores_modernos import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, BACKGROUND_COLOR, CARD_COLOR, TEXT_COLOR, SUBTEXT_COLOR, SUCCESS_COLOR, ERROR_COLOR, BUTTON_COLOR, BUTTON_TEXT_COLOR, BORDER_RADIUS, FONT_FAMILY, TITLE_FONT_SIZE, SUBTITLE_FONT_SIZE, TEXT_FONT_SIZE, BUTTON_FONT_SIZE
import tkinter as tk
from icon_manager import icon_manager

class ProveedoresWindow:
    def __init__(self, master, db, update_callback=None):
        self.db = db
        self.master = master
        self.update_callback = update_callback
        self.proveedor_seleccionado = None
        
        self.window = ctk.CTkToplevel(master, fg_color=BACKGROUND_COLOR)
        self.window.title("Gestión de Proveedores")
        
        # Configuración responsive
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Ventana grande y centrada (aumentada para ver claramente los botones)
        window_width = min(1200, int(screen_width * 0.9))
        window_height = min(900, int(screen_height * 0.92))
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Establecer tamaño y asegurar redimensionable
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.minsize(1000, 800)
        self.window.transient(master)
        self.window.grab_set()
        self.window.lift()
        self.window.focus_force()
        
        # Configurar protocolo de cierre
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Aplicar iconos
        icon_manager.apply_to_window(self.window)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Título principal
        title_frame = ctk.CTkFrame(self.window)
        title_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            title_frame, 
            text="🏢 Gestión de Proveedores", 
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=20)
        
        # Frame principal con dos paneles
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Panel izquierdo - Formulario
        self.setup_form_panel(main_frame)
        
        # Panel derecho - Lista y búsqueda
        self.setup_list_panel(main_frame)
        
        # Frame de botones inferiores
        self.setup_action_buttons()
        
        # Cargar datos iniciales
        self.cargar_proveedores()
        
    def setup_form_panel(self, parent):
        """Configura el panel del formulario"""
        form_frame = ctk.CTkFrame(parent)
        form_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Título del formulario
        form_title = ctk.CTkLabel(
            form_frame, 
            text="📝 Datos del Proveedor", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        form_title.pack(pady=(15, 20))
        
        # Campos del formulario
        self.setup_form_fields(form_frame)
        
    def setup_form_fields(self, parent):
        """Configura los campos del formulario"""
        # Frame scrollable para los campos
        fields_frame = ctk.CTkScrollableFrame(parent)
        fields_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Nombre (obligatorio)
        ctk.CTkLabel(
            fields_frame, 
            text="* Nombre de la Empresa:", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        self.entry_nombre = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Ej: Distribuidora ABC C.A.",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.entry_nombre.pack(fill="x", pady=(0, 15))
        
        # Persona de contacto
        ctk.CTkLabel(
            fields_frame, 
            text="Persona de Contacto:", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.entry_contacto = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Ej: Juan Pérez",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.entry_contacto.pack(fill="x", pady=(0, 15))
        
        # Teléfono
        ctk.CTkLabel(
            fields_frame, 
            text="Teléfono:", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.entry_telefono = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Ej: 0212-555-1234",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.entry_telefono.pack(fill="x", pady=(0, 15))
        
        # Email
        ctk.CTkLabel(
            fields_frame, 
            text="Correo Electrónico:", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.entry_email = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Ej: contacto@empresa.com",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.entry_email.pack(fill="x", pady=(0, 15))
        
        # RIF
        ctk.CTkLabel(
            fields_frame, 
            text="RIF:", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.entry_rif = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Ej: J-12345678-9",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.entry_rif.pack(fill="x", pady=(0, 15))
        
        # Dirección
        ctk.CTkLabel(
            fields_frame, 
            text="Dirección:", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.entry_direccion = ctk.CTkEntry(
            fields_frame,
            placeholder_text="Dirección completa...",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.entry_direccion.pack(fill="x", pady=(0, 15))
        
        # Notas
        ctk.CTkLabel(
            fields_frame, 
            text="Notas:", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(0, 5))
        
        self.text_notas = ctk.CTkTextbox(
            fields_frame,
            height=80,
            font=ctk.CTkFont(size=12)
        )
        self.text_notas.pack(fill="x", pady=(0, 15))
        
        # Botones del formulario
        form_buttons = ctk.CTkFrame(fields_frame)
        form_buttons.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            form_buttons,
            text="✅ Guardar Proveedor",
            command=self.guardar_proveedor,
            fg_color="#2fa572",
            hover_color="#106A43",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        ctk.CTkButton(
            form_buttons,
            text="🔄 Actualizar",
            command=self.actualizar_proveedor,
            fg_color="#ff8c00",
            hover_color="#cc7000",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(5, 10), fill="x", expand=True)
        
        ctk.CTkButton(
            form_buttons,
            text="🗑️ Eliminar",
            command=self.eliminar_proveedor,
            fg_color="#dc3545",
            hover_color="#a02834",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="right", padx=(10, 0), fill="x", expand=True)
        
        # Botón limpiar formulario
        ctk.CTkButton(
            form_buttons,
            text="🧹 Limpiar",
            command=self.limpiar_formulario,
            fg_color="#6c757d",
            hover_color="#545b62",
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(fill="x", pady=(10, 0))
        
    def setup_list_panel(self, parent):
        """Configura el panel de lista de proveedores"""
        list_frame = ctk.CTkFrame(parent)
        list_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Título de la lista
        list_title = ctk.CTkLabel(
            list_frame, 
            text="📋 Lista de Proveedores", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        list_title.pack(pady=(15, 10))
        
        # Búsqueda
        search_frame = ctk.CTkFrame(list_frame)
        search_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(
            search_frame,
            text="🔍 Buscar:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(10, 5))
        
        self.entry_busqueda = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar por nombre, contacto, teléfono o RIF...",
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.entry_busqueda.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_busqueda.bind('<KeyRelease>', self.buscar_proveedores)
        
        ctk.CTkButton(
            search_frame,
            text="🔄",
            command=self.cargar_proveedores,
            width=40,
            height=35
        ).pack(side="right", padx=(5, 10))
        
        # Treeview para lista de proveedores
        self.setup_treeview(list_frame)
        
    def setup_treeview(self, parent):
        """Configura el Treeview de proveedores"""
        tree_frame = ctk.CTkFrame(parent)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Configurar Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("nombre", "contacto", "telefono", "email"),
            show="headings",
            height=15
        )
        
        # Configurar encabezados
        self.tree.heading("nombre", text="Nombre Empresa")
        self.tree.heading("contacto", text="Contacto")
        self.tree.heading("telefono", text="Teléfono")
        self.tree.heading("email", text="Email")
        
        # Configurar anchos de columna
        self.tree.column("nombre", width=200, anchor="w")
        self.tree.column("contacto", width=150, anchor="w")
        self.tree.column("telefono", width=120, anchor="center")
        self.tree.column("email", width=180, anchor="w")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        self.tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        # Bind para selección
        self.tree.bind('<<TreeviewSelect>>', self.on_select_proveedor)
        
    def setup_action_buttons(self):
        """Configura los botones de acción principales"""
        buttons_frame = ctk.CTkFrame(self.window)
        buttons_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Información
        info_frame = ctk.CTkFrame(buttons_frame)
        info_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            info_frame,
            text="* Campos obligatorios",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(side="left", padx=10, pady=10)
        
        # Botón cerrar
        ctk.CTkButton(
            buttons_frame,
            text="✖ Cerrar",
            command=self.on_closing,
            fg_color="#6c757d",
            hover_color="#545b62",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="right", padx=10, pady=10)
        
    def cargar_proveedores(self):
        """Carga la lista de proveedores"""
        try:
            # Limpiar tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            proveedores = self.db.get_proveedores()
            
            for proveedor in proveedores:
                self.tree.insert("", "end", values=(
                    proveedor['nombre'],
                    proveedor['contacto'] or '',
                    proveedor['telefono'] or '',
                    proveedor['email'] or ''
                ), tags=(proveedor['id'],))
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar proveedores: {e}")
    
    def buscar_proveedores(self, event=None):
        """Busca proveedores por término"""
        termino = self.entry_busqueda.get().strip()
        
        try:
            # Limpiar tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            if termino:
                proveedores = self.db.buscar_proveedores(termino)
            else:
                proveedores = self.db.get_proveedores()
            
            for proveedor in proveedores:
                self.tree.insert("", "end", values=(
                    proveedor['nombre'],
                    proveedor['contacto'] or '',
                    proveedor['telefono'] or '',
                    proveedor['email'] or ''
                ), tags=(proveedor['id'],))
        
        except Exception as e:
            messagebox.showerror("Error", f"Error en búsqueda: {e}")
    
    def on_select_proveedor(self, event):
        """Maneja la selección de un proveedor"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        proveedor_id = int(item['tags'][0])
        
        try:
            proveedor = self.db.get_proveedor_by_id(proveedor_id)
            if proveedor:
                self.cargar_datos_formulario(proveedor)
                self.proveedor_seleccionado = proveedor_id
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {e}")
    
    def cargar_datos_formulario(self, proveedor):
        """Carga los datos del proveedor en el formulario"""
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, proveedor['nombre'])
        
        self.entry_contacto.delete(0, tk.END)
        if proveedor['contacto']:
            self.entry_contacto.insert(0, proveedor['contacto'])
        
        self.entry_telefono.delete(0, tk.END)
        if proveedor['telefono']:
            self.entry_telefono.insert(0, proveedor['telefono'])
        
        self.entry_email.delete(0, tk.END)
        if proveedor['email']:
            self.entry_email.insert(0, proveedor['email'])
        
        self.entry_rif.delete(0, tk.END)
        if proveedor['rif']:
            self.entry_rif.insert(0, proveedor['rif'])
        
        self.entry_direccion.delete(0, tk.END)
        if proveedor['direccion']:
            self.entry_direccion.insert(0, proveedor['direccion'])
        
        self.text_notas.delete("1.0", tk.END)
        if proveedor['notas']:
            self.text_notas.insert("1.0", proveedor['notas'])
    
    def limpiar_formulario(self):
        """Limpia todos los campos del formulario"""
        self.entry_nombre.delete(0, tk.END)
        self.entry_contacto.delete(0, tk.END)
        self.entry_telefono.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_rif.delete(0, tk.END)
        self.entry_direccion.delete(0, tk.END)
        self.text_notas.delete("1.0", tk.END)
        self.proveedor_seleccionado = None
        
        # Limpiar selección del tree
        for item in self.tree.selection():
            self.tree.selection_remove(item)
    
    def validar_formulario(self):
        """Valida los datos del formulario"""
        nombre = self.entry_nombre.get().strip()
        
        if not nombre:
            messagebox.showerror("Error", "El nombre de la empresa es obligatorio")
            self.entry_nombre.focus()
            return False
        
        if len(nombre) < 2:
            messagebox.showerror("Error", "El nombre debe tener al menos 2 caracteres")
            self.entry_nombre.focus()
            return False
        
        # Validar email si se proporciona
        email = self.entry_email.get().strip()
        if email and '@' not in email:
            messagebox.showerror("Error", "Ingrese un email válido")
            self.entry_email.focus()
            return False
        
        return True
    
    def guardar_proveedor(self):
        """Guarda un nuevo proveedor"""
        if not self.validar_formulario():
            return
        
        try:
            proveedor_id = self.db.agregar_proveedor(
                nombre=self.entry_nombre.get().strip(),
                contacto=self.entry_contacto.get().strip() or None,
                telefono=self.entry_telefono.get().strip() or None,
                email=self.entry_email.get().strip() or None,
                direccion=self.entry_direccion.get().strip() or None,
                rif=self.entry_rif.get().strip() or None,
                notas=self.text_notas.get("1.0", tk.END).strip() or None
            )
            
            messagebox.showinfo(
                "✅ Éxito", 
                f"Proveedor registrado exitosamente\nID: {proveedor_id}"
            )
            
            self.limpiar_formulario()
            self.cargar_proveedores()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar proveedor: {e}")
    
    def actualizar_proveedor(self):
        """Actualiza el proveedor seleccionado"""
        if not self.proveedor_seleccionado:
            messagebox.showerror("Error", "Seleccione un proveedor para actualizar")
            return
        
        if not self.validar_formulario():
            return
        
        try:
            success = self.db.actualizar_proveedor(
                proveedor_id=self.proveedor_seleccionado,
                nombre=self.entry_nombre.get().strip(),
                contacto=self.entry_contacto.get().strip() or None,
                telefono=self.entry_telefono.get().strip() or None,
                email=self.entry_email.get().strip() or None,
                direccion=self.entry_direccion.get().strip() or None,
                rif=self.entry_rif.get().strip() or None,
                notas=self.text_notas.get("1.0", tk.END).strip() or None
            )
            
            if success:
                messagebox.showinfo("✅ Éxito", "Proveedor actualizado exitosamente")
                self.cargar_proveedores()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el proveedor")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar proveedor: {e}")
    
    def eliminar_proveedor(self):
        """Elimina el proveedor seleccionado"""
        if not self.proveedor_seleccionado:
            messagebox.showerror("Error", "Seleccione un proveedor para eliminar")
            return
        
        nombre = self.entry_nombre.get().strip()
        respuesta = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar el proveedor:\n\n'{nombre}'?\n\nEsta acción no se puede deshacer."
        )
        
        if respuesta:
            try:
                success = self.db.eliminar_proveedor(self.proveedor_seleccionado)
                if success:
                    messagebox.showinfo("✅ Eliminado", "Proveedor eliminado exitosamente")
                    self.limpiar_formulario()
                    self.cargar_proveedores()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el proveedor")
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar proveedor: {e}")
    
    def on_closing(self):
        """Maneja el cierre de la ventana"""
        if self.update_callback:
            self.update_callback()
        self.window.destroy()
