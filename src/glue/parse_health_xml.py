"""
AWS Glue Python Shell script for parsing Apple Health exportar.xml.

Streams the XML from S3 using iterparse to maintain O(1) memory usage
regardless of file size. Writes normalized health records to DynamoDB
in batches with exponential backoff.

Arguments (passed via Step Functions):
  --BUCKET: S3 bucket name
  --KEY: S3 object key for the export ZIP
  --USER_ID: User ID for record association
  --JOB_ID: Job ID for tracking
  --TABLE_NAME: DynamoDB table name
"""

import io
import logging
import sys
import time
import xml.etree.ElementTree as ET
import zipfile

import boto3
from botocore.exceptions import ClientError

# Glue job arguments
from awsglue.utils import getResolvedOptions

logger = logging.getLogger("parse_health_xml")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)

BATCH_SIZE = 25
MAX_RETRIES = 5
BASE_BACKOFF_SECONDS = 0.5

HEALTH_RECORD_TYPES = {
    "HKQuantityTypeIdentifierHeartRate",
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN",
    "HKQuantityTypeIdentifierBloodPressureSystolic",
    "HKQuantityTypeIdentifierBloodPressureDiastolic",
    "HKQuantityTypeIdentifierOxygenSaturation",
    "HKQuantityTypeIdentifierRespiratoryRate",
    "HKQuantityTypeIdentifierRestingHeartRate",
    "HKQuantityTypeIdentifierWalkingHeartRateAverage",
    "HKCategoryTypeIdentifierSleepAnalysis",
    "HKQuantityTypeIdentifierStepCount",
    "HKQuantityTypeIdentifierDistanceWalkingRunning",
    "HKQuantityTypeIdentifierActiveEnergyBurned",
    "HKQuantityTypeIdentifierBasalEnergyBurned",
    "HKQuantityTypeIdentifierAppleExerciseTime",
    "HKQuantityTypeIdentifierBodyMass",
    "HKQuantityTypeIdentifierBodyMassIndex",
    "HKQuantityTypeIdentifierBodyTemperature",
}


def main() -> None:
    args = getResolvedOptions(sys.argv, ["BUCKET", "KEY", "USER_ID", "JOB_ID", "TABLE_NAME"])

    bucket = args["BUCKET"]
    key = args["KEY"]
    user_id = args["USER_ID"]
    job_id = args["JOB_ID"]
    table_name = args["TABLE_NAME"]

    logger.info("Starting XML parse: bucket=%s, key=%s, user=%s", bucket, key, user_id)

    s3_client = boto3.client("s3")
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    obj = s3_client.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read()
    zf = zipfile.ZipFile(io.BytesIO(body))

    xml_filename = _find_xml_file(zf)
    if not xml_filename:
        raise ValueError("No exportar.xml or export.xml found in ZIP")

    logger.info("Parsing XML file: %s", xml_filename)

    with zf.open(xml_filename) as xml_file:
        records_written = _stream_parse_and_write(xml_file, user_id, table)

    zf.close()
    logger.info("Completed: %d health records written for user %s", records_written, user_id)


def _find_xml_file(zf: zipfile.ZipFile) -> str | None:
    """Find the main health export XML file in the ZIP."""
    for name in zf.namelist():
        lower = name.lower()
        if lower.endswith("exportar.xml") or lower.endswith("export.xml"):
            return name
    return None


def _stream_parse_and_write(xml_file: io.BufferedReader, user_id: str, table: "boto3.resources.factory.dynamodb.Table") -> int:
    """Stream-parse the XML and batch-write records to DynamoDB."""
    batch: list[dict] = []
    total_written = 0
    records_skipped = 0

    context = ET.iterparse(xml_file, events=("end",))

    for event, elem in context:
        if elem.tag != "Record":
            continue

        record_type = elem.get("type", "")

        if record_type not in HEALTH_RECORD_TYPES:
            records_skipped += 1
            elem.clear()
            continue

        start_date = elem.get("startDate", "")
        value = elem.get("value", "")
        unit = elem.get("unit", "")
        source_name = elem.get("sourceName", "")
        creation_date = elem.get("creationDate", "")

        short_type = record_type.replace("HKQuantityTypeIdentifier", "").replace("HKCategoryTypeIdentifier", "")

        item = {
            "PK": f"USER#{user_id}",
            "SK": f"RECORD#{short_type}#{start_date}",
            "GSI1SK": f"{short_type}#{start_date}",
            "recordType": short_type,
            "value": value,
            "unit": unit,
            "startDate": start_date,
            "creationDate": creation_date,
        }

        batch.append(item)
        elem.clear()

        if len(batch) >= BATCH_SIZE:
            _write_batch(table, batch)
            total_written += len(batch)
            batch = []

            if total_written % 1000 == 0:
                logger.info("Progress: %d records written", total_written)

    if batch:
        _write_batch(table, batch)
        total_written += len(batch)

    logger.info("Skipped %d records of non-tracked types", records_skipped)
    return total_written


def _write_batch(table: "boto3.resources.factory.dynamodb.Table", items: list[dict]) -> None:
    """Write a batch of items to DynamoDB with exponential backoff."""
    with table.batch_writer() as writer:
        for item in items:
            for attempt in range(MAX_RETRIES):
                try:
                    writer.put_item(Item=item)
                    break
                except ClientError as e:
                    if e.response["Error"]["Code"] == "ProvisionedThroughputExceededException":
                        wait_time = BASE_BACKOFF_SECONDS * (2 ** attempt)
                        logger.warning(
                            "Throttled on write, retrying in %.1fs (attempt %d/%d)",
                            wait_time,
                            attempt + 1,
                            MAX_RETRIES,
                        )
                        time.sleep(wait_time)
                    else:
                        raise


if __name__ == "__main__":
    main()
