"""Подключение к PostgreSQL и фабрика сессий SQLAlchemy."""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""


def get_db() -> Iterator[Session]:
    """Открывает сессию БД для одного запроса и закрывает её по завершении."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
