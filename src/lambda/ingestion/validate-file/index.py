import io
import zipfile
from typing import Any, Dict

import boto3

from common import get_logger

logger = get_logger(__name__)
s3_client = boto3.client("s3")

MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024 * 1024  # 2 GB


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Validate the uploaded export ZIP: integrity, size, and presence of exportar.xml."""
    bucket = event["bucket"]
    key = event["key"]
    user_id = event["userId"]
    job_id = event.get("jobId", key)

    logger.info("Validating file: bucket=%s, key=%s", bucket, key)

    head = s3_client.head_object(Bucket=bucket, Key=key)
    file_size = head["ContentLength"]

    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"File exceeds maximum allowed size of 2GB (actual: {file_size} bytes)"
        )

    logger.info("File size: %d bytes", file_size)

    obj = s3_client.get_object(Bucket=bucket, Key=key)
    body_stream = obj["Body"].read()

    try:
        zf = zipfile.ZipFile(io.BytesIO(body_stream))
    except zipfile.BadZipFile:
        raise ValueError("File is not a valid ZIP archive")

    names = zf.namelist()
    has_export_xml = any(
        name.endswith("exportar.xml") or name.endswith("export.xml") for name in names
    )

    if not has_export_xml:
        raise ValueError("ZIP does not contain exportar.xml or export.xml")

    zf.close()

    logger.info("Validation passed: %d files in archive", len(names))

    return {
        "bucket": bucket,
        "key": key,
        "userId": user_id,
        "jobId": job_id,
        "fileCount": len(names),
        "fileSizeBytes": file_size,
        "status": "VALIDATED",
    }
