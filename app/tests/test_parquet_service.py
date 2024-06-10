from fastapi.testclient import TestClient
from app.main import app  # Assuming your FastAPI app instance is named `app`
import json

client = TestClient(app)

def test_get_token():
    response = client.post(
        "/get_token",
        json={"email": "test@example.com", "password": "ola12345"}
    )
    assert response.status_code == 200
    assert "token" in response.json()

    response = client.post(
        "/get_token",
        json={"email": "invalid@example.com", "password": "invalidpassword"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid credentials"}