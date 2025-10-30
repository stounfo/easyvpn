import os

SQL_ECHO = os.getenv("SQL_ECHO", "True") in ("True", "true", "1")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///sqlite.db")
XRAY_SERVER = os.getenv("XRAY_SERVER")
XRAY_PORT = os.getenv("XRAY_PORT")
INBOUND_TAG = os.getenv("INBOUND_TAG")
XRAY_CONFIG_PATH = os.getenv("XRAY_CONFIG_PATH")
