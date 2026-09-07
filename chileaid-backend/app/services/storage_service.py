import os

import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, status

_s3_client = None


def _get_client():
    """Builds the boto3 client lazily, on first actual use.

    Building it at import time crashed the whole backend (ValueError: Invalid
    endpoint) whenever S3_* env vars were unset, even for requests that never
    touch storage.
    """
    global _s3_client
    if _s3_client is None:
        endpoint_url = os.getenv("S3_ENDPOINT_URL")
        if not endpoint_url or not os.getenv("S3_BUCKET_NAME"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Almacenamiento de documentos no configurado (faltan variables S3_*).",
            )
        _s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=os.getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("S3_SECRET_KEY"),
            region_name=os.getenv("S3_REGION", "hel1"),
        )
    return _s3_client


def generate_presigned_upload_url(object_name: str, expiration=3600):
    """Generates a URL the Nuxt frontend can use to upload a document directly to Hetzner."""
    try:
        response = _get_client().generate_presigned_post(
            os.getenv("S3_BUCKET_NAME"),
            object_name,
            Fields=None,
            Conditions=None,
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        print(e)
        return None

def generate_presigned_download_url(object_name: str, expiration=3600):
    """Generates a URL to read/download a private document."""
    try:
        response = _get_client().generate_presigned_url(
            'get_object',
            Params={'Bucket': os.getenv("S3_BUCKET_NAME"), 'Key': object_name},
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        print(e)
        return None