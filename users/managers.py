from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Кастомный менеджер для модели User, реализующий аутентификацию по email вместо username.
    Наследуется от BaseUserManager Django и переопределяет методы создания пользователей.

    Особенности:
    - Требует обязательного указания email при регистрации
    - Автоматически нормализует email (приводит домен к нижнему регистру)
    - Поддерживает создание обычных пользователей и суперпользователей
    - Совместим с системой миграций Django (use_in_migrations=True)

    Пример использования:
    > user = User.objects.create_user(email='user@example.com', password='123')
    > admin = User.objects.create_superuser(email='admin@example.com', password='admin123')"""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Внутренний метод для создания и сохранения пользователя с email и паролем.
        Выполняет базовые проверки и нормализацию данных.

        Аргументы:
            email (str): Email пользователя (обязательное поле)
            password (str): Пароль пользователя
            **extra_fields: Дополнительные атрибуты пользователя (is_active, first_name и т.д.)

        Исключения:
            ValueError: Если email не указан

        Возвращает:
            User: Созданный объект пользователя"""

        if not email:
            raise ValueError('Требуется указать email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Создает обычного пользователя с указанными учетными данными.

        Аргументы:
            email (str): Email пользователя
            password (str, optional): Пароль. Если None - пользователь получит непригодный пароль.
            **extra_fields: Дополнительные атрибуты пользователя

        Возвращает:
            User: Созданный объект обычного пользователя

        По умолчанию:
            - is_staff = False (нет доступа к админке)
            - is_superuser = False (обычные права)"""

        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Создает суперпользователя с расширенными правами.

        Аргументы:
            email (str): Email администратора
            password (str): Пароль администратора
            **extra_fields: Дополнительные атрибуты

        Исключения:
            ValueError: Если is_staff или is_superuser не установлены в True

        Возвращает:
            User: Созданный объект суперпользователя

        Требования:
            - is_staff = True (доступ к админке)
            - is_superuser = True (полные права)"""

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True')

        return self._create_user(email, password, **extra_fields)
