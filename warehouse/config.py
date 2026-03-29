from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
EXPORT_DIR = DATA_DIR / "exports"
DB_PATH = PROJECT_ROOT / "customer_360.duckdb"
MODELS_DIR = PROJECT_ROOT / "models"

RAW_FILES = {
    "customers": RAW_DIR / "customers.csv",
    "orders": RAW_DIR / "orders.csv",
    "payments": RAW_DIR / "payments.csv",
    "support_tickets": RAW_DIR / "support_tickets.csv",
}

MODEL_FOLDERS = ["staging", "core", "marts"]

