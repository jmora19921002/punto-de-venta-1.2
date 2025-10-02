import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
from datetime import datetime, date, timedelta
from colores_modernos import PRIMARY_COLOR, SECONDARY_COLOR, ACCENT_COLOR, BACKGROUND_COLOR, CARD_COLOR, TEXT_COLOR, SUBTEXT_COLOR, SUCCESS_COLOR, ERROR_COLOR, BUTTON_COLOR, BUTTON_TEXT_COLOR, BORDER_RADIUS, FONT_FAMILY, TITLE_FONT_SIZE, SUBTITLE_FONT_SIZE, TEXT_FONT_SIZE, BUTTON_FONT_SIZE

class CorteDiaWindow:
    def __init__(self, parent, database_manager):
        self.parent = parent
        self.db = database_manager
        # Obtener la fecha con las ventas más recientes
        self.fecha_actual = self.get_fecha_con_ventas()
        
        # Crear ventana de corte del día
        self.window = ctk.CTkToplevel(parent, fg_color=BACKGROUND_COLOR)
        self.window.title("Corte del Día")
        self.window.geometry("1200x800")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.cargar_corte()
    
    def get_fecha_con_ventas(self):
        """Obtiene la fecha con ventas más recientes o la fecha actual"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Buscar la fecha de la venta más reciente
            cursor.execute("SELECT DATE(fecha_venta) FROM ventas ORDER BY fecha_venta DESC LIMIT 1")
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado:
                return resultado[0]
            else:
                # Si no hay ventas, usar fecha actual
                return date.today().strftime('%Y-%m-%d')
                
        except Exception:
            # Si hay error, usar fecha actual
            return date.today().strftime('%Y-%m-%d')
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Header con título y fecha
        self.frame_header = ctk.CTkFrame(self.window, height=80, fg_color=BACKGROUND_COLOR, corner_radius=BORDER_RADIUS)
        self.frame_header.pack(fill="x", padx=10, pady=(10, 5))

        
        # Título principal
        ctk.CTkLabel(
            self.frame_header,
            text="📊 CORTE DEL DÍA",
            font=ctk.CTkFont(size=TITLE_FONT_SIZE+6, weight="bold"),
            text_color=PRIMARY_COLOR
        ).pack(side="left", padx=20, pady=20)
        
        # Controles de fecha
        self.frame_fecha = ctk.CTkFrame(self.frame_header, fg_color=BACKGROUND_COLOR, corner_radius=BORDER_RADIUS)
        self.frame_fecha.pack(side="right", padx=20, pady=15)
        
        ctk.CTkLabel(self.frame_fecha, text="Fecha:", font=ctk.CTkFont(size=TEXT_FONT_SIZE, weight="bold"), text_color=TEXT_COLOR).pack(side="left", padx=5)
        
        self.entry_fecha = ctk.CTkEntry(self.frame_fecha, width=120, height=35, fg_color=CARD_COLOR, text_color=TEXT_COLOR, font=ctk.CTkFont(size=TEXT_FONT_SIZE))
        self.entry_fecha.pack(side="left", padx=5)
        self.entry_fecha.insert(0, self.fecha_actual)
        
        btn_hoy = ctk.CTkButton(self.frame_fecha, text="Hoy", width=60, height=35, command=self.fecha_hoy, fg_color=BUTTON_COLOR, text_color=BUTTON_TEXT_COLOR, font=ctk.CTkFont(size=BUTTON_FONT_SIZE), corner_radius=BORDER_RADIUS)
        btn_hoy.pack(side="left", padx=2)

        btn_ayer = ctk.CTkButton(self.frame_fecha, text="Ayer", width=60, height=35, command=self.fecha_ayer, fg_color=BUTTON_COLOR, text_color=BUTTON_TEXT_COLOR, font=ctk.CTkFont(size=BUTTON_FONT_SIZE), corner_radius=BORDER_RADIUS)
        btn_ayer.pack(side="left", padx=2)

        btn_ventas = ctk.CTkButton(self.frame_fecha, text="Ventas", width=60, height=35, command=self.fecha_con_ventas, fg_color=BUTTON_COLOR, text_color=BUTTON_TEXT_COLOR, font=ctk.CTkFont(size=BUTTON_FONT_SIZE), corner_radius=BORDER_RADIUS)
        btn_ventas.pack(side="left", padx=2)

        btn_actualizar = ctk.CTkButton(
            self.frame_fecha, text="🔄", width=40, height=35, 
            command=self.cargar_corte,
            fg_color=ACCENT_COLOR, text_color=BUTTON_TEXT_COLOR, font=ctk.CTkFont(size=BUTTON_FONT_SIZE), corner_radius=BORDER_RADIUS
        )
        btn_actualizar.pack(side="left", padx=5)
        
        # Contenedor principal con scroll
        self.scroll_frame = ctk.CTkScrollableFrame(self.window, width=1160, height=650, fg_color=BACKGROUND_COLOR)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Crear secciones
        self.create_resumen_section()
        self.create_metodos_pago_section()
        self.create_productos_section()
        self.create_actividad_section()
        self.create_estadisticas_section()
        
        # Botones inferiores
        self.frame_botones = ctk.CTkFrame(self.window, height=60, fg_color=BACKGROUND_COLOR, corner_radius=BORDER_RADIUS)
        self.frame_botones.pack(fill="x", padx=10, pady=5)

        btn_exportar = ctk.CTkButton(
            self.frame_botones, text="📄 Exportar PDF", width=150, height=40,
            command=self.exportar_pdf,
            fg_color=ACCENT_COLOR, hover_color=SECONDARY_COLOR, text_color=BUTTON_TEXT_COLOR, font=ctk.CTkFont(size=BUTTON_FONT_SIZE), corner_radius=BORDER_RADIUS
        )
        btn_exportar.pack(side="left", padx=10, pady=10)

        btn_imprimir = ctk.CTkButton(
            self.frame_botones, text="🖨️ Imprimir", width=150, height=40,
            command=self.imprimir_corte,
            fg_color=PRIMARY_COLOR, hover_color=SECONDARY_COLOR, text_color=BUTTON_TEXT_COLOR, font=ctk.CTkFont(size=BUTTON_FONT_SIZE), corner_radius=BORDER_RADIUS
        )
        btn_imprimir.pack(side="left", padx=5, pady=10)

        btn_cerrar = ctk.CTkButton(
            self.frame_botones, text="❌ Cerrar", width=100, height=40,
            command=self.window.destroy,
            fg_color=ERROR_COLOR, hover_color=SUBTEXT_COLOR, text_color=BUTTON_TEXT_COLOR, font=ctk.CTkFont(size=BUTTON_FONT_SIZE), corner_radius=BORDER_RADIUS
        )
        btn_cerrar.pack(side="right", padx=10, pady=10)
    
    def create_resumen_section(self):
        """Crea la sección de resumen general"""
        frame = ctk.CTkFrame(self.scroll_frame, height=200)
        frame.pack(fill="x", pady=10)
        
        # Título de sección
        ctk.CTkLabel(
            frame, 
            text="💰 RESUMEN GENERAL", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#27AE60"
        ).pack(pady=(15, 10))
        
        # Grid de estadísticas principales
        stats_frame = ctk.CTkFrame(frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        # Primera fila de estadísticas
        row1 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        
        self.stat_ventas = self.create_stat_card(row1, "Ventas Totales", "0", "#3498DB", "📊")
        self.stat_ventas.pack(side="left", padx=10, fill="x", expand=True)
        
        self.stat_ingresos = self.create_stat_card(row1, "Ingresos Totales", "$0.00", "#27AE60", "💰")
        self.stat_ingresos.pack(side="left", padx=10, fill="x", expand=True)
        
        self.stat_promedio = self.create_stat_card(row1, "Ticket Promedio", "$0.00", "#E67E22", "🎯")
        self.stat_promedio.pack(side="left", padx=10, fill="x", expand=True)
        
        # Segunda fila de estadísticas
        row2 = ctk.CTkFrame(stats_frame, fg_color="transparent")
        row2.pack(fill="x", pady=5)
        
        self.stat_descuentos = self.create_stat_card(row2, "Descuentos", "$0.00", "#E74C3C", "🔻")
        self.stat_descuentos.pack(side="left", padx=10, fill="x", expand=True)
        
        self.stat_impuestos = self.create_stat_card(row2, "Impuestos", "$0.00", "#9B59B6", "📋")
        self.stat_impuestos.pack(side="left", padx=10, fill="x", expand=True)
        
        self.stat_clientes = self.create_stat_card(row2, "Clientes Únicos", "0", "#1ABC9C", "👥")
        self.stat_clientes.pack(side="left", padx=10, fill="x", expand=True)
    
    def create_stat_card(self, parent, titulo, valor, color, emoji):
        """Crea una tarjeta de estadística"""
        card = ctk.CTkFrame(parent, fg_color=color, height=80)
        
        # Emoji
        ctk.CTkLabel(
            card, 
            text=emoji, 
            font=ctk.CTkFont(size=24)
        ).pack(pady=(10, 0))
        
        # Valor
        valor_label = ctk.CTkLabel(
            card, 
            text=valor, 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="white"
        )
        valor_label.pack()
        
        # Título
        ctk.CTkLabel(
            card, 
            text=titulo, 
            font=ctk.CTkFont(size=12),
            text_color="white"
        ).pack(pady=(0, 10))
        
        # Guardar referencia del label del valor para actualizarlo
        card.valor_label = valor_label
        return card
    
    def create_metodos_pago_section(self):
        """Crea la sección de métodos de pago"""
        frame = ctk.CTkFrame(self.scroll_frame)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            frame, 
            text="💳 INGRESOS POR MÉTODO DE PAGO", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#8E44AD"
        ).pack(pady=15)
        
        # Frame para la tabla
        table_frame = tk.Frame(frame, bg='white')
        table_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Crear treeview para métodos de pago
        self.tree_pagos = ttk.Treeview(
            table_frame,
            columns=("metodo", "ventas", "total", "promedio", "porcentaje"),
            show="headings",
            height=8
        )
        
        # Configurar encabezados
        self.tree_pagos.heading("metodo", text="Método de Pago")
        self.tree_pagos.heading("ventas", text="# Ventas")
        self.tree_pagos.heading("total", text="Total")
        self.tree_pagos.heading("promedio", text="Promedio")
        self.tree_pagos.heading("porcentaje", text="%")
        
        # Configurar columnas
        self.tree_pagos.column("metodo", width=200, anchor="w")
        self.tree_pagos.column("ventas", width=100, anchor="center")
        self.tree_pagos.column("total", width=120, anchor="e")
        self.tree_pagos.column("promedio", width=120, anchor="e")
        self.tree_pagos.column("porcentaje", width=80, anchor="center")
        
        # Scrollbar
        scrollbar_pagos = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_pagos.yview)
        self.tree_pagos.configure(yscrollcommand=scrollbar_pagos.set)
        
        # Pack
        self.tree_pagos.pack(side="left", fill="both", expand=True)
        scrollbar_pagos.pack(side="right", fill="y")
    
    def create_productos_section(self):
        """Crea la sección de productos más vendidos"""
        frame = ctk.CTkFrame(self.scroll_frame)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            frame, 
            text="🏆 PRODUCTOS MÁS VENDIDOS", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#E67E22"
        ).pack(pady=15)
        
        # Frame para la tabla
        table_frame = tk.Frame(frame, bg='white')
        table_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Crear treeview para productos
        self.tree_productos = ttk.Treeview(
            table_frame,
            columns=("posicion", "producto", "cantidad", "precio", "total"),
            show="headings",
            height=8
        )
        
        # Configurar encabezados
        self.tree_productos.heading("posicion", text="#")
        self.tree_productos.heading("producto", text="Producto")
        self.tree_productos.heading("cantidad", text="Cant. Vendida")
        self.tree_productos.heading("precio", text="Precio Unit.")
        self.tree_productos.heading("total", text="Total Vendido")
        
        # Configurar columnas
        self.tree_productos.column("posicion", width=50, anchor="center")
        self.tree_productos.column("producto", width=250, anchor="w")
        self.tree_productos.column("cantidad", width=120, anchor="center")
        self.tree_productos.column("precio", width=100, anchor="e")
        self.tree_productos.column("total", width=120, anchor="e")
        
        # Scrollbar
        scrollbar_productos = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_productos.yview)
        self.tree_productos.configure(yscrollcommand=scrollbar_productos.set)
        
        # Pack
        self.tree_productos.pack(side="left", fill="both", expand=True)
        scrollbar_productos.pack(side="right", fill="y")
    
    def create_actividad_section(self):
        """Crea la sección de actividad por períodos"""
        frame = ctk.CTkFrame(self.scroll_frame)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            frame, 
            text="⏰ ACTIVIDAD POR PERÍODOS", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1ABC9C"
        ).pack(pady=15)
        
        # Frame para las barras de actividad
        self.actividad_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.actividad_frame.pack(fill="x", padx=20, pady=(0, 20))
    
    def create_estadisticas_section(self):
        """Crea la sección de estadísticas adicionales"""
        frame = ctk.CTkFrame(self.scroll_frame)
        frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            frame, 
            text="📈 ESTADÍSTICAS ADICIONALES", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#E74C3C"
        ).pack(pady=15)
        
        # Frame para estadísticas en dos columnas
        stats_container = ctk.CTkFrame(frame, fg_color="transparent")
        stats_container.pack(fill="x", padx=20, pady=(0, 20))
        
        # Columna izquierda
        col_izq = ctk.CTkFrame(stats_container)
        col_izq.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.label_venta_min = ctk.CTkLabel(col_izq, text="🔻 Venta Mínima: $0.00", font=ctk.CTkFont(size=14))
        self.label_venta_min.pack(pady=10)
        
        self.label_venta_max = ctk.CTkLabel(col_izq, text="🔺 Venta Máxima: $0.00", font=ctk.CTkFont(size=14))
        self.label_venta_max.pack(pady=10)
        
        # Columna derecha
        col_der = ctk.CTkFrame(stats_container)
        col_der.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        self.label_hora_pico = ctk.CTkLabel(col_der, text="⏰ Hora Pico: --", font=ctk.CTkFont(size=14))
        self.label_hora_pico.pack(pady=10)
        
        self.label_productos_vendidos = ctk.CTkLabel(col_der, text="📦 Productos Diferentes: 0", font=ctk.CTkFont(size=14))
        self.label_productos_vendidos.pack(pady=10)
    
    def fecha_hoy(self):
        """Establece la fecha de hoy real del sistema"""
        fecha_hoy_real = date.today().strftime('%Y-%m-%d')
        self.entry_fecha.delete(0, 'end')
        self.entry_fecha.insert(0, fecha_hoy_real)
        self.cargar_corte()
    
    def fecha_ayer(self):
        """Establece la fecha de ayer"""
        ayer = date.today() - timedelta(days=1)
        self.fecha_actual = ayer.strftime('%Y-%m-%d')
        self.entry_fecha.delete(0, 'end')
        self.entry_fecha.insert(0, self.fecha_actual)
        self.cargar_corte()
    
    def fecha_con_ventas(self):
        """Establece la fecha con ventas más recientes"""
        fecha_ventas = self.get_fecha_con_ventas()
        self.entry_fecha.delete(0, 'end')
        self.entry_fecha.insert(0, fecha_ventas)
        self.cargar_corte()
    
    def cargar_corte(self):
        """Carga los datos del corte del día"""
        try:
            fecha = self.entry_fecha.get()
            if not fecha:
                fecha = date.today().strftime('%Y-%m-%d')
            
            # Obtener datos del corte
            corte = self.db.get_corte_dia(fecha)
            
            # Actualizar resumen general
            self.actualizar_resumen(corte['totales'])
            
            # Actualizar métodos de pago
            self.actualizar_metodos_pago(corte['resumen_pagos'], corte['totales']['total_ingresos'])
            
            # Actualizar productos más vendidos
            self.actualizar_productos_vendidos(corte['productos_mas_vendidos'])
            
            # Actualizar actividad por períodos
            self.actualizar_actividad_periodos(corte['actividad_por_periodo'])
            
            # Actualizar estadísticas adicionales
            self.actualizar_estadisticas_adicionales(corte['estadisticas_adicionales'], corte)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el corte del día: {str(e)}")
    
    def actualizar_resumen(self, totales):
        """Actualiza las tarjetas de resumen"""
        self.stat_ventas.valor_label.configure(text=str(totales['total_ventas']))
        self.stat_ingresos.valor_label.configure(text=f"${totales['total_ingresos']:.2f}")
        self.stat_promedio.valor_label.configure(text=f"${totales['ticket_promedio']:.2f}")
        self.stat_descuentos.valor_label.configure(text=f"${totales['total_descuento']:.2f}")
        self.stat_impuestos.valor_label.configure(text=f"${totales['total_impuesto']:.2f}")
        self.stat_clientes.valor_label.configure(text="0")  # Se actualiza en estadísticas adicionales
    
    def actualizar_metodos_pago(self, resumen_pagos, total_ingresos):
        """Actualiza la tabla de métodos de pago"""
        # Limpiar tabla
        for item in self.tree_pagos.get_children():
            self.tree_pagos.delete(item)
        
        # Insertar datos
        for pago in resumen_pagos:
            porcentaje = (pago['total_por_metodo'] / total_ingresos * 100) if total_ingresos > 0 else 0
            
            self.tree_pagos.insert('', 'end', values=(
                pago['metodo_pago'].title(),
                pago['ventas_por_metodo'],
                f"${pago['total_por_metodo']:.2f}",
                f"${pago['promedio_por_metodo']:.2f}",
                f"{porcentaje:.1f}%"
            ))
    
    def actualizar_productos_vendidos(self, productos):
        """Actualiza la tabla de productos más vendidos"""
        # Limpiar tabla
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        # Insertar datos
        for i, producto in enumerate(productos, 1):
            self.tree_productos.insert('', 'end', values=(
                f"{i}°",
                producto['nombre'],
                producto['cantidad_vendida'],
                f"${producto['precio_unitario']:.2f}",
                f"${producto['total_vendido']:.2f}"
            ))
    
    def actualizar_actividad_periodos(self, actividad):
        """Actualiza las barras de actividad por períodos"""
        # Limpiar frame anterior
        for widget in self.actividad_frame.winfo_children():
            widget.destroy()
        
        if not actividad:
            ctk.CTkLabel(self.actividad_frame, text="No hay datos de actividad").pack(pady=20)
            return
        
        # Encontrar el máximo para escalar las barras
        max_ventas = max(p['ventas_periodo'] for p in actividad) if actividad else 1
        
        for periodo in actividad:
            # Frame para cada período
            periodo_frame = ctk.CTkFrame(self.actividad_frame)
            periodo_frame.pack(fill="x", pady=5)
            
            # Nombre del período
            ctk.CTkLabel(
                periodo_frame, 
                text=periodo['periodo'], 
                width=150,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(side="left", padx=10, pady=10)
            
            # Barra de progreso visual
            barra_frame = ctk.CTkFrame(periodo_frame, height=30)
            barra_frame.pack(side="left", fill="x", expand=True, padx=10, pady=5)
            
            # Porcentaje de la barra
            porcentaje = (periodo['ventas_periodo'] / max_ventas) if max_ventas > 0 else 0
            barra_width = int(400 * porcentaje)
            
            # Crear barra visual
            if barra_width > 0:
                barra = ctk.CTkFrame(barra_frame, width=barra_width, height=20, fg_color="#3498DB")
                barra.pack(side="left", pady=5)
            
            # Estadísticas del período
            stats_text = f"{periodo['ventas_periodo']} ventas - ${periodo['total_periodo']:.2f}"
            ctk.CTkLabel(
                periodo_frame, 
                text=stats_text, 
                width=150,
                font=ctk.CTkFont(size=11)
            ).pack(side="right", padx=10, pady=10)
    
    def actualizar_estadisticas_adicionales(self, stats, corte):
        """Actualiza las estadísticas adicionales"""
        self.label_venta_min.configure(text=f"🔻 Venta Mínima: ${stats['venta_minima']:.2f}")
        self.label_venta_max.configure(text=f"🔺 Venta Máxima: ${stats['venta_maxima']:.2f}")
        
        # Actualizar clientes únicos en el resumen
        self.stat_clientes.valor_label.configure(text=str(stats['clientes_unicos']))
        
        # Hora pico (período con más ventas)
        if corte['actividad_por_periodo']:
            periodo_pico = max(corte['actividad_por_periodo'], key=lambda x: x['ventas_periodo'])
            self.label_hora_pico.configure(text=f"⏰ Hora Pico: {periodo_pico['periodo']}")
        
        # Productos diferentes vendidos
        productos_diferentes = len(corte['productos_mas_vendidos'])
        self.label_productos_vendidos.configure(text=f"📦 Productos Diferentes: {productos_diferentes}")
    
    def exportar_pdf(self):
        """Exporta el corte del día a PDF"""
        messagebox.showinfo("Próximamente", "Función de exportar PDF estará disponible pronto")
    
    def imprimir_corte(self):
        """Imprime el corte del día"""
        try:
            fecha = self.entry_fecha.get()
            corte = self.db.get_corte_dia(fecha)
            
            # Crear ventana de vista previa para imprimir
            preview = ctk.CTkToplevel(self.window)
            preview.title("Vista Previa - Corte del Día")
            preview.geometry("600x700")
            preview.transient(self.window)
            
            # Generar contenido para imprimir
            contenido = self.generar_contenido_impresion(corte)
            
            textbox = ctk.CTkTextbox(preview, width=580, height=650, font=ctk.CTkFont(family="Courier", size=10))
            textbox.pack(padx=10, pady=10)
            textbox.insert("1.0", contenido)
            textbox.configure(state="disabled")
            
            btn_cerrar = ctk.CTkButton(preview, text="Cerrar", command=preview.destroy)
            btn_cerrar.pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar vista previa: {str(e)}")
    
    def generar_contenido_impresion(self, corte):
        """Genera el contenido formateado para impresión"""
        linea = "=" * 50
        fecha_formato = datetime.strptime(corte['fecha'], '%Y-%m-%d').strftime('%d/%m/%Y')
        
        contenido = f"""
{linea}
         CORTE DEL DÍA
{linea}
Fecha: {fecha_formato}
Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

