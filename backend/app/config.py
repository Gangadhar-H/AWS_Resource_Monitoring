"""Central configuration, read from environment variables / .env file."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()


def _split(value: str) -> List[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


@dataclass(frozen=True)
class Settings:
    cloud_provider: str = os.getenv("CLOUD_PROVIDER", "aws")
    aws_region: str = os.getenv("AWS_REGION", "ap-south-1")
    aws_profile: Optional[str] = os.getenv("AWS_PROFILE") or None

    # Rule thresholds
    cpu_threshold_percent: float = float(os.getenv("CPU_THRESHOLD_PERCENT", "5"))
    lookback_days: int = int(os.getenv("LOOKBACK_DAYS", "14"))
    underutilized_savings_factor: float = float(
        os.getenv("UNDERUTILIZED_SAVINGS_FACTOR", "0.5")
    )

    # Storage
    mongo_uri: Optional[str] = os.getenv("MONGO_URI") or None
    mongo_db: str = os.getenv("MONGO_DB", "cloud_cost_monitor")
    data_file: str = os.getenv("DATA_FILE", "data/scans.json")

    cors_origins: List[str] = field(
        default_factory=lambda: _split(
            os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000")
        )
    )


settings = Settings()
