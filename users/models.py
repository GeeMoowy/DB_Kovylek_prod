from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.managers import UserManager


class User(AbstractUser):
    """Кастомная модель пользователя с отключенным полем username и подключенным кастомным менеджером"""

    username = None
    email = models.EmailField(
        'email address',
        unique=True
    )

    # Кастомные поля (аватар, телефон и т.д.)
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True, null=True
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True)
    bio = models.TextField(
        _('about'),
        max_length=500,
        blank=True)
    birth_date = models.DateField(
        _('birth date'),
        null=True,
        blank=True)

    # Указываем email как поле для входа
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Пустой список, так как email уже обязателен

    # Подключаем кастомный менеджер
    objects = UserManager()

    def __str__(self):
        return self.email
