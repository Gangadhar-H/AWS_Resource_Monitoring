from fastapi.testclient import TestClient

from app.database import JsonStore
from app.providers.demo.provider import DemoProvider
from app.services.scan_service import ResourceNotFound, rescan_resource, run_scan

import pytest


def test_inventory_contains_every_resource(tmp_path):
    scan = run_scan(provider=DemoProvider(), store=JsonStore(str(tmp_path / "s.json")))
    inv = {i["resource_id"]: i for i in scan["inventory"]}
    assert len(inv) == 12
    assert inv["i-0demo000000000003"]["status"] == "healthy"
    assert inv["i-0demo000000000003"]["flagged"] is False
    assert inv["i-0demo000000000003"]["monthly_cost"] > 0
    assert inv["i-0demo000000000001"]["metrics"]["avg_cpu_percent"] == 2.3
    assert inv["vol-0demo0000000000e"]["cost_basis"].startswith("200 GB")
    assert scan["summary"]["estimated_monthly_spend"] > 0


def test_rescan_single_resource(tmp_path):
    store = JsonStore(str(tmp_path / "s.json"))
    first = run_scan(provider=DemoProvider(), store=store)
    scan, item = rescan_resource("ebs", "vol-0demo0000000000e", provider=DemoProvider(), store=store)
    assert item["status"] == "unused" and item["potential_savings"] == 16.0
    assert scan["scan_id"] != first["scan_id"]
    # CPU of other instances is preserved from the previous scan
    busy = next(i for i in scan["inventory"] if i["resource_id"] == "i-0demo000000000003")
    assert busy["metrics"]["avg_cpu_percent"] == 46.0


def test_rescan_missing_resource(tmp_path):
    with pytest.raises(ResourceNotFound):
        rescan_resource("ebs", "vol-nope", provider=DemoProvider(), store=JsonStore(str(tmp_path / "s.json")))


def test_inventory_api(tmp_path, monkeypatch):
    from app.routes import inventory as inv_route
    from app.services import scan_service

    store = JsonStore(str(tmp_path / "s.json"))
    run_scan(provider=DemoProvider(), store=store)
    monkeypatch.setattr(inv_route, "get_store", lambda: store)
    monkeypatch.setattr(scan_service, "get_store", lambda: store)
    monkeypatch.setattr(scan_service, "get_provider", lambda: DemoProvider())

    from app.main import app
    c = TestClient(app)
    r = c.get("/api/inventory?type=ebs").json()
    assert r["total"] == 6 and r["counts_by_type"] == {"ec2": 4, "ebs": 6, "eip": 2}
    assert c.get("/api/inventory?q=old-db").json()["total"] == 1
    assert c.get("/api/inventory/ebs/vol-0demo0000000000e").json()["item"]["status"] == "unused"
    assert c.get("/api/inventory/ebs/nope").status_code == 404
    assert c.post("/api/inventory/eip/eipalloc-0demo00000000001/scan").json()["item"]["potential_savings"] == 3.65
    assert c.post("/api/inventory/ebs/nope/scan").status_code == 404
