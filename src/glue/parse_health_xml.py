"""
AWS Glue Python Shell script for parsing Apple Health exportar.xml.

Streams the XML from S3 using lxml iterparse for fast O(1) memory parsing.
Writes normalized health records to DynamoDB using parallel batch writers.

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
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

from lxml import etree

import boto3

# Glue job arguments
from awsglue.utils import getResolvedOptions

logger = logging.getLogger("parse_health_xml")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)

WRITE_CHUNK_SIZE = 2500
WRITE_WORKERS = 16

HEALTH_RECORD_TYPES = {
    "HKQuantityTypeIdentifierHeartRate": "HeartRate",
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": "HeartRateVariabilitySDNN",
    "HKQuantityTypeIdentifierBloodPressureSystolic": "BloodPressureSystolic",
    "HKQuantityTypeIdentifierBloodPressureDiastolic": "BloodPressureDiastolic",
    "HKQuantityTypeIdentifierOxygenSaturation": "OxygenSaturation",
    "HKQuantityTypeIdentifierRespiratoryRate": "RespiratoryRate",
    "HKQuantityTypeIdentifierRestingHeartRate": "RestingHeartRate",
    "HKQuantityTypeIdentifierWalkingHeartRateAverage": "WalkingHeartRateAverage",
    "HKCategoryTypeIdentifierSleepAnalysis": "SleepAnalysis",
    "HKQuantityTypeIdentifierStepCount": "StepCount",
    "HKQuantityTypeIdentifierDistanceWalkingRunning": "DistanceWalkingRunning",
    "HKQuantityTypeIdentifierActiveEnergyBurned": "ActiveEnergyBurned",
    "HKQuantityTypeIdentifierBasalEnergyBurned": "BasalEnergyBurned",
    "HKQuantityTypeIdentifierAppleExerciseTime": "AppleExerciseTime",
    "HKQuantityTypeIdentifierBodyMass": "BodyMass",
    "HKQuantityTypeIdentifierBodyMassIndex": "BodyMassIndex",
    "HKQuantityTypeIdentifierBodyTemperature": "BodyTemperature",
    "HKQuantityTypeIdentifierPhysicalEffort": "PhysicalEffort",
    "HKQuantityTypeIdentifierRunningPower": "RunningPower",
    "HKQuantityTypeIdentifierRunningSpeed": "RunningSpeed",
    "HKQuantityTypeIdentifierRunningStrideLength": "RunningStrideLength",
    "HKQuantityTypeIdentifierRunningVerticalOscillation": "RunningVerticalOscillation",
    "HKQuantityTypeIdentifierRunningGroundContactTime": "RunningGroundContactTime",
    "HKQuantityTypeIdentifierEnvironmentalAudioExposure": "EnvironmentalAudioExposure",
    "HKQuantityTypeIdentifierHeadphoneAudioExposure": "HeadphoneAudioExposure",
    "HKQuantityTypeIdentifierVO2Max": "VO2Max",
    "HKQuantityTypeIdentifierWalkingSpeed": "WalkingSpeed",
    "HKQuantityTypeIdentifierWalkingStepLength": "WalkingStepLength",
    "HKQuantityTypeIdentifierWalkingAsymmetryPercentage": "WalkingAsymmetryPercentage",
    "HKQuantityTypeIdentifierWalkingDoubleSupportPercentage": "WalkingDoubleSupportPercentage",
    "HKQuantityTypeIdentifierStairAscentSpeed": "StairAscentSpeed",
    "HKQuantityTypeIdentifierStairDescentSpeed": "StairDescentSpeed",
    "HKQuantityTypeIdentifierSixMinuteWalkTestDistance": "SixMinuteWalkTestDistance",
    "HKQuantityTypeIdentifierAppleWalkingSteadiness": "AppleWalkingSteadiness",
    "HKQuantityTypeIdentifierFlightsClimbed": "FlightsClimbed",
    "HKQuantityTypeIdentifierDistanceCycling": "DistanceCycling",
    "HKQuantityTypeIdentifierDistanceSwimming": "DistanceSwimming",
    "HKQuantityTypeIdentifierSwimmingStrokeCount": "SwimmingStrokeCount",
    "HKQuantityTypeIdentifierHeight": "Height",
    "HKQuantityTypeIdentifierLeanBodyMass": "LeanBodyMass",
    "HKQuantityTypeIdentifierBodyFatPercentage": "BodyFatPercentage",
    "HKQuantityTypeIdentifierBloodGlucose": "BloodGlucose",
    "HKQuantityTypeIdentifierInsulinDelivery": "InsulinDelivery",
    "HKQuantityTypeIdentifierDietaryEnergyConsumed": "DietaryEnergyConsumed",
    "HKQuantityTypeIdentifierDietaryCarbohydrates": "DietaryCarbohydrates",
    "HKQuantityTypeIdentifierDietaryFatTotal": "DietaryFatTotal",
    "HKQuantityTypeIdentifierDietaryProtein": "DietaryProtein",
    "HKQuantityTypeIdentifierDietaryWater": "DietaryWater",
    "HKQuantityTypeIdentifierUVExposure": "UVExposure",
    "HKQuantityTypeIdentifierTimeInDaylight": "TimeInDaylight",
    "HKCategoryTypeIdentifierMindfulSession": "MindfulSession",
    "HKCategoryTypeIdentifierHighHeartRateEvent": "HighHeartRateEvent",
    "HKCategoryTypeIdentifierLowHeartRateEvent": "LowHeartRateEvent",
    "HKCategoryTypeIdentifierIrregularHeartRhythmEvent": "IrregularHeartRhythmEvent",
    "HKCategoryTypeIdentifierAppleWalkingSteadinessEvent": "AppleWalkingSteadinessEvent",
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
    """Stream-parse the XML with lxml and write records to DynamoDB with parallel batch writers."""
    total_written = 0
    records_skipped = 0
    chunk: list[dict] = []
    pk = f"USER#{user_id}"

    context = etree.iterparse(xml_file, events=("end",), tag="Record")
    executor = ThreadPoolExecutor(max_workers=WRITE_WORKERS)
    futures = []

    for _, elem in context:
        record_type = elem.get("type", "")
        short_type = HEALTH_RECORD_TYPES.get(record_type)

        if short_type is None:
            records_skipped += 1
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
            continue

        start_date = elem.get("startDate", "")
        sk = f"RECORD#{short_type}#{start_date}"

        chunk.append({
            "PK": pk,
            "SK": sk,
            "GSI1SK": f"{short_type}#{start_date}",
            "recordType": short_type,
            "value": elem.get("value", ""),
            "unit": elem.get("unit", ""),
            "startDate": start_date,
            "creationDate": elem.get("creationDate", ""),
        })
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]

        if len(chunk) >= WRITE_CHUNK_SIZE:
            futures.append(executor.submit(_write_chunk, table, chunk))
            total_written += len(chunk)
            chunk = []

            if total_written % 50000 == 0:
                logger.info("Progress: %d records written", total_written)

    if chunk:
        futures.append(executor.submit(_write_chunk, table, chunk))
        total_written += len(chunk)

    for future in as_completed(futures):
        future.result()

    executor.shutdown(wait=True)

    logger.info("Skipped %d non-tracked records", records_skipped)
    return total_written


def _write_chunk(table: "boto3.resources.factory.dynamodb.Table", items: list[dict]) -> None:
    """Write a chunk of items to DynamoDB using batch_writer."""
    with table.batch_writer(overwrite_by_pkeys=["PK", "SK"]) as writer:
        for item in items:
            writer.put_item(Item=item)


if __name__ == "__main__":
    main()
