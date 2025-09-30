import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
from datetime import datetime
import json

class PagosWindow:
    def __init__(self, parent, database_manager, carrito_items, cliente_info=None):
        self.parent = parent
        self.db = database_manager
        self.carrito_items = carrito_items
        self.cliente_info = cliente_info
        
        self.subtotal = sum(item['cantidad'] * item['precio_unitario'] for item in carrito_items)
        self.descuento = 0.0
        self.impuesto = 0.0
        self.total = self.subtotal
        
        self.metodo_pago = "efectivo"
        self.pagado = False
        
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Procesar Pago")
        self.window.geometry("1000x800")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.actualizar_totales()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        
        self.frame_resumen = ctk.CTkFrame(self.window, width=350, height=780)
        self.frame_resumen.place(x=10, y=10)
        
        self.frame_pago = ctk.CTkFrame(self.window, width=320, height=780)
        self.frame_pago.place(x=370, y=10)
        
        self.frame_totales = ctk.CTkFrame(self.window, width=300, height=780)
        self.frame_totales.place(x=700, y=10)
        
        self.setup_resumen_compra()
        self.setup_metodos_pago()
        self.setup_totales_acciones()
    
    def setup_resumen_compra(self):
        """Configura la sección de resumen de compra"""
        ctk.CTkLabel(
            self.frame_resumen, 
            text="Resumen de Compra", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).place(x=10, y=10)
        
        # Información del cliente
        cliente_text = "Cliente: Público General"
        if self.cliente_info:
            cliente_text = f"Cliente: {self.cliente_info.get('nombre', 'Sin nombre')}"
        
        ctk.CTkLabel(
            self.frame_resumen, 
            text=cliente_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="blue"
        ).place(x=10, y=40)
        
        # Lista de productos
        ctk.CTkLabel(
            self.frame_resumen, 
            text="Productos:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).place(x=10, y=70)
        
        # Frame scrollable para productos
        self.productos_frame = ctk.CTkScrollableFrame(
            self.frame_resumen, width=320, height=400
        )
        self.productos_frame.place(x=10, y=100)
        
        # Mostrar productos
        for i, item in enumerate(self.carrito_items):
            producto_frame = ctk.CTkFrame(self.productos_frame, width=300, height=60)
            producto_frame.grid(row=i, column=0, padx=5, pady=5, sticky="ew")
            
            # Nombre del producto
            ctk.CTkLabel(
                producto_frame, 
                text=item['nombre'][:25] + ("..." if len(item['nombre']) > 25 else ""),
                font=ctk.CTkFont(size=12, weight="bold")
            ).place(x=10, y=5)
            
            # Cantidad y precio
            cantidad_precio = f"{item['cantidad']} x ${item['precio_unitario']:.2f}"
            ctk.CTkLabel(
                producto_frame,
                text=cantidad_precio,
                font=ctk.CTkFont(size=11)
            ).place(x=10, y=25)
            
            # Subtotal
            subtotal_item = item['cantidad'] * item['precio_unitario']
            ctk.CTkLabel(
                producto_frame,
                text=f"${subtotal_item:.2f}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="green"
            ).place(x=230, y=15)
        
        # Fecha y hora
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
        ctk.CTkLabel(
            self.frame_resumen, 
            text=f"Fecha: {fecha_actual}",
            font=ctk.CTkFont(size=10)
        ).place(x=10, y=520)
    
    def setup_metodos_pago(self):
        """Configura la sección de métodos de pago"""
        ctk.CTkLabel(
            self.frame_pago, 
            text="Método de Pago", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).place(x=10, y=10)
        
        # Variable para método de pago
        self.var_metodo = tk.StringVar(value="efectivo")
        
        # Efectivo
        frame_efectivo = ctk.CTkFrame(self.frame_pago, width=290, height=120)
        frame_efectivo.place(x=10, y=50)
        
        self.radio_efectivo = ctk.CTkRadioButton(
            frame_efectivo, text="💵 Efectivo", 
            variable=self.var_metodo, value="efectivo",
            command=self.cambiar_metodo_pago,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.radio_efectivo.place(x=10, y=10)
        
        ctk.CTkLabel(frame_efectivo, text="Monto recibido:").place(x=10, y=40)
        self.entry_efectivo = ctk.CTkEntry(
            frame_efectivo, width=150, height=35,
            placeholder_text="0.00"
        )
        self.entry_efectivo.place(x=130, y=40)
        self.entry_efectivo.bind('<KeyRelease>', self.calcular_cambio)
        
        self.label_cambio = ctk.CTkLabel(
            frame_efectivo, text="Cambio: $0.00",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="red"
        )
        self.label_cambio.place(x=10, y=85)
        
        # Tarjeta
        frame_tarjeta = ctk.CTkFrame(self.frame_pago, width=290, height=100)
        frame_tarjeta.place(x=10, y=180)
        
        self.radio_tarjeta = ctk.CTkRadioButton(
            frame_tarjeta, text="💳 Tarjeta", 
            variable=self.var_metodo, value="tarjeta",
            command=self.cambiar_metodo_pago,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.radio_tarjeta.place(x=10, y=10)
        
        self.combo_tarjeta = ctk.CTkComboBox(
            frame_tarjeta, 
            values=["Débito", "Crédito", "American Express", "Otro"],
            width=200
        )
        self.combo_tarjeta.place(x=10, y=40)
        self.combo_tarjeta.set("Débito")
        
        # Transferencia
        frame_transferencia = ctk.CTkFrame(self.frame_pago, width=290, height=80)
        frame_transferencia.place(x=10, y=290)
        
        self.radio_transferencia = ctk.CTkRadioButton(
            frame_transferencia, text="🏦 Transferencia", 
            variable=self.var_metodo, value="transferencia",
            command=self.cambiar_metodo_pago,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.radio_transferencia.place(x=10, y=10)
        
        ctk.CTkLabel(frame_transferencia, text="Banco destino:").place(x=10, y=40)
        self.combo_banco_transferencia = ctk.CTkComboBox(
            frame_transferencia,
            values=["Banco de Venezuela", "Bancaribe", "Banco Mercantil", "Banco Provincial", "Banesco", "Banco Occidental de Descuento (BOD)", "Banco Fondo Común", "Banco Nacional de Crédito (BNC)", "Banco Exterior", "100% Banco", "Banco Plaza", "Banco Venezolano de Crédito (BVC)", "Banco Caroní", "Bangente", "Banco Activo", "Banco Bicentenario", "Banco del Tesoro", "Banfoandes", "Banco Internacional de Desarrollo", "Mi Banco"],
            width=150
        )
        self.combo_banco_transferencia.place(x=120, y=40)
        
        # Pago móvil
        frame_pago_movil = ctk.CTkFrame(self.frame_pago, width=290, height=140)
        frame_pago_movil.place(x=10, y=380)
        
        self.radio_pago_movil = ctk.CTkRadioButton(
            frame_pago_movil, text="📱 Pago Móvil", 
            variable=self.var_metodo, value="pago_movil",
            command=self.cambiar_metodo_pago,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.radio_pago_movil.place(x=10, y=10)
        
        # Campos para pago móvil
        ctk.CTkLabel(frame_pago_movil, text="Teléfono:").place(x=10, y=40)
        self.entry_telefono_pm = ctk.CTkEntry(frame_pago_movil, width=80, height=25)
        self.entry_telefono_pm.place(x=70, y=40)
        
        ctk.CTkLabel(frame_pago_movil, text="Cédula:").place(x=160, y=40)
        self.entry_cedula_pm = ctk.CTkEntry(frame_pago_movil, width=80, height=25)
        self.entry_cedula_pm.place(x=205, y=40)
        
        ctk.CTkLabel(frame_pago_movil, text="Banco:").place(x=10, y=70)
        self.combo_banco_pm = ctk.CTkComboBox(
            frame_pago_movil,
            values=["Banco de Venezuela", "Bancaribe", "Banco Mercantil", "Banco Provincial", "Banesco", "Banco Occidental de Descuento (BOD)", "Banco Fondo Común", "Banco Nacional de Crédito (BNC)", "Banco Exterior", "100% Banco", "Banco Plaza", "Banco Venezolano de Crédito (BVC)", "Banco Caroní", "Bangente", "Banco Activo", "Banco Bicentenario", "Banco del Tesoro", "Banfoandes", "Banco Internacional de Desarrollo", "Mi Banco"],
            width=200
        )
        self.combo_banco_pm.place(x=60, y=70)
        self.combo_banco_pm.set("Seleccionar banco")
        
        # Referencia
        ctk.CTkLabel(frame_pago_movil, text="Referencia:").place(x=10, y=100)
        self.entry_referencia_pm = ctk.CTkEntry(frame_pago_movil, width=200, height=25)
        self.entry_referencia_pm.place(x=80, y=100)
        
        # Pago mixto
        frame_mixto = ctk.CTkFrame(self.frame_pago, width=290, height=100)
        frame_mixto.place(x=10, y=530)
        
        self.radio_mixto = ctk.CTkRadioButton(
            frame_mixto, text="🔄 Pago Mixto", 
            variable=self.var_metodo, value="mixto",
            command=self.cambiar_metodo_pago,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.radio_mixto.place(x=10, y=10)
        
        # Campos para pago mixto
        ctk.CTkLabel(frame_mixto, text="Efectivo:").place(x=10, y=40)
        self.entry_mixto_efectivo = ctk.CTkEntry(frame_mixto, width=80, height=30)
        self.entry_mixto_efectivo.place(x=70, y=40)
        
        ctk.CTkLabel(frame_mixto, text="Tarjeta:").place(x=160, y=40)
        self.entry_mixto_tarjeta = ctk.CTkEntry(frame_mixto, width=80, height=30)
        self.entry_mixto_tarjeta.place(x=210, y=40)
        
        # Notas adicionales
        ctk.CTkLabel(
            self.frame_pago, 
            text="Notas:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).place(x=10, y=650)
        
        self.text_notas = ctk.CTkTextbox(self.frame_pago, width=290, height=60)
        self.text_notas.place(x=10, y=680)
    
    def setup_totales_acciones(self):
        """Configura la sección de totales y acciones"""
        ctk.CTkLabel(
            self.frame_totales, 
            text="Totales", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).place(x=10, y=10)
        
        # Descuentos
        frame_descuentos = ctk.CTkFrame(self.frame_totales, width=280, height=120)
        frame_descuentos.place(x=10, y=50)
        
        ctk.CTkLabel(
            frame_descuentos, 
            text="Descuentos",
            font=ctk.CTkFont(size=14, weight="bold")
        ).place(x=10, y=10)
        
        # Descuento por porcentaje
        ctk.CTkLabel(frame_descuentos, text="% Descuento:").place(x=10, y=40)
        self.entry_desc_porcentaje = ctk.CTkEntry(frame_descuentos, width=80, height=30)
        self.entry_desc_porcentaje.place(x=100, y=40)
        self.entry_desc_porcentaje.bind('<KeyRelease>', self.aplicar_descuento)
        
        # Descuento en pesos
        ctk.CTkLabel(frame_descuentos, text="$ Descuento:").place(x=10, y=75)
        self.entry_desc_pesos = ctk.CTkEntry(frame_descuentos, width=80, height=30)
        self.entry_desc_pesos.place(x=100, y=75)
        self.entry_desc_pesos.bind('<KeyRelease>', self.aplicar_descuento_pesos)
        
        btn_limpiar_desc = ctk.CTkButton(
            frame_descuentos, text="Limpiar", width=70, height=30,
            command=self.limpiar_descuentos
        )
        btn_limpiar_desc.place(x=200, y=55)
        
        # Totales
        frame_totales_info = ctk.CTkFrame(self.frame_totales, width=280, height=150)
        frame_totales_info.place(x=10, y=180)
        
        self.label_subtotal = ctk.CTkLabel(
            frame_totales_info, 
            text="Subtotal: $0.00",
            font=ctk.CTkFont(size=14)
        )
        self.label_subtotal.place(x=10, y=20)
        
        self.label_descuento = ctk.CTkLabel(
            frame_totales_info, 
            text="Descuento: $0.00",
            font=ctk.CTkFont(size=14),
            text_color="orange"
        )
        self.label_descuento.place(x=10, y=50)
        
        self.label_impuesto = ctk.CTkLabel(
            frame_totales_info, 
            text="Impuesto: $0.00",
            font=ctk.CTkFont(size=14)
        )
        self.label_impuesto.place(x=10, y=80)
        
        # Línea separadora
        separator = ctk.CTkFrame(frame_totales_info, width=250, height=2)
        separator.place(x=10, y=105)
        
        self.label_total = ctk.CTkLabel(
            frame_totales_info, 
            text="TOTAL: $0.00",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="red"
        )
        self.label_total.place(x=10, y=115)
        
        # Botones de acción
        frame_acciones = ctk.CTkFrame(self.frame_totales, width=280, height=280)
        frame_acciones.place(x=10, y=350)
        
        # Botón de pago rápido (monto exacto)
        btn_pago_exacto = ctk.CTkButton(
            frame_acciones, text="💰 Pago Exacto", width=250, height=50,
            command=self.pago_exacto,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="green", hover_color="darkgreen"
        )
        btn_pago_exacto.place(x=10, y=20)
        
        # Botón procesar pago
        btn_procesar = ctk.CTkButton(
            frame_acciones, text="✅ PROCESAR PAGO", width=250, height=60,
            command=self.procesar_pago,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="blue", hover_color="darkblue"
        )
        btn_procesar.place(x=10, y=80)
        
        # Botón imprimir ticket (sin pagar)
        btn_ticket = ctk.CTkButton(
            frame_acciones, text="🖨️ Imprimir Ticket", width=120, height=40,
            command=self.imprimir_ticket
        )
        btn_ticket.place(x=10, y=150)
        
        # Botón guardar para después
        btn_guardar = ctk.CTkButton(
            frame_acciones, text="💾 Guardar", width=120, height=40,
            command=self.guardar_para_despues,
            fg_color="orange", hover_color="darkorange"
        )
        btn_guardar.place(x=140, y=150)
        
        # Botón cancelar
        btn_cancelar = ctk.CTkButton(
            frame_acciones, text="❌ Cancelar", width=250, height=40,
            command=self.cancelar_pago,
            fg_color="gray", hover_color="darkgray"
        )
        btn_cancelar.place(x=10, y=200)
    
    def cambiar_metodo_pago(self):
        """Cambia el método de pago seleccionado"""
        self.metodo_pago = self.var_metodo.get()
        
        # Limpiar campos según el método
        if self.metodo_pago == "efectivo":
            self.entry_efectivo.focus()
        elif self.metodo_pago == "mixto":
            self.entry_mixto_efectivo.focus()
        elif self.metodo_pago == "pago_movil":
            self.entry_telefono_pm.focus()
    
    def calcular_cambio(self, event=None):
        """Calcula el cambio para pago en efectivo"""
        try:
            monto_recibido = float(self.entry_efectivo.get() or 0)
            cambio = monto_recibido - self.total
            
            if cambio >= 0:
                self.label_cambio.configure(
                    text=f"Cambio: ${cambio:.2f}",
                    text_color="green"
                )
            else:
                self.label_cambio.configure(
                    text=f"Falta: ${abs(cambio):.2f}",
                    text_color="red"
                )
        except ValueError:
            self.label_cambio.configure(
                text="Cambio: $0.00",
                text_color="red"
            )
    
    def aplicar_descuento(self, event=None):
        """Aplica descuento por porcentaje"""
        try:
            porcentaje = float(self.entry_desc_porcentaje.get() or 0)
            if 0 <= porcentaje <= 100:
                self.descuento = self.subtotal * (porcentaje / 100)
                self.entry_desc_pesos.delete(0, 'end')
                self.actualizar_totales()
        except ValueError:
            pass
    
    def aplicar_descuento_pesos(self, event=None):
        """Aplica descuento en pesos"""
        try:
            descuento_pesos = float(self.entry_desc_pesos.get() or 0)
            if 0 <= descuento_pesos <= self.subtotal:
                self.descuento = descuento_pesos
                self.entry_desc_porcentaje.delete(0, 'end')
                self.actualizar_totales()
        except ValueError:
            pass
    
    def limpiar_descuentos(self):
        """Limpia los descuentos aplicados"""
        self.descuento = 0.0
        self.entry_desc_porcentaje.delete(0, 'end')
        self.entry_desc_pesos.delete(0, 'end')
        self.actualizar_totales()
    
    def actualizar_totales(self):
        """Actualiza los totales en la interfaz"""
        self.total = self.subtotal + self.impuesto - self.descuento
        
        self.label_subtotal.configure(text=f"Subtotal: ${self.subtotal:.2f}")
        self.label_descuento.configure(text=f"Descuento: ${self.descuento:.2f}")
        self.label_impuesto.configure(text=f"Impuesto: ${self.impuesto:.2f}")
        self.label_total.configure(text=f"TOTAL: ${self.total:.2f}")
        
        # Actualizar cálculo de cambio si es efectivo
        if self.metodo_pago == "efectivo":
            self.calcular_cambio()
    
    def pago_exacto(self):
        """Establece el monto exacto para pago en efectivo"""
        if self.metodo_pago == "efectivo":
            self.entry_efectivo.delete(0, 'end')
            self.entry_efectivo.insert(0, f"{self.total:.2f}")
            self.calcular_cambio()
    
    def validar_pago(self):
        """Valida que el pago esté completo"""
        if self.metodo_pago == "efectivo":
            try:
                monto_recibido = float(self.entry_efectivo.get() or 0)
                if monto_recibido < self.total:
                    messagebox.showerror(
                        "Error", 
                        f"El monto recibido (${monto_recibido:.2f}) es menor al total (${self.total:.2f})"
                    )
                    return False
            except ValueError:
                messagebox.showerror("Error", "Ingrese un monto válido")
                return False
        
        elif self.metodo_pago == "pago_movil":
            # Validar campos del pago móvil
            if not self.entry_telefono_pm.get().strip():
                messagebox.showerror("Error", "El número de teléfono es requerido para pago móvil")
                return False
            if not self.entry_cedula_pm.get().strip():
                messagebox.showerror("Error", "La cédula es requerida para pago móvil")
                return False
            if self.combo_banco_pm.get() == "Seleccionar banco":
                messagebox.showerror("Error", "Debe seleccionar un banco para pago móvil")
                return False
            if not self.entry_referencia_pm.get().strip():
                messagebox.showerror("Error", "La referencia es requerida para pago móvil")
                return False
        
        elif self.metodo_pago == "mixto":
            try:
                efectivo = float(self.entry_mixto_efectivo.get() or 0)
                tarjeta = float(self.entry_mixto_tarjeta.get() or 0)
                total_pagado = efectivo + tarjeta
                
                if abs(total_pagado - self.total) > 0.01:  # Tolerancia de 1 centavo
                    messagebox.showerror(
                        "Error", 
                        f"La suma de pagos (${total_pagado:.2f}) no coincide con el total (${self.total:.2f})"
                    )
                    return False
            except ValueError:
                messagebox.showerror("Error", "Ingrese montos válidos para el pago mixto")
                return False
        
        return True
    
    def procesar_pago(self):
        """Procesa el pago y registra la venta"""
        if not self.validar_pago():
            return
        
        try:
            # Preparar información del método de pago
            metodo_detalle = self.metodo_pago
            
            if self.metodo_pago == "tarjeta":
                metodo_detalle += f" ({self.combo_tarjeta.get()})"
            elif self.metodo_pago == "transferencia":
                metodo_detalle += f" ({self.combo_banco_transferencia.get()})"
            elif self.metodo_pago == "pago_movil":
                telefono = self.entry_telefono_pm.get()
                cedula = self.entry_cedula_pm.get()
                banco = self.combo_banco_pm.get()
                referencia = self.entry_referencia_pm.get()
                metodo_detalle += f" (Tel: {telefono}, CI: {cedula}, Banco: {banco}, Ref: {referencia})"
            elif self.metodo_pago == "mixto":
                efectivo = float(self.entry_mixto_efectivo.get() or 0)
                tarjeta = float(self.entry_mixto_tarjeta.get() or 0)
                metodo_detalle = f"mixto (${efectivo:.2f} efectivo + ${tarjeta:.2f} tarjeta)"
            
            # Preparar items para la venta
            items_venta = []
            for item in self.carrito_items:
                items_venta.append({
                    'producto_id': item['producto_id'],
                    'cantidad': item['cantidad'],
                    'precio_unitario': item['precio_unitario']
                })
            
            # Obtener notas
            notas = self.text_notas.get('1.0', 'end').strip()
            
            # Crear venta en la base de datos
            cliente_id = self.cliente_info['id'] if self.cliente_info else None
            
            venta_id = self.db.crear_venta(
                items_venta,
                cliente_id=cliente_id,
                metodo_pago=metodo_detalle,
                descuento=self.descuento,
                impuesto=self.impuesto,
                notas=notas
            )
            
            # Mostrar confirmación
            mensaje_exito = f"¡Pago procesado exitosamente!\\n\\nFolio de venta: {venta_id}\\nTotal: ${self.total:.2f}\\nMétodo: {metodo_detalle}"
            
            if self.metodo_pago == "efectivo":
                monto_recibido = float(self.entry_efectivo.get())
                cambio = monto_recibido - self.total
                if cambio > 0:
                    mensaje_exito += f"\\n\\nCambio a entregar: ${cambio:.2f}"
            
            messagebox.showinfo("Pago Exitoso", mensaje_exito)
            
            # Imprimir ticket automáticamente
            self.imprimir_ticket_venta(venta_id)
            
            self.pagado = True
            # Cerrar ventana automáticamente después de 2 segundos
            self.window.after(2000, self.window.destroy)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar el pago: {str(e)}")
    
    def imprimir_ticket(self):
        """Genera e imprime el ticket de venta (vista previa)"""
        ticket_content = self.generar_ticket_content()
        
        # Crear ventana de vista previa
        ventana_ticket = ctk.CTkToplevel(self.window)
        ventana_ticket.title("Vista Previa - Ticket")
        ventana_ticket.geometry("400x600")
        ventana_ticket.transient(self.window)
        
        # Mostrar contenido del ticket
        textbox_ticket = ctk.CTkTextbox(ventana_ticket, width=380, height=550, font=ctk.CTkFont(family="Courier", size=10))
        textbox_ticket.place(x=10, y=10)
        textbox_ticket.insert("1.0", ticket_content)
        textbox_ticket.configure(state="disabled")
        
        # Botón para cerrar
        btn_cerrar = ctk.CTkButton(ventana_ticket, text="Cerrar", command=ventana_ticket.destroy)
        btn_cerrar.place(x=150, y=570)
    
    def imprimir_ticket_venta(self, venta_id):
        """Imprime el ticket de una venta procesada"""
        # Obtener detalles de la venta
        venta = self.db.get_venta_detalle(venta_id)
        
        if venta:
            ticket_content = self.generar_ticket_venta_content(venta)
            
            # Crear ventana de vista previa
            ventana_ticket = ctk.CTkToplevel(self.window)
            ventana_ticket.title(f"Ticket - Venta #{venta_id}")
            ventana_ticket.geometry("400x600")
            
            # Mostrar contenido del ticket
            textbox_ticket = ctk.CTkTextbox(ventana_ticket, width=380, height=550, font=ctk.CTkFont(family="Courier", size=10))
            textbox_ticket.place(x=10, y=10)
            textbox_ticket.insert("1.0", ticket_content)
            textbox_ticket.configure(state="disabled")
            
            # Botón para cerrar
            btn_cerrar = ctk.CTkButton(ventana_ticket, text="Cerrar", command=ventana_ticket.destroy)
            btn_cerrar.place(x=150, y=570)
    
    def generar_ticket_content(self):
        """Genera el contenido del ticket"""
        linea = "=" * 40
        fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        ticket = f"""
{linea}
        MI PUNTO DE VENTA
{linea}
Fecha: {fecha_actual}
Cliente: {self.cliente_info.get('nombre', 'Público General') if self.cliente_info else 'Público General'}

PRODUCTOS:
{linea}
"""
        
        for item in self.carrito_items:
            nombre = item['nombre'][:25]
            cantidad = item['cantidad']
            precio = item['precio_unitario']
            subtotal = cantidad * precio
            
            ticket += f"{nombre:<25}\n"
            ticket += f"{cantidad:>3} x ${precio:>6.2f} = ${subtotal:>8.2f}\n"
            ticket += "-" * 40 + "\n"
        
        ticket += f"""
{linea}
Subtotal:        ${self.subtotal:>10.2f}
Descuento:       ${self.descuento:>10.2f}
Impuesto:        ${self.impuesto:>10.2f}
{linea}
TOTAL:           ${self.total:>10.2f}
{linea}

Método de pago: {self.metodo_pago.upper()}
"""
        
        if self.metodo_pago == "efectivo":
            try:
                recibido = float(self.entry_efectivo.get() or 0)
                cambio = recibido - self.total
                ticket += f"Recibido:        ${recibido:>10.2f}\n"
                ticket += f"Cambio:          ${cambio:>10.2f}\n"
            except ValueError:
                pass
        
        ticket += f"""
{linea}
    ¡GRACIAS POR SU COMPRA!
{linea}
"""
        
        return ticket
    
    def generar_ticket_venta_content(self, venta):
        """Genera el contenido del ticket para una venta procesada"""
        linea = "=" * 40
        fecha_venta = venta['fecha_venta'][:19]  # Sin microsegundos
        
        cliente_nombre = "Público General"
        if venta.get('cliente_nombre'):
            cliente_nombre = f"{venta['cliente_nombre']} {venta.get('cliente_apellido', '')}"
        
        ticket = f"""
{linea}
        MI PUNTO DE VENTA
{linea}
Folio: {venta['id']}
Fecha: {fecha_venta}
Cliente: {cliente_nombre}

PRODUCTOS:
{linea}
"""
        
        for detalle in venta['detalles']:
            nombre = detalle['producto_nombre'][:25]
            cantidad = detalle['cantidad']
            precio = detalle['precio_unitario']
            subtotal = detalle['subtotal']
            
            ticket += f"{nombre:<25}\n"
            ticket += f"{cantidad:>3} x ${precio:>6.2f} = ${subtotal:>8.2f}\n"
            ticket += "-" * 40 + "\n"
        
        ticket += f"""
{linea}
Subtotal:        ${venta['subtotal']:>10.2f}
Descuento:       ${venta['descuento']:>10.2f}
Impuesto:        ${venta['impuesto']:>10.2f}
{linea}
TOTAL:           ${venta['total']:>10.2f}
{linea}

Método de pago: {venta['metodo_pago'].upper()}

{linea}
    ¡GRACIAS POR SU COMPRA!
{linea}
"""
        
        return ticket
    
    def guardar_para_despues(self):
        """Guarda la operación para procesar después"""
        nombre_operacion = f"Venta {datetime.now().strftime('%Y%m%d_%H%M')}"
        
        dialog = ctk.CTkInputDialog(
            text="Nombre para guardar la operación:",
            title="Guardar Operación"
        )
        nombre_input = dialog.get_input()
        
        if nombre_input:
            nombre_operacion = nombre_input
        
        try:
            # Preparar datos para guardar
            carrito_data = {
                'carrito': self.carrito_items,
                'cliente': self.cliente_info,
                'descuento': self.descuento,
                'metodo_pago': self.metodo_pago,
                'notas': self.text_notas.get('1.0', 'end').strip()
            }
            
            cliente_id = self.cliente_info['id'] if self.cliente_info else None
            
            operacion_id = self.db.guardar_operacion_espera(
                nombre_operacion, carrito_data, cliente_id
            )
            
            messagebox.showinfo("Guardado", f"Operación guardada con ID: {operacion_id}")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def cancelar_pago(self):
        """Cancela el proceso de pago"""
        if messagebox.askyesno("Confirmar", "¿Está seguro de cancelar el pago?"):
            self.window.destroy()
