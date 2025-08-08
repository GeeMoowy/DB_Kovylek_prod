from django.urls import reverse_lazy
from django.views.generic import ListView, FormView, CreateView
from django.db.models import Count, Q
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, reverse
from django.contrib import messages
from django.http import HttpResponseRedirect

from attendance.models import Repetition, AttendanceRecord
from students.models import Group
from attendance.utils import get_academic_year_dates
from attendance.forms import AttendanceRecordForm, RepetitionForm


class HomeView(ListView):
    """Контроллер для отображения домашней страницы приложения "Журнал посещаемости" со списком активных учебных групп.
    Наследуется от Django's ListView для отображения списка объектов.
    Отображает шаблон home.html с контекстом, содержащим активные учебные группы
    и количество проведенных повторений (занятий) для каждой группы в текущем учебном году.
    Attributes:
        - model (Model): Модель Group, используемая для получения данных.
        - template_name (str): Путь к шаблону для рендеринга страницы.
        - context_object_name (str): Имя переменной контекста для списка групп.
    Methods:
        - get_queryset: Возвращает queryset активных групп с аннотацией количества повторений."""

    model = Group
    template_name = 'attendance/home.html'
    context_object_name = 'groups'

    def get_queryset(self):
        """Возвращает queryset активных учебных групп с аннотацией количества проведенных занятий
        в текущем учебном году.
        Вычисляет даты начала и конца текущего учебного года с помощью функции
        get_academic_year_dates(), затем фильтрует активные группы и добавляет аннотацию
        с количеством связанных объектов Repetition в пределах учебного года.
        Returns:
            QuerySet: Аннотированный queryset групп со следующими полями:
                - Все стандартные поля модели Group
                - current_year_repetitions (int): Количество повторений в текущем учебном году
        Prefetch:
            Использует prefetch_related для оптимизации загрузки связанных студентов.
        """

        start_date, end_date = get_academic_year_dates()
        return Group.objects.filter(is_active=True).prefetch_related('students').annotate(
            current_year_repetitions=Count(
                'repetition',
                filter=Q(
                    repetition__date__gte=start_date,
                    repetition__date__lte=end_date
                )
            )
        )


class RepetitionListView(ListView):
    """Контроллер для отображения списка занятий (repetitions) конкретной учебной группы
    с возможностью фильтрации по датам и пагинацией.
    Наследуется от Django's ListView для отображения списка занятий с:
    - Пагинацией по 10 элементов на страницу
    - Фильтрацией по диапазону дат
    - Сортировкой по дате (новые сначала) и времени начала
    Attributes:
        template_name (str): Путь к шаблону repetition_list.html
        context_object_name (str): Имя переменной контекста для списка занятий
        paginate_by (int): Количество элементов на страницу пагинации
    Methods:
        get_queryset: Возвращает отфильтрованный и отсортированный queryset занятий
        get_context_data: Добавляет в контекст информацию о группе"""

    template_name = 'repetition_list.html'
    context_object_name = 'repetitions'
    paginate_by = 10

    def get_queryset(self):
        """Возвращает queryset занятий для конкретной группы с возможной фильтрацией по датам.
        Получает ID группы из URL параметров, затем:
            1. Базовый queryset всех занятий этой группы
            2. Применяет фильтрацию по дате начала (если передан параметр date_from)
            3. Применяет фильтрацию по дате окончания (если передан параметр date_to)
            4. Сортирует результаты по убыванию даты и возрастанию времени начала
        Returns:
            QuerySet: Отфильтрованный и отсортированный список объектов Repetition"""

        group_id = self.kwargs['pk']
        queryset = Repetition.objects.filter(group_id=self.kwargs['pk'])

        # Фильтрация по дате (если переданы параметры)
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset.order_by('-date', 'start_time')

    def get_context_data(self, **kwargs):
        """Расширяет базовый контекст шаблона информацией о текущей учебной группе.
        Добавляет в контекст:
            - Объект группы (Group), к которой относятся отображаемые занятия
            - Все стандартные переменные контекста ListView
        Returns:
            dict: Контекст данных для передачи в шаблон"""

        context = super().get_context_data(**kwargs)
        group_id = self.kwargs['pk']
        context['group'] = Group.objects.get(id=group_id)
        return context


class AttendanceFormView(FormView):
    template_name = 'attendance/attendance_form.html'

    def get_form_class(self):
        self.formset_class = modelformset_factory(
            AttendanceRecord,
            form=AttendanceRecordForm,
            extra=0,
            can_delete=False
        )
        return self.formset_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.repetition = get_object_or_404(Repetition, pk=self.kwargs['pk'])
        self.students = self.repetition.group.students.all()

        # Создаем или получаем записи посещаемости
        records = []
        for student in self.students:
            record, created = AttendanceRecord.objects.get_or_create(
                repetition=self.repetition,
                student=student,
                defaults={
                    'present': False,
                    'status': 'absent',
                    'notes': ''
                }
            )
            records.append(record)

        kwargs['queryset'] = AttendanceRecord.objects.filter(
            pk__in=[r.pk for r in records]
        ).select_related('student').order_by('student__last_name')

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formset = context.get('form', None)  # Для FormView основная форма в 'form'

        context.update({
            'repetition': self.repetition,
            'group': self.repetition.group,
            'students_count': self.students.count(),
            'records_count': len(formset.forms) if formset else 0,
            'formset': formset  # Явно добавляем formset в контекст
        })
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Посещаемость успешно сохранена!')
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('attendance:repetition_list', kwargs={'pk': self.repetition.group.id})


class RepetitionCreateView(CreateView):
    model = Repetition
    fields = ['date', 'start_time', 'duration', 'notes']
    template_name = 'attendance/repetition_form.html'

    def form_valid(self, form):
        form.instance.group = get_object_or_404(Group, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('attendance:repetition_list', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = get_object_or_404(Group, pk=self.kwargs['pk'])
        return context


