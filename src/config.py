from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DB_PATH = ROOT / "data" / "app.db"
LOG_PATH = ROOT / "logs" / "indexer.log"

