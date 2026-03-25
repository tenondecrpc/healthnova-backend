import io
import os
import time
import xml.etree.ElementTree as ET
import zipfile
from typing import Any, Dict, List

import boto3

from common import get_logger

logger = get_logger(__name__)
dynamodb = boto3.resource("dynamodb")
s3_client = boto3.client("s3")
table_name = os.environ.get("HEALTH_RECORDS_TABLE_NAME", "")
table = dynamodb.Table(table_name)

GPX_NS = {"gpx": "http://www.topografix.com/GPX/1/1"}


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Parse GPX workout route files from the export ZIP and write records to DynamoDB."""
    bucket = event["bucket"]
    key = event["key"]
    user_id = event["userId"]
    gpx_files: List[str] = event.get("gpxFiles", [])

    if not gpx_files:
        logger.info("No GPX files to process")
        return {"userId": user_id, "gpxRecordCount": 0}

    logger.info("Processing %d GPX files", len(gpx_files))

    obj = s3_client.get_object(Bucket=bucket, Key=key)
    body = obj["Body"].read()
    zf = zipfile.ZipFile(io.BytesIO(body))

    total_records = 0

    with table.batch_writer() as batch:
        for gpx_file in gpx_files:
            try:
                with zf.open(gpx_file) as f:
                    tree = ET.parse(f)
                    root = tree.getroot()

                    tracks = root.findall(".//gpx:trk", GPX_NS)
                    for track in tracks:
                        segments = track.findall("gpx:trkseg", GPX_NS)
                        waypoints: List[Dict[str, str]] = []

                        for seg in segments:
                            for pt in seg.findall("gpx:trkpt", GPX_NS):
                                lat = pt.get("lat", "")
                                lon = pt.get("lon", "")
                                ele_el = pt.find("gpx:ele", GPX_NS)
                                time_el = pt.find("gpx:time", GPX_NS)
                                waypoints.append({
                                    "lat": lat,
                                    "lon": lon,
                                    "ele": ele_el.text if ele_el is not None else "",
                                    "time": time_el.text if time_el is not None else "",
                                })

                        if waypoints:
                            route_time = waypoints[0].get("time", str(int(time.time())))
                            item = {
                                "PK": f"USER#{user_id}",
                                "SK": f"RECORD#GPX#{route_time}#{total_records}",
                                "recordType": "GPX",
                                "sourceFile": gpx_file,
                                "waypointCount": len(waypoints),
                                "startLat": waypoints[0]["lat"],
                                "startLon": waypoints[0]["lon"],
                                "endLat": waypoints[-1]["lat"],
                                "endLon": waypoints[-1]["lon"],
                                "createdAt": str(int(time.time())),
                            }
                            batch.put_item(Item=item)
                            total_records += 1

            except Exception as e:
                logger.error("Error parsing GPX file %s: %s", gpx_file, str(e))

    zf.close()
    logger.info("Processed %d GPX route records", total_records)

    return {"userId": user_id, "gpxRecordCount": total_records}
