"""Маршруты, возвращающие HTML-страницы через шаблоны Jinja2."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..auth import current_user, require_admin, require_user
from ..config import TEMPLATES_DIR
from ..database import get_db
from ..models import Favorite, Like, Recipe, User

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def _ctx(request: Request, user: User | None, **extra) -> dict:
    """Базовый контекст для шаблонов (всегда содержит request и user)."""
    return {"request": request, "user": user, **extra}


@router.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(current_user),
):
    """Главная: каталог всех опубликованных рецептов."""
    recipes = db.query(Recipe).order_by(Recipe.created_at.desc()).all()
    fav_ids = _favorite_ids(db, user)
    return templates.TemplateResponse(
        "index.html", _ctx(request, user, recipes=recipes, fav_ids=fav_ids, title="Главная")
    )


@router.get("/recipe/{recipe_id}", response_class=HTMLResponse)
def recipe_page(
    recipe_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User | None = Depends(current_user),
):
    """Карточка одного рецепта."""
    recipe = db.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    in_favorites = False
    liked = False
    if user:
        in_favorites = db.query(Favorite).filter_by(user_id=user.id, recipe_id=recipe.id).first() is not None
        liked = db.query(Like).filter_by(user_id=user.id, recipe_id=recipe.id).first() is not None
    return templates.TemplateResponse(
        "recipe.html",
        _ctx(request, user, recipe=recipe, in_favorites=in_favorites, liked=liked, title=recipe.title),
    )


@router.get("/auth", response_class=HTMLResponse)
def auth_page(request: Request, user: User | None = Depends(current_user)):
    """Форма входа и регистрации (на одной странице)."""
    error = request.query_params.get("error")
    return templates.TemplateResponse("auth.html", _ctx(request, user, error=error, title="Войти"))


@router.get("/new", response_class=HTMLResponse)
def new_recipe_page(request: Request, user: User = Depends(require_user)):
    """Форма публикации нового рецепта."""
    return templates.TemplateResponse("new_recipe.html", _ctx(request, user, title="Новый рецепт"))


@router.get("/favorites", response_class=HTMLResponse)
def favorites_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    """Список рецептов, добавленных пользователем в избранное."""
    recipes = (
        db.query(Recipe)
        .join(Favorite, Favorite.recipe_id == Recipe.id)
        .filter(Favorite.user_id == user.id)
        .order_by(Recipe.created_at.desc())
        .all()
    )
    fav_ids = {r.id for r in recipes}
    return templates.TemplateResponse(
        "favorites.html", _ctx(request, user, recipes=recipes, fav_ids=fav_ids, title="Избранное")
    )


@router.get("/my", response_class=HTMLResponse)
def my_recipes_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_user),
):
    """Список рецептов текущего пользователя."""
    recipes = db.query(Recipe).filter(Recipe.author_id == user.id).order_by(Recipe.created_at.desc()).all()
    fav_ids = _favorite_ids(db, user)
    return templates.TemplateResponse(
        "index.html", _ctx(request, user, recipes=recipes, fav_ids=fav_ids, title="Мои рецепты", heading="Мои рецепты")
    )


@router.get("/admin", response_class=HTMLResponse)
def admin_page(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """Админ-панель: списки рецептов и пользователей."""
    recipes = db.query(Recipe).order_by(Recipe.created_at.desc()).all()
    users = db.query(User).order_by(User.created_at.desc()).all()
    return templates.TemplateResponse(
        "admin.html", _ctx(request, user, recipes=recipes, users=users, title="Админ")
    )


def _favorite_ids(db: Session, user: User | None) -> set[int]:
    """Возвращает множество id рецептов, которые пользователь добавил в избранное."""
    if user is None:
        return set()
    rows = db.query(Favorite.recipe_id).filter(Favorite.user_id == user.id).all()
    return {r[0] for r in rows}
