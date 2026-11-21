"""Orchestrates scans: collect -> fetch metrics -> analyze -> summarize -> save."""
from __future__ import annotations

import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from app.analysis import rules
from app.analysis.analyzer import analyze, build_inventory
from app.config import settings
from app.cost import estimator
from app.database import get_store
from app.providers import get_provider


class ResourceNotFound(Exception):
    pass


def build_summary(resources: List[dict], findings: List[dict]) -> dict:
    by_type: Dict[str, dict] = defaultdict(lambda: {"count": 0, "monthly_cost": 0.0, "potential_savings": 0.0})
    for f in findings:
        b = by_type[f["resource_type"]]
        b["count"] += 1
        b["monthly_cost"] = round(b["monthly_cost"] + f["monthly_cost"], 2)
        b["potential_savings"] = round(b["potential_savings"] + f["potential_savings"], 2)
    return {
        "total_resources_scanned": len(resources),
        "scanned_by_type": dict(Counter(r["resource_type"] for r in resources)),
        "flagged_count": len(findings),
        "estimated_monthly_spend": round(sum(estimator.base_cost(r)[0] for r in resources), 2),
        "estimated_monthly_waste": round(sum(f["monthly_cost"] for f in findings), 2),
        "potential_monthly_savings": round(sum(f["potential_savings"] for f in findings), 2),
        "by_type": dict(by_type),
        "by_status": dict(Counter(f["status"] for f in findings)),
    }


def _assemble(provider, resources: List[dict], cpu: Dict[str, Optional[float]], now: datetime) -> dict:
    findings = analyze(resources, cpu)
    return {
        "scan_id": uuid.uuid4().hex[:12],
        "scanned_at": now.isoformat(),
        "provider": provider.name,
        "region": provider.region,
        "summary": build_summary(resources, findings),
        "findings": findings,
        "inventory": build_inventory(resources, findings, cpu, now),
    }


def run_scan(provider=None, store=None, now: Optional[datetime] = None) -> dict:
    provider = provider or get_provider()
    store = store or get_store()
    now = now or datetime.now(timezone.utc)

    resources = provider.collect_resources()
    cpu: Dict[str, Optional[float]] = {}
    for r in resources:
        if r["resource_type"] == "ec2" and rules.should_check_cpu(r, now, settings.lookback_days):
            cpu[r["resource_id"]] = provider.get_cpu_utilization(r["resource_id"], settings.lookback_days)

    scan = _assemble(provider, resources, cpu, now)
    store.save_scan(scan)
    return scan


def rescan_resource(resource_type: str, resource_id: str, provider=None, store=None,
                    now: Optional[datetime] = None) -> Tuple[dict, dict]:
    """Re-check ONE resource with fresh data. Other resources reuse their last CPU
    reading. The result is saved as a new coherent scan. Returns (scan, item)."""
    provider = provider or get_provider()
    store = store or get_store()
    now = now or datetime.now(timezone.utc)

    resources = provider.collect_resources()
    target = next((r for r in resources
                   if r["resource_type"] == resource_type and r["resource_id"] == resource_id), None)
    if target is None:
        raise ResourceNotFound(f"{resource_type} {resource_id} no longer exists in this account/region.")

    previous = (store.latest_scan() or {}).get("inventory", [])
    cpu: Dict[str, Optional[float]] = {
        i["resource_id"]: i["metrics"]["avg_cpu_percent"]
        for i in previous
        if i.get("metrics") and i["metrics"].get("avg_cpu_percent") is not None
    }
    if resource_type == "ec2" and rules.should_check_cpu(target, now, settings.lookback_days):
        cpu[resource_id] = provider.get_cpu_utilization(resource_id, settings.lookback_days)

    scan = _assemble(provider, resources, cpu, now)
    store.save_scan(scan)
    item = next(i for i in scan["inventory"]
                if i["resource_type"] == resource_type and i["resource_id"] == resource_id)
    return scan, item
