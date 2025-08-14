from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import FileExtensionValidator

from .constants import AGE_CHOICES, GENDER_CHOICES



class Group(models.Model):
    """Модель группы"""

    age_category = models.CharField(
        'Возрастная категория',
        max_length=20,
        choices=AGE_CHOICES
    )
    year = models.PositiveSmallIntegerField(
        'Год набора',
    )
    gender = models.CharField(
        'Пол группы',
        max_length=10,
        choices=GENDER_CHOICES
    )
    is_active = models.BooleanField(
        'Активна',
        default=True
    )
    image = models.ImageField(
        'Фото группы',
        upload_to='groups/images/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text='Рекомендуемый размер: 800x600px'
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        unique_together = ["age_category", "year", "gender"]  # чтобы не было дубликатов

    def __str__(self):
        return f"{self.get_age_category_display()} {self.year}-{self.get_gender_display()}"


class Student(models.Model):
    """Модель участника с оптимизированной структурой"""

    last_name = models.CharField(
        'Фамилия',
        max_length=50,
        blank=True
    )
    first_name = models.CharField(
        'Имя',
        max_length=50,
        blank=True
    )
    middle_name = models.CharField(
        'Отчество',
        max_length=50,
        blank=True
    )
    birth_date = models.DateField(
        'Дата рождения',
        blank=True,
        null=True)
    gender = models.CharField(
        'Пол',
        max_length=20,
        choices=GENDER_CHOICES
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        related_name='students',
        verbose_name='Группа'
    )
    notes = models.TextField(
        'Дополнительная информация',
        blank=True
    )
    phone = PhoneNumberField(
        'Телефон',
        blank=True,
        null=True
    )
    enrollment_date = models.DateField(
        'Дата зачисления',
        null=True,
        blank=True
    )
    expulsion_date = models.DateField(
        'Дата отчисления',
        null=True,
        blank=True
    )
    graduation_year = models.PositiveIntegerField(
        'Год выпуска',
        null=True,
        blank=True
    )
    photo = models.ImageField(
        'Фото',
        upload_to='participants/photos/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        'Создано',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        'Обновлено',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return self.full_name or f"Участник #{self.id}"

    @property
    def full_name(self):
        """Полное имя участника"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)
