import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
from datetime import datetime, date
import json
from database import DatabaseManager
from responsive_manager import ResponsiveManager
from icon_manager import icon_manager
from colores_modernos import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, BACKGROUND_COLOR, CARD_COLOR, TEXT_COLOR, SUBTEXT_COLOR, SUCCESS_COLOR, ERROR_COLOR, BUTTON_COLOR, BUTTON_TEXT_COLOR, BORDER_RADIUS, FONT_FAMILY, TITLE_FONT_SIZE, SUBTITLE_FONT_SIZE, TEXT_FONT_SIZE, BUTTON_FONT_SIZE

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class PuntoVentaApp:
    def get_user_buttons(self):
        """Retorna los botones disponibles según el rol del usuario"""
        botones = []
        rol_actual = getattr(self.usuario_actual, 'rol', self.usuario_actual.get('rol', None))
        if rol_actual != 'cajero':
            botones.extend([
                ("📊\nCorte", self.mostrar_corte_dia),
                ("📦\nItems", self.abrir_inventario),
                ("🛍️\nCompras", self.abrir_compras)
            ])
        botones.extend([
            ("👤\nClientes", self.abrir_clientes),
            ("⏳\nOp. Esp", self.mostrar_operaciones_espera),
            ("🔄\n Tasa", self.actualizar_tasa_cambio_ui),
            ("🏷️\nCategoría", self.abrir_categorias)
        ])
        if rol_actual == 'sistema':
            botones.extend([
                ("👤\nUser", self.abrir_usuarios),
                ("⚙️\nConfig", self.abrir_empresa)
            ])
        elif rol_actual == 'soporte':
            botones.append(("🏢\nEmpresa", self.abrir_empresa))
        return botones

    def __init__(self, usuario_autenticado):
            self.db = DatabaseManager()
            self.usuario_actual = usuario_autenticado
            self.carrito = []
            self.cliente_seleccionado = None
            self.categoria_seleccionada = None
            monedas = self.db.get_monedas_activas() or []
            self.monedas_activas = []
            for m in monedas:
                tasa = 1.0 if m['codigo'] == 'VES' else self.db.get_tasa_cambio() or 0.0
                self.monedas_activas.append({
                    'codigo': m['codigo'],
                    'simbolo': m['simbolo'],
                    'tasa': tasa
                })
            self.moneda_principal = self.monedas_activas[0]['codigo'] if self.monedas_activas else 'VES'
            self.ventana = ctk.CTk(fg_color=BACKGROUND_COLOR)
            
            self.responsive = ResponsiveManager(self.ventana)
            
            # Establecer icono en la barra de tareas y ventana principal
            try:
                from PIL import Image, ImageTk
                icon_path = icon_manager.get_icon_path('main_png')
                if icon_path:
                    img = Image.open(icon_path)
                    icon = ImageTk.PhotoImage(img)
                    self.ventana.iconphoto(False, icon)
            except Exception as e:
                print(f"Error al establecer icono en barra de tareas: {e}")
            icon_manager.set_window_icon(self.ventana)
            titulo_ventana = f"Sistema de Punto de Venta - {usuario_autenticado['nombre_completo']} ({usuario_autenticado['rol'].title()})"
            self.ventana.title(titulo_ventana)
            
            self.ventana.geometry(self.responsive.get_window_geometry())
            self.screen_width = self.responsive.screen_width
            self.screen_height = self.responsive.screen_height
            self.ventana.state('zoomed')
            
            self.setup_responsive_logo()
            self.setup_responsive_ui()
            
            self.enable_responsive_features()
            
            self.cargar_productos()
            self.cargar_categorias()

    def set_moneda_principal(self, codigo):
        """Permite cambiar la moneda principal y recarga productos y carrito"""
        self.moneda_principal = codigo
        
        # Actualizar precios en carrito existente según nueva moneda
        for item in self.carrito:
            # Buscar el producto en la base de datos para obtener sus precios
            productos = self.db.get_productos()
            for producto in productos:
                if producto['id'] == item['producto_id']:
                    if self.moneda_principal == 'USD':
                        item['precio_unitario'] = producto.get('precio_venta_usd', 0) or 0
                    else:  # VES
                        item['precio_unitario'] = producto.get('precio_venta', 0) or 0
                    break
        
        self.cargar_productos(self.categoria_seleccionada)
        self.actualizar_carrito_ui()

    def convertir_precio(self, precio_base, moneda_destino):
        """
        El precio_base ya está en la moneda correcta según el contexto.
        Esta función ahora simplemente devuelve el precio tal como está.
        """
        return precio_base

    def formatear_precio_multimoneda(self, producto):
        """Devuelve el texto de precio en todas las monedas activas"""
        precios = []
        for moneda in self.monedas_activas:
            precio = self.convertir_precio(producto['precio_venta'], moneda['codigo'])
            precios.append(f"{moneda['simbolo']} {precio:.2f}")
        return '\n'.join(precios)
    
    def setup_responsive_logo(self):
        """Configura el logo de manera responsive"""
        try:
            logo_size = self.responsive.get_logo_size()
            positions = self.responsive.get_positions()
            
            # Usar IconManager para obtener la imagen
            logo_img = icon_manager.get_ctk_image('main_png', size=(logo_size, logo_size))
            
            frame_size = logo_size + 10
            self.logo_frame = ctk.CTkFrame(
                self.ventana, 
                width=frame_size, 
                height=frame_size, 
                fg_color="#e3f0ff", 
                corner_radius=frame_size//2
            )
            self.logo_frame.place(x=positions['logo_x'], y=positions['logo_y'])
            
            if logo_img:
                self.logo_label = ctk.CTkLabel(
                    self.logo_frame, 
                    image=logo_img, 
                    text="", 
                    width=logo_size, 
                    height=logo_size
                )
            else:
                # Fallback si no se puede cargar la imagen
                self.logo_label = ctk.CTkLabel(
                    self.logo_frame, 
                    text="📋", 
                    font=ctk.CTkFont(size=logo_size//2),
                    width=logo_size, 
                    height=logo_size
                )
            self.logo_label.place(x=5, y=5)
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")
    
    def setup_responsive_ui(self):
        """Configura la interfaz de usuario de manera responsive"""
        dims = self.responsive.get_dimensions()
        positions = self.responsive.get_positions()
        
        # Frame principal para productos (izquierda)
        self.frame_productos = ctk.CTkFrame(
            self.ventana, 
            width=dims['productos_width'], 
            height=dims['productos_height'], 
            corner_radius=10,
            fg_color="#e3f0ff"
        )
        self.frame_productos.place(x=positions['main_x'], y=positions['main_y'])

        # Frame para carrito (derecha)
        self.frame_carrito = ctk.CTkFrame(
            self.ventana, 
            width=dims['carrito_width'], 
            height=dims['carrito_height'], 
            corner_radius=10,
            fg_color="#e3f0ff"
        )
        self.frame_carrito.place(x=positions['carrito_x'], y=positions['carrito_y'])

        # Frame inferior para botones de funciones
        self.frame_funciones = ctk.CTkFrame(
            self.ventana, 
            width=dims['funciones_width'], 
            height=dims['funciones_height'], 
            corner_radius=10,
            fg_color="#e3f0ff"
        )
        self.frame_funciones.place(x=positions['funciones_x'], y=positions['funciones_y'])

        # Configurar secciones
        self.setup_responsive_productos_section()
        self.setup_responsive_carrito_section()
        self.setup_responsive_funciones_section()
        
        # Bind para detectar cambios de resolución
        self.ventana.bind('<Configure>', self.on_window_resize)
    
    def on_window_resize(self, event):
        """Maneja el redimensionado de la ventana"""
        # Solo actualizar si es la ventana principal la que se redimensiona
        if event.widget == self.ventana:
            self.responsive.refresh_layout()
            # Opcional: actualizar layout en tiempo real (puede ser costoso)
            # self.refresh_responsive_layout()

    def cambiar_moneda_evento(self, choice):
        """Callback que se ejecuta cuando se cambia la moneda en el ComboBox"""
        self.set_moneda_principal(choice)
    
    def setup_responsive_productos_section(self):
        """Configura la sección de productos de manera responsive"""
        dims = self.responsive.get_dimensions()
        positions = self.responsive.get_positions()
        
        # Búsqueda de productos
        self.entry_busqueda = ctk.CTkEntry(
            self.frame_productos, 
            placeholder_text="Buscar producto (nombre o código)", 
            width=dims['entry_width'], 
            height=dims['entry_height'], 
            corner_radius=10,
            font=self.responsive.create_responsive_font(12, "normal", "normal")
        )
        self.entry_busqueda.place(x=positions['search_x'], y=positions['search_y'])
        self.entry_busqueda.bind('<KeyRelease>', self.buscar_productos_evento)

        # Botón de búsqueda
        btn_buscar = ctk.CTkButton(
            self.frame_productos, 
            text="🔍", 
            width=dims['btn_buscar_width'], 
            height=dims['btn_buscar_height'],
            command=self.buscar_productos, 
            corner_radius=10,
            font=self.responsive.create_responsive_font(14, "bold", "button")
        )
        btn_buscar.place(x=positions['search_btn_x'], y=positions['search_btn_y'])

        # Scroll horizontal para categorías
        self.frame_categorias_scroll = ctk.CTkScrollableFrame(
            self.frame_productos, 
            width=dims['categorias_width'], 
            height=dims['categorias_height'], 
            orientation="horizontal",
            fg_color="#e3f0ff"
        )
        self.frame_categorias_scroll.place(x=positions['categorias_x'], y=positions['categorias_y'])

        # ScrollableFrame para productos
        self.frame_productos_scroll = ctk.CTkScrollableFrame(
            self.frame_productos, 
            width=dims['scroll_width'], 
            height=dims['scroll_height'],
            fg_color="#e3f0ff"
        )
        self.frame_productos_scroll.place(x=positions['productos_scroll_x'], y=positions['productos_scroll_y'])

        # Guardar dimensiones para uso en cargar_productos y cargar_categorias
        self.productos_btn_width = dims['productos_btn_width']
        self.productos_btn_height = dims['productos_btn_height']
        self.categorias_btn_width = dims['categorias_btn_width']
        self.categorias_btn_height = dims['categorias_btn_height']
    
    def setup_responsive_carrito_section(self):
        """Configura la sección del carrito de manera responsive"""
        dims = self.responsive.get_dimensions()
        positions = self.responsive.get_positions()
        
        # Cliente
        cliente_font = self.responsive.create_responsive_font(12, "bold", "normal")
        ctk.CTkLabel(
            self.frame_carrito, 
            text="Cliente:", 
            font=cliente_font
        ).place(x=positions['cliente_label_x'], y=positions['cliente_label_y'])

        self.entry_cliente = ctk.CTkEntry(
            self.frame_carrito, 
            placeholder_text="Nombre del cliente", 
            width=dims['cliente_entry_width'], 
            height=dims['cliente_entry_height'], 
            corner_radius=10,
            font=self.responsive.create_responsive_font(16, "normal", "normal")
        )
        self.entry_cliente.place(x=positions['cliente_entry_x'], y=positions['cliente_entry_y'])

        btn_buscar_cliente = ctk.CTkButton(
            self.frame_carrito, 
            text="👤", 
            width=dims['btn_cliente_width'], 
            height=dims['btn_cliente_height'],
            command=self.buscar_cliente_dialog, 
            corner_radius=10,
            font=self.responsive.create_responsive_font(16, "normal", "button")
        )
        btn_buscar_cliente.place(x=positions['cliente_btn_x'], y=positions['cliente_btn_y'])

        btn_nuevo_cliente = ctk.CTkButton(
            self.frame_carrito, 
            text="+", 
            width=dims['btn_cliente_width'], 
            height=dims['btn_cliente_height'],
            command=self.nuevo_cliente_dialog, 
            corner_radius=10,
            font=self.responsive.create_responsive_font(16, "bold", "button")
        )
        btn_nuevo_cliente.place(x=positions['cliente_btn2_x'], y=positions['cliente_btn2_y'])

        # Etiqueta para productos seleccionados
        productos_font = self.responsive.create_responsive_font(16, "bold", "normal")
        ctk.CTkLabel(
            self.frame_carrito, 
            text="Productos seleccionados:", 
            font=productos_font
        ).place(x=positions['carrito_label_x'], y=positions['carrito_label_y'])

        # Treeview para el carrito
        self.setup_responsive_carrito_treeview()

        # Totales
        self.frame_totales = ctk.CTkFrame(
            self.frame_carrito, 
            width=dims['totales_width'], 
            height=dims['totales_height'],
            fg_color="#e3f0ff"
        )
        self.frame_totales.place(x=positions['totales_x'], y=positions['totales_y'])

        subtotal_font = self.responsive.create_responsive_font(12, "normal", "normal")
        self.label_subtotal = ctk.CTkLabel(
            self.frame_totales, 
            text="Subtotal: $0.00", 
            font=subtotal_font
        )
        self.label_subtotal.place(x=dims['margin'], y=dims['padding'])

        total_font = self.responsive.create_responsive_font(14, "bold", "large")
        self.label_total = ctk.CTkLabel(
            self.frame_totales, 
            text="TOTAL: $0.00", 
            font=total_font, 
            text_color="red"
        )
        self.label_total.place(x=dims['margin'], y=dims['padding'] + 25)
        
        # Selector de moneda principal (debajo del total)
        moneda_font = self.responsive.create_responsive_font(14, "normal", "normal")
        self.label_moneda = ctk.CTkLabel(
            self.frame_totales, 
            text="Moneda:", 
            font=moneda_font
        )
        self.label_moneda.place(x=dims['margin'], y=dims['padding'] + 55)
        
        opciones_monedas = [m['codigo'] for m in self.monedas_activas]
        combo_width = 80
        combo_height = 25
        
        self.combo_moneda = ctk.CTkComboBox(
            self.frame_totales, 
            values=opciones_monedas, 
            width=combo_width, 
            height=combo_height,
            command=self.cambiar_moneda_evento,
            font=self.responsive.create_responsive_font(9, "normal", "normal")
        )
        self.combo_moneda.set(self.moneda_principal)
        self.combo_moneda.place(x=dims['margin'] + 60, y=dims['padding'] + 55)

        # Información del usuario
        info_frame_width = int(dims['carrito_width'] * 0.96)
        info_frame_height = max(35, int(dims['carrito_height'] * 0.04))
        
        user_info_frame = ctk.CTkFrame(
            self.frame_carrito, 
            width=info_frame_width, 
            height=info_frame_height,
            fg_color="#e3f0ff"
        )
        user_info_frame.place(x=positions['user_info_x'], y=positions['user_info_y'])

        user_font = self.responsive.create_responsive_font(20, "normal", "small")
        user_label = ctk.CTkLabel(
            user_info_frame, 
            text=f"Usuario: {self.usuario_actual['username']} | {self.usuario_actual['rol'].title()}",
            font=user_font,
            text_color="#00023b"
        )
        user_label.place(x=dims['margin'], y=5)

        logout_btn_width = int(info_frame_width * 0.15)
        logout_btn_height = max(25, int(info_frame_height * 0.7))
        logout_font = self.responsive.create_responsive_font(20, "normal", "bold")
        
        btn_logout = ctk.CTkButton(
            user_info_frame, 
            text="🚺 Salir", 
            width=120, 
            height=logout_btn_height,
            command=self.logout, 
            corner_radius=10,
            fg_color="#00a1e1", 
            hover_color="#025474",
            font=logout_font
        )
        btn_logout.place(x=int(info_frame_width * 0.8), y=2)

        # Botones de acción
        self.frame_acciones = ctk.CTkFrame(
            self.frame_carrito, 
            width=dims['acciones_width'], 
            height=dims['acciones_height'],
            fg_color="#e3f0ff" 

        )
        self.frame_acciones.place(x=positions['acciones_x'], y=positions['acciones_y'])

        # Configurar botones de acción
        self.setup_responsive_action_buttons()
    
    def setup_responsive_carrito_treeview(self):
        """Configura el Treeview del carrito de manera responsive"""
        dims = self.responsive.get_dimensions()
        positions = self.responsive.get_positions()
        
        # Crear frame para el treeview
        self.tree_frame = tk.Frame(self.frame_carrito, bg='white')
        self.tree_frame.place(
            x=positions['tree_x'], 
            y=positions['tree_y'], 
            width=dims['tree_width'], 
            height=dims['tree_height']
        )

        # Configurar el Treeview
        self.tree_carrito = ttk.Treeview(
            self.tree_frame, 
            columns=("producto", "cantidad", "precio_unit", "subtotal"), 
            show="headings",
            height=max(10, int(dims['tree_height'] / 25))  # Altura adaptativa
        )

        # Configurar encabezados con fuente responsive
        header_font = ('Arial', self.responsive.get_font_size(13, 'normal'))
        style = ttk.Style()
        style.configure("Treeview.Heading", font=header_font, background="#ffffff", foreground="#010577")
        style.configure("Treeview", font=('Arial', self.responsive.get_font_size(15, 'normal')), rowheight=55)

        
        self.tree_carrito.heading("producto", text="Producto")
        self.tree_carrito.heading("cantidad", text="Cant.")
        self.tree_carrito.heading("precio_unit", text="Precio Unit.")
        self.tree_carrito.heading("subtotal", text="Subtotal")

        # Configurar anchos de columnas de manera proporcional
        tree_width = dims['tree_width']
        self.tree_carrito.column("producto", width=int(tree_width * 0.45), anchor="w")
        self.tree_carrito.column("cantidad", width=int(tree_width * 0.15), anchor="center")
        self.tree_carrito.column("precio_unit", width=int(tree_width * 0.2), anchor="e")
        self.tree_carrito.column("subtotal", width=int(tree_width * 0.2), anchor="e")

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree_carrito.yview)
        self.tree_carrito.configure(yscrollcommand=scrollbar.set)

        # Empaquetar elementos
        self.tree_carrito.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind para editar cantidad
        self.tree_carrito.bind('<Double-1>', self.editar_cantidad_carrito)
    
    def setup_responsive_funciones_section(self):
        """Configura la sección de funciones del sistema de manera responsive"""
        dims = self.responsive.get_dimensions()
        
        # Obtener botones según el rol del usuario
        botones = self.get_user_buttons()
        
        # Configuración para botones cuadrados en una sola línea
        num_cols = len(botones)  # Todos los botones en una línea
        num_rows = 1
        
        # Hacer botones cuadrados y más pequeños para que quepan todos
        btn_size = min(dims['funciones_height'] - 40, (dims['funciones_width'] - (dims['margin'] * 2)) // len(botones) - 10)
        btn_width = btn_size
        btn_height = btn_size
        
        # Calcular espaciado para botones en una sola línea
        available_width = dims['funciones_width'] - (dims['margin'] * 2)
        total_btn_width = num_cols * btn_width
        spacing_x = max(5, (available_width - total_btn_width) // (num_cols + 1))
        spacing_y = (dims['funciones_height'] - btn_height) // 2
        
        start_x = dims['margin'] + spacing_x
        start_y = spacing_y

        # Fuente para botones cuadrados (más grande para el nombre y el icono)
        button_font = self.responsive.create_responsive_font(20, "bold", "button")

        for idx, (texto, comando) in enumerate(botones):
            row = idx // num_cols
            col = idx % num_cols

            x_pos = start_x + col * (btn_width + spacing_x)
            y_pos = start_y + row * (btn_height + spacing_y)

            # Color especial para el botón de actualizar tasa
            fg_color = "blue" if "Actualizar Tasa" in texto else None
            hover_color = "darkblue" if "Actualizar Tasa" in texto else None

            btn = ctk.CTkButton(
                self.frame_funciones,
                text=texto,
                width=btn_width,
                height=btn_height,
                command=comando,
                corner_radius=10,
                font=button_font,
                fg_color=fg_color,
                hover_color=hover_color
            )
            btn.place(x=x_pos, y=y_pos)
    
    def setup_responsive_action_buttons(self):
        """Configura los botones de acción de manera responsive"""
        dims = self.responsive.get_dimensions()
        # Fuente aumentada para botones de acción
        button_font = self.responsive.create_responsive_font(18, "bold", "button")
        
        btn_width = 110
        btn_height = 90
        margin = dims['margin']
        
        buttons = [
            {
                'text': '🗑️\nLimpiar',
                'command': self.limpiar_carrito,
                'text_color': "#023d61",
                'fg_color': '#d0ecf8',
                'hover_color': '#04a2e1'
            },
            {
                'text': '💾\nGuardar',
                'command': self.guardar_operacion_dialog,
                'text_color': "#023d61",
                'fg_color': '#d0ecf8',
                'hover_color': '#04a2e1'
            },
            {
                'text': '💰\nCobrar',
                'command': self.procesar_venta_dialog,
                'text_color': "#023d61",
                'fg_color': '#d0ecf8',
                'hover_color': '#04a2e1'
            },
            {
                'text': '➖\nQuitar\nProducto',
                'command': self.eliminar_item_carrito,
                'text_color': "#023d61",
                'fg_color': '#d0ecf8',
                'hover_color': '#04a2e1'
            },
            {
                'text': '📝\nPrecio\nManual',
                'command': self.cambiar_precio_manual,
                'text_color': "#023d61",
                'fg_color': '#d0ecf8',
                'hover_color': '#04a2e1'
            }
        ]
        
        # Configuración para máximo 3 botones por línea
        max_cols = 5
        num_buttons = len(buttons)
        num_rows_needed = (num_buttons + max_cols - 1) // max_cols
        
        for idx, btn_config in enumerate(buttons):
            row = idx // max_cols
            col = idx % max_cols
            
            x_pos = margin + col * (btn_width + margin)
            y_pos = margin + row * (btn_height + margin)
            
            btn = ctk.CTkButton(
                self.frame_acciones,
                text=btn_config['text'],
                width=btn_width,
                height=btn_height,
                command=btn_config['command'],
                corner_radius=10,
                fg_color=btn_config.get('fg_color'),
                hover_color=btn_config.get('hover_color'),
                text_color=btn_config.get('text_color'),
                font=button_font
            )
            btn.place(x=x_pos, y=y_pos)
    
    def clear_all_ui_elements(self):
        """Limpia todos los elementos de la UI para recrearlos"""
        try:
            # Destruir frames principales
            if hasattr(self, 'frame_productos'):
                self.frame_productos.destroy()
            if hasattr(self, 'frame_carrito'):
                self.frame_carrito.destroy()
            if hasattr(self, 'frame_funciones'):
                self.frame_funciones.destroy()
            if hasattr(self, 'logo_frame'):
                self.logo_frame.destroy()
        except Exception as e:
            print(f"Error al limpiar elementos UI: {e}")
    
    def enable_responsive_features(self):
        """Habilita características responsive adicionales"""
        # Configurar ventana para ser redimensionable (opcional)
        self.ventana.resizable(True, True)
        
        # Establecer tamaños mínimos
        self.ventana.minsize(1024, 768)
        
        # Configurar el protocolo de cierre para limpiar recursos
        self.ventana.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        try:
            self.ventana.quit()
            self.ventana.destroy()
        except:
            pass
    
    def get_responsive_info(self):
        """Retorna información sobre el estado responsive actual (para debug)"""
        return {
            'device_type': self.responsive.device_type,
            'screen_resolution': f"{self.responsive.screen_width}x{self.responsive.screen_height}",
            'scale_factor': self.responsive.scale_factor,
            'dpi': self.responsive.dpi,
            'compact_mode': self.responsive.should_use_compact_mode()
        }

    def abrir_empresa(self):
        """Abre la ventana para editar los datos de la empresa (tabla configuracion)"""
        try:
            from tkinter import Toplevel, Label, Entry, Button
            win = Toplevel(self.ventana)
            win.title("Datos de la Empresa")
            win.geometry("400x400")
            win.transient(self.ventana)
            win.grab_set()
            win.lift()
            win.focus_force()
            # Obtener datos actuales
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT nombre_tienda, direccion_tienda, telefono_tienda, impuesto_por_defecto, moneda FROM configuracion LIMIT 1")
            datos = cursor.fetchone()
            conn.close()
            # Labels y entries
            Label(win, text="Nombre de la empresa:").pack(pady=5)
            entry_nombre = Entry(win, width=40)
            entry_nombre.pack(pady=5)
            Label(win, text="Dirección:").pack(pady=5)
            entry_direccion = Entry(win, width=40)
            entry_direccion.pack(pady=5)
            Label(win, text="Teléfono:").pack(pady=5)
            entry_telefono = Entry(win, width=40)
            entry_telefono.pack(pady=5)
            Label(win, text="Impuesto por defecto (%):").pack(pady=5)
            entry_impuesto = Entry(win, width=40)
            entry_impuesto.pack(pady=5)
            Label(win, text="Moneda:").pack(pady=5)
            entry_moneda = Entry(win, width=40)
            entry_moneda.pack(pady=5)
            # Cargar datos si existen
            if datos:
                entry_nombre.insert(0, datos[0] or "")
                entry_direccion.insert(0, datos[1] or "")
                entry_telefono.insert(0, datos[2] or "")
                entry_impuesto.insert(0, str(datos[3]) if datos[3] is not None else "")
                entry_moneda.insert(0, datos[4] or "")
            def guardar():
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE configuracion SET nombre_tienda=?, direccion_tienda=?, telefono_tienda=?, impuesto_por_defecto=?, moneda=? WHERE id=1", (
                    entry_nombre.get(), entry_direccion.get(), entry_telefono.get(), entry_impuesto.get(), entry_moneda.get()
                ))
                conn.commit()
                conn.close()
                win.destroy()
            Button(win, text="Guardar", command=guardar, bg="green", fg="white").pack(pady=20)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"No se pudo abrir la ventana de empresa: {e}")

    def abrir_compras(self):
        """Abre la ventana de compras para dar existencia a inventario"""
        try:
            from compras_window import ComprasWindow
            ComprasWindow(self.ventana, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Compras: {e}")

    def abrir_categorias(self):
        """Abre la ventana para registrar/borrar/actualizar categorías"""
        try:
            from categorias_window import CategoriasWindow
            # Pasar callback para actualizar lista de categorías al cerrar
            CategoriasWindow(self.ventana, self.db, self.cargar_categorias)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Categorías: {e}")

    def abrir_usuarios(self):
        """Abre la ventana para registrar/gestionar usuarios"""
        try:
            from usuarios_window import UsuariosWindow
            UsuariosWindow(self.ventana, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Usuarios: {e}")
    def actualizar_tasa_cambio_ui(self):
        """Abre la ventana avanzada para actualizar la tasa de cambio"""
        try:
            from tasa_cambio_window import TasaCambioWindow
            
            def callback_actualizar():
                """Callback que se ejecuta después de actualizar la tasa"""
                # ACTUALIZAR tasa_camb en todos los productos
                nueva_tasa = self.db.get_tasa_cambio()
                self.actualizar_tasa_camb_productos(nueva_tasa)
                
                # Recargar monedas activas y tasas
                monedas = self.db.get_monedas_activas() or []
                self.monedas_activas = []
                for m in monedas:
                    tasa = 1.0 if m['codigo'] == 'VES' else self.db.get_tasa_cambio() or 0.0
                    self.monedas_activas.append({
                        'codigo': m['codigo'],
                        'simbolo': m['simbolo'],
                        'tasa': tasa
                    })
                self.moneda_principal = self.monedas_activas[0]['codigo'] if self.monedas_activas else 'VES'
                
                # Actualizar selector de moneda
                opciones_monedas = [m['codigo'] for m in self.monedas_activas]
                self.combo_moneda.configure(values=opciones_monedas)
                self.combo_moneda.set(self.moneda_principal)
                
                # Recargar productos y carrito
                self.cargar_productos(self.categoria_seleccionada)
                self.actualizar_carrito_ui()
            
            # Abrir ventana de tasa de cambio
            TasaCambioWindow(self.ventana, self.db, callback_actualizar)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir ventana de tasa: {e}")

    def actualizar_tasa_camb_productos(self, nueva_tasa):
        """Actualiza el campo tasa_camb en todos los productos"""
        try:
            import sqlite3, os
            db_path = os.path.join(os.path.dirname(__file__), 'punto_venta.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE productos SET tasa_camb = ?", (nueva_tasa,))
            conn.commit()
            conn.close()
        except Exception as err:
            messagebox.showerror("Error", f"No se pudo actualizar tasa_camb en productos: {err}")
    
    def cargar_categorias(self):
        """Carga las categorías desde la base de datos"""
        categorias = self.db.get_categorias()
        # Limpiar frame scroll
        for widget in self.frame_categorias_scroll.winfo_children():
            widget.destroy()
        # Botón "Todos"
        btn_todos = ctk.CTkButton(
            self.frame_categorias_scroll, text="Todos", width=self.categorias_btn_width, height=self.categorias_btn_height,
            command=lambda: self.filtrar_por_categoria(None),
            corner_radius=10,
            font=ctk.CTkFont(size=max(10, int(self.categorias_btn_height * 0.5)))
        )
        btn_todos.grid(row=0, column=0, padx=5, pady=5)
        # Botones de categorías
        for i, categoria in enumerate(categorias):
            btn = ctk.CTkButton(
                self.frame_categorias_scroll, text=categoria['nombre'], width=self.categorias_btn_width, height=self.categorias_btn_height,
                command=lambda cat_id=categoria['id']: self.filtrar_por_categoria(cat_id),
                corner_radius=10,
                font=ctk.CTkFont(size=max(10, int(self.categorias_btn_height * 0.5)))
            )
            btn.grid(row=0, column=i+1, padx=5, pady=5)
    
    def cargar_productos(self, categoria_id=None, busqueda=""):
        """Carga productos desde la base de datos y muestra precios en la moneda principal seleccionada"""
        # Limpiar productos actuales
        for widget in self.frame_productos_scroll.winfo_children():
            widget.destroy()
        if busqueda:
            productos = self.db.buscar_productos(busqueda)
        else:
            productos = self.db.get_productos(categoria_id)
        # Crear botones de productos en grid (cuadrados)
        # Calcular cuántos botones cuadrados caben por fila
        size_btn = min(self.productos_btn_width, self.productos_btn_height)
        scroll_width_available = int(self.frame_productos_scroll.winfo_reqwidth() or 800)
        productos_por_fila = max(3, scroll_width_available // (size_btn + 10))
        
        for i, producto in enumerate(productos):
            fila = i // productos_por_fila
            columna = i % productos_por_fila
            stock_info = f"Stock: {producto['stock_actual']}"
            # Mostrar precio según moneda principal usando la fórmula correcta
            if self.moneda_principal == 'USD':
                precio = producto.get('precio_venta_usd', 0) or 0
                precio_texto = f"$ {precio:.2f}"
            elif self.moneda_principal == 'VES':
                precio = producto.get('precio_venta', 0) or 0
                precio_texto = f"Bs {precio:.2f}"
            else:
                precio = producto.get('precio_venta', 0) or 0
                precio_texto = f"{self.moneda_principal} {precio:.2f}"
            # Hacer el botón de producto cuadrado y de tono más claro
            size_btn = min(self.productos_btn_width, self.productos_btn_height)
            btn_producto = ctk.CTkButton(
                self.frame_productos_scroll,
                text=f"{producto['nombre']}\n{precio_texto}\n{stock_info}",
                width=size_btn, height=size_btn,
                command=lambda p=producto: self.agregar_al_carrito(p),
                corner_radius=10,
                fg_color="#00a1e2",
                hover_color="#d0ecf8",
                font=ctk.CTkFont(size=max(12, int(size_btn * 0.12)),weight="bold"),
                text_color="#FFFFFF",  # gris oscuro
                state="normal" if producto['stock_actual'] > 0 else "disabled"
            )
            btn_producto.grid(row=fila, column=columna, padx=5, pady=5, sticky="nsew")
    
    def filtrar_por_categoria(self, categoria_id):
        """Filtra productos por categoría"""
        self.categoria_seleccionada = categoria_id
        self.cargar_productos(categoria_id)
    
    def buscar_productos_evento(self, event=None):
        """Busca productos en tiempo real"""
        termino = self.entry_busqueda.get()
        if len(termino) >= 2:  # Buscar solo si hay al menos 2 caracteres
            self.cargar_productos(busqueda=termino)
        elif len(termino) == 0:
            self.cargar_productos(self.categoria_seleccionada)
    
    def buscar_productos(self):
        """Busca productos manualmente"""
        termino = self.entry_busqueda.get()
        self.cargar_productos(busqueda=termino)
    
    def mostrar_dialogo_modo_venta(self, nombre_producto, unidades_por_bulto):
        """Muestra un diálogo con botones para elegir Unidad o Bulto"""
        dialog = ctk.CTkToplevel(self.ventana)
        dialog.title("Modo de venta")
        dialog.geometry("360x160")
        dialog.transient(self.ventana)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text=f"¿Cómo desea vender {nombre_producto}?\nCada bulto trae {unidades_por_bulto} unidades.",
            font=ctk.CTkFont(size=14, weight="bold")
        ).place(x=10, y=10)
        
        resultado = {'bulto': False}
        
        def elegir_bulto():
            resultado['bulto'] = True
            dialog.destroy()
        
        def elegir_unidad():
            resultado['bulto'] = False
            dialog.destroy()
        
        btn_bulto = ctk.CTkButton(dialog, text="🧱 Bulto", width=120, height=45, command=elegir_bulto, fg_color="#1f538d", hover_color="#14375e")
        btn_unidad = ctk.CTkButton(dialog, text="🧩 Unidad", width=120, height=45, command=elegir_unidad, fg_color="#2fa572", hover_color="#106A43")
        
        btn_bulto.place(x=40, y=90)
        btn_unidad.place(x=190, y=90)
        
        self.ventana.wait_window(dialog)
        return resultado['bulto']

    def agregar_al_carrito(self, producto):
        """Agrega un producto al carrito (soporta venta por bulto cuando aplique)"""
        if producto['stock_actual'] <= 0:
            messagebox.showwarning("Sin Stock", f"El producto {producto['nombre']} no tiene stock disponible.")
            return
        
        # Obtener el precio correcto según la moneda principal
        if self.moneda_principal == 'USD':
            precio_unitario = producto.get('precio_venta_usd', 0) or 0
        else:  # VES o cualquier otra moneda
            precio_unitario = producto.get('precio_venta', 0) or 0
        
        # Determinar modo (unidad o bulto) si aplica
        modo_bulto = False
        unidades_por_bulto = int(producto.get('unidades_por_bulto', 0) or 0)
        if int(producto.get('vende_al_mayor', 0) or 0) == 1 and unidades_por_bulto > 0:
            modo_bulto = self.mostrar_dialogo_modo_venta(producto['nombre'], unidades_por_bulto)
        
        # Helper para solicitar cantidad
        def solicitar_cantidad(mensaje):
            dialog = ctk.CTkInputDialog(text=mensaje, title="Cantidad")
            valor = dialog.get_input()
            return valor
        
        # Verificar si el producto ya está en el carrito
        for item in self.carrito:
            if item['producto_id'] == producto['id']:
                # Permitir sumar cantidades decimales (o bultos convertidos a unidades)
                if item['cantidad'] < producto['stock_actual']:
                    if modo_bulto:
                        max_bultos = int(producto['stock_actual'] // unidades_por_bulto)
                        if max_bultos <= 0:
                            messagebox.showwarning("Sin Stock", "No hay suficiente stock para un bulto.")
                            return
                        cantidad_input = solicitar_cantidad(f"Bultos a agregar (máx {max_bultos}):")
                        try:
                            bultos = float(cantidad_input)
                            if bultos <= 0:
                                return
                            unidades = bultos * unidades_por_bulto
                        except Exception:
                            messagebox.showerror("Error", "Ingrese un número válido.")
                            return
                    else:
                        cantidad_input = solicitar_cantidad(f"Cantidad a agregar para {producto['nombre']} (stock: {producto['stock_actual']}):")
                        try:
                            unidades = float(cantidad_input)
                            if unidades <= 0:
                                return
                        except Exception:
                            messagebox.showerror("Error", "Ingrese un número válido.")
                            return
                    if item['cantidad'] + unidades > producto['stock_actual']:
                        messagebox.showwarning(
                            "Stock Insuficiente",
                            f"No hay suficiente stock. Disponible: {producto['stock_actual']}"
                        )
                        return
                    item['cantidad'] += unidades
                    item['precio_unitario'] = precio_unitario
                    self.actualizar_carrito_ui()
                    return
                else:
                    messagebox.showwarning(
                        "Stock Insuficiente", 
                        f"No hay suficiente stock. Disponible: {producto['stock_actual']}"
                    )
                    return
        
        # Agregar nuevo producto al carrito
        # Solicitar cantidad inicial
        if modo_bulto:
            max_bultos = int(producto['stock_actual'] // unidades_por_bulto)
            if max_bultos <= 0:
                messagebox.showwarning("Sin Stock", "No hay suficiente stock para un bulto.")
                return
            cantidad_input = solicitar_cantidad(f"Bultos a vender (máx {max_bultos}):")
            try:
                bultos = float(cantidad_input)
                unidades = bultos * unidades_por_bulto
            except Exception:
                messagebox.showerror("Error", "Ingrese un número válido.")
                return
        else:
            cantidad_input = solicitar_cantidad(f"Cantidad para {producto['nombre']} (stock: {producto['stock_actual']}):")
            try:
                unidades = float(cantidad_input)
            except Exception:
                messagebox.showerror("Error", "Ingrese un número válido.")
                return
        
        if unidades <= 0 or unidades > producto['stock_actual']:
            messagebox.showwarning("Cantidad inválida", f"Ingrese una cantidad válida (máx: {producto['stock_actual']})")
            return
        item_carrito = {
            'producto_id': producto['id'],
            'nombre': producto['nombre'],
            'precio_unitario': precio_unitario,
            'cantidad': unidades,
            'stock_disponible': producto['stock_actual']
        }
        self.carrito.append(item_carrito)
        self.actualizar_carrito_ui()
    
    def actualizar_carrito_ui(self):
        """Actualiza la interfaz del carrito mostrando solo la moneda principal seleccionada"""
        # Limpiar treeview
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        
        # Calcular total en moneda principal
        subtotal_principal = 0
        for item in self.carrito:
            precio_unitario = item['precio_unitario']
            subtotal_item = item['cantidad'] * precio_unitario
            subtotal_principal += subtotal_item
            
            # Obtener símbolo de la moneda principal
            simbolo = next((m['simbolo'] for m in self.monedas_activas if m['codigo'] == self.moneda_principal), self.moneda_principal)
            
            self.tree_carrito.insert('', 'end', values=(
                item['nombre'],
                item['cantidad'],
                f"{simbolo} {precio_unitario:.2f}",
                f"{simbolo} {subtotal_item:.2f}"
            ))
        
        # Actualizar totales solo en moneda principal
        simbolo = next((m['simbolo'] for m in self.monedas_activas if m['codigo'] == self.moneda_principal), self.moneda_principal)
        self.label_subtotal.configure(text=f"Subtotal: {simbolo} {subtotal_principal:.2f}")
        self.label_total.configure(text=f"TOTAL: {simbolo} {subtotal_principal:.2f}")
    
    def editar_cantidad_carrito(self, event):
        """Permite editar la cantidad de un producto en el carrito"""
        selection = self.tree_carrito.selection()
        if not selection:
            return
        
        item_id = selection[0]
        index = self.tree_carrito.index(item_id)
        item_carrito = self.carrito[index]
        
        # Dialog para editar cantidad
        dialog = ctk.CTkInputDialog(
            text=f"Cantidad para {item_carrito['nombre']}:\n(Stock disponible: {item_carrito['stock_disponible']})",
            title="Editar Cantidad"
        )
        nueva_cantidad = dialog.get_input()
        
        if nueva_cantidad:
            try:
                nueva_cantidad = float(nueva_cantidad)
                if nueva_cantidad <= 0:
                    # Eliminar del carrito
                    self.carrito.pop(index)
                elif nueva_cantidad <= item_carrito['stock_disponible']:
                    item_carrito['cantidad'] = nueva_cantidad
                else:
                    messagebox.showwarning(
                        "Stock Insuficiente", 
                        f"Solo hay {item_carrito['stock_disponible']} unidades disponibles."
                    )
                    return
                self.actualizar_carrito_ui()
            except ValueError:
                messagebox.showerror("Error", "Ingrese un número válido.")
    
    def eliminar_item_carrito(self):
        """Elimina el item seleccionado del carrito"""
        selection = self.tree_carrito.selection()
        if not selection:
            messagebox.showinfo("Información", "Seleccione un producto para eliminar.")
            return
        
        item_id = selection[0]
        index = self.tree_carrito.index(item_id)
        
        # Confirmar eliminación
        if messagebox.askyesno("Confirmar", "¿Desea eliminar este producto del carrito?"):
            self.carrito.pop(index)
            self.actualizar_carrito_ui()
    
    def cambiar_precio_manual(self):
        """Permite cambiar manualmente el precio unitario del item seleccionado"""
        selection = self.tree_carrito.selection()
        if not selection:
            messagebox.showinfo("Información", "Seleccione un producto del carrito para cambiar el precio.")
            return
        item_id = selection[0]
        index = self.tree_carrito.index(item_id)
        item_carrito = self.carrito[index]
        simbolo = next((m['simbolo'] for m in self.monedas_activas if m['codigo'] == self.moneda_principal), self.moneda_principal)
        dialog = ctk.CTkInputDialog(
            text=f"Nuevo precio unitario ({simbolo}) para {item_carrito['nombre']} (actual: {simbolo} {item_carrito['precio_unitario']:.2f}):",
            title="Precio manual"
        )
        nuevo = dialog.get_input()
        if nuevo is None:
            return
        try:
            nuevo_val = float(nuevo)
            if nuevo_val < 0:
                messagebox.showwarning("Precio inválido", "El precio no puede ser negativo")
                return
            item_carrito['precio_unitario'] = nuevo_val
            self.actualizar_carrito_ui()
        except Exception:
            messagebox.showerror("Error", "Ingrese un número válido.")

    def limpiar_carrito(self):
        """Limpia todo el carrito"""
        if not self.carrito:
            return
        
        if messagebox.askyesno("Confirmar", "¿Desea limpiar todo el carrito?"):
            self.carrito.clear()
            self.cliente_seleccionado = None
            self.entry_cliente.delete(0, 'end')
            self.actualizar_carrito_ui()
    
    def buscar_cliente_dialog(self):
        """Abre dialog para buscar cliente"""
        # Crear ventana de búsqueda de clientes
        busqueda_window = ctk.CTkToplevel(self.ventana)
        busqueda_window.title("Buscar Cliente")
        busqueda_window.geometry("500x400")
        busqueda_window.transient(self.ventana)
        busqueda_window.grab_set()
        
        # Campo de búsqueda
        ctk.CTkLabel(busqueda_window, text="Buscar cliente:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        entry_busqueda = ctk.CTkEntry(busqueda_window, width=400, height=35, placeholder_text="Nombre, teléfono...")
        entry_busqueda.pack(pady=5)
        
        # Lista de resultados
        frame_resultados = tk.Frame(busqueda_window, bg='white')
        frame_resultados.pack(pady=10, padx=10, fill='both', expand=True)
        
        tree_clientes = ttk.Treeview(
            frame_resultados,
            columns=("nombre", "telefono", "email"),
            show="headings",
            height=12
        )
        
        tree_clientes.heading("nombre", text="Nombre")
        tree_clientes.heading("telefono", text="Teléfono")
        tree_clientes.heading("email", text="Email")
        
        tree_clientes.column("nombre", width=200)
        tree_clientes.column("telefono", width=120)
        tree_clientes.column("email", width=150)
        
        scrollbar_clientes = ttk.Scrollbar(frame_resultados, orient="vertical", command=tree_clientes.yview)
        tree_clientes.configure(yscrollcommand=scrollbar_clientes.set)
        
        tree_clientes.pack(side="left", fill="both", expand=True)
        scrollbar_clientes.pack(side="right", fill="y")
        
        def buscar_clientes_tiempo_real(event=None):
            termino = entry_busqueda.get()
            # Limpiar resultados anteriores
            for item in tree_clientes.get_children():
                tree_clientes.delete(item)
            
            if len(termino) >= 2:
                clientes = self.db.buscar_cliente(termino)
                for cliente in clientes:
                    tree_clientes.insert('', 'end', values=(
                        f"{cliente['nombre']} {cliente.get('apellido', '')}".strip(),
                        cliente.get('telefono', ''),
                        cliente.get('email', '')
                    ), tags=(cliente['id'],))
        
        def seleccionar_cliente():
            selection = tree_clientes.selection()
            if selection:
                item = tree_clientes.item(selection[0])
                cliente_id = tree_clientes.item(selection[0])['tags'][0]
                nombre_completo = item['values'][0]
                
                # Actualizar cliente seleccionado
                self.cliente_seleccionado = int(cliente_id)
                self.entry_cliente.delete(0, 'end')
                self.entry_cliente.insert(0, nombre_completo)
                
                busqueda_window.destroy()
        
        # Eventos
        entry_busqueda.bind('<KeyRelease>', buscar_clientes_tiempo_real)
        tree_clientes.bind('<Double-1>', lambda e: seleccionar_cliente())
        
        # Botones
        frame_botones = ctk.CTkFrame(busqueda_window)
        frame_botones.pack(pady=10)
        
        ctk.CTkButton(frame_botones, text="Seleccionar", command=seleccionar_cliente).pack(side="left", padx=5)
        ctk.CTkButton(frame_botones, text="Cancelar", command=busqueda_window.destroy).pack(side="right", padx=5)
        
        # Cargar todos los clientes inicialmente
        buscar_clientes_tiempo_real()
    
    def nuevo_cliente_dialog(self):
        """Abre dialog para crear nuevo cliente"""
        # Crear ventana de nuevo cliente
        cliente_window = ctk.CTkToplevel(self.ventana)
        cliente_window.title("Nuevo Cliente")
        cliente_window.geometry("400x350")
        cliente_window.transient(self.ventana)
        cliente_window.grab_set()
        
        # Campos del formulario
        ctk.CTkLabel(cliente_window, text="Nuevo Cliente", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        
        # Nombre
        ctk.CTkLabel(cliente_window, text="Nombre:*").pack(anchor="w", padx=20)
        entry_nombre = ctk.CTkEntry(cliente_window, width=350, height=35)
        entry_nombre.pack(pady=5, padx=20)
        
        # Apellido
        ctk.CTkLabel(cliente_window, text="Apellido:").pack(anchor="w", padx=20, pady=(10,0))
        entry_apellido = ctk.CTkEntry(cliente_window, width=350, height=35)
        entry_apellido.pack(pady=5, padx=20)
        
        # Teléfono
        ctk.CTkLabel(cliente_window, text="Teléfono:").pack(anchor="w", padx=20, pady=(10,0))
        entry_telefono = ctk.CTkEntry(cliente_window, width=350, height=35)
        entry_telefono.pack(pady=5, padx=20)
        
        # Email
        ctk.CTkLabel(cliente_window, text="Email:").pack(anchor="w", padx=20, pady=(10,0))
        entry_email = ctk.CTkEntry(cliente_window, width=350, height=35)
        entry_email.pack(pady=5, padx=20)
        
        def guardar_cliente():
            nombre = entry_nombre.get().strip()
            if not nombre:
                messagebox.showerror("Error", "El nombre es requerido")
                return
            
            try:
                cliente_id = self.db.agregar_cliente(
                    nombre=nombre,
                    apellido=entry_apellido.get().strip(),
                    telefono=entry_telefono.get().strip(),
                    email=entry_email.get().strip()
                )
                
                # Seleccionar el nuevo cliente
                self.cliente_seleccionado = cliente_id
                nombre_completo = f"{nombre} {entry_apellido.get().strip()}".strip()
                self.entry_cliente.delete(0, 'end')
                self.entry_cliente.insert(0, nombre_completo)
                
                messagebox.showinfo("Éxito", "Cliente creado correctamente")
                cliente_window.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear cliente: {str(e)}")
        
        # Botones
        frame_botones = ctk.CTkFrame(cliente_window)
        frame_botones.pack(pady=20)
        
        ctk.CTkButton(
            frame_botones, text="Guardar", command=guardar_cliente,
            fg_color="green", hover_color="darkgreen"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            frame_botones, text="Cancelar", command=cliente_window.destroy,
            fg_color="gray", hover_color="darkgray"
        ).pack(side="right", padx=10)
        
        # Enfocar en el primer campo
        entry_nombre.focus()
    
    def guardar_operacion_dialog(self):
        """Guarda la operación actual en espera"""
        if not self.carrito:
            messagebox.showinfo("Información", "No hay productos en el carrito.")
            return
        
        dialog = ctk.CTkInputDialog(
            text="Nombre para la operación:",
            title="Guardar Operación"
        )
        nombre_operacion = dialog.get_input()
        
        if nombre_operacion:
            try:
                carrito_data = {
                    'carrito': self.carrito,
                    'cliente': self.entry_cliente.get() if self.entry_cliente.get() else None
                }
                
                operacion_id = self.db.guardar_operacion_espera(
                    nombre_operacion, carrito_data, self.cliente_seleccionado
                )
                
                messagebox.showinfo("Éxito", "Operación guardada correctamente.")
                self.limpiar_carrito()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def procesar_venta_dialog(self):
        """Abre la ventana de procesamiento de pagos"""
        if not self.carrito:
            messagebox.showinfo("Información", "No hay productos en el carrito.")
            return
        
        # Preparar información del cliente
        cliente_info = None
        if self.cliente_seleccionado:
            # Buscar información completa del cliente
            clientes = self.db.get_clientes()
            for cliente in clientes:
                if cliente['id'] == self.cliente_seleccionado:
                    cliente_info = cliente
                    break
        elif self.entry_cliente.get().strip():
            # Crear cliente temporal con el nombre ingresado
            cliente_info = {
                'nombre': self.entry_cliente.get().strip(),
                'id': None
            }
        
        # Abrir ventana de pagos
        from pagos_window import PagosWindow
        ventana_pagos = PagosWindow(self.ventana, self.db, self.carrito, cliente_info)
        
        # Esperar a que se cierre la ventana de pagos
        self.ventana.wait_window(ventana_pagos.window)
        
        # Si el pago fue exitoso, limpiar carrito y recargar productos
        if hasattr(ventana_pagos, 'pagado') and ventana_pagos.pagado:
            self.limpiar_carrito()
            self.cargar_productos(self.categoria_seleccionada)
    
    # FUNCIONES DEL MENÚ INFERIOR
    def abrir_configuracion_monedas(self):
        """Abre la ventana de configuración de monedas y actualiza la UI al guardar"""
        try:
            from configuracion_monedas_window import ConfiguracionMonedasWindow
            def on_configuracion_guardada():
                # Recargar monedas activas y tasas
                monedas = self.db.get_monedas_activas() or []
                self.monedas_activas = []
                for m in monedas:
                    tasa = 1.0 if m['codigo'] == 'VES' else self.db.get_tasa_cambio() or 0.0
                    self.monedas_activas.append({
                        'codigo': m['codigo'],
                        'simbolo': m['simbolo'],
                        'tasa': tasa
                    })
                self.moneda_principal = self.monedas_activas[0]['codigo'] if self.monedas_activas else 'VES'
                # Actualizar selector de moneda
                opciones_monedas = [m['codigo'] for m in self.monedas_activas]
                self.combo_moneda.configure(values=opciones_monedas)
                self.combo_moneda.set(self.moneda_principal)
                # Recargar productos y carrito
                self.cargar_productos(self.categoria_seleccionada)
                self.actualizar_carrito_ui()
            ConfiguracionMonedasWindow(self.ventana, on_configuracion_guardada)
        except Exception as e:
            messagebox.showerror("Error", f"Error abriendo configuración de monedas: {e}")
    
    def mostrar_corte_dia(self):
        """Muestra el corte del día con interfaz mejorada"""
        try:
            from corte_dia_window import CorteDiaWindow
            CorteDiaWindow(self.ventana, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir corte del día: {str(e)}")
    
    def abrir_inventario(self):
        """Abre la ventana de gestión de inventario"""
        from inventario_window import InventarioWindow
        InventarioWindow(self.ventana, self.db)
    
    def abrir_clientes(self):
        """Abre la ventana de gestión de clientes"""
        from clientes_window import ClientesWindow
        ClientesWindow(self.ventana, self.db)

    def abrir_usuarios(self):
        """Abre la ventana para registrar/gestionar usuarios (solo rol sistema)"""
        try:
            from usuarios_window import UsuariosWindow
            UsuariosWindow(self.ventana, self.db)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir Usuarios: {e}")
    
    def mostrar_operaciones_espera(self):
        """Muestra las operaciones en espera"""
        operaciones = self.db.get_operaciones_espera()
        
        if not operaciones:
            messagebox.showinfo("Información", "No hay operaciones en espera.")
            return
        
        # Crear ventana de operaciones en espera
        ventana_espera = ctk.CTkToplevel(self.ventana)
        ventana_espera.title("Operaciones en Espera")
        ventana_espera.geometry("800x500")
        
        # Lista de operaciones
        lista_frame = ctk.CTkScrollableFrame(ventana_espera, width=760, height=400)
        lista_frame.place(x=10, y=10)
        
        for i, operacion in enumerate(operaciones):
            frame_op = ctk.CTkFrame(lista_frame, width=740, height=80)
            frame_op.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            
            # Información de la operación
            info_text = f"{operacion['nombre_operacion']} - {operacion['fecha_creacion'][:16]}"
            if operacion['cliente_nombre']:
                info_text += f"\nCliente: {operacion['cliente_nombre']}"
            
            label_info = ctk.CTkLabel(frame_op, text=info_text, anchor="w")
            label_info.place(x=10, y=10)
            
            # Botones
            btn_cargar = ctk.CTkButton(
                frame_op, text="Cargar", width=100, height=30,
                command=lambda op_id=operacion['id']: self.cargar_operacion_espera(op_id, ventana_espera)
            )
            btn_cargar.place(x=550, y=10)
            
            btn_eliminar = ctk.CTkButton(
                frame_op, text="Eliminar", width=100, height=30,
                command=lambda op_id=operacion['id']: self.eliminar_operacion_espera(op_id, ventana_espera),
                fg_color="red", hover_color="darkred"
            )
            btn_eliminar.place(x=550, y=45)
    
    def cargar_operacion_espera(self, operacion_id, ventana_padre):
        """Carga una operación en espera"""
        operacion = self.db.cargar_operacion_espera(operacion_id)
        
        if operacion:
            # Cargar datos al carrito actual
            self.carrito = operacion['datos_carrito']['carrito']
            if operacion['datos_carrito']['cliente']:
                self.entry_cliente.delete(0, 'end')
                self.entry_cliente.insert(0, operacion['datos_carrito']['cliente'])
            
            self.actualizar_carrito_ui()
            
            # Eliminar la operación de espera
            self.db.eliminar_operacion_espera(operacion_id)
            
            messagebox.showinfo("Éxito", "Operación cargada correctamente.")
            ventana_padre.destroy()
    
    def eliminar_operacion_espera(self, operacion_id, ventana_padre):
        """Elimina una operación en espera"""
        if messagebox.askyesno("Confirmar", "¿Desea eliminar esta operación?"):
            self.db.eliminar_operacion_espera(operacion_id)
            messagebox.showinfo("Éxito", "Operación eliminada.")
            ventana_padre.destroy()
            self.mostrar_operaciones_espera()
    
    def abrir_reportes(self):
        """Abre la ventana de reportes"""
        messagebox.showinfo("Información", "Funcionalidad en desarrollo")
    
    def logout(self):
        """Cerrar sesión y volver al login"""
        from tkinter import messagebox
        if messagebox.askyesno("Cerrar Sesión", "¿Desea cerrar sesión?"):
            self.ventana.destroy()
            # Volver a mostrar login
            main()
    
    def run(self):
        """Ejecuta la aplicación"""
        self.ventana.mainloop()

def main():
    """Función principal que maneja el login y lanza la aplicación"""
    from login_window import LoginWindow
    
    # Mostrar ventana de login
    login_app = LoginWindow()
    usuario = login_app.run()
    
    # Si el login fue exitoso, abrir la aplicación principal
    if usuario:
        app = PuntoVentaApp(usuario)
        app.run()
    else:
        print("Aplicación cerrada por el usuario")

if __name__ == "__main__":
    main()
