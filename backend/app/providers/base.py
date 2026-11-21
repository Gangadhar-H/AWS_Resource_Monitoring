"""Provider interface. Implement this to add Azure / GCP later.

Every resource returned by collect_resources() is a plain dict with at least:
    resource_type: "ec2" | "ebs" | "eip"   (generic: vm | volume | public_ip)
    resource_id:   str
    name:          str
    region:        str
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class CloudProvider(ABC):
    name: str = "base"
    region: str = ""

    @abstractmethod
    def collect_resources(self) -> List[Dict]:
        """Return all VMs, volumes and public IPs in the account/region."""

    @abstractmethod
    def get_cpu_utilization(self, resource_id: str, days: int) -> Optional[float]:
        """Average CPU % over the last `days` days, or None if no data."""
