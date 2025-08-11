from django import template
from datetime import timedelta

register = template.Library()


@register.filter
def format_timedelta(value):
    """Форматирует timedelta в Д дни ЧЧ:ММ"""
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())

        # Вычисляем дни, часы и минуты
        days = total_seconds // 86400  # 86400 секунд в дне
        remaining_seconds = total_seconds % 86400
        hours = remaining_seconds // 3600
        minutes = (remaining_seconds % 3600) // 60

        # Формируем строку в зависимости от наличия дней
        if days > 0:
            return f"{days} дн {hours:02d}:{minutes:02d}"
        return f"{hours:02d}:{minutes:02d}"
    return value