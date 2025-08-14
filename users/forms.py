from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import User


class RegisterForm(UserCreationForm):
    """Форма регистрации нового пользователя, расширяющая стандартную UserCreationForm"""

    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('email', 'avatar', 'phone', 'bio', 'birth_date')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }

    def clean_email(self):
        """Валидация поля email. Проверяет, что указанный email еще не зарегистрирован в системе.
            Возвращает:
                str: Валидный email
            Вызывает:
                ValidationError: Если email уже существует в системе"""

        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже зарегистрирован")
        return email


class UserProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""

    class Meta:
        """Мета-класс для настройки поведения формы"""

        model = User
        fields = ['avatar', 'phone', 'bio', 'birth_date']
        widgets = {
            'avatar': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
        }
        help_texts = {
            'avatar': 'Загрузите изображение для вашего профиля',
        }
        labels = {
            'avatar': 'Аватар профиля',
        }
