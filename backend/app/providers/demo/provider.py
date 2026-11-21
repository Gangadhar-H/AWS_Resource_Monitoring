"""Demo provider: sample resources so the whole app can be tried WITHOUT any cloud
account. Enable with CLOUD_PROVIDER=demo in .env. It goes through the exact same
rules, cost and storage code as the real AWS provider."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from app.providers.base import CloudProvider

_CPU = {"i-0demo000000000001": 2.3, "i-0demo000000000002": 1.1, "i-0demo000000000003": 46.0}


class DemoProvider(CloudProvider):
    name = "demo"

    def __init__(self, region: str = "ap-south-1"):
        self.region = region

    def collect_resources(self) -> List[Dict]:
        now = datetime.now(timezone.utc)
        old = (now - timedelta(days=60)).isoformat()

        def ec2(i, name, itype, state, vols):
            return {"resource_type": "ec2", "resource_id": i, "name": name, "region": self.region,
                    "instance_type": itype, "state": state, "launch_time": old, "volume_ids": vols}

        def ebs(i, name, size, vtype, state):
            return {"resource_type": "ebs", "resource_id": i, "name": name, "region": self.region,
                    "size_gb": size, "volume_type": vtype, "state": state, "create_time": old,
                    "attached_to": []}

        def eip(i, ip, assoc):
            return {"resource_type": "eip", "resource_id": i, "name": "", "region": self.region,
                    "public_ip": ip, "associated": assoc}

        return [
            ec2("i-0demo000000000001", "dev-server", "t3.medium", "running", ["vol-0demo0000000000a"]),
            ec2("i-0demo000000000002", "test-api", "m5.large", "running", ["vol-0demo0000000000b"]),
            ec2("i-0demo000000000003", "prod-web", "t3.large", "running", ["vol-0demo0000000000c"]),
            ec2("i-0demo000000000004", "old-staging", "t3.small", "stopped", ["vol-0demo0000000000d"]),
            ebs("vol-0demo0000000000a", "", 30, "gp3", "in-use"),
            ebs("vol-0demo0000000000b", "", 50, "gp3", "in-use"),
            ebs("vol-0demo0000000000c", "", 100, "gp3", "in-use"),
            ebs("vol-0demo0000000000d", "", 40, "gp2", "in-use"),
            ebs("vol-0demo0000000000e", "old-db-backup", 200, "gp3", "available"),
            ebs("vol-0demo0000000000f", "", 50, "gp2", "available"),
            eip("eipalloc-0demo00000000001", "13.233.10.21", False),
            eip("eipalloc-0demo00000000002", "13.233.10.22", True),
        ]

    def get_cpu_utilization(self, resource_id: str, days: int) -> Optional[float]:
        return _CPU.get(resource_id)
