from __future__ import annotations

from typing import Dict, List, Optional

from app.providers.base import CloudProvider
from app.providers.aws import client, collector, metrics


class AwsProvider(CloudProvider):
    name = "aws"

    def __init__(self, region: str, profile: Optional[str] = None):
        self.region = region
        session = client.get_session(region, profile)
        self._ec2 = client.get_ec2_client(session)
        self._cw = client.get_cloudwatch_client(session)

    def collect_resources(self) -> List[Dict]:
        return (
            collector.collect_instances(self._ec2, self.region)
            + collector.collect_volumes(self._ec2, self.region)
            + collector.collect_elastic_ips(self._ec2, self.region)
        )

    def get_cpu_utilization(self, resource_id: str, days: int) -> Optional[float]:
        return metrics.get_average_cpu(self._cw, resource_id, days)
