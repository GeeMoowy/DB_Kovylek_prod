from django.views.generic import TemplateView, ListView

from students.models import Student, Group


class MainView(TemplateView):
    """Контроллер главной страницы"""

    template_name = 'students/main.html'


class StudentsListView(ListView):
    """Контроллер списка участников"""

    model = Student
    template_name = 'students/students_list.html'
    context_object_name = 'students'

    def get_context_data(self, **kwargs):
        """Добавляем список групп в контекст"""

        context = super().get_context_data(**kwargs)
        context['unique_groups'] = Group.objects.filter(is_active=True).order_by('id')

        return context
