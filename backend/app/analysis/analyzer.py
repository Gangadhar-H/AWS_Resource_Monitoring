"""Applies the rules to collected resources and produces findings with costs."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from app.analysis import rules
from app.config import settings
from app.cost import estimator
from app.recommendations.engine import recommend


def _finding(res: dict, status: str, reason: str, monthly_cost: float,
             savings: float, details: Optional[dict] = None) -> dict:
    return {
        "resource_type": res["resource_type"],
        "resource_id": res["resource_id"],
        "name": res.get("name", ""),
        "region": res.get("region", ""),
        "status": status,  # "underutilized" | "unused" | "stopped"
        "reason": reason,
        "monthly_cost": round(monthly_cost, 2),
        "potential_savings": round(savings, 2),
        "recommendation": recommend(res["resource_type"], status),
        "details": details or {},
    }


def analyze(
    resources: List[dict],
    cpu_by_instance: Dict[str, Optional[float]],
    threshold: float = settings.cpu_threshold_percent,
    days: int = settings.lookback_days,
    savings_factor: float = settings.underutilized_savings_factor,
) -> List[dict]:
    volumes = {r["resource_id"]: r for r in resources if r["resource_type"] == "ebs"}
    findings: List[dict] = []

    for res in resources:
        rtype = res["resource_type"]

        if rtype == "ebs":
            reason = rules.rule_unattached_volume(res)
            if reason:
                cost = estimator.ebs_monthly_cost(res["size_gb"], res["volume_type"])
                findings.append(_finding(res, "unused", reason, cost, cost,
                                         {"size_gb": res["size_gb"], "volume_type": res["volume_type"]}))

        elif rtype == "eip":
            reason = rules.rule_unassociated_eip(res)
            if reason:
                cost = estimator.eip_monthly_cost()
                findings.append(_finding(res, "unused", reason, cost, cost,
                                         {"public_ip": res.get("public_ip")}))

        elif rtype == "ec2":
            avg_cpu = cpu_by_instance.get(res["resource_id"])
            reason = rules.rule_low_cpu(res, avg_cpu, threshold, days)
            if reason:
                cost = estimator.ec2_monthly_cost(res["instance_type"])
                findings.append(_finding(
                    res, "underutilized", reason, cost, cost * savings_factor,
                    {"instance_type": res["instance_type"],
                     "avg_cpu_percent": round(avg_cpu, 2), "lookback_days": days}))
                continue

            reason = rules.rule_stopped_with_volumes(res)
            if reason:
                cost = sum(
                    estimator.ebs_monthly_cost(volumes[v]["size_gb"], volumes[v]["volume_type"])
                    for v in res["volume_ids"] if v in volumes
                )
                findings.append(_finding(res, "stopped", reason, cost, cost,
                                         {"instance_type": res["instance_type"],
                                          "volume_ids": res["volume_ids"]}))
    return findings


SAVINGS_BASIS = {
    "unused": "The full monthly cost is saved by deleting / releasing the resource.",
    "stopped": "The attached volumes' cost is saved by deleting them (or terminating the instance).",
    "underutilized": "Assumes about 50% saving by moving to a smaller instance size.",
}


def _cpu_note(res: dict, avg_cpu: Optional[float], now: datetime, days: int) -> str:
    if avg_cpu is not None:
        return ""
    if res.get("state") != "running":
        return "Instance is not running, so CPU was not checked."
    if not rules.should_check_cpu(res, now, days):
        return f"Instance is younger than {days} days: not enough data for a fair decision."
    return "No CloudWatch CPU data was available."


def build_inventory(resources: List[dict], findings: List[dict],
                    cpu: Dict[str, Optional[float]], now: datetime,
                    threshold: float = settings.cpu_threshold_percent,
                    days: int = settings.lookback_days) -> List[dict]:
    """One item per collected resource (flagged or healthy) for the Resources pages."""
    by_key = {(f["resource_type"], f["resource_id"]): f for f in findings}
    items: List[dict] = []
    for res in resources:
        f = by_key.get((res["resource_type"], res["resource_id"]))
        cost, basis = estimator.base_cost(res)
        common = ("resource_type", "resource_id", "name", "region")
        item = {k: res.get(k, "") for k in common}
        item.update({
            "status": f["status"] if f else "healthy",
            "flagged": bool(f),
            "reason": f["reason"] if f else "No wasteful usage detected by the current rules.",
            "recommendation": f["recommendation"] if f else "No action needed.",
            "monthly_cost": f["monthly_cost"] if f else cost,
            "potential_savings": f["potential_savings"] if f else 0.0,
            "cost_basis": ("Sum of attached EBS volume costs (still billed while stopped)"
                           if f and f["status"] == "stopped" else basis),
            "savings_basis": SAVINGS_BASIS.get(f["status"], "") if f else "",
            "metrics": None,
            "details": {k: v for k, v in res.items() if k not in common},
        })
        if res["resource_type"] == "ec2":
            avg = cpu.get(res["resource_id"])
            item["metrics"] = {
                "avg_cpu_percent": round(avg, 2) if avg is not None else None,
                "lookback_days": days,
                "cpu_threshold_percent": threshold,
                "note": _cpu_note(res, avg, now, days),
            }
        items.append(item)
    return items
