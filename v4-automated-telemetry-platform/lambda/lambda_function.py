import os
import json
import boto3
import time
import math
from datetime import datetime, timezone
from decimal import Decimal

# DEV deployment validation test
S3_BUCKET = "indusstream-telemetry-data-dev"
S3_PREFIX = "analytics"

SNS_TOPIC_ARN = os.environ["snstopic"]
CO_RAW_ALERT_THRESHOLD = 500
CO_ALERT_PPM = 50

TEMP_OFFSET_C = 6.29
R0 = 23500
SOUND_RAW_MAX_VALID = 120

TABLE_NAME = "indusstream_telemetry_dev"
TTL_DAYS = 7

S3_ARCHIVE_INTERVAL_MINUTES = 10

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)

s3 = boto3.client("s3")
sns = boto3.client("sns")


def json_default(value):
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError


def clean_number(value):
    if value is None:
        return None
    if isinstance(value, dict) and "N" in value:
        return Decimal(value["N"])
    return Decimal(str(value))


def clean_temperature(value):
    temp = clean_number(value)
    if temp is None:
        return None

    corrected = temp - Decimal(str(TEMP_OFFSET_C))

    if corrected < 0 or corrected > 35:
        return None

    return corrected


def clean_sound_raw(value):
    sound = clean_number(value)
    if sound is None:
        return None

    if sound < 0 or sound > SOUND_RAW_MAX_VALID:
        return None

    return sound


def estimate_co_ppm(rs_value):
    if rs_value is None or rs_value <= 0:
        return None

    ratio = float(rs_value) / R0

    if ratio <= 0:
        return None

    return Decimal(str(round(10 ** ((-1.5 * math.log10(ratio)) + 1.7), 2)))


def should_archive_to_s3(timestamp):
    try:
        minute = int(timestamp[14:16])
        return minute % S3_ARCHIVE_INTERVAL_MINUTES == 0
    except Exception:
        return False
    

def write_analytics_record_to_s3(item):
    metrics = item["metrics"]
    status = item["status"]

    analytics_record = {
        "device_id": item["device_id"],
        "timestamp": item["timestamp"],
        "temperature_c": metrics.get("temperature_c"),
        "co_ppm_est": metrics.get("co_ppm_est"),
        "sound_raw": metrics.get("sound_raw"),
        "light_raw": metrics.get("light_raw"),
    }

    date_part = item["timestamp"][:10]
    year, month, day = date_part.split("-")

    safe_timestamp = item["timestamp"].replace(":", "-")
    key = (
        f"{S3_PREFIX}/year={year}/month={month}/day={day}/"
        f"{item['device_id']}_{safe_timestamp}.json"
    )

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=json.dumps(analytics_record, default=json_default) + "\n",
        ContentType="application/json",
    )


def lambda_handler(event, context):
    print(f"Processing telemetry for {event.get('device_id', 'unknown-device')}")

    reading = event.get("reading", {})
    timestamp = reading.get("timestamp") or datetime.now(timezone.utc).isoformat()

    co_raw = clean_number(reading.get("co_raw"))
    co_rs_ohms = clean_number(reading.get("co_rs_ohms"))
    co_ppm_est = estimate_co_ppm(co_rs_ohms)

    item = {
        "device_id": event.get("device_id") or reading.get("device_id", "unknown-device"),
        "timestamp": timestamp,
        "schema_version": "v1",
        "source_id": reading.get("source_id", "unknown-source"),
        "source": event.get("source", "sqlite-local-buffer"),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "temperature_c": clean_temperature(reading.get("temperature_c")),
            "light_raw": clean_number(reading.get("light_raw")),
            "sound_raw": clean_sound_raw(reading.get("sound_raw")),
            "co_raw": co_raw,
            "co_voltage": clean_number(reading.get("co_voltage")),
            "co_rs_ohms": co_rs_ohms,
            "co_ppm_est": co_ppm_est,
        },
        "status": {
            "light_state": reading.get("light_state"),
            "sound_event": bool(reading.get("sound_event", 0)),
        },
        "ttl": int(time.time()) + (TTL_DAYS * 24 * 60 * 60),
    }

    if co_raw is not None and co_raw >= CO_RAW_ALERT_THRESHOLD:
        try:
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="IndusStream Alert: High CO Reading",
                Message=(
                    f"High CO reading detected.\n\n"
                    f"Device: {item['device_id']}\n"
                    f"Timestamp: {item['timestamp']}\n"
                    f"CO Raw: {co_raw}\n"
                    f"CO PPM Estimate: {co_ppm_est}\n"
                    f"Source: {item['source_id']}"
                ),
            )
        except Exception as e:
            print("SNS publish failed:", str(e))

    table.put_item(Item=item)

    if should_archive_to_s3(item["timestamp"]):
        write_analytics_record_to_s3(item)

    return {
        "statusCode": 200,
        "message": "Telemetry stored",
        "device_id": item["device_id"],
        "timestamp": item["timestamp"],
    }# DEV redeploy trigger Fri May 15 00:38:37 GMTDT 2026
# DEV redeploy trigger Fri May 15 00:48:33 GMTDT 2026
# DEV redeploy trigger Fri May 15 01:15:51 GMTDT 2026
# DEV redeploy trigger Fri May 15 01:28:11 GMTDT 2026
