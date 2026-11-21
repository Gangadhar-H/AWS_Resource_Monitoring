"""The MVP detection rules. Each rule returns a reason string if the resource is
flagged, otherwise None. Pure functions: easy to unit test."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional


def _parse(ts: str) -> datetime:
    return datetime.fromisoformat(ts)


def should_check_cpu(instance: dict, now: datetime, days: int) -> bool:
    """Only running instances that existed for the whole lookback window have
    enough CloudWatch history for a fair decision."""
    if instance.get("state") != "running":
        return False
    return now - _parse(instance["launch_time"]) >= timedelta(days=days)


def rule_low_cpu(instance: dict, avg_cpu: Optional[float], threshold: float, days: int) -> Optional[str]:
    if instance.get("state") != "running" or avg_cpu is None:
        return None
    if avg_cpu < threshold:
        return f"Average CPU {avg_cpu:.2f}% over {days} days (below {threshold:g}% threshold)"
    return None


def rule_stopped_with_volumes(instance: dict) -> Optional[str]:
    if instance.get("state") == "stopped" and instance.get("volume_ids"):
        return "Instance is stopped but its attached EBS volumes are still billed"
    return None


def rule_unattached_volume(volume: dict) -> Optional[str]:
    if volume.get("state") == "available":
        return "Volume is not attached to any instance"
    return None


def rule_unassociated_eip(eip: dict) -> Optional[str]:
    if not eip.get("associated"):
        return "Elastic IP is not associated with any resource"
    return None
