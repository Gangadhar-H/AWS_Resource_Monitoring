from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from fastapi import HTTPException


def cloud_error_to_http(e: Exception) -> HTTPException:
    """Translate cloud SDK errors into friendly HTTP errors."""
    if isinstance(e, NoCredentialsError):
        return HTTPException(400, "Cloud credentials not found. Check your .env file (or set CLOUD_PROVIDER=demo).")
    if isinstance(e, ClientError):
        return HTTPException(502, f"Cloud API error: {e.response.get('Error', {}).get('Message', str(e))}")
    return HTTPException(502, f"Cloud connection error: {e}")


CLOUD_ERRORS = (BotoCoreError, ClientError, NoCredentialsError)
