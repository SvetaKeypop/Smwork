# Лёгкий образ под Linux: Python 3.11 на базе Debian slim.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Системные зависимости для psycopg.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY pyproject.toml ./
COPY src ./src
RUN pip install -e .

# Каталог для загруженных фото.
RUN mkdir -p /app/media/uploads

EXPOSE 8000

CMD ["uvicorn", "culinary_blog.main:app", "--host", "0.0.0.0", "--port", "8000"]
