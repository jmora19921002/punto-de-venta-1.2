import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from icon_manager import icon_manager
from colores_modernos import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, BACKGROUND_COLOR, CARD_COLOR, TEXT_COLOR, SUBTEXT_COLOR, SUCCESS_COLOR, ERROR_COLOR, BUTTON_COLOR, BUTTON_TEXT_COLOR, BORDER_RADIUS, FONT_FAMILY, TITLE_FONT_SIZE, SUBTITLE_FONT_SIZE, TEXT_FONT_SIZE, BUTTON_FONT_SIZE

class TasaCambioWindow:
    def __init__(self, parent, db, callback_actualizar=None):
        self.parent = parent
        self.db = db
        self.callback_actualizar = callback_actualizar
        
        # Obtener datos actuales
        self.tasa_actual = self.db.get_tasa_cambio()
        
        # Crear ventana responsive y más grande
        self.window = ctk.CTkToplevel(parent, fg_color=BACKGROUND_COLOR)
        self.window.title("Actualizar Tasa de Cambio")
        # Configuración responsive
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        # Ventana más grande y adaptativa
        window_width = min(600, int(screen_width * 0.4))
        window_height = min(650, int(screen_height * 0.7))
        # Centrar ventana
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.window.transient(parent)
        self.window.grab_set()
        self.window.lift()
        self.window.focus_force()
        # Aplicar iconos
        icon_manager.apply_to_window(self.window)
        self.setup_ui()
    
    def setup_ui(self):
        # Título principal con más espacio
        title_frame = ctk.CTkFrame(self.window, fg_color=CARD_COLOR, corner_radius=BORDER_RADIUS)
        title_frame.pack(fill="x", padx=20, pady=15)
        
        titulo = ctk.CTkLabel(
            title_frame,
            text="💱 ACTUALIZAR TASA DE CAMBIO",
            font=ctk.CTkFont(family=FONT_FAMILY, size=TITLE_FONT_SIZE, weight="bold"),
            text_color=PRIMARY_COLOR
        )
        titulo.pack(pady=20)
        
        # Frame para información actual con más espacio
        frame_actual = ctk.CTkFrame(self.window, fg_color=CARD_COLOR, corner_radius=BORDER_RADIUS)
        frame_actual.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(
            frame_actual,
            text="📊 INFORMACIÓN ACTUAL",
            font=ctk.CTkFont(family=FONT_FAMILY, size=SUBTITLE_FONT_SIZE, weight="bold"),
            text_color=SECONDARY_COLOR
        ).pack(pady=10)
        
        self.label_tasa_actual = ctk.CTkLabel(
            frame_actual,
            text=f"Tasa Actual: 1 USD = {self.tasa_actual:.2f} VES",
            font=ctk.CTkFont(family=FONT_FAMILY, size=TEXT_FONT_SIZE),
            text_color=PRIMARY_COLOR
        )
        self.label_tasa_actual.pack(pady=5)
        
        # Fecha de última actualización
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        ctk.CTkLabel(
            frame_actual,
            text=f"Última actualización: {fecha_actual}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=TEXT_FONT_SIZE-2),
            text_color=SUBTEXT_COLOR
        ).pack(pady=5)
        
        # Frame para nueva tasa con más espacio
        frame_nueva = ctk.CTkFrame(self.window, fg_color=CARD_COLOR, corner_radius=BORDER_RADIUS)
        frame_nueva.pack(pady=15, padx=20, fill="x")
        
        ctk.CTkLabel(
            frame_nueva, 
            text="🔄 NUEVA TASA DE CAMBIO", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=15)
        
        # Campo para nueva tasa
        ctk.CTkLabel(
            frame_nueva,
            text="Ingrese la nueva tasa USD/VES:",
            font=ctk.CTkFont(size=12)
        ).pack(pady=5)
        
        self.entry_nueva_tasa = ctk.CTkEntry(
            frame_nueva,
            width=250,
            height=45,
            placeholder_text=f"{self.tasa_actual:.2f}",
            font=ctk.CTkFont(size=16),
            justify="center"
        )
        self.entry_nueva_tasa.pack(pady=15)
        
        # Validación en tiempo real
        self.entry_nueva_tasa.bind("<KeyRelease>", self.validar_entrada)
        
        # Label para mostrar previsualización
        self.label_preview = ctk.CTkLabel(
            frame_nueva,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="green"
        )
        self.label_preview.pack(pady=5)
        
        # Frame para botones con más espacio
        frame_botones = ctk.CTkFrame(self.window)
        frame_botones.pack(pady=20, padx=20, fill="x")
        
        # Contenedor interno para centrar botones
        botones_container = ctk.CTkFrame(frame_botones)
        botones_container.pack(pady=20)
        
        # Botón actualizar más grande
        btn_actualizar = ctk.CTkButton(
            botones_container,
            text="✅ ACTUALIZAR TASA",
            width=180,
            height=45,
            command=self.actualizar_tasa,
            fg_color="#2fa572",
            hover_color="#106A43",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_actualizar.pack(side="left", padx=10)
        
        # Botón cancelar más grande
        btn_cancelar = ctk.CTkButton(
            botones_container,
            text="❌ CANCELAR",
            width=180,
            height=45,
            command=self.window.destroy,
            fg_color="#dc3545",
            hover_color="#a02834",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        btn_cancelar.pack(side="right", padx=10)
        
        # Espacio adicional para el botón de cerrar
        close_frame = ctk.CTkFrame(self.window)
        close_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Botón de cerrar alternativo
        btn_cerrar = ctk.CTkButton(
            close_frame,
            text="✖ Cerrar Ventana",
            width=140,
            height=35,
            command=self.window.destroy,
            fg_color="#6c757d",
            hover_color="#545b62",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        btn_cerrar.pack(pady=10)
        
        # Enfocar en el campo de entrada
        self.entry_nueva_tasa.focus()
        
        # Bind Enter para actualizar
        self.window.bind('<Return>', lambda e: self.actualizar_tasa())
    
    def validar_entrada(self, event=None):
        """Valida la entrada en tiempo real y muestra previsualización"""
        try:
            texto = self.entry_nueva_tasa.get()
            if texto:
                nueva_tasa = float(texto)
                if nueva_tasa > 0:
                    diferencia = nueva_tasa - self.tasa_actual
                    porcentaje = (diferencia / self.tasa_actual) * 100
                    
                    if diferencia > 0:
                        color = "red"
                        simbolo = "📈"
                        direccion = "aumento"
                    else:
                        color = "green" 
                        simbolo = "📉"
                        direccion = "disminución"
                    
                    preview_text = f"{simbolo} {direccion.upper()}: {abs(diferencia):.2f} VES ({abs(porcentaje):.1f}%)"
                    self.label_preview.configure(text=preview_text, text_color=color)
                else:
                    self.label_preview.configure(text="⚠️ La tasa debe ser mayor a cero", text_color="red")
            else:
                self.label_preview.configure(text="")
        except ValueError:
            if self.entry_nueva_tasa.get():
                self.label_preview.configure(text="⚠️ Ingrese un número válido", text_color="red")
            else:
                self.label_preview.configure(text="")
    
    def actualizar_tasa(self):
        """Actualiza la tasa de cambio"""
        try:
            nueva_tasa_str = self.entry_nueva_tasa.get().strip()
            if not nueva_tasa_str:
                messagebox.showerror("Error", "Por favor ingrese una tasa de cambio.")
                return
            
            nueva_tasa = float(nueva_tasa_str)
            if nueva_tasa <= 0:
                messagebox.showerror("Error", "La tasa debe ser mayor a cero.")
                return
            
            # Confirmar actualización
            diferencia = nueva_tasa - self.tasa_actual
            porcentaje = (diferencia / self.tasa_actual) * 100
            
            mensaje = f"""¿Confirmar actualización de tasa de cambio?

📊 CAMBIOS:
• Tasa anterior: {self.tasa_actual:.2f} VES
• Tasa nueva: {nueva_tasa:.2f} VES
• Diferencia: {diferencia:+.2f} VES ({porcentaje:+.1f}%)

⚠️ IMPORTANTE:
• Se actualizarán TODOS los productos
• Se recalcularán los precios automáticamente
• Esta acción no se puede deshacer

¿Continuar?"""
            
            if messagebox.askyesno("Confirmar Actualización", mensaje):
                # Mostrar progreso
                self.mostrar_progreso()
                
                # Actualizar en base de datos
                self.db.actualizar_tasa_cambio(nueva_tasa)
                # La función actualizar_tasa_cambio ya llama a recalcular_precios_ves
                
                # Ejecutar callback si existe
                if self.callback_actualizar:
                    self.callback_actualizar()
                
                messagebox.showinfo(
                    "Actualización Exitosa", 
                    f"✅ Tasa actualizada correctamente\n\nNueva tasa: 1 USD = {nueva_tasa:.2f} VES"
                )
                
                self.window.destroy()
        
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese un número válido.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar la tasa: {str(e)}")
    
    def mostrar_progreso(self):
        """Muestra indicador de progreso durante la actualización"""
        # Deshabilitar botones
        for child in self.window.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                for subchild in child.winfo_children():
                    if isinstance(subchild, ctk.CTkButton):
                        subchild.configure(state="disabled")
        
        # Cambiar cursor
        self.window.configure(cursor="wait")
        self.window.update()