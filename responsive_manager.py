"""
ResponsiveManager - Maneja todas las configuraciones responsive de la aplicación
Autor: AI Assistant
Versión: 1.0
"""

import customtkinter as ctk
import tkinter as tk
import math

class ResponsiveManager:
    """Clase para manejar configuraciones responsive de la aplicación"""
    
    # Breakpoints para diferentes tamaños de pantalla
    BREAKPOINTS = {
        'xs': 1024,    # Pantallas muy pequeñas
        'sm': 1366,    # Pantallas pequeñas (laptops básicos)
        'md': 1600,    # Pantallas medianas (desktop estándar)
        'lg': 1920,    # Pantallas grandes (Full HD)
        'xl': 2560,    # Pantallas extra grandes (2K/4K)
        'xxl': 3840    # Pantallas ultra grandes (4K+)
    }
    
    def __init__(self, root_window):
        """
        Inicializa el ResponsiveManager
        
        Args:
            root_window: Ventana principal de la aplicación
        """
        self.root = root_window
        self.update_screen_info()
        self.device_type = self.get_device_type()
        self.scale_factor = self.calculate_scale_factor()
        
    def update_screen_info(self):
        """Actualiza la información de la pantalla"""
        try:
            self.screen_width = self.root.winfo_screenwidth()
            self.screen_height = self.root.winfo_screenheight()
            self.dpi = self.root.winfo_fpixels('1i')  # DPI de la pantalla
        except:
            # Valores por defecto si hay error
            self.screen_width = 1920
            self.screen_height = 1080
            self.dpi = 96
            
    def get_device_type(self):
        """Determina el tipo de dispositivo basado en la resolución"""
        width = self.screen_width
        
        if width <= self.BREAKPOINTS['xs']:
            return 'xs'
        elif width <= self.BREAKPOINTS['sm']:
            return 'sm'
        elif width <= self.BREAKPOINTS['md']:
            return 'md'
        elif width <= self.BREAKPOINTS['lg']:
            return 'lg'
        elif width <= self.BREAKPOINTS['xl']:
            return 'xl'
        else:
            return 'xxl'
    
    def calculate_scale_factor(self):
        """Calcula el factor de escala basado en la resolución y DPI"""
        # Factor base usando resolución Full HD como referencia
        base_width = 1920
        base_height = 1080
        base_dpi = 96
        
        # Factor de escala por resolución
        width_scale = self.screen_width / base_width
        height_scale = self.screen_height / base_height
        resolution_scale = (width_scale + height_scale) / 2
        
        # Factor de escala por DPI
        dpi_scale = self.dpi / base_dpi
        
        # Combinar factores con peso hacia la resolución
        scale = (resolution_scale * 0.7) + (dpi_scale * 0.3)
        
        # Limitar el factor de escala entre 0.5 y 3.0
        return max(0.5, min(3.0, scale))
    
    def get_layout_config(self):
        """Retorna la configuración de layout según el tipo de dispositivo"""
        configs = {
            'xs': {  # Pantallas muy pequeñas
                'productos_width_ratio': 0.68,
                'productos_height_ratio': 0.72,
                'carrito_width_ratio': 0.30,
                'carrito_height_ratio': 0.92,
                'funciones_height_ratio': 0.22,
                'padding': 3,
                'margin': 8,
                'min_button_size': 25,
                'font_scale': 0.8
            },
            'sm': {  # Pantallas pequeñas
                'productos_width_ratio': 0.66,
                'productos_height_ratio': 0.73,
                'carrito_width_ratio': 0.32,
                'carrito_height_ratio': 0.93,
                'funciones_height_ratio': 0.20,
                'padding': 4,
                'margin': 10,
                'min_button_size': 30,
                'font_scale': 0.9
            },
            'md': {  # Pantallas medianas
                'productos_width_ratio': 0.65,
                'productos_height_ratio': 0.75,
                'carrito_width_ratio': 0.32,
                'carrito_height_ratio': 0.94,
                'funciones_height_ratio': 0.18,
                'padding': 5,
                'margin': 10,
                'min_button_size': 35,
                'font_scale': 1.0
            },
            'lg': {  # Pantallas grandes
                'productos_width_ratio': 0.64,
                'productos_height_ratio': 0.76,
                'carrito_width_ratio': 0.33,
                'carrito_height_ratio': 0.95,
                'funciones_height_ratio': 0.17,
                'padding': 6,
                'margin': 12,
                'min_button_size': 40,
                'font_scale': 1.1
            },
            'xl': {  # Pantallas extra grandes
                'productos_width_ratio': 0.63,
                'productos_height_ratio': 0.77,
                'carrito_width_ratio': 0.34,
                'carrito_height_ratio': 0.96,
                'funciones_height_ratio': 0.16,
                'padding': 8,
                'margin': 15,
                'min_button_size': 45,
                'font_scale': 1.2
            },
            'xxl': {  # Pantallas ultra grandes
                'productos_width_ratio': 0.62,
                'productos_height_ratio': 0.78,
                'carrito_width_ratio': 0.35,
                'carrito_height_ratio': 0.97,
                'funciones_height_ratio': 0.15,
                'padding': 10,
                'margin': 18,
                'min_button_size': 50,
                'font_scale': 1.4
            }
        }
        
        return configs.get(self.device_type, configs['md'])
    
    def get_dimensions(self):
        """Retorna las dimensiones calculadas para todos los elementos"""
        config = self.get_layout_config()
        
        # Dimensiones principales
        productos_width = int(self.screen_width * config['productos_width_ratio'])
        productos_height = int(self.screen_height * config['productos_height_ratio'])
        carrito_width = int(self.screen_width * config['carrito_width_ratio'])
        carrito_height = int(self.screen_height * config['carrito_height_ratio'])
        funciones_width = productos_width
        funciones_height = int(self.screen_height * config['funciones_height_ratio'])
        
        # Dimensiones para sección de productos
        entry_width = int(productos_width * 0.82)
        entry_height = max(30, int(productos_height * 0.05))
        btn_buscar_width = int(productos_width * 0.08)
        categorias_width = int(productos_width * 0.96)
        categorias_height = max(45, int(productos_height * 0.07))
        scroll_width = categorias_width
        scroll_height = int(productos_height * 0.80)
        
        # Dimensiones para botones de productos
        productos_btn_width = int(scroll_width / 4) - config['margin']
        productos_btn_height = max(config['min_button_size'], int(scroll_height / 6))
        categorias_btn_width = max(80, int(categorias_width / 10))
        categorias_btn_height = max(35, int(categorias_height * 0.8))
        
        # Dimensiones para sección de carrito
        cliente_entry_width = int(carrito_width * 0.55)
        cliente_entry_height = max(25, int(carrito_height * 0.035))
        btn_cliente_width = max(30, int(carrito_width * 0.08))
        
        # Dimensiones para Treeview del carrito
        tree_width = int(carrito_width * 0.98)
        tree_height = int(carrito_height * 0.60)
        
        # Dimensiones para frames de carrito
        totales_width = int(carrito_width * 0.96)
        totales_height = max(90, int(carrito_height * 0.12))  # Aumentado para acomodar selector de moneda
        acciones_width = totales_width
        acciones_height = max(80, int(carrito_height * 0.12))
        
        # Dimensiones para botones de acción
        accion_btn_width = max(60, int(acciones_width * 0.22))
        accion_btn_height = max(30, int(acciones_height * 0.4))
        
        # Dimensiones para funciones
        funciones_btn_width = max(100, int(funciones_width / 5) - config['margin'])
        funciones_btn_height = max(35, int(funciones_height * 0.35))
        
        return {
            # Principales
            'productos_width': productos_width,
            'productos_height': productos_height,
            'carrito_width': carrito_width,
            'carrito_height': carrito_height,
            'funciones_width': funciones_width,
            'funciones_height': funciones_height,
            
            # Productos
            'entry_width': entry_width,
            'entry_height': entry_height,
            'btn_buscar_width': btn_buscar_width,
            'btn_buscar_height': entry_height,
            'categorias_width': categorias_width,
            'categorias_height': categorias_height,
            'scroll_width': scroll_width,
            'scroll_height': scroll_height,
            'productos_btn_width': productos_btn_width,
            'productos_btn_height': productos_btn_height,
            'categorias_btn_width': categorias_btn_width,
            'categorias_btn_height': categorias_btn_height,
            
            # Carrito
            'cliente_entry_width': cliente_entry_width,
            'cliente_entry_height': cliente_entry_height,
            'btn_cliente_width': btn_cliente_width,
            'btn_cliente_height': cliente_entry_height,
            'tree_width': tree_width,
            'tree_height': tree_height,
            'totales_width': totales_width,
            'totales_height': totales_height,
            'acciones_width': acciones_width,
            'acciones_height': acciones_height,
            'accion_btn_width': accion_btn_width,
            'accion_btn_height': accion_btn_height,
            
            # Funciones
            'funciones_btn_width': funciones_btn_width,
            'funciones_btn_height': funciones_btn_height,
            
            # Configuración
            'padding': config['padding'],
            'margin': config['margin'],
            'font_scale': config['font_scale']
        }
    
    def get_font_size(self, base_size=12, category='normal'):
        """
        Calcula el tamaño de fuente escalado
        
        Args:
            base_size: Tamaño base de la fuente
            category: Categoría de texto ('small', 'normal', 'large', 'title')
        """
        config = self.get_layout_config()
        
        # Modificadores por categoría
        category_multipliers = {
            'small': 0.8,
            'normal': 1.0,
            'large': 1.2,
            'title': 1.5,
            'button': 1.0
        }
        
        multiplier = category_multipliers.get(category, 1.0)
        scaled_size = int(base_size * config['font_scale'] * multiplier * self.scale_factor)
        
        # Limitar tamaños mínimos y máximos
        return max(8, min(32, scaled_size))
    
    def get_positions(self):
        """Retorna las posiciones calculadas para todos los elementos"""
        dims = self.get_dimensions()
        config = self.get_layout_config()
        
        margin = config['margin']
        padding = config['padding']
        
        # Posiciones principales
        main_x = padding
        main_y = padding
        carrito_x = dims['productos_width'] + margin * 2
        funciones_y = dims['productos_height'] + margin * 2
        
        # Logo
        logo_x = margin
        logo_y = margin
        
        # Posiciones en sección de productos
        search_x = margin
        search_y = margin
        search_btn_x = dims['entry_width'] + margin * 2
        categorias_x = margin
        categorias_y = dims['entry_height'] + margin * 2
        productos_scroll_x = margin
        productos_scroll_y = dims['entry_height'] + dims['categorias_height'] + margin * 3
        
        # Posiciones en carrito
        cliente_label_x = margin
        cliente_label_y = margin
        cliente_entry_x = 70
        cliente_entry_y = margin
        cliente_btn_x = cliente_entry_x + dims['cliente_entry_width'] + margin
        cliente_btn2_x = cliente_btn_x + dims['btn_cliente_width'] + margin
        
        carrito_label_x = margin
        carrito_label_y = dims['cliente_entry_height'] + margin * 2
        tree_x = margin
        tree_y = dims['cliente_entry_height'] + margin * 4
        
        moneda_label_x = margin
        moneda_label_y = int(dims['carrito_height'] * 0.64)
        moneda_combo_x = int(dims['carrito_width'] * 0.25)
        moneda_combo_y = moneda_label_y
        
        totales_x = margin
        totales_y = int(dims['carrito_height'] * 0.68)
        
        user_info_x = margin
        user_info_y = int(dims['carrito_height'] * 0.80)
        
        acciones_x = margin
        acciones_y = int(dims['carrito_height'] * 0.85)
        
        return {
            # Principales
            'main_x': main_x,
            'main_y': main_y,
            'carrito_x': carrito_x,
            'carrito_y': main_y,
            'funciones_x': main_x,
            'funciones_y': funciones_y,
            
            # Logo
            'logo_x': logo_x,
            'logo_y': logo_y,
            
            # Productos
            'search_x': search_x,
            'search_y': search_y,
            'search_btn_x': search_btn_x,
            'search_btn_y': search_y,
            'categorias_x': categorias_x,
            'categorias_y': categorias_y,
            'productos_scroll_x': productos_scroll_x,
            'productos_scroll_y': productos_scroll_y,
            
            # Carrito
            'cliente_label_x': cliente_label_x,
            'cliente_label_y': cliente_label_y,
            'cliente_entry_x': cliente_entry_x,
            'cliente_entry_y': cliente_entry_y,
            'cliente_btn_x': cliente_btn_x,
            'cliente_btn_y': cliente_entry_y,
            'cliente_btn2_x': cliente_btn2_x,
            'cliente_btn2_y': cliente_entry_y,
            'carrito_label_x': carrito_label_x,
            'carrito_label_y': carrito_label_y,
            'tree_x': tree_x,
            'tree_y': tree_y,
            'moneda_label_x': moneda_label_x,
            'moneda_label_y': moneda_label_y,
            'moneda_combo_x': moneda_combo_x,
            'moneda_combo_y': moneda_combo_y,
            'totales_x': totales_x,
            'totales_y': totales_y,
            'user_info_x': user_info_x,
            'user_info_y': user_info_y,
            'acciones_x': acciones_x,
            'acciones_y': acciones_y
        }
    
    def create_responsive_font(self, size=12, weight="normal", category='normal'):
        """Crea una fuente responsive"""
        scaled_size = self.get_font_size(size, category)
        return ctk.CTkFont(size=scaled_size, weight=weight)
    
    def optimize_for_performance(self):
        """Optimizaciones específicas según el tipo de dispositivo"""
        config = self.get_layout_config()
        
        optimizations = {
            'reduce_animations': self.device_type in ['xs', 'sm'],
            'simplify_gradients': self.device_type in ['xs'],
            'reduce_corner_radius': self.device_type in ['xs'],
            'optimize_scrolling': True
        }
        
        return optimizations
    
    def get_window_geometry(self):
        """Retorna la geometría óptima de la ventana"""
        if self.device_type in ['xs', 'sm']:
            # Para pantallas pequeñas, usar casi toda la pantalla
            width = int(self.screen_width * 0.98)
            height = int(self.screen_height * 0.95)
        else:
            # Para pantallas grandes, usar toda la pantalla
            width = self.screen_width
            height = self.screen_height
            
        return f"{width}x{height}"
    
    def should_use_compact_mode(self):
        """Determina si se debe usar modo compacto"""
        return self.device_type in ['xs', 'sm'] or self.screen_height < 800
    
    def get_logo_size(self):
        """Retorna el tamaño óptimo para el logo"""
        base_size = 64
        
        if self.device_type == 'xs':
            return int(base_size * 0.6)
        elif self.device_type == 'sm':
            return int(base_size * 0.8)
        elif self.device_type in ['xl', 'xxl']:
            return int(base_size * 1.2)
        else:
            return base_size
    
    def refresh_layout(self):
        """Refresca el layout cuando cambia la resolución"""
        self.update_screen_info()
        self.device_type = self.get_device_type()
        self.scale_factor = self.calculate_scale_factor()