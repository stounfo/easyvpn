import os

SQL_ECHO = os.getenv("SQL_ECHO", "True") in ("True", "true", "1")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///sqlite.db")
API_TOKEN = os.getenv("API_TOKEN")
