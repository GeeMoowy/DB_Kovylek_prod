from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.contrib.auth import login, get_user_model
from django.views.generic import UpdateView

from .forms import RegisterForm, UserProfileForm

User = get_user_model()


class RegisterView(View):
    """Представление для регистрации пользователя. Обрабатывает GET и POST запросы для регистрации:
        - GET: Отображает пустую форму регистрации.
        - POST: Проверяет данные формы, создает пользователя, выполняет вход и перенаправляет на главную страницу.
    Атрибуты:
        template_name (str): Путь к шаблону страницы регистрации
        form_class (Form): Класс формы для регистрации"""

    template_name = 'users/register.html'
    form_class = RegisterForm

    def get(self, request):
        """Обработка GET-запроса"""

        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Обработка POST-запроса"""

        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('diary:home')
        return render(request, self.template_name, {'form': form})


class ProfileEditView(UpdateView):
    """Представление для редактирования профиля пользователя. Предоставляет функционал для обновления существующего
    профиля пользователя. Автоматически использует текущего аутентифицированного пользователя в качестве объекта для
    редактирования.
        Атрибуты:
            model (Model): Модель User, которая будет редактироваться.
            form_class (Form): Класс формы для редактирования профиля (UserProfileForm).
            template_name (str): Шаблон для отображения страницы редактирования ('profile.html').
            context_object_name (str): Имя объекта в контексте шаблона ('user').
            success_url (str): URL для перенаправления после успешного обновления профиля (reverse_lazy('diary:home')).
        Методы:
            get_object: Возвращает экземпляр текущего аутентифицированного пользователя для редактирования"""

    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    context_object_name = 'user'
    success_url = reverse_lazy('students:main')

    def get_object(self, queryset=None):
        """Получает объект пользователя для редактирования. Переопределяет метод get_object родительского класса,
        чтобы всегда возвращать текущего аутентифицированного пользователя.
            Аргументы:
                queryset: Не используется (оставлен для совместимости с родительским классом).
            Возвращает:
                User: Экземпляр текущего аутентифицированного пользователя"""

        return self.request.user

