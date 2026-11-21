"""Boto3 session / client factory. Credentials come from the standard AWS chain
(.env variables, ~/.aws/credentials, or an IAM role)."""
from __future__ import annotations

from typing import Optional

import boto3


def get_session(region: str, profile: Optional[str] = None) -> boto3.Session:
    if profile:
        return boto3.Session(profile_name=profile, region_name=region)
    return boto3.Session(region_name=region)


def get_ec2_client(session: boto3.Session):
    return session.client("ec2")


def get_cloudwatch_client(session: boto3.Session):
    return session.client("cloudwatch")
