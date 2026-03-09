import io
import os
import zipfile
from typing import Any, Dict, Optional

import boto3

from common import get_logger

logger = get_logger(__name__)
s3_client = boto3.client("s3")

MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024 * 1024  # 2 GB


class _S3SeekableStream:
    """Seekable file-like object backed by S3 byte-range reads.

    Allows zipfile.ZipFile to read the ZIP central directory without
    loading the full file body into memory. Each read issues an S3
    range request for only the bytes requested.
    """

    def __init__(self, s3_client: Any, bucket: str, key: str, file_size: int) -> None:
        self._s3 = s3_client
        self._bucket = bucket
        self._key = key
        self._size = file_size
        self._pos = 0

    def seekable(self) -> bool:
        return True

    def readable(self) -> bool:
        return True

    def seek(self, pos: int, whence: int = 0) -> int:
        if whence == 0:
            self._pos = pos
        elif whence == 1:
            self._pos += pos
        elif whence == 2:
            self._pos = self._size + pos
        self._pos = max(0, min(self._pos, self._size))
        return self._pos

    def tell(self) -> int:
        return self._pos

    def read(self, size: int = -1) -> bytes:
        if self._pos >= self._size:
            return b""
        if size == -1 or size is None:
            end = self._size - 1
        else:
            end = min(self._pos + size - 1, self._size - 1)
        range_header = f"bytes={self._pos}-{end}"
        obj = self._s3.get_object(Bucket=self._bucket, Key=self._key, Range=range_header)
        data: bytes = obj["Body"].read()
        self._pos += len(data)
        return data


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Validate the uploaded export ZIP: size, integrity, and presence of exportar.xml.

    Uses S3 byte-range reads to read only the ZIP central directory —
    never loads the full file body into memory.
    """
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

    stream = _S3SeekableStream(s3_client, bucket, key, file_size)
    try:
        zf = zipfile.ZipFile(stream)  # type: ignore[arg-type]
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
