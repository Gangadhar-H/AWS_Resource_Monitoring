from datetime import datetime, timedelta, timezone

from app.analysis import rules
from app.analysis.analyzer import analyze
from app.cost import estimator

NOW = datetime(2026, 10, 18, tzinfo=timezone.utc)


def ec2(id="i-1", state="running", days_old=30, itype="t3.small", vols=None):
    return {"resource_type": "ec2", "resource_id": id, "name": "", "region": "r",
            "instance_type": itype, "state": state, "volume_ids": vols or [],
            "launch_time": (NOW - timedelta(days=days_old)).isoformat()}


def test_cost_estimates():
    assert estimator.ec2_monthly_cost("t3.small") == round(0.0208 * 730, 2)
    assert estimator.ebs_monthly_cost(100, "gp3") == 8.0
    assert estimator.eip_monthly_cost() == 3.65
    assert estimator.ec2_monthly_cost("unknown.type") == round(0.05 * 730, 2)


def test_new_instance_not_checked():
    assert rules.should_check_cpu(ec2(days_old=3), NOW, 14) is False
    assert rules.should_check_cpu(ec2(days_old=20), NOW, 14) is True
    assert rules.should_check_cpu(ec2(state="stopped"), NOW, 14) is False


def test_low_cpu_rule():
    assert rules.rule_low_cpu(ec2(), 2.0, 5, 14)
    assert rules.rule_low_cpu(ec2(), 40.0, 5, 14) is None
    assert rules.rule_low_cpu(ec2(), None, 5, 14) is None


def test_analyze_all_rules():
    resources = [
        ec2("i-idle"), ec2("i-busy"),
        ec2("i-stop", state="stopped", vols=["vol-a"]),
        {"resource_type": "ebs", "resource_id": "vol-a", "state": "in-use", "size_gb": 50, "volume_type": "gp3", "name": "", "region": "r"},
        {"resource_type": "ebs", "resource_id": "vol-free", "state": "available", "size_gb": 100, "volume_type": "gp3", "name": "", "region": "r"},
        {"resource_type": "eip", "resource_id": "eipalloc-1", "associated": False, "public_ip": "1.2.3.4", "name": "", "region": "r"},
        {"resource_type": "eip", "resource_id": "eipalloc-2", "associated": True, "public_ip": "5.6.7.8", "name": "", "region": "r"},
    ]
    f = {x["resource_id"]: x for x in analyze(resources, {"i-idle": 1.0, "i-busy": 60.0})}
    assert set(f) == {"i-idle", "i-stop", "vol-free", "eipalloc-1"}
    assert f["i-idle"]["status"] == "underutilized"
    assert f["i-idle"]["potential_savings"] == round(f["i-idle"]["monthly_cost"] * 0.5, 2)
    assert f["i-stop"]["monthly_cost"] == 4.0          # 50 GB gp3
    assert f["vol-free"]["monthly_cost"] == 8.0        # 100 GB gp3
    assert f["eipalloc-1"]["monthly_cost"] == 3.65


def test_demo_provider_end_to_end(tmp_path):
    from app.database import JsonStore
    from app.providers.demo.provider import DemoProvider
    from app.services.scan_service import run_scan

    scan = run_scan(provider=DemoProvider(), store=JsonStore(str(tmp_path / "s.json")))
    ids = {f["resource_id"]: f["status"] for f in scan["findings"]}
    assert ids["i-0demo000000000001"] == "underutilized"
    assert ids["i-0demo000000000002"] == "underutilized"
    assert "i-0demo000000000003" not in ids          # busy instance not flagged
    assert ids["i-0demo000000000004"] == "stopped"
    assert scan["summary"]["flagged_count"] == 6
