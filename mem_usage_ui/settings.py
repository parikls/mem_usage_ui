import pathlib

BASE_DIR = pathlib.Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

WS_HEARTBEAT_INTERVAL = 30  # seconds
