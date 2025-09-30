import customtkinter as ctk
from tkinter import messagebox, ttk

class UsuariosWindow:
    def __init__(self, master, db):
        self.db = db
        self.window = ctk.CTkToplevel(master, fg_color="#FFFFFF")
        self.window.title("Gestión de Usuarios")
        self.window.geometry("700x500")
        self.window.transient(master)
        self.window.grab_set()
        self.window.lift()
        self.window.focus_force()
        ctk.CTkLabel(self.window, text="Gestión de Usuarios", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        # Frame para lista de usuarios
        self.frame_lista = ctk.CTkFrame(self.window, fg_color="#e3f0ff")
        self.frame_lista.pack(side="left", fill="y", padx=10, pady=10)
        ctk.CTkLabel(self.frame_lista, text="Usuarios registrados:").pack()
        self.tree_usuarios = ttk.Treeview(self.frame_lista, columns=("id", "username", "nombre", "rol"), show="headings", height=18)
        self.tree_usuarios.heading("id", text="ID")
        self.tree_usuarios.heading("username", text="Usuario")
        self.tree_usuarios.heading("nombre", text="Nombre")
        self.tree_usuarios.heading("rol", text="Rol")
        self.tree_usuarios.column("id", width=40)
        self.tree_usuarios.column("username", width=80)
        self.tree_usuarios.column("nombre", width=120)
        self.tree_usuarios.column("rol", width=60)
        self.tree_usuarios.pack(pady=5)
        self.tree_usuarios.bind("<<TreeviewSelect>>", self.seleccionar_usuario_evento)

        # Frame para edición/registro
        self.frame_edicion = ctk.CTkFrame(self.window, fg_color="#e3f0ff")
        self.frame_edicion.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(self.frame_edicion, text="Nombre:").pack(anchor="w", padx=20)
        self.entry_nombre = ctk.CTkEntry(self.frame_edicion, width=400, height=35)
        self.entry_nombre.pack(pady=5, padx=20)
        ctk.CTkLabel(self.frame_edicion, text="Usuario:").pack(anchor="w", padx=20)
        self.entry_usuario = ctk.CTkEntry(self.frame_edicion, width=400, height=35)
        self.entry_usuario.pack(pady=5, padx=20)
        ctk.CTkLabel(self.frame_edicion, text="Rol:").pack(anchor="w", padx=20)
        self.combo_rol = ctk.CTkComboBox(self.frame_edicion, values=["sistema", "admin", "cajero"], width=200, height=35)
        self.combo_rol.set("cajero")
        self.combo_rol.pack(pady=5, padx=20)
        ctk.CTkLabel(self.frame_edicion, text="Contraseña:").pack(anchor="w", padx=20)
        self.entry_password = ctk.CTkEntry(self.frame_edicion, width=400, height=35, show="*")
        self.entry_password.pack(pady=5, padx=20)
        ctk.CTkButton(self.frame_edicion, text="Registrar Usuario", command=self.registrar_usuario, fg_color="green").pack(pady=10)
        ctk.CTkButton(self.frame_edicion, text="Actualizar Usuario", command=self.actualizar_usuario, fg_color="orange").pack(pady=10)
        ctk.CTkButton(self.frame_edicion, text="Cambiar Contraseña", command=self.cambiar_contraseña, fg_color="blue").pack(pady=10)

        self.usuario_seleccionado = None
        self.cargar_usuarios()

    def cargar_usuarios(self):
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)
        self.usuarios = self.db.get_usuarios()
        for usuario in self.usuarios:
            self.tree_usuarios.insert("", "end", values=(usuario['id'], usuario['username'], usuario['nombre_completo'], usuario['rol']))

    def seleccionar_usuario_evento(self, event):
        selected = self.tree_usuarios.selection()
        if not selected:
            return
        item = self.tree_usuarios.item(selected[0])
        values = item['values']
        user_id = int(values[0])
        usuario = next((u for u in self.usuarios if u['id'] == user_id), None)
        if usuario:
            self.usuario_seleccionado = usuario
            self.entry_nombre.delete(0, "end")
            self.entry_nombre.insert(0, usuario['nombre_completo'])
            self.entry_usuario.delete(0, "end")
            self.entry_usuario.insert(0, usuario['username'])
            self.combo_rol.set(usuario['rol'])
            self.entry_password.delete(0, "end")

    def registrar_usuario(self):
        nombre = self.entry_nombre.get().strip()
        usuario = self.entry_usuario.get().strip()
        rol = self.combo_rol.get()
        password = self.entry_password.get().strip()
        if not nombre or not usuario or not rol or not password:
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        try:
            self.db.crear_usuario(usuario, password, nombre, rol)
            messagebox.showinfo("Éxito", "Usuario registrado")
            self.cargar_usuarios()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def actualizar_usuario(self):
        if not self.usuario_seleccionado:
            messagebox.showerror("Error", "Seleccione un usuario para editar")
            return
        nombre = self.entry_nombre.get().strip()
        usuario = self.entry_usuario.get().strip()
        rol = self.combo_rol.get()
        # Aquí deberías agregar el método en database.py para actualizar usuario
        # self.db.actualizar_usuario(self.usuario_seleccionado['id'], usuario, nombre, rol)
        messagebox.showinfo("Éxito", "Usuario actualizado (implementa lógica en database.py)")
        self.cargar_usuarios()

    def cambiar_contraseña(self):
        if not self.usuario_seleccionado:
            messagebox.showerror("Error", "Seleccione un usuario para cambiar la contraseña")
            return
        password = self.entry_password.get().strip()
        if not password:
            messagebox.showerror("Error", "Ingrese la nueva contraseña")
            return
        # Aquí deberías agregar el método en database.py para cambiar contraseña
        # self.db.cambiar_contraseña(self.usuario_seleccionado['id'], password)
        messagebox.showinfo("Éxito", "Contraseña cambiada (implementa lógica en database.py)")
