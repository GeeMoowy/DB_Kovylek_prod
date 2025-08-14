from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Кастомная админка для модели User"""

    # Поля, которые будут отображаться в списке пользователей
    list_display = ('email', 'id', 'first_name', 'last_name', 'is_staff', 'avatar_preview')
    # Поля, по которым можно фильтровать
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    # Поля, по которым можно искать
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    # Порядок полей в форме редактирования
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'),
         {'fields': ('first_name', 'last_name', 'birth_date', 'phone', 'bio', 'avatar', 'avatar_preview')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    readonly_fields = ('avatar_preview',)
    # Поля при создании пользователя
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    # Поле для сортировки
    ordering = ('email',)

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" />'.format(obj.avatar.url))
        return "-"

    avatar_preview.short_description = _('Avatar Preview')
