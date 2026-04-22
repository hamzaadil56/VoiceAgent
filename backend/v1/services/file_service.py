"""File upload service with S3-compatible storage.

Uses local filesystem by default. Set S3_BUCKET, AWS_ACCESS_KEY_ID,
AWS_SECRET_ACCESS_KEY, and S3_ENDPOINT_URL for S3/R2 storage.
"""

from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/talkforms_uploads")
S3_BUCKET = os.getenv("S3_BUCKET", "")
S3_ENDPOINT_URL = os.getenv("S3_ENDPOINT_URL", "")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024


def get_upload_path(form_id: str, session_id: str, filename: str) -> str:
    ext = Path(filename).suffix
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return f"uploads/{form_id}/{session_id}/{unique_name}"


async def save_file_local(path: str, content: bytes) -> str:
    full_path = os.path.join(UPLOAD_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "wb") as f:
        f.write(content)
    return full_path


async def save_file_s3(path: str, content: bytes, content_type: str) -> str:
    """Upload to S3/R2 and return the storage path."""
    try:
        import boto3

        s3_kwargs = {}
        if S3_ENDPOINT_URL:
            s3_kwargs["endpoint_url"] = S3_ENDPOINT_URL

        s3 = boto3.client("s3", **s3_kwargs)
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=path,
            Body=content,
            ContentType=content_type,
        )
        return f"s3://{S3_BUCKET}/{path}"
    except ImportError:
        logger.warning("boto3 not installed, falling back to local storage")
        return await save_file_local(path, content)
    except Exception as exc:
        logger.exception("S3 upload failed: %s", exc)
        return await save_file_local(path, content)


async def save_file(
    form_id: str,
    session_id: str,
    filename: str,
    content: bytes,
    content_type: str = "application/octet-stream",
) -> str:
    if len(content) > MAX_FILE_SIZE:
        raise ValueError(f"File exceeds maximum size of {MAX_FILE_SIZE // (1024*1024)}MB")

    path = get_upload_path(form_id, session_id, filename)

    if S3_BUCKET:
        return await save_file_s3(path, content, content_type)
    return await save_file_local(path, content)


async def generate_presigned_upload_url(
    form_id: str, session_id: str, filename: str, content_type: str
) -> dict:
    """Generate a presigned URL for direct client upload to S3."""
    if not S3_BUCKET:
        return {"method": "direct", "upload_url": f"/v1/public/sessions/{session_id}/upload"}

    try:
        import boto3

        s3_kwargs = {}
        if S3_ENDPOINT_URL:
            s3_kwargs["endpoint_url"] = S3_ENDPOINT_URL

        s3 = boto3.client("s3", **s3_kwargs)
        path = get_upload_path(form_id, session_id, filename)

        url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": S3_BUCKET,
                "Key": path,
                "ContentType": content_type,
            },
            ExpiresIn=3600,
        )
        return {"method": "presigned", "upload_url": url, "storage_path": path}
    except ImportError:
        return {"method": "direct", "upload_url": f"/v1/public/sessions/{session_id}/upload"}
