from typing import Optional

from fastapi import APIRouter

from app.database import get_store

router = APIRouter(tags=["resources"])


@router.get("/resources")
def get_resources(type: Optional[str] = None, status: Optional[str] = None):
    """Flagged resources from the latest scan. Optional filters: ?type=ebs&status=unused"""
    scan = get_store().latest_scan()
    if not scan:
        return {"scan_id": None, "scanned_at": None, "findings": []}
    findings = scan["findings"]
    if type:
        findings = [f for f in findings if f["resource_type"] == type]
    if status:
        findings = [f for f in findings if f["status"] == status]
    return {"scan_id": scan["scan_id"], "scanned_at": scan["scanned_at"], "findings": findings}
