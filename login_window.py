import customtkinter as ctk
from tkinter import messagebox
from database import DatabaseManager
from datetime import datetime
from PIL import Image

class LoginWindow:
    def __init__(self):
        self.db = DatabaseManager()
        self.usuario_autenticado = None
        
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.window = ctk.CTk(fg_color="#FFFFFF")
        self.window.title("Sistema de Punto de Venta - Login")
        self.window.geometry("420x500")
        self.window.resizable(False, False)
        self.centrar_ventana()
        self.setup_ui()
        self.entry_username.focus()
        self.window.overrideredirect(True)
    
    def centrar_ventana(self):
        self.window.update_idletasks()
        ancho_pantalla = self.window.winfo_screenwidth()
        alto_pantalla = self.window.winfo_screenheight()
        x = (ancho_pantalla - 420) // 2
        y = (alto_pantalla - 600) // 2
        self.window.geometry(f"420x600+{x}+{y}")
    
    def setup_ui(self):
        self.encabezado_frame = ctk.CTkFrame(
            self.window, 
            width=420, 
            height=140, 
            fg_color="transparent",
            corner_radius=0
        )
        self.encabezado_frame.place(x=0, y=0)

        self.main_frame = ctk.CTkFrame(
            self.window, 
            width=360, 
            height=490, 
            fg_color="#ffffff",
            corner_radius=20,
            border_width=1,
            border_color="#e0e0e0"
        )
        self.main_frame.place(relx=0.5, y=100, anchor="n")


        logo_img = ctk.CTkImage(
            light_image=Image.open("imagen/puntero-del-mapa.png"),
            size=(60, 60)
)

        ctk.CTkLabel(
            self.encabezado_frame,
            image=logo_img,
            text="",
            font=ctk.CTkFont(size=45),
            text_color="#1976D2"
        ).place(relx=0.1, y=40, anchor="center")

        ctk.CTkLabel(
            self.encabezado_frame,
            text="MI PUNTO DE VENTA",
            font=ctk.CTkFont(size=27, weight="bold"),
            text_color="#1976D2"
        ).place(relx=0.5, y=60, anchor="center")

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT nombre_tienda FROM configuracion LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            nombre_tienda = row[0] if row and row[0] else "Mi Tienda"
        except Exception:
            nombre_tienda = "Mi Tienda"
            
        self.label_nombre_tienda = ctk.CTkLabel(
            self.main_frame,
            text=nombre_tienda,
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color="#2E7D32"
        )
        self.label_nombre_tienda.place(relx=0.5, y=50, anchor="center")
        
        form_title = ctk.CTkLabel(
            self.main_frame,
            text="Iniciar Sesión",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#424242"
        )
        form_title.place(relx=0.5, y=120, anchor="center")

        self.entry_container = ctk.CTkFrame(
            self.main_frame,
            width=300,
            height=190,
            fg_color="#f8f9fa",
            corner_radius=12
        )
        self.entry_container.place(relx=0.5, y=140, anchor="n")

        self.entry_username = ctk.CTkEntry(
            self.entry_container,
            width=260,
            height=45,
            placeholder_text="👤 Usuario",
            font=ctk.CTkFont(size=16),
            corner_radius=10,
            border_width=1,
            border_color="#e0e0e0"
        )
        self.entry_username.place(relx=0.5, y=20, anchor="n")

        self.entry_password = ctk.CTkEntry(
            self.entry_container,
            width=260,
            height=45,
            placeholder_text="🔒 Contraseña",
            font=ctk.CTkFont(size=16),
            show="•",
            corner_radius=10,
            border_width=1,
            border_color="#e0e0e0"
        )
        self.entry_password.place(relx=0.5, y=75, anchor="n")
        
        self.check_mostrar = ctk.CTkCheckBox(
            self.entry_container,
            text="Mostrar contraseña",
            command=self.toggle_password_visibility,
            font=ctk.CTkFont(size=14),
            fg_color="#1976D2",
            hover_color="#1565C0"
        )
        self.check_mostrar.place(relx=0.3, y=130, anchor="n")
        
        self.btn_login = ctk.CTkButton(
            self.main_frame,
            text="INICIAR SESIÓN",
            width=300,
            height=45,
            command=self.iniciar_sesion,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#1976D2",
            hover_color="#1565C0",
            text_color="#FFFFFF",
            corner_radius=12
        )
        self.btn_login.place(relx=0.5, y=310, anchor="n")

        self.btn_salir = ctk.CTkButton(
            self.main_frame,
            text="SALIR",
            width=300,
            height=45,
            command=self.window.destroy,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="transparent",
            hover_color="#f5f5f5",
            text_color="#666666",
            corner_radius=12,
            border_width=1,
            border_color="#e0e0e0"
        )
        self.btn_salir.place(relx=0.5, y=370, anchor="n")
        
        self.status_frame = ctk.CTkFrame(
            self.main_frame,
            width=300,
            height=50,
            fg_color="#f8f9fa",
            corner_radius=10
        )
        self.status_frame.place(relx=0.5, y=430, anchor="n")
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="#666666"
        )
        self.status_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self.entry_username.bind('<Return>', lambda e: self.entry_password.focus())
        self.entry_password.bind('<Return>', lambda e: self.iniciar_sesion())
        
        self.verificar_conexion()
    
    def verificar_conexion(self):
        try:
            usuarios = self.db.get_usuarios()
            self.status_label.configure(
                text=f"✅ Conectado - {len(usuarios)} usuarios",
                text_color="#2E7D32"
            )
        except Exception as e:
            self.status_label.configure(
                text="❌ Error de conexión con base de datos",
                text_color="#D32F2F"
            )
    
    def toggle_password_visibility(self):
        if self.check_mostrar.get():
            self.entry_password.configure(show="")
        else:
            self.entry_password.configure(show="•")
    
    def iniciar_sesion(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()
        
        if not username:
            messagebox.showerror("Error", "Por favor ingrese su Usuario")
            self.entry_username.focus()
            return
        
        if not password:
            messagebox.showerror("Error", "Por favor ingrese su Contraseña")
            self.entry_password.focus()
            return
        
        self.btn_login.configure(state="disabled", text="VERIFICANDO...")
        self.window.update_idletasks()
        
        try:
            usuario = self.db.validar_usuario(username, password)
            
            if usuario:
                self.usuario_autenticado = usuario
                
                messagebox.showinfo(
                    "Bienvenido", 
                    f"¡Bienvenido {usuario['nombre_completo']}!\n"
                    f"Rol: {usuario['rol'].title()}\n"
                    f"Hora: {datetime.now().strftime('%H:%M:%S')}"
                )
                
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
            try:
                if self.window.winfo_exists() and self.btn_login.winfo_exists():
                    self.btn_login.configure(state="normal", text="INICIAR SESIÓN")
            except Exception:
                pass
    
    def run(self):
        self.window.mainloop()
        return self.usuario_autenticado

def test_login():
    app = LoginWindow()
    usuario = app.run()
    if usuario:
        print(f"Login exitoso: {usuario}")
    else:
        print("Login cancelado")

if __name__ == "__main__":
    test_login()