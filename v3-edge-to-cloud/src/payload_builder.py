from datetime import datetime, timezone


def build_payload(reading: dict) -> dict:
    if not reading:
        raise ValueError("No reading provided")
    
    now = datetime.now(timezone.utc).isoformat()
    
    reading["timestamp"] = now

    return {
        "device_id": "raspberry-pi-edge-gateway",
        "source": "sqlite-local-buffer",
        "published_at": now,
        "reading": reading,
    }
