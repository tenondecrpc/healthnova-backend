import io
import zipfile
from typing import Any, Dict, List

import boto3

from common import get_logger

logger = get_logger(__name__)
s3_client = boto3.client("s3")


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """List files inside the ZIP and categorize them for downstream processing."""
    bucket = event["bucket"]
    key = event["key"]
    user_id = event["userId"]
    job_id = event["jobId"]

    logger.info("Extracting manifest: bucket=%s, key=%s", bucket, key)

    obj = s3_client.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read()
    zf = zipfile.ZipFile(io.BytesIO(body))

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
