"""Read-only collectors for EC2 instances, EBS volumes and Elastic IPs.
Each function returns plain, JSON-serialisable dicts."""
from __future__ import annotations

from typing import Dict, List


def _name_from_tags(tags) -> str:
    for t in tags or []:
        if t.get("Key") == "Name":
            return t.get("Value", "")
    return ""


def collect_instances(ec2, region: str) -> List[Dict]:
    out: List[Dict] = []
    for page in ec2.get_paginator("describe_instances").paginate():
        for reservation in page["Reservations"]:
            for i in reservation["Instances"]:
                state = i["State"]["Name"]
                if state in ("terminated", "shutting-down"):
                    continue
                out.append(
                    {
                        "resource_type": "ec2",
                        "resource_id": i["InstanceId"],
                        "name": _name_from_tags(i.get("Tags")),
                        "region": region,
                        "instance_type": i.get("InstanceType", "unknown"),
                        "state": state,
                        "launch_time": i["LaunchTime"].isoformat(),
                        "availability_zone": i.get("Placement", {}).get("AvailabilityZone"),
                        "public_ip": i.get("PublicIpAddress"),
                        "private_ip": i.get("PrivateIpAddress"),
                        "volume_ids": [
                            m["Ebs"]["VolumeId"]
                            for m in i.get("BlockDeviceMappings", [])
                            if "Ebs" in m
                        ],
                    }
                )
    return out


def collect_volumes(ec2, region: str) -> List[Dict]:
    out: List[Dict] = []
    for page in ec2.get_paginator("describe_volumes").paginate():
        for v in page["Volumes"]:
            out.append(
                {
                    "resource_type": "ebs",
                    "resource_id": v["VolumeId"],
                    "name": _name_from_tags(v.get("Tags")),
                    "region": region,
                    "size_gb": v["Size"],
                    "volume_type": v.get("VolumeType", "gp2"),
                    "state": v["State"],  # "available" == not attached
                    "create_time": v["CreateTime"].isoformat(),
                    "availability_zone": v.get("AvailabilityZone"),
                    "encrypted": v.get("Encrypted"),
                    "iops": v.get("Iops"),
                    "attached_to": [a["InstanceId"] for a in v.get("Attachments", [])],
                }
            )
    return out


def collect_elastic_ips(ec2, region: str) -> List[Dict]:
    out: List[Dict] = []
    for a in ec2.describe_addresses().get("Addresses", []):
        out.append(
            {
                "resource_type": "eip",
                "resource_id": a.get("AllocationId") or a["PublicIp"],
                "name": _name_from_tags(a.get("Tags")),
                "region": region,
                "public_ip": a["PublicIp"],
                "associated": bool(a.get("AssociationId") or a.get("InstanceId")),
                "instance_id": a.get("InstanceId"),
                "domain": a.get("Domain"),
            }
        )
    return out
