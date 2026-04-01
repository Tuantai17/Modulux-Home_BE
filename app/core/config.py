import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/modulux_db",
)

SECRET_KEY = os.getenv("SECRET_KEY", "yoursecretkeyhere")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", str(BASE_DIR / "media")))
MEDIA_URL = os.getenv("MEDIA_URL", "/media")
BACKEND_PUBLIC_URL = os.getenv("BACKEND_PUBLIC_URL", "http://localhost:8000").rstrip("/")
MEDIA_BASE_URL = os.getenv("MEDIA_BASE_URL", f"{BACKEND_PUBLIC_URL}{MEDIA_URL}").rstrip("/")

BLOG_SOURCE_BASE_URL = os.getenv("BLOG_SOURCE_BASE_URL", "https://moduluxhomes.com").rstrip("/")
BLOG_SOURCE_LIST_API = os.getenv(
    "BLOG_SOURCE_LIST_API",
    "https://api-gateway.tranduc.com/api/modulux-homes/blog/list",
)
BLOG_SOURCE_DETAIL_API_TEMPLATE = os.getenv(
    "BLOG_SOURCE_DETAIL_API_TEMPLATE",
    "https://api-gateway.tranduc.com/api/modulux-homes/blog/detail/{slug}",
)
BLOG_HTTP_TIMEOUT_SECONDS = int(os.getenv("BLOG_HTTP_TIMEOUT_SECONDS", "30"))
BLOG_HTTP_RETRY_ATTEMPTS = int(os.getenv("BLOG_HTTP_RETRY_ATTEMPTS", "3"))

BLOG_SYNC_SCHEDULER_ENABLED = os.getenv("BLOG_SYNC_SCHEDULER_ENABLED", "false").lower() == "true"
BLOG_SYNC_INTERVAL_HOURS = int(os.getenv("BLOG_SYNC_INTERVAL_HOURS", "6"))
