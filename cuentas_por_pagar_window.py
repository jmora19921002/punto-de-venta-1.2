import customtkinter as ctk
from tkinter import ttk, messagebox

class CuentasPorPagarWindow:
    def __init__(self, master, db):
        self.db = db
        self.window = ctk.CTkToplevel(master)
        self.window.title("Cuentas por Pagar - Compras")
        self.window.geometry("1800x700")
        self.window.transient(master)
        self.window.grab_set()
        
        self.setup_ui()
        self.cargar_compras()

    def setup_ui(self):
        # Encabezado
        ctk.CTkLabel(self.window, text="Compras registradas", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)
        
        # Frame principal dividido
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sección izquierda: lista de compras
        left = ctk.CTkFrame(main_frame)
        left.pack(side="left", fill="both", expand=True, padx=(0,5))
        
        self.tree_compras = ttk.Treeview(
            left,
            columns=("id","fecha","documento","proveedor","tasa","subtotal","total","estado"),
            show="headings",
            height=14
        )
        headers = {
            "id": ("ID", 60),
            "fecha": ("Fecha", 100),
            "documento": ("Documento", 120),
            "proveedor": ("Proveedor", 220),
            "tasa": ("Tasa", 80),
            "subtotal": ("Subtotal Bs", 120),
            "total": ("Total Bs", 120),
            "estado": ("Estado", 100)
        }
        for col,(txt,w) in headers.items():
            self.tree_compras.heading(col, text=txt)
            self.tree_compras.column(col, width=w, anchor="center")
        
        scrollbar_y = ttk.Scrollbar(left, orient="vertical", command=self.tree_compras.yview)
        self.tree_compras.configure(yscrollcommand=scrollbar_y.set)
        self.tree_compras.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        
        self.tree_compras.bind('<<TreeviewSelect>>', self.on_select_compra)
        
        # Sección derecha: detalle de compra
        right = ctk.CTkFrame(main_frame)
        right.pack(side="right", fill="both", expand=True, padx=(5,0))
        ctk.CTkLabel(right, text="Detalle de la compra", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)
        
        self.tree_detalle = ttk.Treeview(
            right,
            columns=("producto","cantidad","precio_usd","precio_bs","subtotal_bs"),
            show="headings",
            height=12
        )
        det_headers = {
            "producto": ("Producto", 220),
            "cantidad": ("Cant.", 80),
            "precio_usd": ("P. USD", 90),
            "precio_bs": ("P. Bs", 90),
            "subtotal_bs": ("Subtotal Bs", 120)
        }
        for col,(txt,w) in det_headers.items():
            self.tree_detalle.heading(col, text=txt)
            self.tree_detalle.column(col, width=w, anchor="center" if col in ("cantidad",) else "e" if col != "producto" else "w")
        
        scroll_y_det = ttk.Scrollbar(right, orient="vertical", command=self.tree_detalle.yview)
        self.tree_detalle.configure(yscrollcommand=scroll_y_det.set)
        self.tree_detalle.pack(side="left", fill="both", expand=True)
        scroll_y_det.pack(side="right", fill="y")
        
        # Pie con acciones básicas (futuro: registrar pagos)
        pie = ctk.CTkFrame(self.window)
        pie.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(pie, text="Cerrar", command=self.window.destroy).pack(side="right")

    def cargar_compras(self):
        # Limpiar
        for item in self.tree_compras.get_children():
            self.tree_compras.delete(item)
        try:
            compras = self.db.get_compras()
            for co in compras:
                self.tree_compras.insert('', 'end', values=(
                    co['id'], co['fecha_compra'], co.get('documento',''), co.get('proveedor_nombre',''),
                    f"{float(co.get('tasa_cambio',0)):.2f}", f"{float(co.get('subtotal_ves',0)):.2f}",
                    f"{float(co.get('total_ves',0)):.2f}", co.get('estado','')
                ), tags=(co['id'],))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar compras: {e}")

    def on_select_compra(self, event=None):
        selection = self.tree_compras.selection()
        if not selection:
            return
        compra_id = int(self.tree_compras.item(selection[0])['tags'][0])
        # Cargar detalle
        for item in self.tree_detalle.get_children():
            self.tree_detalle.delete(item)
        try:
            detalle = self.db.get_detalle_compra(compra_id)
            for d in detalle:
                self.tree_detalle.insert('', 'end', values=(
                    d['producto'], d['cantidad'], f"{float(d['precio_unitario_usd']):.2f}",
                    f"{float(d['precio_unitario_ves']):.2f}", f"{float(d['subtotal_ves']):.2f}"
                ))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar detalle: {e}")
