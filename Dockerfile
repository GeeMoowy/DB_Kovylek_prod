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

# 1. Копируем только зависимости
COPY pyproject.toml poetry.lock* ./

# 2. Устанавливаем зависимости (без текущего проекта)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# 3. Копируем ВЕСЬ код
COPY --chown=www-data:www-data . .

# 4. Сборка статики (после копирования всех файлов)
RUN python manage.py collectstatic --noinput --ignore=*.admin && \
    chown -R www-data:www-data /app/staticfiles && \
    chmod -R 755 /app/staticfiles
