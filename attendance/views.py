from datetime import timedelta, date
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import ListView, FormView, CreateView, TemplateView, UpdateView, DeleteView
from django.db.models import Count, Q, Prefetch
from django.forms import modelformset_factory
from django.shortcuts import get_object_or_404, reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.defaulttags import register

from attendance.models import Repetition, AttendanceRecord
from students.models import Group, Student
from attendance.utils import get_academic_year_dates
from attendance.forms import AttendanceRecordForm


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


class HomeView(ListView):
    """Контроллер для отображения домашней страницы приложения 'Журнал посещаемости'"""

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
        ).order_by('id')

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


class RepetitionCreateView(CreateView):
    """Контроллер для создания новой репетиции"""
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
        group = get_object_or_404(Group, pk=self.kwargs['pk'])
        context['group'] = group
        context['is_edit'] = False  # Флаг для шаблона, что это создание
        return context

class RepetitionEditView(UpdateView):
    """Контроллер для редактирования существующей репетиции"""
    model = Repetition
    fields = ['date', 'start_time', 'duration', 'notes']
    template_name = 'attendance/repetition_form.html'
    pk_url_kwarg = 'pk'  # Параметр из URL для идентификации репетиции

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.object.group  # Группа из редактируемой репетиции
        context['is_edit'] = True  # Флаг для шаблона, что это редактирование
        return context

    def get_success_url(self):
        return reverse('attendance:repetition_list', kwargs={'pk': self.object.group.id})


class RepetitionDeleteView(LoginRequiredMixin, DeleteView):
    model = Repetition
    template_name = 'attendance/repetition_list.html'  # тот же шаблон

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse('attendance:repetition_list', kwargs={'pk': self.object.group.id})


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


class CalendarView(TemplateView):
    template_name = 'attendance/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group = get_object_or_404(Group, pk=self.kwargs['pk'])
        today = timezone.now().date()

        # Получаем год и месяц из параметров или текущую дату
        year = int(self.kwargs.get('year', today.year))
        month = int(self.kwargs.get('month', today.month))
        month_date = date(year, month, 1)

        # Рассчитываем соседние месяцы
        prev_month = (month_date - timedelta(days=1)).replace(day=1)
        next_month = (month_date + timedelta(days=32)).replace(day=1)

        # Годы для выпадающего списка (текущий год ±5 лет)
        years = range(today.year - 5, today.year + 6)

        # Получаем репетиции за выбранный месяц
        repetitions = Repetition.objects.filter(
            group=group,
            date__year=year,
            date__month=month
        ).order_by('date')

        # Получаем участников и их посещаемость
        students = Student.objects.filter(group=group).order_by('last_name', 'first_name')

        calendar_data = []
        for student in students:
            attendance = {
                rep.date: rep.attendance_records.filter(student=student).first().status
                if rep.attendance_records.filter(student=student).exists() else None
                for rep in repetitions
            }
            calendar_data.append({
                'student': student,
                'attendance': attendance
            })

        context.update({
            'group': group,
            'month_date': month_date,
            'prev_month': prev_month,
            'next_month': next_month,
            'years': years,
            'months': [
                (1, 'Январь'), (2, 'Февраль'), (3, 'Март'),
                (4, 'Апрель'), (5, 'Май'), (6, 'Июнь'),
                (7, 'Июль'), (8, 'Август'), (9, 'Сентябрь'),
                (10, 'Октябрь'), (11, 'Ноябрь'), (12, 'Декабрь')
            ],
            'current_year': year,
            'current_month': month,
            'repetitions': repetitions,
            'calendar_data': calendar_data
        })
        return context
