"""
AWS Glue ETL script for parsing Apple Health exportar.xml.

Runs on a G.1X driver (4 vCPU, 16GB RAM) for fast XML parsing with lxml.
Uses ThreadPoolExecutor for parallel DynamoDB batch writes.
Spark is initialized only to satisfy the Glue ETL runtime requirement.

Arguments (passed via Step Functions):
  --BUCKET: S3 bucket name
  --KEY: S3 object key for the export ZIP
  --USER_ID: User ID for record association
  --HEALTH_JOB_ID: Job ID for tracking
  --TABLE_NAME: DynamoDB table name
"""

from __future__ import annotations

import io
import logging
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed, Future

from lxml import etree

import boto3
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext

logger = logging.getLogger("parse_health_xml")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)

BATCH_WRITE_SIZE = 25
WRITE_WORKERS = 32
MAX_INFLIGHT = 128
NUM_SHARDS = 10

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
    args = getResolvedOptions(sys.argv, ["BUCKET", "KEY", "USER_ID", "HEALTH_JOB_ID", "TABLE_NAME"])

    bucket = args["BUCKET"]
    key = args["KEY"]
    user_id = args["USER_ID"]
    job_id = args["HEALTH_JOB_ID"]
    table_name = args["TABLE_NAME"]

    logger.info("Starting XML parse: bucket=%s, key=%s, user=%s", bucket, key, user_id)

    sc = SparkContext.getOrCreate()
    GlueContext(sc)

    s3_client = boto3.client("s3")
    dynamodb_client = boto3.client("dynamodb")

    obj = s3_client.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read()
    zf = zipfile.ZipFile(io.BytesIO(body))

    xml_filename = _find_xml_file(zf)
    if not xml_filename:
        raise ValueError("No exportar.xml or export.xml found in ZIP")

    logger.info("Parsing XML file: %s", xml_filename)

    with zf.open(xml_filename) as xml_file:
        records_written = _stream_parse_and_write(xml_file, user_id, table_name, dynamodb_client)

    zf.close()
    logger.info("Completed: %d health records written for user %s", records_written, user_id)


def _find_xml_file(zf: zipfile.ZipFile) -> str | None:
    for name in zf.namelist():
        lower = name.lower()
        if lower.endswith("exportar.xml") or lower.endswith("export.xml"):
            return name
    return None


def _stream_parse_and_write(xml_file: io.BufferedReader, user_id: str, table_name: str, dynamodb_client) -> int:
    total_submitted = 0
    records_skipped = 0
    shard_idx = 0
    batch: list[dict] = []

    context = etree.iterparse(xml_file, events=("end",), tag="Record")
    executor = ThreadPoolExecutor(max_workers=WRITE_WORKERS)
    inflight: set[Future] = set()
    failed = 0

    def _drain_completed(target_size: int) -> None:
        nonlocal failed
        while len(inflight) >= target_size:
            done, _ = _wait_any(inflight)
            for f in done:
                inflight.discard(f)
                failed += f.result()

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
        pk = f"USER#{user_id}#SHARD#{shard_idx}"
        shard_idx = (shard_idx + 1) % NUM_SHARDS

        batch.append({
            "PutRequest": {
                "Item": {
                    "PK": {"S": pk},
                    "SK": {"S": sk},
                    "GSI1SK": {"S": f"{short_type}#{start_date}"},
                    "recordType": {"S": short_type},
                    "value": {"S": elem.get("value", "")},
                    "unit": {"S": elem.get("unit", "")},
                    "startDate": {"S": start_date},
                    "creationDate": {"S": elem.get("creationDate", "")},
                }
            }
        })
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]

        if len(batch) >= BATCH_WRITE_SIZE:
            _drain_completed(MAX_INFLIGHT)
            deduped = _dedupe_batch(batch)
            inflight.add(executor.submit(_write_batch, dynamodb_client, table_name, deduped))
            total_submitted += len(deduped)
            batch = []

            if total_submitted % 100000 == 0:
                logger.info("Progress: %d records submitted", total_submitted)

    if batch:
        deduped = _dedupe_batch(batch)
        inflight.add(executor.submit(_write_batch, dynamodb_client, table_name, deduped))
        total_submitted += len(deduped)

    _drain_completed(1)

    executor.shutdown(wait=True)

    logger.info("Skipped %d non-tracked records, %d unprocessed items", records_skipped, failed)
    return total_submitted


def _dedupe_batch(batch: list[dict]) -> list[dict]:
    seen: dict[str, dict] = {}
    for item in batch:
        attrs = item["PutRequest"]["Item"]
        key = f"{attrs['PK']['S']}#{attrs['SK']['S']}"
        seen[key] = item
    return list(seen.values())


def _wait_any(futures: set[Future]) -> tuple[set[Future], set[Future]]:
    from concurrent.futures import wait, FIRST_COMPLETED
    return wait(futures, return_when=FIRST_COMPLETED)


def _write_batch(client, table_name: str, items: list[dict]) -> int:
    request = {table_name: items}
    max_retries = 8

    for attempt in range(max_retries):
        response = client.batch_write_item(RequestItems=request)
        unprocessed = response.get("UnprocessedItems", {})
        if not unprocessed:
            return 0
        request = unprocessed
        time.sleep(min(0.1 * (2 ** attempt), 5.0))

    return sum(len(v) for v in request.values()) if request else 0


if __name__ == "__main__":
    main()
