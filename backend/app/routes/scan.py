from fastapi import APIRouter

from app.models.schemas import ScanResult
from app.services.scan_service import run_scan
from app.utils.errors import CLOUD_ERRORS, cloud_error_to_http

router = APIRouter(tags=["scan"])


@router.post("/scan", response_model=ScanResult)
def trigger_scan():
    """Run a fresh read-only scan of the cloud account and store the result."""
    try:
        return run_scan()
    except CLOUD_ERRORS as e:
        raise cloud_error_to_http(e)
