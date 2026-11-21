"""End-to-end scan against mocked AWS (no real account needed)."""
import os

import pytest

moto = pytest.importorskip("moto")
import boto3  # noqa: E402
from moto import mock_aws  # noqa: E402

os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")

from app.database import JsonStore  # noqa: E402
from app.providers.aws.provider import AwsProvider  # noqa: E402
from app.services.scan_service import run_scan  # noqa: E402


@mock_aws
def test_scan_detects_wasted_resources(tmp_path):
    ec2 = boto3.client("ec2", region_name="us-east-1")
    ec2.create_volume(AvailabilityZone="us-east-1a", Size=100, VolumeType="gp3")
    ec2.create_volume(AvailabilityZone="us-east-1a", Size=20, VolumeType="gp2")
    ec2.allocate_address(Domain="vpc")

    store = JsonStore(str(tmp_path / "scans.json"))
    scan = run_scan(provider=AwsProvider(region="us-east-1"), store=store)

    kinds = [f["resource_type"] for f in scan["findings"]]
    assert kinds.count("ebs") == 2 and kinds.count("eip") == 1
    assert scan["summary"]["flagged_count"] == 3
    assert scan["summary"]["estimated_monthly_waste"] == round(8.0 + 2.0 + 3.65, 2)
    assert store.latest_scan()["scan_id"] == scan["scan_id"]
