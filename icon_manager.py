"""
Icon Manager - Maneja todos los iconos del sistema de manera centralizada
Autor: AI Assistant
Versión: 1.0
"""

import customtkinter as ctk
import os
import tkinter as tk

class IconManager:
    """Clase para manejar iconos del sistema"""
    
    def __init__(self):
        """Inicializa el manejador de iconos"""
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.imagen_path = os.path.join(self.base_path, "imagen")
        
        # Paths de iconos disponibles
        self.icons = {
            'main_ico': os.path.join(self.imagen_path, "puntero-del-mapa.ico"),
            'main_png': os.path.join(self.imagen_path, "puntero-del-mapa.png"),
        }
        
        # Cache de imágenes CTk
        self._ctk_images = {}
    
    def get_icon_path(self, icon_name):
        """Retorna la ruta de un icono"""
        return self.icons.get(icon_name, None)
    
    def set_window_icon(self, window, icon_name='main_ico'):
        """Establece el icono de una ventana"""
        try:
            icon_path = self.get_icon_path(icon_name)
            if icon_path and os.path.exists(icon_path):
                window.iconbitmap(icon_path)
                return True
        except Exception as e:
            print(f"Error al establecer icono de ventana: {e}")
        return False
    
    def get_ctk_image(self, icon_name, size=(24, 24), cache_key=None):
        """Retorna una imagen CTk para un icono dado"""
        try:
            from PIL import Image
            # Generar clave de cache
            if not cache_key:
                cache_key = f"{icon_name}_{size[0]}x{size[1]}"
            # Verificar cache
            if cache_key in self._ctk_images:
                return self._ctk_images[cache_key]
            # Obtener ruta del icono
            icon_path = self.get_icon_path(icon_name)
            if not icon_path or not os.path.exists(icon_path):
                return None
            # Crear imagen CTk
            if icon_name.endswith('_png'):
                pil_img = Image.open(icon_path).convert("RGBA")
                ctk_image = ctk.CTkImage(
                    light_image=pil_img,
                    size=size
                )
            else:
                # Para archivos .ico, intentar convertir a CTkImage
                # CustomTkinter funciona mejor con PNG
                ctk_image = None
            # Guardar en cache
            if ctk_image:
                self._ctk_images[cache_key] = ctk_image
            return ctk_image
        except Exception as e:
            print(f"Error al cargar imagen CTk: {e}")
            return None
    
    def create_icon_label(self, parent, icon_name, size=(64, 64), **kwargs):
        """
        Crea un label con icono
        
        Args:
            parent: Widget padre
            icon_name: Nombre del icono
            size: Tamaño del icono
            **kwargs: Argumentos adicionales para CTkLabel
        """
        try:
            ctk_image = self.get_ctk_image(icon_name, size)
            if ctk_image:
                return ctk.CTkLabel(
                    parent,
                    image=ctk_image,
                    text="",
                    **kwargs
                )
            else:
                # Fallback: label sin imagen
                return ctk.CTkLabel(
                    parent,
                    text="📋",  # Emoji como fallback
                    font=ctk.CTkFont(size=size[0]//2),
                    **kwargs
                )
        except Exception as e:
            print(f"Error al crear label con icono: {e}")
            return None
    
    def apply_to_window(self, window, icon_name='main_ico'):
        """
        Aplica iconos a una ventana de manera completa
        
        Args:
            window: Ventana CTk
            icon_name: Nombre del icono a usar
        """
        try:
            # Establecer icono de ventana
            self.set_window_icon(window, icon_name)
            
            # Configurar título con icono (emoji como fallback)
            current_title = window.title()
            if not current_title.startswith("📋"):
                window.title(f"📋 {current_title}")
            
            return True
        except Exception as e:
            print(f"Error al aplicar iconos a ventana: {e}")
            return False
    
    def get_emoji_fallback(self, icon_type):
        """
        Retorna emoji como fallback para diferentes tipos de iconos
        
        Args:
            icon_type: Tipo de icono ('main', 'search', 'add', 'edit', etc.)
        """
        fallbacks = {
            'main': '📋',
            'search': '🔍',
            'add': '➕',
            'edit': '✏️',
            'delete': '🗑️',
            'save': '💾',
            'cancel': '❌',
            'ok': '✅',
            'warning': '⚠️',
            'error': '❌',
            'info': 'ℹ️',
            'money': '💰',
            'cart': '🛒',
            'user': '👤',
            'settings': '⚙️',
            'category': '🏷️',
            'product': '📦',
            'company': '🏢',
            'report': '📊',
            'print': '🖨️',
            'export': '📤',
            'import': '📥',
            'home': '🏠',
            'exit': '🚪',
            'help': '❓'
        }
        
        return fallbacks.get(icon_type, '📋')
    
    def create_button_with_icon(self, parent, text, icon_type=None, size=(24, 24), **kwargs):
        """
        Crea un botón con icono usando emoji como fallback
        
        Args:
            parent: Widget padre
            text: Texto del botón
            icon_type: Tipo de icono
            size: Tamaño del icono
            **kwargs: Argumentos para CTkButton
        """
        try:
            # Intentar usar icono CTk primero
            if icon_type and icon_type in self.icons:
                ctk_image = self.get_ctk_image(icon_type, size)
                if ctk_image:
                    return ctk.CTkButton(
                        parent,
                        text=text,
                        image=ctk_image,
                        compound="left",
                        **kwargs
                    )
            
            # Fallback: usar emoji
            if icon_type:
                emoji = self.get_emoji_fallback(icon_type)
                button_text = f"{emoji} {text}"
            else:
                button_text = text
            
            return ctk.CTkButton(
                parent,
                text=button_text,
                **kwargs
            )
            
        except Exception as e:
            print(f"Error al crear botón con icono: {e}")
            return ctk.CTkButton(parent, text=text, **kwargs)
    
    def validate_icons(self):
        """Valida que todos los iconos existan"""
        missing_icons = []
        
        for icon_name, icon_path in self.icons.items():
            if not os.path.exists(icon_path):
                missing_icons.append(icon_name)
        
        if missing_icons:
            print(f"Iconos faltantes: {missing_icons}")
            print(f"Ruta de imágenes: {self.imagen_path}")
        
        return len(missing_icons) == 0
    
    def clear_cache(self):
        """Limpia el cache de imágenes"""
        self._ctk_images.clear()

# Instancia global del manejador de iconos
icon_manager = IconManager()