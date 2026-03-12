from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_chat_endpoint():
    response = client.get("/api/v1/chat")
    assert response.status_code == 200
