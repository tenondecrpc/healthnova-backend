"""
AWS Glue Python Shell script for parsing Apple Health exportar.xml.

Streams the XML from S3 using iterparse to maintain O(1) memory usage
regardless of file size. Writes normalized health records to DynamoDB
using parallel batch writers for throughput.

Arguments (passed via Step Functions):
  --BUCKET: S3 bucket name
  --KEY: S3 object key for the export ZIP
  --USER_ID: User ID for record association
  --JOB_ID: Job ID for tracking
  --TABLE_NAME: DynamoDB table name
"""

from __future__ import annotations

import io
import logging
import sys
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

import boto3

# Glue job arguments
from awsglue.utils import getResolvedOptions

logger = logging.getLogger("parse_health_xml")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)

WRITE_CHUNK_SIZE = 1000
WRITE_WORKERS = 8

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
    "HKQuantityTypeIdentifierPhysicalEffort",
    "HKQuantityTypeIdentifierRunningPower",
    "HKQuantityTypeIdentifierRunningSpeed",
    "HKQuantityTypeIdentifierRunningStrideLength",
    "HKQuantityTypeIdentifierRunningVerticalOscillation",
    "HKQuantityTypeIdentifierRunningGroundContactTime",
    "HKQuantityTypeIdentifierEnvironmentalAudioExposure",
    "HKQuantityTypeIdentifierHeadphoneAudioExposure",
    "HKQuantityTypeIdentifierVO2Max",
    "HKQuantityTypeIdentifierWalkingSpeed",
    "HKQuantityTypeIdentifierWalkingStepLength",
    "HKQuantityTypeIdentifierWalkingAsymmetryPercentage",
    "HKQuantityTypeIdentifierWalkingDoubleSupportPercentage",
    "HKQuantityTypeIdentifierStairAscentSpeed",
    "HKQuantityTypeIdentifierStairDescentSpeed",
    "HKQuantityTypeIdentifierSixMinuteWalkTestDistance",
    "HKQuantityTypeIdentifierAppleWalkingSteadiness",
    "HKQuantityTypeIdentifierFlightsClimbed",
    "HKQuantityTypeIdentifierDistanceCycling",
    "HKQuantityTypeIdentifierDistanceSwimming",
    "HKQuantityTypeIdentifierSwimmingStrokeCount",
    "HKQuantityTypeIdentifierHeight",
    "HKQuantityTypeIdentifierLeanBodyMass",
    "HKQuantityTypeIdentifierBodyFatPercentage",
    "HKQuantityTypeIdentifierBloodGlucose",
    "HKQuantityTypeIdentifierInsulinDelivery",
    "HKQuantityTypeIdentifierDietaryEnergyConsumed",
    "HKQuantityTypeIdentifierDietaryCarbohydrates",
    "HKQuantityTypeIdentifierDietaryFatTotal",
    "HKQuantityTypeIdentifierDietaryProtein",
    "HKQuantityTypeIdentifierDietaryWater",
    "HKQuantityTypeIdentifierUVExposure",
    "HKQuantityTypeIdentifierTimeInDaylight",
    "HKCategoryTypeIdentifierMindfulSession",
    "HKCategoryTypeIdentifierHighHeartRateEvent",
    "HKCategoryTypeIdentifierLowHeartRateEvent",
    "HKCategoryTypeIdentifierIrregularHeartRhythmEvent",
    "HKCategoryTypeIdentifierAppleWalkingSteadinessEvent",
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
    """Stream-parse the XML and write records to DynamoDB with parallel batch writers."""
    seen_keys: set = set()
    total_written = 0
    records_skipped = 0
    duplicates_skipped = 0
    chunk: list[dict] = []

    context = ET.iterparse(xml_file, events=("end",))
    executor = ThreadPoolExecutor(max_workers=WRITE_WORKERS)
    futures = []

    for event, elem in context:
        if elem.tag != "Record":
            elem.clear()
            continue

        record_type = elem.get("type", "")

        if record_type not in HEALTH_RECORD_TYPES:
            records_skipped += 1
            elem.clear()
            continue

        start_date = elem.get("startDate", "")
        short_type = record_type.replace("HKQuantityTypeIdentifier", "").replace("HKCategoryTypeIdentifier", "")
        sk = f"RECORD#{short_type}#{start_date}"
        key = f"USER#{user_id}|{sk}"

        if key in seen_keys:
            duplicates_skipped += 1
            elem.clear()
            continue
        seen_keys.add(key)

        chunk.append({
            "PK": f"USER#{user_id}",
            "SK": sk,
            "GSI1SK": f"{short_type}#{start_date}",
            "recordType": short_type,
            "value": elem.get("value", ""),
            "unit": elem.get("unit", ""),
            "startDate": start_date,
            "creationDate": elem.get("creationDate", ""),
        })
        elem.clear()

        if len(chunk) >= WRITE_CHUNK_SIZE:
            futures.append(executor.submit(_write_chunk, table, chunk))
            total_written += len(chunk)
            chunk = []

            if total_written % 10000 == 0:
                logger.info("Progress: %d records written", total_written)

    if chunk:
        futures.append(executor.submit(_write_chunk, table, chunk))
        total_written += len(chunk)

    for future in as_completed(futures):
        future.result()

    executor.shutdown(wait=True)

    logger.info("Skipped %d non-tracked, %d duplicates", records_skipped, duplicates_skipped)
    return total_written


def _write_chunk(table: "boto3.resources.factory.dynamodb.Table", items: list[dict]) -> None:
    """Write a chunk of items to DynamoDB using batch_writer."""
    with table.batch_writer(overwrite_by_pkeys=["PK", "SK"]) as writer:
        for item in items:
            writer.put_item(Item=item)


if __name__ == "__main__":
    main()
