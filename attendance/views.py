from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Контроллер главной страницы"""

    template_name = 'attendance/home.html'
