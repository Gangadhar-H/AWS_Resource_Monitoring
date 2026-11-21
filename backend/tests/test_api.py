from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_endpoints_respond():
    r = client.get("/api/summary")
    assert r.status_code == 200 and "summary" in r.json()
    assert client.get("/api/resources").status_code == 200
