"""CloudWatch metric helpers."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional


def get_average_cpu(cloudwatch, instance_id: str, days: int) -> Optional[float]:
    """Mean of daily average CPUUtilization over `days`. None if no datapoints."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    resp = cloudwatch.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
        StartTime=start,
        EndTime=end,
        Period=86400,  # one datapoint per day
        Statistics=["Average"],
    )
    points = resp.get("Datapoints", [])
    if not points:
        return None
    return sum(p["Average"] for p in points) / len(points)
