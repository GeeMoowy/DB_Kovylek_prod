from datetime import date


def get_academic_year_dates(today=None):
    """
    Возвращает даты начала и конца текущего учебного года
    Учебный год: с 1 июня текущего года по 31 мая следующего года

    Args:
        today (date, optional): Дата для расчета. Если None - используется текущая дата.

    Returns:
        tuple: (start_date, end_date)
    """
    today = today or date.today()

    if today.month >= 6:  # июнь-декабрь
        start_date = date(today.year, 6, 1)
        end_date = date(today.year + 1, 5, 31)
    else:  # январь-май
        start_date = date(today.year - 1, 6, 1)
        end_date = date(today.year, 5, 31)

    return start_date, end_date