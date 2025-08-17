FROM python:3.12.6

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]