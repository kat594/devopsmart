from app import create_app


def test_home_page():
    app = create_app()
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 200


def test_health():
    app = create_app()
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"
    assert data["application"] == "DevOpsMart"


def test_products_api():
    app = create_app()
    client = app.test_client()

    response = client.get("/api/products")

    assert response.status_code == 200

    data = response.get_json()

    assert isinstance(data, list)
    assert len(data) >= 1


def test_product_details():
    app = create_app()
    client = app.test_client()

    response = client.get("/products/1")

    assert response.status_code == 200


def test_product_not_found():
    app = create_app()
    client = app.test_client()

    response = client.get("/products/9999")

    assert response.status_code == 404


def test_ready():
    app = create_app()
    client = app.test_client()

    response = client.get("/ready")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "ready"
    assert data["application"] == "DevOpsMart"
    assert data["database"] == "connected"
