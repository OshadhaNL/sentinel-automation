import json
import os
from pathlib import Path

CONFIG_FILE = Path(__file__).with_name("config.json")

with CONFIG_FILE.open(encoding="utf-8") as file:
    CONFIG = json.load(file)

BASE_URL = os.getenv("BASE_URL") or CONFIG["base_url"]

BROWSER = CONFIG.get("browser", "chromium")
TIMEOUT = CONFIG.get("timeout", 30000)
ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    CONFIG.get("environment", "staging"),
)