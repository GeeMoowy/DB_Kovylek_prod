from datetime import timedelta

from django.utils import timezone
from dateutil.utils import today
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView, CreateView
from django.db.models import Count, Q, Prefetch
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
        start_date, end_date = get_academic_year_dates()
        today = timezone.now().date()

        # Оптимизированный запрос для групп
        return Group.objects.filter(is_active=True).prefetch_related(
            Prefetch(
                'repetition_set',
                queryset=Repetition.objects.filter(date=today),
                to_attr='todays_repetitions'
            ),
            'students'
        ).annotate(
            current_year_repetitions=Count(
                'repetition',
                filter=Q(
                    repetition__date__gte=start_date,
                    repetition__date__lte=end_date
                )
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # Получаем все сегодняшние репетиции для всех групп
        context['todays_repetitions'] = Repetition.objects.filter(
            date=today,
            group__in=context['groups']
        ).select_related('group').order_by('start_time')
        return context


class RepetitionListView(ListView):
    """Контроллер для отображения списка занятий (repetitions) конкретной учебной группы
    с возможностью фильтрации по датам и пагинацией."""

    template_name = 'repetition_list.html'
    context_object_name = 'repetitions'
    paginate_by = 10

    def get_queryset(self):
        """Возвращает queryset занятий для конкретной группы с возможной фильтрацией по датам."""
        group_id = self.kwargs['pk']
        queryset = Repetition.objects.filter(group_id=group_id).select_related('group')

        # Фильтрация по дате
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')

        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset.order_by('-date', 'start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group_id = self.kwargs['pk']
        context['group'] = Group.objects.get(id=group_id)

        now = timezone.now()

        for repetition in context['repetitions']:
            # Проверяем, можно ли отмечать посещаемость
            repetition_datetime = timezone.make_aware(
                timezone.datetime.combine(repetition.date, repetition.start_time)
            )
            time_until = repetition_datetime - now

            repetition.can_mark = time_until <= timedelta(minutes=30)
            repetition.time_until_start = time_until

            # Сохраняем существующую логику по заполненности
            repetition.is_attendance_completed = repetition.attendance_records.exists()

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


