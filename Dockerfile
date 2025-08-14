FROM python:3.12.6-slim-bookworm

WORKDIR /app

# Установка зависимостей для psycopg2 (если нужно)
RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
ENV POETRY_VERSION=1.8.5
RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Копируем зависимости и устанавливаем их (кешируемый слой)
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Создаем непривилегированного пользователя
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Копируем остальные файлы (с учетом .dockerignore)
COPY . .

# Настройки Gunicorn
ENV GUNICORN_WORKERS=4
EXPOSE 8000
CMD ["poetry", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]