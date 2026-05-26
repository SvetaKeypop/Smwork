"""Маршруты регистрации, входа и выхода."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..auth import hash_password, verify_password
from ..database import get_db
from ..models import User

router = APIRouter(tags=["auth"])


@router.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(..., min_length=8),
    db: Session = Depends(get_db),
):
    """Создаёт нового пользователя и сразу логинит его."""
    email = email.strip().lower()
    if db.query(User).filter(User.email == email).first():
        return RedirectResponse(url="/auth?error=email_taken", status_code=303)

    user = User(email=email, name=name.strip(), password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=303)


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    """Проверяет пароль и сохраняет id пользователя в сессии."""
    email = email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if user is None or user.is_blocked or not verify_password(password, user.password_hash):
        return RedirectResponse(url="/auth?error=invalid_credentials", status_code=303)

    request.session["user_id"] = user.id
    return RedirectResponse(url="/", status_code=303)


@router.post("/logout")
def logout(request: Request):
    """Очищает сессию."""
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
