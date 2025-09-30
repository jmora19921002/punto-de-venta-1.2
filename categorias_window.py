import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from icon_manager import icon_manager

class CategoriasWindow:
    def __init__(self, master, db, update_callback=None):
        self.db = db
        self.master = master
        self.update_callback = update_callback
        self.window = ctk.CTkToplevel(master)
        self.window.title("Gestión de Categorías")
        
        # Configuración responsive
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # Ventana más grande y centrada
        window_width = min(800, int(screen_width * 0.6))
        window_height = min(700, int(screen_height * 0.8))
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
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
        """Configura la interfaz de usuario mejorada"""
        # Título principal
        title_frame = ctk.CTkFrame(self.window)
        title_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            title_frame, 
            text="🏷️ Gestión de Categorías", 
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=15)
        
        # Sección de nueva categoría
        new_cat_frame = ctk.CTkFrame(self.window)
        new_cat_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            new_cat_frame, 
            text="➕ Nueva Categoría:", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        entry_frame = ctk.CTkFrame(new_cat_frame)
        entry_frame.pack(fill="x", padx=20, pady=5)
        
        self.entry_categoria = ctk.CTkEntry(
            entry_frame, 
            placeholder_text="Nombre de la nueva categoría...",
            width=500, 
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.entry_categoria.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        
        ctk.CTkButton(
            entry_frame, 
            text="➕ Registrar", 
            command=self.registrar_categoria, 
            fg_color="#2fa572", 
            hover_color="#106A43",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="right", padx=10, pady=10)
        
        # Sección de lista y edición
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Lista de categorías
        list_label = ctk.CTkLabel(
            main_frame, 
            text="📊 Lista de Categorías:", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        list_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        # Frame para la listbox con scrollbar
        listbox_frame = ctk.CTkFrame(main_frame)
        listbox_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        # Listbox mejorada
        self.listbox = tk.Listbox(
            listbox_frame, 
            font=("Consolas", 12),
            selectmode=tk.SINGLE,
            activestyle='none',
            selectbackground='#1f538d',
            selectforeground='white',
            bg='white',
            fg='black',
            borderwidth=0,
            highlightthickness=0
        )
        
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical")
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        
        self.listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y", pady=10)
        
        self.listbox.bind('<<ListboxSelect>>', self.on_select_categoria)
        
        # Sección de edición
        edit_frame = ctk.CTkFrame(main_frame)
        edit_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            edit_frame, 
            text="✏️ Editar Categoría Seleccionada:", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        edit_entry_frame = ctk.CTkFrame(edit_frame)
        edit_entry_frame.pack(fill="x", padx=20, pady=5)
        
        self.entry_editar = ctk.CTkEntry(
            edit_entry_frame, 
            placeholder_text="Seleccione una categoría para editar...",
            width=400, 
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.entry_editar.pack(side="left", padx=10, pady=10, expand=True, fill="x")
        
        # Botones de acción
        buttons_frame = ctk.CTkFrame(edit_frame)
        buttons_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            buttons_frame, 
            text="✏️ Actualizar", 
            command=self.actualizar_categoria, 
            fg_color="#ff8c00", 
            hover_color="#cc7000",
            width=140,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            buttons_frame, 
            text="🗑️ Eliminar", 
            command=self.borrar_categoria, 
            fg_color="#dc3545", 
            hover_color="#a02834",
            width=140,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="right", padx=10, pady=10)
        
        # Botón de cerrar
        close_frame = ctk.CTkFrame(self.window)
        close_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(
            close_frame, 
            text="✖ Cerrar", 
            command=self.on_closing, 
            fg_color="#6c757d", 
            hover_color="#545b62",
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=15)
        
        # Cargar datos iniciales
        self.cargar_categorias()
        
        # Focus en el campo de nueva categoría
        self.entry_categoria.focus()
    
    def on_closing(self):
        """Maneja el cierre de la ventana y actualiza la lista principal"""
        if self.update_callback:
            self.update_callback()
        self.window.destroy()
    def on_select_categoria(self, event):
        """Maneja la selección de categoría en la lista"""
        seleccion = self.listbox.curselection()
        if seleccion:
            item = self.listbox.get(seleccion[0])
            # Verificar si no es el mensaje de "no hay categorías"
            if "No hay categorías" in item:
                return
            
            try:
                # Extraer nombre de la categoría (formato: "N. ID - Nombre")
                if " - " in item:
                    nombre = item.split(" - ", 1)[1]
                    self.entry_editar.delete(0, tk.END)
                    self.entry_editar.insert(0, nombre)
            except Exception as e:
                print(f"Error al seleccionar categoría: {e}")
    def cargar_categorias(self):
        """Carga las categorías desde la base de datos con formato mejorado"""
        self.listbox.delete(0, tk.END)
        try:
            categorias = self.db.get_categorias()
            if not categorias:
                self.listbox.insert(tk.END, "No hay categorías registradas")
                return
            
            for i, cat in enumerate(categorias, 1):
                # Formato mejorado: "N° ID - Nombre"
                display_text = f"{i:2d}. {cat['id']:3d} - {cat['nombre']}"
                self.listbox.insert(tk.END, display_text)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar categorías: {e}")

    def registrar_categoria(self):
        """Registra una nueva categoría"""
        nombre = self.entry_categoria.get().strip()
        
        # Validaciones
        if not nombre:
            messagebox.showerror("Error", "El nombre de la categoría es obligatorio")
            self.entry_categoria.focus()
            return
            
        if len(nombre) < 2:
            messagebox.showerror("Error", "El nombre debe tener al menos 2 caracteres")
            self.entry_categoria.focus()
            return
            
        if len(nombre) > 50:
            messagebox.showerror("Error", "El nombre no puede exceder 50 caracteres")
            self.entry_categoria.focus()
            return
            
        try:
            # Verificar si ya existe una categoría con ese nombre
            categorias_existentes = self.db.get_categorias()
            for cat in categorias_existentes:
                if cat['nombre'].lower() == nombre.lower():
                    messagebox.showerror(
                        "Error", 
                        f"Ya existe una categoría con el nombre '{nombre}'"
                    )
                    self.entry_categoria.focus()
                    return
            
            # Registrar la nueva categoría
            self.db.agregar_categoria(nombre)
            self.cargar_categorias()
            self.entry_categoria.delete(0, tk.END)
            
            messagebox.showinfo(
                "✓ Éxito", 
                f"Categoría '{nombre}' registrada exitosamente"
            )
            
            # Focus para siguiente entrada
            self.entry_categoria.focus()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al registrar categoría: {str(e)}")
    def borrar_categoria(self):
        """Elimina la categoría seleccionada"""
        seleccion = self.listbox.curselection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione una categoría para eliminar")
            return
        
        item = self.listbox.get(seleccion[0])
        
        # Verificar si no es el mensaje de "no hay categorías"
        if "No hay categorías" in item:
            messagebox.showwarning("Aviso", "No hay categorías para eliminar")
            return
        
        try:
            # Extraer ID de la categoría (formato: "N. ID - Nombre")
            parts = item.split(". ", 1)[1].split(" - ", 1)
            categoria_id = int(parts[0].strip())
            categoria_nombre = parts[1] if len(parts) > 1 else "Desconocido"
            
            # Confirmar eliminación
            respuesta = messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Está seguro de que desea eliminar la categoría:\n\n'{categoria_nombre}'?\n\nEsta acción no se puede deshacer."
            )
            
            if respuesta:
                self.db.eliminar_categoria(categoria_id)
                self.cargar_categorias()
                self.entry_editar.delete(0, tk.END)
                messagebox.showinfo("✓ Eliminado", f"Categoría '{categoria_nombre}' eliminada exitosamente")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar categoría: {str(e)}")
    def actualizar_categoria(self):
        """Actualiza la categoría seleccionada"""
        seleccion = self.listbox.curselection()
        if not seleccion:
            messagebox.showerror("Error", "Seleccione una categoría para actualizar")
            return
            
        item = self.listbox.get(seleccion[0])
        
        # Verificar si no es el mensaje de "no hay categorías"
        if "No hay categorías" in item:
            messagebox.showwarning("Aviso", "No hay categorías para actualizar")
            return
        
        nuevo_nombre = self.entry_editar.get().strip()
        if not nuevo_nombre:
            messagebox.showerror("Error", "Ingrese el nuevo nombre de la categoría")
            self.entry_editar.focus()
            return
            
        try:
            # Extraer ID de la categoría (formato: "N. ID - Nombre")
            parts = item.split(". ", 1)[1].split(" - ", 1)
            categoria_id = int(parts[0].strip())
            nombre_actual = parts[1] if len(parts) > 1 else "Desconocido"
            
            # Verificar si el nombre realmente cambió
            if nuevo_nombre == nombre_actual:
                messagebox.showinfo("Sin cambios", "El nombre de la categoría no ha cambiado")
                return
            
            self.db.actualizar_categoria(categoria_id, nuevo_nombre)
            self.cargar_categorias()
            self.entry_editar.delete(0, tk.END)
            messagebox.showinfo(
                "✓ Actualizado", 
                f"Categoría actualizada exitosamente:\n\nDe: '{nombre_actual}'\nA: '{nuevo_nombre}'"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar categoría: {str(e)}")
