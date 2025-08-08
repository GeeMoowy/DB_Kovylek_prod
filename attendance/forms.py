from django import forms

from students.models import Group
from .models import AttendanceRecord, Repetition


class AttendanceRecordForm(forms.ModelForm):
    """Форма для отметки посещаемости студентов (AttendanceRecord).
    Используется для создания и редактирования записей о посещаемости студентов на занятиях.
    Содержит основные поля для фиксации присутствия, статуса и заметок, а также скрытые поля
    для связи со студентом и занятием.
        Attributes:
            Meta (class): Вложенный класс для конфигурации формы.

        Meta:
            - model (Model): Модель AttendanceRecord, на основе которой строится форма.
            - fields (list): Список включаемых полей формы:
                - present (bool): Отметка о присутствии (чекбокс)
                - status (str): Статус посещения (выпадающий список)
                - notes (str): Дополнительные заметки (текстовое поле)
            - widgets (dict): Кастомизированные виджеты для полей формы:
                - student: Скрытое поле (HiddenInput) для связи со студентом
                - repetition: Скрытое поле (HiddenInput) для связи с занятием
                - present: Чекбокс для отметки присутствия/отсутствия
                - status: Выпадающий список (Select) для выбора статуса
                - notes: Однострочное текстовое поле (TextInput) для заметок
        Note:
            Скрытые поля (student и repetition) обычно заполняются автоматически
            при создании формы в представлении и не отображаются пользователю"""

    class Meta:
        model = AttendanceRecord
        fields = ['present', 'status', 'notes']
        widgets = {
            'student': forms.HiddenInput(),
            'repetition': forms.HiddenInput(),
            'present': forms.CheckboxInput(),
            'status': forms.Select(),
            'notes': forms.TextInput()
        }


class RepetitionForm(forms.ModelForm):
    class Meta:
        model = Repetition
        fields = ['date', 'start_time', 'duration', 'notes']  # убрали group из полей
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

    def __init__(self, *args, group_pk=None, **kwargs):
        super().__init__(*args, **kwargs)
        if group_pk:
            self.fields['group'] = forms.ModelChoiceField(
                queryset=Group.objects.filter(pk=group_pk),
                initial=group_pk,
                widget=forms.HiddenInput()
            )
