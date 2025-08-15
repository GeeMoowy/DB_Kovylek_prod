FROM python:3.12.6-slim-bookworm

WORKDIR /app

# Создаем пользователя и папки заранее
RUN useradd -m appuser && \
    mkdir -p /app/staticfiles && \
    chown -R appuser:appuser /app

# Установка зависимостей для psycopg2 (если нужно)
RUN apt-get update && \
    apt-get install -y gcc libpq-dev curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Установка Poetry
ENV POETRY_VERSION=1.8.5
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Копируем зависимости и устанавливаем их
COPY --chown=appuser:appuser pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Копируем остальное
USER appuser
COPY --chown=appuser:appuser . .