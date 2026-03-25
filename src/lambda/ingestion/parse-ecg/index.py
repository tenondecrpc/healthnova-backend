import csv
import io
import os
import time
import zipfile
from typing import Any, Dict, List

import boto3

from common import get_logger

logger = get_logger(__name__)
dynamodb = boto3.resource("dynamodb")
s3_client = boto3.client("s3")
table_name = os.environ.get("HEALTH_RECORDS_TABLE_NAME", "")
table = dynamodb.Table(table_name)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Parse ECG CSV files from the export ZIP and write records to DynamoDB."""
    bucket = event["bucket"]
    key = event["key"]
    user_id = event["userId"]
    ecg_files: List[str] = event.get("ecgFiles", [])

    if not ecg_files:
        logger.info("No ECG files to process")
        return {"userId": user_id, "ecgRecordCount": 0}

    logger.info("Processing %d ECG files", len(ecg_files))

    obj = s3_client.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read()
    zf = zipfile.ZipFile(io.BytesIO(body))

    total_records = 0

    with table.batch_writer() as batch:
        for ecg_file in ecg_files:
            try:
                with zf.open(ecg_file) as f:
                    content = f.read().decode("utf-8")
                    reader = csv.DictReader(io.StringIO(content))
                    for row in reader:
                        timestamp = row.get("Date", str(int(time.time())))
                        item = {
                            "PK": f"USER#{user_id}",
                            "SK": f"RECORD#ECG#{timestamp}#{total_records}",
                            "recordType": "ECG",
                            "sourceFile": ecg_file,
                            "classification": row.get("Classification", ""),
                            "averageHeartRate": row.get("Average Heart Rate (bpm)", ""),
                            "createdAt": str(int(time.time())),
                        }
                        batch.put_item(Item=item)
                        total_records += 1
            except Exception as e:
                logger.error("Error parsing ECG file %s: %s", ecg_file, str(e))

    zf.close()
    logger.info("Processed %d ECG records", total_records)

    return {"userId": user_id, "ecgRecordCount": total_records}
