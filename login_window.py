import customtkinter as ctk
from tkinter import messagebox
from database import DatabaseManager
from datetime import datetime

class LoginWindow:
    def __init__(self):
        self.db = DatabaseManager()
        self.usuario_autenticado = None
        
        # Configurar tema
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Crear ventana principal
        self.window = ctk.CTk(fg_color="#FFFFFF")
        self.window.title("Sistema de Punto de Venta - Login")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        # Centrar ventana
        self.centrar_ventana()
        # Configurar UI
        self.setup_ui()
        # Enfocar en username
        self.entry_username.focus()
    
    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.window.update_idletasks()
        x = (1366 // 2) - (400 // 2)
        y = (768 // 2) - (500 // 2)
        self.window.geometry(f"400x500+{x}+{y}")
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.window, width=360, height=460, fg_color="#e3f0ff")
        self.main_frame.place(x=20, y=20)
        
        # Logo/Título
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="🏪 PUNTO DE VENTA",
            font=ctk.CTkFont(size=34, weight="bold"),
            text_color="#1f538d"
        )
        title_label.place(x=180, y=40, anchor="center")
        

        # Mostrar nombre de la tienda debajo del subtítulo
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT nombre_tienda FROM configuracion LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            nombre_tienda = row[0] if row and row[0] else ""
        except Exception:
            nombre_tienda = ""
        self.label_nombre_tienda = ctk.CTkLabel(
            self.main_frame,
            text=nombre_tienda,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#1f538d"
        )
        self.label_nombre_tienda.place(x=180, y=90, anchor="center")
        
        # Separador visual

        
        # Título del formulario
        form_title = ctk.CTkLabel(
            self.main_frame,
            text="Inicio de Sesión",
            font=ctk.CTkFont(size=18, weight="bold"),text_color="#1f538d"
        )
        form_title.place(x=180, y=140, anchor="center")
        
        # Campo Username
        username_label = ctk.CTkLabel(
            self.main_frame,
            text="Usuario:",
            font=ctk.CTkFont(size=18)
        )
        username_label.place(x=20, y=180)
        
        self.entry_username = ctk.CTkEntry(
            self.main_frame,
            width=320,
            height=44,
            placeholder_text="Ingrese su usuario",
            font=ctk.CTkFont(size=20)
        )
        self.entry_username.place(x=20, y=210)
        
        # Campo Password
        password_label = ctk.CTkLabel(
            self.main_frame,
            text="Contraseña:",
            font=ctk.CTkFont(size=18)
        )
        password_label.place(x=20, y=260)
        
        self.entry_password = ctk.CTkEntry(
            self.main_frame,
            width=320,
            height=44,
            placeholder_text="Ingrese su contraseña",
            font=ctk.CTkFont(size=20),
            show="*"
        )
        self.entry_password.place(x=20, y=290)
        
        # Checkbox mostrar contraseña
        self.check_mostrar = ctk.CTkCheckBox(
            self.main_frame,
            text="Mostrar contraseña",
            command=self.toggle_password_visibility,
            font=ctk.CTkFont(size=14)
        )
        self.check_mostrar.place(x=20, y=340)
        
        # Botón Login
        self.btn_login = ctk.CTkButton(
            self.main_frame,
            text="🔐 INICIAR SESIÓN",
            width=320,
            height=52,
            command=self.iniciar_sesion,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#1f538d",
            hover_color="#164a7b"
        )
        self.btn_login.place(x=20, y=380)
        
        # Eventos de teclado
        self.entry_username.bind('<Return>', lambda e: self.entry_password.focus())
        self.entry_password.bind('<Return>', lambda e: self.iniciar_sesion())
        
        # Estado de la conexión
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color="green"
        )
        self.status_label.place(x=20, y=510)
        
        # Verificar conexión con base de datos
        self.verificar_conexion()
    
    def verificar_conexion(self):
        """Verifica la conexión con la base de datos"""
        try:
            usuarios = self.db.get_usuarios()
            self.status_label.configure(
                text=f"✅ Base de datos conectada ({len(usuarios)} usuarios)",
                text_color="green"
            )
        except Exception as e:
            self.status_label.configure(
                text="❌ Error de conexión con base de datos",
                text_color="red"
            )
    
    def toggle_password_visibility(self):
        """Alterna la visibilidad de la contraseña"""
        if self.check_mostrar.get():
            self.entry_password.configure(show="")
        else:
            self.entry_password.configure(show="*")
    
    def iniciar_sesion(self):
        """Procesa el intento de inicio de sesión"""
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        
        # Validar campos
        if not username:
            messagebox.showerror("Error", "Por favor ingrese su Usuario")
            self.entry_username.focus()
            return
        
        if not password:
            messagebox.showerror("Error", "Por favor ingrese su Contraseña")
            self.entry_password.focus()
            return
        
        # Deshabilitar botón temporalmente
        self.btn_login.configure(state="disabled", text="Verificando...")
        # Solo procesar tareas pendientes de dibujo/geometry para evitar callbacks durante destroy
        self.window.update_idletasks()
        
        try:
            # Validar credenciales
            usuario = self.db.validar_usuario(username, password)
            
            if usuario:
                self.usuario_autenticado = usuario
                
                # Mostrar mensaje de bienvenida
                messagebox.showinfo(
                    "Bienvenido", 
                    f"¡Bienvenido {usuario['nombre_completo']}!\n"
                    f"Rol: {usuario['rol'].title()}\n"
                    f"Hora: {datetime.now().strftime('%H:%M:%S')}"
                )
                
                # Cerrar ventana de login
                self.window.destroy()
            else:
                messagebox.showerror(
                    "Error de Autenticación",
                    "Usuario o contraseña incorrectos.\n\n"
                    "Verifique sus credenciales e intente nuevamente."
                )
                self.entry_password.delete(0, 'end')
                self.entry_username.focus()
        
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la autenticación:\n{str(e)}")
        
        finally:
            # Rehabilitar botón solo si la ventana y el botón siguen existiendo (evita TclError tras destroy)
            try:
                if self.window.winfo_exists() and self.btn_login.winfo_exists():
                    self.btn_login.configure(state="normal", text="🔐 INICIAR SESIÓN")
            except Exception:
                # Si la ventana ya fue destruida, no hay nada que re-habilitar
                pass
    
    def run(self):
        """Ejecuta la ventana de login"""
        self.window.mainloop()
        return self.usuario_autenticado

# Función para probar la ventana de login independientemente
def test_login():
    app = LoginWindow()
    usuario = app.run()
    if usuario:
        print(f"Login exitoso: {usuario}")
    else:
        print("Login cancelado")

if __name__ == "__main__":
    test_login()