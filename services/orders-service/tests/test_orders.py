from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_order():
    response = client.post(
        "/orders",
        json={
            "product": "Test Product",
            "quantity": 2,
            "customer": "test-user",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["product"] == "Test Product"
    assert data["quantity"] == 2
    assert data["customer"] == "test-user"
    assert "id" in data


def test_get_order():
    response = client.get("/orders/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1

def test_get_nonexistent_order():
    response = client.get("/orders/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


def test_create_order_with_invalid_quantity():
    response = client.post(
        "/orders",
        json={
            "product": "Test Product",
            "quantity": "not-a-number",
            "customer": "test-user",
        },
    )

    assert response.status_code == 422    