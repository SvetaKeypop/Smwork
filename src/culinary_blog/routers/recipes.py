"""Маршруты для рецептов: создание, лайки, избранное."""

import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..auth import require_user
from ..config import UPLOAD_DIR
from ..database import get_db
from ..models import Favorite, Ingredient, Like, Recipe, Step, User

router = APIRouter(prefix="/recipes", tags=["recipes"])

ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def _save_image(file: UploadFile) -> str | None:
    """Сохраняет загруженное изображение и возвращает относительный путь."""
    if file is None or not file.filename:
        return None
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Недопустимый формат изображения")
    fname = f"{secrets.token_hex(8)}{ext}"
    dest = UPLOAD_DIR / fname
    with dest.open("wb") as f:
        f.write(file.file.read())
    return f"/media/uploads/{fname}"


@router.post("")
async def create_recipe(
    title: str = Form(...),
    description: str = Form(""),
    ingredient_name: list[str] = Form(default=[]),
    ingredient_amount: list[str] = Form(default=[]),
    step_text: list[str] = Form(default=[]),
    image: UploadFile | None = File(default=None),
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    """Создаёт рецепт со списками ингредиентов и шагов из формы."""
    image_path = _save_image(image) if image else None

    recipe = Recipe(
        title=title.strip(),
        description=description.strip(),
        image_path=image_path,
        author_id=user.id,
    )
    for i, (name, amount) in enumerate(zip(ingredient_name, ingredient_amount)):
        if name.strip():
            recipe.ingredients.append(Ingredient(name=name.strip(), amount=amount.strip(), position=i))
    for i, text in enumerate(step_text):
        if text.strip():
            recipe.steps.append(Step(text=text.strip(), position=i))

    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return RedirectResponse(url=f"/recipe/{recipe.id}", status_code=303)


@router.post("/{recipe_id}/like")
def toggle_like(
    recipe_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    """Ставит или снимает лайк (toggle)."""
    if db.get(Recipe, recipe_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    like = db.query(Like).filter_by(user_id=user.id, recipe_id=recipe_id).first()
    if like:
        db.delete(like)
        liked = False
    else:
        db.add(Like(user_id=user.id, recipe_id=recipe_id))
        liked = True
    db.commit()

    count = db.query(Like).filter_by(recipe_id=recipe_id).count()
    return JSONResponse({"liked": liked, "count": count})


@router.post("/{recipe_id}/favorite")
def toggle_favorite(
    recipe_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    """Добавляет/удаляет из избранного (toggle)."""
    if db.get(Recipe, recipe_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    fav = db.query(Favorite).filter_by(user_id=user.id, recipe_id=recipe_id).first()
    if fav:
        db.delete(fav)
        in_favorites = False
    else:
        db.add(Favorite(user_id=user.id, recipe_id=recipe_id))
        in_favorites = True
    db.commit()
    return JSONResponse({"in_favorites": in_favorites})
