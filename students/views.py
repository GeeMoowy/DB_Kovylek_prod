from django.views.generic import TemplateView


class MainView(TemplateView):
    """Контроллер главной страницы"""

    template_name = 'students/main.html'