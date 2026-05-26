"""Настройки приложения, читаемые из переменных окружения."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Каталог пакета, нужен для путей к шаблонам и статике.
PACKAGE_DIR = Path(__file__).resolve().parent

# Корень репозитория (на уровень выше src/).
PROJECT_ROOT = PACKAGE_DIR.parent.parent

def _normalize_db_url(url: str) -> str:
    """Render/Heroku отдают postgres://..., SQLAlchemy ждёт явный драйвер."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


DATABASE_URL = _normalize_db_url(
    os.getenv("DATABASE_URL", "postgresql+psycopg://blog:blog@localhost:5432/culinary_blog")
)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", PROJECT_ROOT / "media" / "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

TEMPLATES_DIR = PACKAGE_DIR / "templates"
STATIC_DIR = PACKAGE_DIR / "static"
