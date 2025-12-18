from flask import Flask, render_template, request, redirect, url_for
from db import init_db, get_conn
import math


app = Flask(__name__)

# Categorías y márgenes (en formato decimal)
# Ej: 13% -> 0.13

CATEGORY_MARGINS = {
    "Cigarrillos": 0.13,
    "Bebidas": 0.40,
    "Lacteos": 0.25,
    "Fiambres": 0.50,
    "Varios": 0.40
}

def calcular_precio_venta(precio_compra: float, categoria: str) -> float:
    
    margen = CATEGORY_MARGINS.get(categoria, 0.40)
    venta = precio_compra * (1 + margen)
    venta_redondeada = redondear_precio(venta, paso=10)
    return venta_redondeada

def redondear_precio(precio: float, paso: int = 10) -> float:
    """
    Redondea hacia arriba al múltiplo más cercano de 'paso'.
    Ej: paso=10 -> 7381 -> 7390
    """
    return math.ceil(precio / paso) * paso

@app.get("/")
def index():
    # 1) Leer filtros desde la URL (query string)
    q = (request.args.get("q") or "").strip()
    cat = (request.args.get("cat") or "").strip()

    # 2) Construir consulta SQL dinámica y segura (con parámetros)
    sql = "SELECT * FROM products WHERE 1=1"
    params = []

    if q:
        sql += " AND name LIKE ?"
        params.append(f"%{q}%")

    if cat and cat in CATEGORY_MARGINS:
        sql += " AND category = ?"
        params.append(cat)

    sql += " ORDER BY id DESC"

    # 3) Ejecutar consulta
    with get_conn() as conn:
        productos = conn.execute(sql, params).fetchall()

    categorias = list(CATEGORY_MARGINS.keys())

    return render_template(
        "index.html",
        products=productos,
        categories=categorias,
        category_margins=CATEGORY_MARGINS,
        q=q,
        cat=cat
    )

@app.post("/add")
def add():
    nombre = request.form["name"].strip()
    categoria = request.form["category"].strip()
    precio_compra = float(request.form["cost"])
    stock = int(request.form.get("stock", 0) or 0)
    min_stock = int(request.form.get("min_stock", 0) or 0)

    # Si por algún motivo llega una categoría desconocida, usamos "Varios"

    if categoria not in CATEGORY_MARGINS:
        categoria = "Varios"

    precio_venta = calcular_precio_venta(precio_compra, categoria)

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO products (name, category, cost, sale, stock, min_stock) VALUES (?, ?, ?, ?, ?, ?)",
            (nombre, categoria, precio_compra, precio_venta, stock, min_stock)
        )
        conn.commit()
    
    return redirect(url_for("index"))

@app.post("/delete/<int:pid>")
def delete(pid: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM products WHERE id = ?", (pid,))
        conn.commit()
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

