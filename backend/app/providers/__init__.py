from app.config import settings
from app.providers.base import CloudProvider


def get_provider(name: str | None = None) -> CloudProvider:
    name = (name or settings.cloud_provider).lower()
    if name == "aws":
        from app.providers.aws.provider import AwsProvider

        return AwsProvider(region=settings.aws_region, profile=settings.aws_profile)
    if name == "demo":
        from app.providers.demo.provider import DemoProvider

        return DemoProvider(region=settings.aws_region)
    raise ValueError(f"Unsupported cloud provider: {name}")
