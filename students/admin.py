from django.contrib import admin
from django.utils.html import format_html
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumber_field.formfields import PhoneNumberField
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Group, Student

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'age_category', 'is_active', 'students_count', 'repetitions_count')
    list_filter = ('age_category', 'year', 'gender', 'is_active')
    search_fields = ['age_category', 'year', 'gender']
    list_editable = ('is_active',)

    def students_count(self, obj):
        return obj.students.count()
    students_count.short_description = 'Количество участников'

    def repetitions_count(self, obj):
        count = obj.repetition_set.count()
        link = reverse("admin:attendance_repetition_changelist") + f"?group__id__exact={obj.id}"
        return mark_safe(f'<a href="{link}">{count} занятий</a>')
    repetitions_count.short_description = 'Занятия'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'group', 'birth_date', 'phone', 'photo_preview')
    list_filter = ('group', 'gender', 'group__age_category')
    search_fields = ('last_name', 'first_name', 'middle_name', 'phone')
    autocomplete_fields = ['group']
    date_hierarchy = 'birth_date'
    formfield_overrides = {
        PhoneNumberField: {'widget': PhoneNumberPrefixWidget},
    }

    fieldsets = (
        (None, {
            'fields': (('last_name', 'first_name', 'middle_name'), 'birth_date', 'gender')
        }),
        ('Группа', {
            'fields': ('group', 'enrollment_date', 'expulsion_date', 'graduation_year')
        }),
        ('Контакты', {
            'fields': ('phone', 'photo', 'photo_preview')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('photo_preview', 'created_at', 'updated_at')

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="100" style="border-radius: 5px;" />', obj.photo.url)
        return "Нет фото"
    photo_preview.short_description = 'Предпросмотр фото'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('group')
