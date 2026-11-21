from fastapi import APIRouter

from app.database import get_store
from app.utils.helpers import EMPTY_SUMMARY

router = APIRouter(tags=["summary"])


@router.get("/summary")
def get_summary():
    """Totals from the latest scan (zeros if no scan has been run yet)."""
    scan = get_store().latest_scan()
    if not scan:
        return {"scan_id": None, "scanned_at": None, "summary": EMPTY_SUMMARY}
    return {"scan_id": scan["scan_id"], "scanned_at": scan["scanned_at"],
            "provider": scan.get("provider"), "region": scan.get("region"),
            "summary": scan["summary"]}


@router.get("/scans")
def get_scan_history(limit: int = 10):
    """Short history of previous scans."""
    return get_store().list_scans(limit)
