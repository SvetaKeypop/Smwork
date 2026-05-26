"""Точка входа: создание FastAPI-приложения, подключение middleware и роутеров."""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from .config import PROJECT_ROOT, SECRET_KEY, STATIC_DIR
from .database import Base, SessionLocal, engine
from .models import User
from .auth import hash_password
from .config import ADMIN_EMAIL, ADMIN_PASSWORD
from .routers import admin, auth, pages, recipes


def create_app() -> FastAPI:
    """Создаёт и настраивает экземпляр FastAPI."""
    app = FastAPI(title="Кулинарный блог", version="0.1.0")

    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, https_only=False)

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.mount(
        "/media", StaticFiles(directory=str(PROJECT_ROOT / "media")), name="media"
    )

    app.include_router(pages.router)
    app.include_router(auth.router)
    app.include_router(recipes.router)
    app.include_router(admin.router)

    @app.on_event("startup")
    def _on_startup() -> None:
        Base.metadata.create_all(bind=engine)
        _ensure_admin()

    return app


def _ensure_admin() -> None:
    """Создаёт администратора по умолчанию, если его ещё нет."""
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == ADMIN_EMAIL).first():
            return
        admin_user = User(
            email=ADMIN_EMAIL,
            name="Администратор",
            password_hash=hash_password(ADMIN_PASSWORD),
            is_admin=True,
        )
        db.add(admin_user)
        db.commit()
    finally:
        db.close()


app = create_app()


def run() -> None:
    """Запуск через `python -m culinary_blog` или установленный скрипт."""
    import uvicorn

    uvicorn.run("culinary_blog.main:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    run()
