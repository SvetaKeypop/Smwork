# Кулинарный блог

Учебный итоговый проект по дисциплине **«Технологии разработки программных приложений»**
(направление WEB-разработка). Веб-приложение — каталог рецептов: пользователи регистрируются,
публикуют свои рецепты, ставят лайки и добавляют понравившееся в избранное. Администратор
модерирует контент.

**Команда:** Лапин Матвей Максимович, Василенко Фёдор (ИКБО-12-24).

## Стек

- **Бэкенд:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Uvicorn, Jinja2.
- **Фронтенд:** HTML5, CSS3, ванильный JS (без фреймворков).
- **БД:** PostgreSQL 15+ (для разработки можно поднять через `docker-compose`).
- **Аутентификация:** cookie-сессии (Starlette `SessionMiddleware`), хеш паролей bcrypt.
- **Сборка пакета:** `setuptools` (`pyproject.toml`).
- **Документация:** Sphinx.
- **Развёртывание:** Docker, docker-compose.

## Структура

```
.
├── src/culinary_blog/        # пакет приложения
│   ├── main.py               # точка входа FastAPI
│   ├── config.py             # настройки из переменных окружения
│   ├── database.py           # SQLAlchemy engine/session
│   ├── models.py             # User, Recipe, Ingredient, Step, Like, Favorite
│   ├── auth.py               # хеширование паролей, current_user/require_user
│   ├── routers/              # маршруты: pages, auth, recipes, admin
│   ├── templates/            # Jinja2-шаблоны
│   └── static/               # CSS и JS
├── sphinx_docs/              # исходники документации
├── docs/                     # User Story, макет, итоговый отчёт
├── media/uploads/            # загруженные фото блюд (git-ignored)
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── .env.example
```

## Локальный запуск (без Docker)

```bash
python -m venv .venv
. .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # подправь DATABASE_URL под свой Postgres

# поднять PostgreSQL отдельно (либо через compose, см. ниже)
python -m culinary_blog        # откроется на http://localhost:8000
```

При первом запуске:
- создаются все таблицы (`SQLAlchemy.metadata.create_all`);
- автоматически заводится администратор с реквизитами из `ADMIN_EMAIL` / `ADMIN_PASSWORD`
  (по умолчанию `admin@example.com` / `admin123`).

## Запуск через Docker Compose

Поднимет PostgreSQL и приложение одной командой:

```bash
docker-compose up --build
```

Приложение будет доступно на `http://localhost:8000`.

## Сборка пакета

```bash
pip install build
python -m build                # появится dist/culinary_blog-0.1.0.tar.gz и .whl
```

## Документация (Sphinx)

```bash
pip install -r requirements.txt
sphinx-build -b html sphinx_docs sphinx_docs/_build/html
```

Готовая документация — в `sphinx_docs/_build/html/index.html`.

## Маршруты

| URL | Метод | Описание | Доступ |
|-----|-------|----------|--------|
| `/` | GET | главная (каталог рецептов) | все |
| `/recipe/{id}` | GET | страница рецепта | все |
| `/auth` | GET | формы входа/регистрации | все |
| `/register` | POST | регистрация | все |
| `/login` | POST | вход | все |
| `/logout` | POST | выход | пользователь |
| `/new` | GET | форма публикации | пользователь |
| `/recipes` | POST | создать рецепт | пользователь |
| `/recipes/{id}/like` | POST | toggle лайк | пользователь |
| `/recipes/{id}/favorite` | POST | toggle избранное | пользователь |
| `/favorites` | GET | список избранного | пользователь |
| `/my` | GET | мои рецепты | пользователь |
| `/admin` | GET | админ-панель | админ |
| `/admin/recipes/{id}/delete` | POST | удалить рецепт | админ |
| `/admin/users/{id}/block` | POST | блок/разблок пользователя | админ |

## User Story

Карточки оформлены в `docs/User_Story_Лапин_Василенко.docx`. Кратко покрываемые истории:
US-01 регистрация · US-02 авторизация · US-03 каталог · US-04 карточка рецепта ·
US-05 публикация · US-06 лайк · US-07 избранное · US-08 модерация.
