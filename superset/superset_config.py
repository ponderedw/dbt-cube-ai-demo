import os

# Use SQLite for Superset metadata (no Postgres needed in this demo)
SQLALCHEMY_DATABASE_URI = "sqlite:////app/superset_home/superset.db"

SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "demo-secret-key-change-in-production")

AUTH_TYPE = 1  # AUTH_DB

APP_NAME = "Education Analytics"

FEATURE_FLAGS = {
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "ENABLE_TEMPLATE_PROCESSING": True,
}

CACHE_CONFIG = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
}

ENABLE_CORS = True
DEFAULT_SQLLAB_LIMIT = 5000
CSV_EXPORT = {"encoding": "utf-8"}
SQLLAB_TIMEOUT = 300
SUPERSET_WEBSERVER_TIMEOUT = 300