{linea}
RESUMEN GENERAL
{linea}
Total de Ventas: {corte['totales']['total_ventas']}
Ingresos Totales: ${corte['totales']['total_ingresos']:.2f}
Ticket Promedio: ${corte['totales']['ticket_promedio']:.2f}
Descuentos: ${corte['totales']['total_descuento']:.2f}
Impuestos: ${corte['totales']['total_impuesto']:.2f}
Clientes Únicos: {corte['estadisticas_adicionales']['clientes_unicos']}

{linea}
MÉTODOS DE PAGO
{linea}
"""
        
        for pago in corte['resumen_pagos']:
            porcentaje = (pago['total_por_metodo'] / corte['totales']['total_ingresos'] * 100) if corte['totales']['total_ingresos'] > 0 else 0
            contenido += f"{pago['metodo_pago'].title():<20} {pago['ventas_por_metodo']:>3} ventas ${pago['total_por_metodo']:>8.2f} ({porcentaje:>5.1f}%)\n"
        
        contenido += f"""
{linea}
PRODUCTOS MÁS VENDIDOS
{linea}
"""
        
        for i, producto in enumerate(corte['productos_mas_vendidos'][:10], 1):
            contenido += f"{i:>2}. {producto['nombre']:<30} {producto['cantidad_vendida']:>3} unids ${producto['total_vendido']:>8.2f}\n"
        
        contenido += f"""
{linea}
ACTIVIDAD POR PERÍODOS
{linea}
"""
        
        for periodo in corte['actividad_por_periodo']:
            contenido += f"{periodo['periodo']:<20} {periodo['ventas_periodo']:>3} ventas ${periodo['total_periodo']:>8.2f}\n"
        
        contenido += f"""
{linea}
ESTADÍSTICAS ADICIONALES
{linea}
Venta Mínima: ${corte['estadisticas_adicionales']['venta_minima']:.2f}
Venta Máxima: ${corte['estadisticas_adicionales']['venta_maxima']:.2f}
Productos Diferentes: {len(corte['productos_mas_vendidos'])}

{linea}
        FIN DEL CORTE
{linea}
"""
        
        return contenido
