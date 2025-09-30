import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseManager
import re

class ConfiguracionMonedasWindow:
    def __init__(self, parent, on_configuracion_guardada=None):
        self.parent = parent
        self.db = DatabaseManager()
        self.on_configuracion_guardada = on_configuracion_guardada
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("💱 Configuración de Monedas")
        self.window.geometry("600x400")
        self.window.resizable(False, False)
        
        # Hacer la ventana modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Centrar ventana
        self.center_window()
        
        # Configurar estilo
        self.setup_styles()
        
        # Crear interfaz
        self.create_widgets()
        
        # Cargar datos actuales
        self.load_current_configuration()
        
        # Focus en la ventana
        self.window.focus_force()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_styles(self):
        """Configura los estilos de la interfaz"""
        style = ttk.Style()
        
        # Configurar estilo para los frames principales
        style.configure("Card.TFrame", background="#f8f9fa", relief="solid", borderwidth=1)
        style.configure("Header.TLabel", font=("Arial", 12, "bold"), background="#f8f9fa")
        style.configure("Success.TButton", background="#28a745")
        style.configure("Warning.TButton", background="#ffc107")
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título principal
        title_label = ttk.Label(main_frame, text="💱 Configuración de Monedas", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame de configuración de tasa de cambio
        self.create_exchange_rate_frame(main_frame)
        
        # Frame de configuración de visualización
        self.create_display_frame(main_frame)
        
        # Frame de símbolos de monedas
        self.create_symbols_frame(main_frame)
        
        # Frame de botones
        self.create_buttons_frame(main_frame)
    
    def create_exchange_rate_frame(self, parent):
        """Crea el frame de configuración de tasa de cambio"""
        # Frame principal
        frame = ttk.LabelFrame(parent, text="💵 Tasa de Cambio", padding="15")
        frame.pack(fill=tk.X, pady=(0, 15))
        
        # Información actual
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(info_frame, text="Tasa actual:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.current_rate_label = ttk.Label(info_frame, text="", font=("Arial", 10))
        self.current_rate_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Input para nueva tasa
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="Nueva tasa (1 USD = ? VES):", 
                 font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.rate_var = tk.StringVar()
        self.rate_entry = ttk.Entry(input_frame, textvariable=self.rate_var, 
                                   width=15, font=("Arial", 11))
        self.rate_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Validar solo números y punto decimal
        vcmd = (self.window.register(self.validate_decimal), '%P')
        self.rate_entry.config(validate='key', validatecommand=vcmd)
        
        # Botón de actualización rápida
        update_btn = ttk.Button(input_frame, text="🔄 Actualizar", 
                               command=self.update_exchange_rate)
        update_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Ejemplos de conversión
        self.create_conversion_examples(frame)
    
    def create_conversion_examples(self, parent):
        """Crea ejemplos de conversión en tiempo real"""
        examples_frame = ttk.Frame(parent)
        examples_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(examples_frame, text="📊 Ejemplos de conversión:", 
                 font=("Arial", 9, "italic")).pack(anchor=tk.W)
        
        self.examples_text = tk.Text(examples_frame, height=3, width=60, 
                                    font=("Consolas", 8), state=tk.DISABLED,
                                    background="#f8f9fa", relief="flat")
        self.examples_text.pack(pady=(5, 0), fill=tk.X)
        
        # Actualizar ejemplos cuando cambie la tasa
        self.rate_var.trace('w', self.update_conversion_examples)
    
    def create_display_frame(self, parent):
        """Crea el frame de configuración de visualización"""
        frame = ttk.LabelFrame(parent, text="👁️ Configuración de Visualización", padding="15")
        frame.pack(fill=tk.X, pady=(0, 15))
        
        # Checkbox para mostrar ambas monedas
        self.show_both_var = tk.BooleanVar()
        show_both_cb = ttk.Checkbutton(frame, text="Mostrar precios en ambas monedas (VES y USD)",
                                      variable=self.show_both_var)
        show_both_cb.pack(anchor=tk.W)
        
        # Información adicional
        info_label = ttk.Label(frame, 
                              text="• Cuando esté activado, se mostrarán los precios en bolívares y dólares\n"
                                   "• Cuando esté desactivado, solo se mostrará la moneda principal",
                              font=("Arial", 8), foreground="#666666")
        info_label.pack(anchor=tk.W, pady=(5, 0))
    
    def create_symbols_frame(self, parent):
        """Crea el frame de configuración de símbolos"""
        frame = ttk.LabelFrame(parent, text="🔤 Símbolos de Monedas", padding="15")
        frame.pack(fill=tk.X, pady=(0, 15))
        
        # Grid para los símbolos
        symbols_grid = ttk.Frame(frame)
        symbols_grid.pack(fill=tk.X)
        
        # Símbolo VES
        ttk.Label(symbols_grid, text="Símbolo Bolívares (VES):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.symbol_ves_var = tk.StringVar()
        ves_entry = ttk.Entry(symbols_grid, textvariable=self.symbol_ves_var, width=10)
        ves_entry.grid(row=0, column=1, padx=(0, 20))
        
        # Símbolo USD  
        ttk.Label(symbols_grid, text="Símbolo Dólares (USD):").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.symbol_usd_var = tk.StringVar()
        usd_entry = ttk.Entry(symbols_grid, textvariable=self.symbol_usd_var, width=10)
        usd_entry.grid(row=0, column=3)
        
        # Configurar pesos de las columnas
        symbols_grid.grid_columnconfigure(1, weight=1)
        symbols_grid.grid_columnconfigure(3, weight=1)
    
    def create_buttons_frame(self, parent):
        """Crea el frame de botones"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=(20, 0))
        
        # Botones alineados a la derecha
        button_frame = ttk.Frame(frame)
        button_frame.pack(side=tk.RIGHT)
        
        # Botón Cancelar
        cancel_btn = ttk.Button(button_frame, text="❌ Cancelar", 
                               command=self.cancel)
        cancel_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón Guardar
        save_btn = ttk.Button(button_frame, text="💾 Guardar Configuración", 
                             command=self.save_configuration,
                             style="Success.TButton")
        save_btn.pack(side=tk.LEFT)
    
    def validate_decimal(self, value):
        """Valida que el input sea un número decimal válido"""
        if value == "":
            return True
        try:
            if re.match(r'^\d+\.?\d*$', value):
                return True
            return False
        except ValueError:
            return False
    
    def load_current_configuration(self):
        """Carga la configuración actual de la base de datos"""
        try:
            # Tasa de cambio
            tasa_actual = self.db.get_tasa_cambio()
            self.current_rate_label.config(text=f"1 USD = {tasa_actual:.2f} VES")
            self.rate_var.set(str(tasa_actual))
            
            # Mostrar ambas monedas
            mostrar_ambas = self.db.mostrar_ambas_monedas()
            self.show_both_var.set(mostrar_ambas)
            
            # Símbolos
            simbolos = self.db.get_simbolos_monedas()
            self.symbol_ves_var.set(simbolos['VES'])
            self.symbol_usd_var.set(simbolos['USD'])
            
            # Actualizar ejemplos
            self.update_conversion_examples()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando configuración: {e}")
    
    def update_conversion_examples(self, *args):
        """Actualiza los ejemplos de conversión en tiempo real"""
        try:
            tasa_str = self.rate_var.get()
            if not tasa_str:
                return
            
            tasa = float(tasa_str)
            
            # Ejemplos de conversión
            ejemplos = [
                f"$1.00 USD = Bs. {tasa:.2f} VES",
                f"$10.00 USD = Bs. {tasa * 10:.2f} VES", 
                f"Bs. {tasa:.2f} VES = $1.00 USD"
            ]
            
            # Actualizar el texto
            self.examples_text.config(state=tk.NORMAL)
            self.examples_text.delete(1.0, tk.END)
            self.examples_text.insert(1.0, "\n".join(ejemplos))
            self.examples_text.config(state=tk.DISABLED)
            
        except ValueError:
            pass  # Ignorar valores inválidos durante la edición
    
    def update_exchange_rate(self):
        """Actualiza solo la tasa de cambio"""
        try:
            tasa_str = self.rate_var.get()
            if not tasa_str:
                messagebox.showwarning("Advertencia", "Por favor ingrese una tasa de cambio")
                return
            
            nueva_tasa = float(tasa_str)
            if nueva_tasa <= 0:
                messagebox.showwarning("Advertencia", "La tasa de cambio debe ser mayor a cero")
                return
            
            # Actualizar en la base de datos
            self.db.actualizar_tasa_cambio(nueva_tasa)
            
            # Actualizar la etiqueta
            self.current_rate_label.config(text=f"1 USD = {nueva_tasa:.2f} VES")
            
            messagebox.showinfo("Éxito", f"Tasa de cambio actualizada a: 1 USD = {nueva_tasa:.2f} VES")
            
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese una tasa de cambio válida")
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando tasa: {e}")
    
    def save_configuration(self):
        """Guarda toda la configuración y llama al callback si existe"""
        try:
            # Validar tasa de cambio
            tasa_str = self.rate_var.get()
            if not tasa_str:
                messagebox.showwarning("Advertencia", "Por favor ingrese una tasa de cambio")
                return
            nueva_tasa = float(tasa_str)
            if nueva_tasa <= 0:
                messagebox.showwarning("Advertencia", "La tasa de cambio debe ser mayor a cero")
                return
            # Validar símbolos
            symbol_ves = self.symbol_ves_var.get().strip()
            symbol_usd = self.symbol_usd_var.get().strip()
            if not symbol_ves or not symbol_usd:
                messagebox.showwarning("Advertencia", "Por favor ingrese ambos símbolos de monedas")
                return
            # Guardar configuración
            self.db.actualizar_tasa_cambio(nueva_tasa)
            self.db.actualizar_configuracion_moneda('mostrar_ambas_monedas', '1' if self.show_both_var.get() else '0')
            self.db.actualizar_configuracion_moneda('simbolo_ves', symbol_ves)
            self.db.actualizar_configuracion_moneda('simbolo_usd', symbol_usd)
            messagebox.showinfo("Éxito", "Configuración de monedas guardada correctamente")
            # Notificar a la ventana principal para refrescar UI
            if self.on_configuracion_guardada:
                self.on_configuracion_guardada()
            # Cerrar ventana
            self.window.destroy()
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese una tasa de cambio válida")
        except Exception as e:
            messagebox.showerror("Error", f"Error guardando configuración: {e}")
    
    def cancel(self):
        """Cancela y cierra la ventana"""
        self.window.destroy()

if __name__ == "__main__":
    # Test de la ventana
    root = tk.Tk()
    root.withdraw()  # Ocultar ventana principal
    
    app = ConfiguracionMonedasWindow(root)
    root.mainloop()
