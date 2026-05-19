import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
CERTS_DIR = BASE_DIR / "certs"
LOGS_DIR = BASE_DIR / "logs"

# Local SQLite database
DB_FILE_PREFIX = "indusstream"
V2_DB_PATH = BASE_DIR.parent / "v2-edge-dashboard" / "data" / "indusstream.db"


def load_env_file(path):
    env_path = Path(path)
    if not env_path.exists():
        raise FileNotFoundError(f"Environment config file not found: {env_path}")

    with open(env_path) as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


ENV_NAME = os.getenv("INDUSSTREAM_ENV", "dev")
ENV_FILE = Path(f"/home/pi/indusstream/config/{ENV_NAME}.env")

load_env_file(ENV_FILE)

# AWS IoT Core MQTT settings
AWS_IOT_ENDPOINT = os.environ["AWS_IOT_ENDPOINT"]
MQTT_PORT = int(os.getenv("MQTT_PORT", "8883"))
MQTT_TOPIC = os.environ["MQTT_TOPIC"]

# AWS IoT certificate paths
ROOT_CA_PATH = Path(os.environ["ROOT_CA_PATH"])
DEVICE_CERT_PATH = Path(os.environ["DEVICE_CERT_PATH"])
PRIVATE_KEY_PATH = Path(os.environ["PRIVATE_KEY_PATH"])

# Publish behaviour
PUBLISH_INTERVAL_SECONDS = int(os.getenv("PUBLISH_INTERVAL_SECONDS", "1800"))
MQTT_CLIENT_ID = os.environ["MQTT_CLIENT_ID"]
