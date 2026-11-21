"""Pydantic response models (also serve as the API contract for the frontend)."""
from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel


class Finding(BaseModel):
    resource_type: str          # ec2 | ebs | eip
    resource_id: str
    name: str = ""
    region: str = ""
    status: str                 # underutilized | unused | stopped
    reason: str
    monthly_cost: float
    potential_savings: float
    recommendation: str
    details: dict = {}


class TypeBreakdown(BaseModel):
    count: int = 0
    monthly_cost: float = 0.0
    potential_savings: float = 0.0


class Summary(BaseModel):
    total_resources_scanned: int = 0
    scanned_by_type: Dict[str, int] = {}
    flagged_count: int = 0
    estimated_monthly_spend: float = 0.0
    estimated_monthly_waste: float = 0.0
    potential_monthly_savings: float = 0.0
    by_type: Dict[str, TypeBreakdown] = {}
    by_status: Dict[str, int] = {}


class ScanResult(BaseModel):
    scan_id: str
    scanned_at: Optional[str] = None
    provider: str = ""
    region: str = ""
    summary: Summary = Summary()
    findings: List[Finding] = []
    inventory: List[dict] = []
