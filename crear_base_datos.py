#!/usr/bin/env python3
"""
Script para crear e inicializar la base de datos del sistema de punto de venta.
Este script crea todas las tablas necesarias y las llena con datos de ejemplo.
"""

import sqlite3
import os
from datetime import datetime, date

def crear_base_datos():
    """Crea la base de datos completa con todas las tablas y datos iniciales"""
    
    db_name = "punto_venta.db"
    
    # Eliminar base de datos existente si queremos empezar desde cero
    if os.path.exists(db_name):
        respuesta = input(f"La base de datos '{db_name}' ya existe. ¿Desea recrearla? (s/n): ")
        if respuesta.lower() in ['s', 'si', 'y', 'yes']:
            os.remove(db_name)
            print(f"✅ Base de datos anterior eliminada.")
        else:
            print("❌ Operación cancelada.")
            return
    
    print(f"🔧 Creando base de datos '{db_name}'...")
    
    # Crear conexión
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    try:
        # 1. Tabla de categorías
        print("📁 Creando tabla 'categorias'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                descripcion TEXT,
                activo BOOLEAN DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. Tabla de productos
        print("📦 Creando tabla 'productos'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_barras TEXT UNIQUE,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                categoria_id INTEGER,
                precio_venta DECIMAL(10,2) NOT NULL,
                precio_compra DECIMAL(10,2),
                stock_actual INTEGER DEFAULT 0,
                stock_minimo INTEGER DEFAULT 0,
                activo BOOLEAN DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (categoria_id) REFERENCES categorias (id)
            )
        ''')
        
        # 3. Tabla de clientes
        print("👥 Creando tabla 'clientes'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN DEFAULT 1
            )
        ''')
        
        # 4. Tabla de ventas
        print("💰 Creando tabla 'ventas'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                subtotal DECIMAL(10,2) NOT NULL,
                impuesto DECIMAL(10,2) DEFAULT 0,
                descuento DECIMAL(10,2) DEFAULT 0,
                total DECIMAL(10,2) NOT NULL,
                metodo_pago TEXT DEFAULT 'efectivo',
                estado TEXT DEFAULT 'completada',
                notas TEXT,
                FOREIGN KEY (cliente_id) REFERENCES clientes (id)
            )
        ''')
        
        # 5. Tabla de detalles de venta
        print("📋 Creando tabla 'detalle_ventas'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario DECIMAL(10,2) NOT NULL,
                subtotal DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas (id),
                FOREIGN KEY (producto_id) REFERENCES productos (id)
            )
        ''')
        
        # 6. Tabla de movimientos de inventario
        print("📊 Creando tabla 'movimientos_inventario'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movimientos_inventario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                tipo_movimiento TEXT NOT NULL, -- 'entrada', 'salida', 'ajuste'
                cantidad INTEGER NOT NULL,
                cantidad_anterior INTEGER NOT NULL,
                cantidad_nueva INTEGER NOT NULL,
                motivo TEXT,
                fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usuario TEXT,
                FOREIGN KEY (producto_id) REFERENCES productos (id)
            )
        ''')
        
        # 7. Tabla de ventas en espera
        print("⏳ Creando tabla 'ventas_espera'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas_espera (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_operacion TEXT NOT NULL,
                cliente_id INTEGER,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                datos_carrito TEXT, -- JSON con los productos del carrito
                notas TEXT,
                FOREIGN KEY (cliente_id) REFERENCES clientes (id)
            )
        ''')
        
        # 8. Tabla de configuración
        print("⚙️ Creando tabla 'configuracion'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_tienda TEXT DEFAULT 'Mi Tienda',
                direccion_tienda TEXT,
                telefono_tienda TEXT,
                impuesto_por_defecto DECIMAL(5,2) DEFAULT 0.0,
                moneda TEXT DEFAULT '$',
                ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        print("✅ Todas las tablas creadas exitosamente.")
        
        # Insertar datos iniciales
        insertar_datos_iniciales(cursor)
        
        # Confirmar cambios
        conn.commit()
        print("💾 Cambios guardados en la base de datos.")
        
    except Exception as e:
        print(f"❌ Error al crear la base de datos: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()
    
    print(f"🎉 Base de datos '{db_name}' creada exitosamente!")

def insertar_datos_iniciales(cursor):
    """Inserta datos iniciales en las tablas"""
    
    print("📝 Insertando datos iniciales...")
    
    # 1. Insertar categorías
    print("  - Insertando categorías...")
    categorias = [
        ('Bebidas', 'Bebidas frías y calientes'),
        ('Comida', 'Alimentos y comida preparada'),
        ('Postres', 'Postres y dulces'),
        ('Limpieza', 'Productos de limpieza para el hogar'),
        ('Higiene', 'Productos de higiene personal'),
        ('Electrónicos', 'Dispositivos y accesorios electrónicos'),
        ('Otros', 'Otros productos diversos')
    ]
    
    cursor.executemany("INSERT INTO categorias (nombre, descripcion) VALUES (?, ?)", categorias)
    
    # 2. Insertar configuración inicial
    print("  - Configuración inicial...")
    cursor.execute("""
        INSERT INTO configuracion (nombre_tienda, direccion_tienda, telefono_tienda, impuesto_por_defecto) 
        VALUES ('Mi Punto de Venta', 'Calle Principal #123, Ciudad', '555-0123', 16.0)
    """)
    
    # 3. Insertar productos de ejemplo
    print("  - Productos de ejemplo...")
    productos_ejemplo = [
        # Bebidas
        ('7501234567890', 'Coca Cola 600ml', 'Refresco de cola 600ml', 1, 20.00, 15.00, 50, 10),
        ('7501234567891', 'Pepsi 600ml', 'Refresco de cola Pepsi 600ml', 1, 18.00, 13.00, 30, 10),
        ('7501234567892', 'Agua Natural 1L', 'Agua purificada 1 litro', 1, 12.00, 8.00, 100, 20),
        ('7501234567893', 'Jugo de Naranja', 'Jugo natural de naranja 500ml', 1, 25.00, 18.00, 25, 5),
        ('7501234567894', 'Café Americano', 'Café americano grande', 1, 30.00, 20.00, 0, 0),
        
        # Comida
        ('7501234567895', 'Sandwich Jamón', 'Sandwich de jamón y queso', 2, 35.00, 25.00, 15, 5),
        ('7501234567896', 'Pizza Personal', 'Pizza individual de pepperoni', 2, 45.00, 30.00, 10, 3),
        ('7501234567897', 'Hamburguesa', 'Hamburguesa con papas', 2, 55.00, 40.00, 8, 2),
        ('7501234567898', 'Ensalada César', 'Ensalada césar con pollo', 2, 42.00, 30.00, 12, 3),
        ('7501234567899', 'Tacos (3 pzs)', 'Orden de 3 tacos', 2, 38.00, 28.00, 20, 5),
        
        # Postres
        ('7501234567900', 'Chocolate Milka', 'Barra de chocolate con leche', 3, 25.00, 18.00, 40, 10),
        ('7501234567901', 'Helado Vainilla', 'Helado de vainilla 1L', 3, 65.00, 45.00, 15, 5),
        ('7501234567902', 'Pastel Chocolate', 'Rebanada de pastel de chocolate', 3, 40.00, 25.00, 8, 2),
        ('7501234567903', 'Galletas', 'Paquete de galletas de chocolate', 3, 22.00, 16.00, 30, 8),
        
        # Limpieza
        ('7501234567904', 'Detergente 1L', 'Detergente líquido para ropa', 4, 55.00, 40.00, 25, 5),
        ('7501234567905', 'Limpiador Multiusos', 'Limpiador multiusos 500ml', 4, 35.00, 25.00, 20, 5),
        ('7501234567906', 'Papel Higiénico', 'Papel higiénico 4 rollos', 4, 48.00, 35.00, 40, 10),
        
        # Higiene
        ('7501234567907', 'Jabón Antibacterial', 'Jabón líquido para manos', 5, 30.00, 22.00, 35, 8),
        ('7501234567908', 'Shampoo', 'Shampoo para cabello graso', 5, 45.00, 32.00, 20, 5),
        ('7501234567909', 'Pasta Dental', 'Pasta dental con flúor', 5, 28.00, 20.00, 25, 8),
        
        # Electrónicos
        ('7501234567910', 'Audífonos', 'Audífonos con cable', 6, 85.00, 60.00, 12, 3),
        ('7501234567911', 'Cable USB', 'Cable USB tipo C', 6, 35.00, 25.00, 15, 5),
        
        # Otros
        ('7501234567912', 'Pilas AA', 'Pack de 4 pilas AA', 7, 45.00, 30.00, 20, 5),
        ('7501234567913', 'Cuaderno', 'Cuaderno profesional 100 hojas', 7, 25.00, 18.00, 30, 8)
    ]
    
    cursor.executemany("""
        INSERT INTO productos (codigo_barras, nombre, descripcion, categoria_id, 
                             precio_venta, precio_compra, stock_actual, stock_minimo) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, productos_ejemplo)
    
    # 4. Insertar clientes de ejemplo
    print("  - Clientes de ejemplo...")
    clientes_ejemplo = [
        ('Juan', 'Pérez', '555-0001', 'juan.perez@email.com', 'Av. Principal 123'),
        ('María', 'González', '555-0002', 'maria.gonzalez@email.com', 'Calle Secundaria 456'),
        ('Carlos', 'Rodríguez', '555-0003', 'carlos.rodriguez@email.com', 'Col. Centro 789'),
        ('Ana', 'Martínez', '555-0004', 'ana.martinez@email.com', 'Fraccionamiento Norte 321'),
        ('Luis', 'Hernández', '555-0005', 'luis.hernandez@email.com', 'Zona Sur 654'),
    ]
    
    cursor.executemany("""
        INSERT INTO clientes (nombre, apellido, telefono, email, direccion)
        VALUES (?, ?, ?, ?, ?)
    """, clientes_ejemplo)
    
    # 5. Registrar movimientos iniciales de inventario
    print("  - Movimientos de inventario iniciales...")
    # Obtener todos los productos para registrar su stock inicial
    cursor.execute("SELECT id, stock_actual FROM productos WHERE stock_actual > 0")
    productos_con_stock = cursor.fetchall()
    
    for producto_id, stock_inicial in productos_con_stock:
        cursor.execute("""
            INSERT INTO movimientos_inventario 
            (producto_id, tipo_movimiento, cantidad, cantidad_anterior, cantidad_nueva, 
             motivo, usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (producto_id, 'entrada', stock_inicial, 0, stock_inicial, 
              'Stock inicial del sistema', 'Sistema'))
    
    print("✅ Datos iniciales insertados correctamente.")

def verificar_base_datos():
    """Verifica que la base de datos se haya creado correctamente"""
    
    db_name = "punto_venta.db"
    
    if not os.path.exists(db_name):
        print(f"❌ La base de datos '{db_name}' no existe.")
        return False
    
    print(f"🔍 Verificando base de datos '{db_name}'...")
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    try:
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        tablas_esperadas = ['categorias', 'productos', 'clientes', 'ventas', 
                           'detalle_ventas', 'movimientos_inventario', 
                           'ventas_espera', 'configuracion']
        
        print(f"📋 Tablas encontradas: {len(tablas)}")
        for tabla in tablas:
            print(f"  - {tabla[0]}")
        
        # Verificar datos
        print("\n📊 Conteo de registros:")
        for tabla in tablas_esperadas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = cursor.fetchone()[0]
            print(f"  - {tabla}: {count} registros")
        
        print("\n✅ Base de datos verificada correctamente.")
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar la base de datos: {e}")
        return False
    
    finally:
        conn.close()

def mostrar_menu():
    """Muestra el menú de opciones"""
    print("\n" + "="*50)
    print("🗄️  GESTOR DE BASE DE DATOS - PUNTO DE VENTA")
    print("="*50)
    print("1. Crear base de datos nueva")
    print("2. Verificar base de datos existente")
    print("3. Mostrar estadísticas")
    print("4. Salir")
    print("="*50)

def mostrar_estadisticas():
    """Muestra estadísticas de la base de datos"""
    db_name = "punto_venta.db"
    
    if not os.path.exists(db_name):
        print(f"❌ La base de datos '{db_name}' no existe.")
        return
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    try:
        print("\n📈 ESTADÍSTICAS DE LA BASE DE DATOS")
        print("-" * 40)
        
        # Productos por categoría
        cursor.execute("""
            SELECT c.nombre, COUNT(p.id) as total_productos
            FROM categorias c
            LEFT JOIN productos p ON c.id = p.categoria_id AND p.activo = 1
            GROUP BY c.id, c.nombre
            ORDER BY total_productos DESC
        """)
        print("\n🏷️  Productos por categoría:")
        for categoria, total in cursor.fetchall():
            print(f"  - {categoria}: {total} productos")
        
        # Productos con stock bajo
        cursor.execute("""
            SELECT nombre, stock_actual, stock_minimo
            FROM productos 
            WHERE stock_actual <= stock_minimo AND activo = 1
            ORDER BY stock_actual
        """)
        productos_stock_bajo = cursor.fetchall()
        print(f"\n⚠️  Productos con stock bajo: {len(productos_stock_bajo)}")
        for nombre, actual, minimo in productos_stock_bajo[:5]:
            print(f"  - {nombre}: {actual}/{minimo}")
        
        # Valor total del inventario
        cursor.execute("""
            SELECT SUM(stock_actual * precio_compra) as valor_inventario
            FROM productos 
            WHERE activo = 1
        """)
        valor_inventario = cursor.fetchone()[0] or 0
        print(f"\n💰 Valor total del inventario: ${valor_inventario:.2f}")
        
        # Total de clientes
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE activo = 1")
        total_clientes = cursor.fetchone()[0]
        print(f"👥 Total de clientes: {total_clientes}")
        
        # Total de ventas
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM ventas")
        total_ventas, total_ingresos = cursor.fetchone()
        print(f"💸 Total de ventas: {total_ventas} (${total_ingresos:.2f})")
        
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    while True:
        mostrar_menu()
        opcion = input("\n👉 Seleccione una opción: ")
        
        if opcion == "1":
            crear_base_datos()
            input("\n✅ Presione Enter para continuar...")
            
        elif opcion == "2":
            if verificar_base_datos():
                print("✅ La base de datos está funcionando correctamente.")
            input("\n✅ Presione Enter para continuar...")
            
        elif opcion == "3":
            mostrar_estadisticas()
            input("\n✅ Presione Enter para continuar...")
            
        elif opcion == "4":
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción no válida. Intente de nuevo.")
            input("Presione Enter para continuar...")
