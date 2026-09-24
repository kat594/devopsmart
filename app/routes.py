from flask import Blueprint, render_template, jsonify, request, session, redirect
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
    search = request.args.get("search", "").strip()

    connection = get_db_connection()

    if search:
        products = connection.execute(
            """
            SELECT * FROM products
            WHERE name LIKE ?
               OR category LIKE ?
               OR description LIKE ?
            """,
            (
                f"%{search}%",
                f"%{search}%",
                f"%{search}%"
            )
        ).fetchall()
    else:
        products = connection.execute(
            "SELECT * FROM products"
        ).fetchall()

    connection.close()

    return render_template(
        "products.html",
        products=products,
        search=search
    )


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


@main.route("/cart/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    connection = get_db_connection()

    product = connection.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    connection.close()

    if product is None:
        return "Product not found", 404

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    session["cart"] = cart

    return redirect("/cart")


@main.route("/cart")
def cart():
    cart = session.get("cart", {})

    cart_items = []
    total = 0

    connection = get_db_connection()

    for product_id, quantity in cart.items():

        product = connection.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()

        if product:
            item_total = product["price"] * quantity

            cart_items.append({
                "product": product,
                "quantity": quantity,
                "item_total": item_total
            })

            total += item_total

    connection.close()

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total
    )


@main.route("/cart/decrease/<int:product_id>", methods=["POST"])
def decrease_cart(product_id):
    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] -= 1

        if cart[product_id] <= 0:
            del cart[product_id]

    session["cart"] = cart

    return redirect("/cart")


@main.route("/cart/remove/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    session["cart"] = cart

    return redirect("/cart")


@main.route("/checkout", methods=["GET"])
def checkout():
    cart = session.get("cart", {})

    if not cart:
        return redirect("/cart")

    cart_items = []
    total = 0

    connection = get_db_connection()

    for product_id, quantity in cart.items():

        product = connection.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()

        if product:
            item_total = product["price"] * quantity

            cart_items.append({
                "product": product,
                "quantity": quantity,
                "item_total": item_total
            })

            total += item_total

    connection.close()

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total=total
    )


@main.route("/checkout", methods=["POST"])
def place_order():
    customer_name = request.form.get("customer_name", "").strip()
    customer_email = request.form.get("customer_email", "").strip()

    cart = session.get("cart", {})

    if not cart:
        return redirect("/cart")

    if not customer_name or not customer_email:
        return "Name and email are required", 400

    connection = get_db_connection()

    total = 0
    cart_items = []

    for product_id, quantity in cart.items():

        product = connection.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()

        if product:
            item_total = product["price"] * quantity
            total += item_total

            cart_items.append({
                "product_id": product["id"],
                "quantity": quantity,
                "price": product["price"]
            })

    if not cart_items:
        connection.close()
        return redirect("/cart")

    cursor = connection.execute(
        """
        INSERT INTO orders
        (customer_name, customer_email, total, status)
        VALUES (?, ?, ?, ?)
        """,
        (
            customer_name,
            customer_email,
            total,
            "PLACED"
        )
    )

    order_id = cursor.lastrowid

    for item in cart_items:
        connection.execute(
            """
            INSERT INTO order_items
            (order_id, product_id, quantity, price)
            VALUES (?, ?, ?, ?)
            """,
            (
                order_id,
                item["product_id"],
                item["quantity"],
                item["price"]
            )
        )

    connection.commit()
    connection.close()

    session.pop("cart", None)

    return redirect(f"/order-success/{order_id}")


@main.route("/order-success/<int:order_id>")
def order_success(order_id):
    connection = get_db_connection()

    order = connection.execute(
        "SELECT * FROM orders WHERE id = ?",
        (order_id,)
    ).fetchone()

    connection.close()

    if order is None:
        return "Order not found", 404

    return render_template(
        "order-success.html",
        order=order
    )


@main.route("/orders")
def orders():
    connection = get_db_connection()

    orders = connection.execute(
        "SELECT * FROM orders ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template(
        "orders.html",
        orders=orders
    )


@main.route("/orders/<int:order_id>")
def order_detail(order_id):
    connection = get_db_connection()

    order = connection.execute(
        "SELECT * FROM orders WHERE id = ?",
        (order_id,)
    ).fetchone()

    if order is None:
        connection.close()
        return "Order not found", 404

    items = connection.execute(
        """
        SELECT
            order_items.quantity,
            order_items.price,
            products.name AS product_name
        FROM order_items
        JOIN products
            ON order_items.product_id = products.id
        WHERE order_items.order_id = ?
        """,
        (order_id,)
    ).fetchall()

    connection.close()

    return render_template(
        "order-detail.html",
        order=order,
        items=items
    )


@main.route("/ready")
def ready():
    try:
        connection = get_db_connection()

        connection.execute(
            "SELECT 1"
        )

        connection.close()

        return jsonify({
            "status": "ready",
            "application": "DevOpsMart",
            "database": "connected"
        })

    except Exception:
        return jsonify({
            "status": "not_ready",
            "application": "DevOpsMart",
            "database": "unavailable"
        }), 503
