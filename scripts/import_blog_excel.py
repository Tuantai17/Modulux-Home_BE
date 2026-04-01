import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import SessionLocal
from app.services.blog_sync_service import BlogSyncService


def main() -> None:
    parser = argparse.ArgumentParser(description="Import blog URLs from an Excel file and sync them into the database.")
    parser.add_argument("--file", required=True, help="Path to the .xlsx file that contains a 'url' column")
    args = parser.parse_args()

    file_path = Path(args.file).resolve()
    if not file_path.exists():
        raise SystemExit(f"File not found: {file_path}")

    db = SessionLocal()
    try:
        summary = BlogSyncService(db).import_from_excel(file_path.read_bytes())
        print(json.dumps(summary.to_dict(), indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()
