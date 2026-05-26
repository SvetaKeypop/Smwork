"""Авторизация: хеширование паролей и получение текущего пользователя из cookie-сессии."""

from fastapi import Depends, HTTPException, Request, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from .database import get_db
from .models import User

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Возвращает bcrypt-хеш пароля."""
    return _pwd.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Проверяет, что пароль соответствует хешу."""
    return _pwd.verify(password, password_hash)


def current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    """Достаёт пользователя из сессии. Возвращает None, если не залогинен."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    user = db.get(User, user_id)
    if user is None or user.is_blocked:
        return None
    return user


def require_user(user: User | None = Depends(current_user)) -> User:
    """Зависимость для эндпоинтов, доступных только авторизованным."""
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Нужна авторизация")
    return user


def require_admin(user: User = Depends(require_user)) -> User:
    """Зависимость для админских эндпоинтов."""
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Только для администратора")
    return user
