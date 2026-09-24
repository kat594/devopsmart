from flask import Blueprint, render_template, jsonify
from app.database import get_db_connection

main = Blueprint("main", __name__)


@main.route("/")
def home():
    connection = get_db_connection()

    products = connection.execute(
        "SELECT * FROM products LIMIT 6"
    ).fetchall()

    connection.close()

    return render_template("index.html", products=products)


@main.route("/products")
def products():
    connection = get_db_connection()

    products = connection.execute(
        "SELECT * FROM products"
    ).fetchall()

    connection.close()

    return render_template("products.html", products=products)


@main.route("/products/<int:product_id>")
def product(product_id):
    connection = get_db_connection()

    product = connection.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    connection.close()

    if product is None:
        return "Product not found", 404

    return render_template("product.html", product=product)


@main.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "application": "DevOpsMart"
    })


@main.route("/api/products")
def api_products():
    connection = get_db_connection()

    products = connection.execute(
        "SELECT * FROM products"
    ).fetchall()

    connection.close()

    return jsonify([
        dict(product)
        for product in products
    ])
