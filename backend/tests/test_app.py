from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthcheck():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

def test_chat():
    payload = {
        "message": {"text": "How was France performance?", "files": []},
        "history": [],
        "system_prompt": None
    }
    r = client.post("/chat", json=payload)
    assert r.status_code == 200
    assert "response" in r.json()
