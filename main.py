import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

# Conexión a la base de datos
conn = sqlite3.connect('gestion_gastos_comunes.db')
cursor = conn.cursor()

# Crear tablas
cursor.execute('''CREATE TABLE IF NOT EXISTS residentes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT
                )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS facturas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    residente_id INTEGER,
                    fecha TEXT,
                    monto REAL,
                    descripcion TEXT,
                    FOREIGN KEY (residente_id) REFERENCES residentes(id)
                )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS gastos_comunes (
                    id INTEGER PRIMARY KEY,
                    monto REAL
                )''')
cursor.execute('''CREATE TABLE IF NOT EXISTS pagos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    residente_id INTEGER,
                    gasto_id INTEGER,
                    monto_pagado REAL,
                    fecha TEXT,
                    FOREIGN KEY (residente_id) REFERENCES residentes(id),
                    FOREIGN KEY (gasto_id) REFERENCES gastos_comunes(id)
                )''')
conn.commit()

# Insertar el gasto común fijo si no existe
cursor.execute("INSERT OR IGNORE INTO gastos_comunes (id, monto) VALUES (1, 150000)")
conn.commit()

cursor.execute("INSERT OR IGNORE INTO residentes (id, nombre) VALUES (1, 'Allan romero')")
conn.commit()
cursor.execute("INSERT OR IGNORE INTO residentes (id, nombre) VALUES (2, 'Maykol Alfaro')")
conn.commit()
cursor.execute("INSERT OR IGNORE INTO residentes (id, nombre) VALUES (3, 'Esteban Fernandez')")
conn.commit()

# Función para mostrar los residentes
def mostrar_residentes():
    for row in tree_residentes.get_children():
        tree_residentes.delete(row)
    cursor.execute("SELECT * FROM residentes")
    for row in cursor.fetchall():
        tree_residentes.insert("", tk.END, values=row)

# Función para mostrar la ventana de deuda del residente
def ver_deuda_residente():
    selected_item = tree_residentes.selection()
    if not selected_item:
        return
    residente_id = tree_residentes.item(selected_item[0])['values'][0]
    nombre_residente = tree_residentes.item(selected_item[0])['values'][1]
    
    # Obtener el monto del gasto común
    cursor.execute("SELECT monto FROM gastos_comunes WHERE id = 1")
    deuda = cursor.fetchone()[0]
    fecha_actual = datetime.now().strftime("%Y-%m-%d")

    # Crear la ventana emergente para mostrar la deuda
    ventana_deuda = tk.Toplevel(root)
    ventana_deuda.title(f"Deuda de {nombre_residente}")

    label_residente = tk.Label(ventana_deuda, text=f"Residente: {nombre_residente}")
    label_residente.pack()
    label_deuda = tk.Label(ventana_deuda, text=f"Deuda Actual: {deuda} CLP")
    label_deuda.pack()
    label_fecha = tk.Label(ventana_deuda, text=f"Fecha: {fecha_actual}")
    label_fecha.pack()

    # Función para procesar el pago
    def pagar():
        # Registrar el pago en la base de datos
        cursor.execute("INSERT INTO pagos (residente_id, gasto_id, monto_pagado, fecha) VALUES (?, ?, ?, ?)",
                       (residente_id, 1, deuda, fecha_actual))
        cursor.execute("INSERT INTO facturas (residente_id, fecha, monto, descripcion) VALUES (?, ?, ?, ?)",
                       (residente_id, fecha_actual, deuda, f"Pago de gasto común de {deuda} CLP"))
        conn.commit()

        # Actualizar la deuda a 0 en la interfaz
        label_deuda.config(text="Deuda Actual: 0 CLP")
        messagebox.showinfo("Pago Realizado", f"Factura generada por {deuda} CLP")
        boton_pagar.config(state="disabled")
        ventana_deuda.destroy()

    # Botón para pagar
    boton_pagar = tk.Button(ventana_deuda, text="Pagar", command=pagar)
    boton_pagar.pack()

# Configuración de la ventana principal
root = tk.Tk()
root.title("Gestión de Gastos Comunes")

# Sección de residentes
frame_residentes = tk.Frame(root)
frame_residentes.pack()

label_residentes = tk.Label(frame_residentes, text="Residentes:")
label_residentes.pack()

tree_residentes = ttk.Treeview(frame_residentes, columns=("ID", "Nombre"), show="headings")
tree_residentes.heading("ID", text="ID")
tree_residentes.heading("Nombre", text="Nombre")
tree_residentes.pack()

# Botón para ver deuda
boton_ver_deuda = tk.Button(root, text="Ver Deuda", command=ver_deuda_residente)
boton_ver_deuda.pack()

# Mostrar residentes en la interfaz
mostrar_residentes()

# Ejecutar la interfaz gráfica
root.mainloop()

# Cerrar la conexión a la base de datos al cerrar la aplicación
conn.close()
