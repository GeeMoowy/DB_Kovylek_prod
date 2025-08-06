from django.db import models
from django.utils import timezone

from attendance.constants import DURATION_CHOICES, STATUS_CHOICES


class Repetition(models.Model):
    """Модель тренировочного занятия"""

    date = models.DateField(
        'Дата занятия',
        default=timezone.now
    )
    start_time = models.TimeField(
        'Время начала',
        default='18:00'
    )
    duration = models.IntegerField(
        'Длительность',
        choices=DURATION_CHOICES,
        default=90
    )
    group = models.ForeignKey(
        'students.Group',
        on_delete=models.PROTECT,
        verbose_name='Группа'
    )
    notes = models.TextField(
        'Примечания',
        blank=True,
        help_text="План занятия, особенности и т.д."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Репетиция'
        verbose_name_plural = 'Репетиции'
        ordering = ['-date']
        unique_together = ['date', 'group', 'start_time']

    def __str__(self):
        return f"{self.date} {self.group}"


class AttendanceRecord(models.Model):
    """Модель записи о посещаемости"""

    repetition = models.ForeignKey(
        Repetition,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    present = models.BooleanField(
        'Присутствовал (быстрая отметка)',
        default=False  # Изменили на False
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='absent'
    )
    notes = models.TextField(
        'Комментарий',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Запись посещаемости'
        verbose_name_plural = 'Записи посещаемости'
        unique_together = ['repetition', 'student']

    def __str__(self):
        return f"{self.student} - {'Присутствовал' if self.present else 'Отсутствовал'}"

    def save(self, *args, **kwargs):
        # Улучшенная логика синхронизации
        if self.present and self.status == 'absent':
            self.status = 'present'
        elif not self.present and self.status in ['present', 'late']:
            self.status = 'absent'
        super().save(*args, **kwargs)

    @property
    def status_display(self):
        """Возвращает читаемый статус с учетом present"""
        if self.status != 'present':
            return self.get_status_display()
        return 'Присутствовал' if self.present else 'Отсутствовал'
