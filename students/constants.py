AGE_SENIOR = "senior"
AGE_MIDDLE = "middle"
AGE_JUNIOR = "junior"
AGE_PREPARATORY = "preparatory"
AGE_KIDS = "kids"

AGE_CHOICES = [
    (AGE_JUNIOR, "Младшая"),
    (AGE_MIDDLE, "Средняя"),
    (AGE_SENIOR, "Старшая"),
    (AGE_PREPARATORY, "Подготовительная"),
    (AGE_KIDS, "Детки"),
]

GENDER_MALE = "M"
GENDER_FEMALE = "Д"

GENDER_CHOICES = [
    (GENDER_MALE, "Мальчики"),
    (GENDER_FEMALE, "Девочки"),
]

STATUS_CHOICES = [
    ('Participant', 'Участник'),
    ('Graduate', 'Выпускник'),
    ('Expelled', 'Отчислен'),
]

PROGRAM_CHOICES = [
    ('DOOP', 'ДООП'),
    ('DOOP_II', 'ДООП вторая ступень'),
    ('DPOP_5', 'ДПОП 5 лет'),
    ('DPOP_8', 'ДПОП 8 лет'),
]