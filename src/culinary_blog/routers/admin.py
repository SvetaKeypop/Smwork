"""Маршруты администратора: удаление рецептов, блокировка и переименование пользователей."""

from fastapi import APIRouter, Depends, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..auth import require_admin
from ..database import get_db
from ..models import Recipe, User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/recipes/{recipe_id}/delete")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    db.delete(recipe)
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/users/{user_id}/block")
def block_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if user.id == admin.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Нельзя заблокировать самого себя")
    user.is_blocked = not user.is_blocked
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/users/{user_id}/rename")
def rename_user(
    user_id: int,
    name: str = Form(..., min_length=1, max_length=80),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    user.name = name.strip()
    db.commit()
    return RedirectResponse(url="/admin", status_code=303)
