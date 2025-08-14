from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv
import os


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY') or get_random_secret_key().replace('django-insecure-', 'prod-')

DEBUG = True if os.getenv('DEBUG') == 'True' else False

# Основные домены (латиница + punycode для кириллицы)
BASE_DOMAINS = [
    'kovylek.ru',
    'xn--b1agncdq6g.xn--p1ai'  # Точный Punycode для ковылек.рф
]

# Автоматически генерируемые варианты
GENERATED_HOSTS = [
    *{host.lower() for host in BASE_DOMAINS},  # Уникализация и приведение к lowercase
    *(f'www.{domain}' for domain in BASE_DOMAINS),
]

# Базовые локальные адреса
LOCAL_HOSTS = [
    'localhost',
    '127.0.0.1',
    '[::1]'  # IPv6 localhost
]

# Яндекс Cloud IP (только если указаны в .env)
YANDEX_HOSTS = list(filter(None, [
    os.getenv('YANDEX_INTERNAL_IP'),
    os.getenv('YANDEX_EXTERNAL_IP')
]))

# Итоговый список ALLOWED_HOSTS
ALLOWED_HOSTS = [
    *GENERATED_HOSTS,
    *LOCAL_HOSTS,
    *YANDEX_HOSTS,
    *filter(None, os.getenv('EXTRA_ALLOWED_HOSTS', '').split(','))
]

# Проверка для production
if not DEBUG:
    if 'ковылек.рф' in ALLOWED_HOSTS:
        raise ImproperlyConfigured(
            'Для production используйте только Punycode (xn--b1agncdq6g.xn--p1ai) вместо кириллицы'
        )

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'phonenumber_field',
    'users',
    'students',
    'attendance',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'Kovylek_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 3,
            'sslmode': 'require'
        }
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "TIMEOUT": 300,  # 5 минут
    }
}

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True
USE_L18N = True

USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STATIC_ROOT = BASE_DIR / 'staticfiles'  # Для collectstatic
MEDIA_ROOT = '/var/www/media'  # Вне контейнера

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

# Увеличим количество элементов на странице
ADMIN_LIST_PER_PAGE = 50

# Включим "быстрое редактирование" в списке
ADMIN_QUICK_EDIT = True

DATE_INPUT_FORMATS = ['%d-%m-%Y', '%Y-%m-%d']
DATE_FORMAT = 'd-m-Y'

LOGIN_REDIRECT_URL = '/'  # Куда перенаправлять после успешного входа
LOGOUT_REDIRECT_URL = 'students:main'  # Куда перенаправлять после выхода

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
