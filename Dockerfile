FROM python:3.12.6-slim-bookworm

WORKDIR /app

# Создаем папки статики и медиа с правильными правами
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R www-data:www-data /app/staticfiles /app/media

# Установка зависимостей для psycopg2 (если нужно)
RUN apt-get update && \
    apt-get install -y gcc libpq-dev curl && \
    apt-get clean

# Фикс прав для Poetry (добавьте эти строки)
RUN mkdir -p /var/www/.cache/pypoetry && \
    chown -R www-data:www-data /var/www/.cache

# Установка Poetry
ENV POETRY_VERSION=1.8.5
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Копируем зависимости и устанавливаем их
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi && \
    python manage.py collectstatic --noinput

# Копируем остальное
COPY --chown=appuser:appuser . .