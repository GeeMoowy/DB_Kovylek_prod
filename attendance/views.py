from datetime import date
from django.views.generic import ListView
from django.db.models import Count, Q

from attendance.models import Repetition
from students.models import Group
from attendance.utils import get_academic_year_dates


class HomeView(ListView):
    """Контроллер главной страницы"""

    model = Group
    template_name = 'attendance/home.html'
    context_object_name = 'groups'

    def get_queryset(self):
        """  """

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
    """  """

    template_name = 'repetition_list.html'
    context_object_name = 'repetitions'
    paginate_by = 10

    def get_queryset(self):
        group_id = self.kwargs['pk']
        queryset = Repetition.objects.filter(group_id=group_id)

        # Фильтрация по дате (если переданы параметры)
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
        return context


class RepetitionDitailView():
    """"""
