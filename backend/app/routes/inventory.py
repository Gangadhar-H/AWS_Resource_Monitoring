"""Every resource found in the latest scan (flagged or healthy) + per-resource scan."""
from collections import Counter
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.database import get_store
from app.services.scan_service import ResourceNotFound, rescan_resource
from app.utils.errors import CLOUD_ERRORS, cloud_error_to_http

router = APIRouter(tags=["inventory"])


def _matches(item: dict, q: str) -> bool:
    q = q.lower()
    haystack = [item["resource_id"], item.get("name", ""), str(item["details"].get("public_ip") or "")]
    return any(q in (h or "").lower() for h in haystack)


@router.get("/inventory")
def list_inventory(type: Optional[str] = None, status: Optional[str] = None, q: Optional[str] = None):
    """All resources from the latest scan. Filters: ?type=ec2&status=unused&q=text"""
    scan = get_store().latest_scan() or {}
    items = scan.get("inventory", [])
    counts = dict(Counter(i["resource_type"] for i in items))
    if type:
        items = [i for i in items if i["resource_type"] == type]
    if status:
        items = [i for i in items if i["status"] == status]
    if q:
        items = [i for i in items if _matches(i, q)]
    return {"scan_id": scan.get("scan_id"), "scanned_at": scan.get("scanned_at"),
            "counts_by_type": counts, "total": len(items), "items": items}


@router.get("/inventory/{resource_type}/{resource_id}")
def get_resource(resource_type: str, resource_id: str):
    scan = get_store().latest_scan() or {}
    for i in scan.get("inventory", []):
        if i["resource_type"] == resource_type and i["resource_id"] == resource_id:
            return {"scan_id": scan["scan_id"], "scanned_at": scan["scanned_at"], "item": i}
    raise HTTPException(404, "Resource not found in the latest scan. Run a scan first.")


@router.post("/inventory/{resource_type}/{resource_id}/scan")
def scan_resource(resource_type: str, resource_id: str):
    """Re-check a single resource and return its updated details and savings."""
    try:
        scan, item = rescan_resource(resource_type, resource_id)
    except ResourceNotFound as e:
        raise HTTPException(404, str(e))
    except CLOUD_ERRORS as e:
        raise cloud_error_to_http(e)
    return {"scan_id": scan["scan_id"], "scanned_at": scan["scanned_at"], "item": item}
