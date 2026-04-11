from __future__ import annotations

import os

from databricks import sql
from dotenv import load_dotenv


load_dotenv()


def _get_env_value(key: str) -> str:
    value = os.getenv(key, "").strip()
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {key}. "
            "Update your .env file before starting the Streamlit app."
        )
    return value


def get_connection():
    server_hostname = _get_env_value("DATABRICKS_SERVER_HOSTNAME")
    http_path = _get_env_value("DATABRICKS_HTTP_PATH")
    access_token = _get_env_value("DATABRICKS_TOKEN")

    return sql.connect(
        server_hostname=server_hostname,
        http_path=http_path,
        access_token=access_token,
    )
