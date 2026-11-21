"""Monthly cost calculations built on the pricing assumptions."""
from __future__ import annotations

from app.cost import pricing


def ec2_monthly_cost(instance_type: str) -> float:
    hourly = pricing.EC2_HOURLY.get(instance_type, pricing.EC2_DEFAULT_HOURLY)
    return round(hourly * pricing.HOURS_PER_MONTH, 2)


def ebs_monthly_cost(size_gb: float, volume_type: str) -> float:
    rate = pricing.EBS_GB_MONTH.get(volume_type, pricing.EBS_DEFAULT_GB_MONTH)
    return round(size_gb * rate, 2)


def eip_monthly_cost() -> float:
    return round(pricing.EIP_HOURLY * pricing.HOURS_PER_MONTH, 2)


def base_cost(res: dict):
    """(monthly_cost, human-readable basis) for ANY resource, flagged or not."""
    t = res["resource_type"]
    if t == "ec2":
        if res.get("state") != "running":
            return 0.0, "Not running: no compute charge (attached volumes are billed separately)"
        itype = res.get("instance_type", "unknown")
        known = itype in pricing.EC2_HOURLY
        hourly = pricing.EC2_HOURLY.get(itype, pricing.EC2_DEFAULT_HOURLY)
        basis = f"{itype} x ${hourly}/hr x {pricing.HOURS_PER_MONTH} hrs"
        if not known:
            basis += " (default rate: instance type not in price table)"
        return ec2_monthly_cost(itype), basis
    if t == "ebs":
        rate = pricing.EBS_GB_MONTH.get(res.get("volume_type"), pricing.EBS_DEFAULT_GB_MONTH)
        return (ebs_monthly_cost(res["size_gb"], res.get("volume_type")),
                f"{res['size_gb']} GB x ${rate}/GB-month ({res.get('volume_type')})")
    if t == "eip":
        return (eip_monthly_cost(),
                f"${pricing.EIP_HOURLY}/hr x {pricing.HOURS_PER_MONTH} hrs (public IPv4 addresses are billed)")
    return 0.0, "No pricing available for this resource type"
