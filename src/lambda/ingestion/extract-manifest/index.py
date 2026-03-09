import io
import os
import zipfile
from typing import Any, Dict, List

import boto3

from common import get_logger

logger = get_logger(__name__)
s3_client = boto3.client("s3")


class _S3SeekableStream:
    """Seekable file-like object backed by S3 byte-range reads.

    Allows zipfile.ZipFile to read the ZIP central directory without
    loading the full file body into memory.
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
    """List files inside the ZIP and categorize them for downstream processing.

    Uses S3 byte-range reads to enumerate file names from the ZIP central
    directory without loading the full file body into memory.
    """
    bucket = event["bucket"]
    key = event["key"]
    user_id = event["userId"]
    job_id = event["jobId"]

    logger.info("Extracting manifest: bucket=%s, key=%s", bucket, key)

    head = s3_client.head_object(Bucket=bucket, Key=key)
    file_size = head["ContentLength"]

    stream = _S3SeekableStream(s3_client, bucket, key, file_size)
    zf = zipfile.ZipFile(stream)  # type: ignore[arg-type]
    names = zf.namelist()
    zf.close()

    xml_files: List[str] = []
    ecg_files: List[str] = []
    gpx_files: List[str] = []

    for name in names:
        lower = name.lower()
        if lower.endswith("exportar.xml") or lower.endswith("export.xml"):
            xml_files.append(name)
        elif "electrocardiograms" in lower and lower.endswith(".csv"):
            ecg_files.append(name)
        elif "workout-routes" in lower and lower.endswith(".gpx"):
            gpx_files.append(name)

    logger.info(
        "Manifest: %d XML, %d ECG, %d GPX files",
        len(xml_files),
        len(ecg_files),
        len(gpx_files),
    )

    return {
        "bucket": bucket,
        "key": key,
        "userId": user_id,
        "jobId": job_id,
        "xmlFiles": xml_files,
        "ecgFiles": ecg_files,
        "gpxFiles": gpx_files,
        "status": "PROCESSING",
    }
