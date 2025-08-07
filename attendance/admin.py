from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django import forms

from attendance.constants import STATUS_CHOICES
from attendance.models import Repetition, AttendanceRecord


class AttendanceRecordInlineForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['student', 'present', 'status', 'notes']
        widgets = {
            'status': forms.RadioSelect(choices=STATUS_CHOICES),
        }


class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    form = AttendanceRecordInlineForm
    extra = 0  # Не показывать пустые формы
    can_delete = False
    verbose_name_plural = 'Участники группы'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('student').order_by('student__last_name')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "student":
            # Получаем ID репетиции из URL
            repetition_id = request.resolver_match.kwargs.get('object_id')
            if repetition_id:
                # Фильтруем студентов только из группы этой репетиции
                repetition = Repetition.objects.get(id=repetition_id)
                kwargs["queryset"] = repetition.group.students.order_by('last_name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    fields = ('student_link', 'present', 'status', 'notes')
    readonly_fields = ('student_link',)

    def student_link(self, obj):
        link = reverse("admin:students_student_change", args=[obj.student.id])
        return format_html('<a href="{}">{}</a>', link, obj.student.full_name)

    student_link.short_description = 'Участник'

    def get_fields(self, request, obj=None):
        if obj:  # Если объект уже существует
            return ('student_link', 'present', 'status', 'notes')
        return super().get_fields(request, obj)


@admin.register(Repetition)
class RepetitionAdmin(admin.ModelAdmin):
    """ Модель репетиции в админке Django """

    list_display = ('date', 'group_link', 'start_time', 'duration_display', 'attendance_count', 'created_at')
    list_filter = ('date', 'group', 'duration')
    search_fields = ('group__age_category', 'group__year', 'notes')
    date_hierarchy = 'date'
    ordering = ('-date', 'start_time')
    fieldsets = (
        (None, {
            'fields': ('date', 'start_time', 'duration', 'group')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'attendance_summary'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('attendance_summary', 'created_at', 'updated_at')
    inlines = [AttendanceRecordInline]
    actions = ['create_attendance_records']

    def create_attendance_records(self, request, queryset):
        for repetition in queryset:
            existing_records = set(repetition.attendance_records.values_list('student_id', flat=True))
            students_to_add = repetition.group.students.exclude(id__in=existing_records)

            created = 0
            for student in students_to_add:
                AttendanceRecord.objects.create(
                    repetition=repetition,
                    student=student,
                    present=False,
                    status='absent'
                )
                created += 1

            self.message_user(request, f"Для {repetition} создано {created} записей")
    create_attendance_records.short_description = "Создать записи посещаемости для всех студентов"

    def group_link(self, obj):
        link = reverse("admin:students_group_change", args=[obj.group.id])
        return mark_safe(f'<a href="{link}">{obj.group}</a>')
    group_link.short_description = 'Группа'

    def duration_display(self, obj):
        return f"{obj.duration} мин"
    duration_display.short_description = 'Длительность'

    def attendance_count(self, obj):
        count = obj.attendance_records.count()
        link = reverse("admin:attendance_attendancerecord_changelist") + f"?repetition__id__exact={obj.id}"
        return mark_safe(f'<a href="{link}">{count} записей</a>')
    attendance_count.short_description = 'Посещаемость'

    def attendance_summary(self, obj):
        presents = obj.attendance_records.filter(present=True).count()
        total = obj.attendance_records.count()
        return f"Присутствовало: {presents}/{total} ({round(presents/total*100) if total else 0}%)"
    attendance_summary.short_description = 'Статистика посещаемости'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('group')

    def save_formset(self, request, form, formset, change):
        # Автоматическое создание записей посещаемости при создании репетиции
        instances = formset.save(commit=False)
        for instance in instances:
            if not instance.pk:  # Если запись новая
                instance.repetition = form.instance
            instance.save()
        formset.save_m2m()

        # Создаем отсутствующие записи для всех студентов группы
        if not change:  # Только при создании новой репетиции
            existing_students = set(form.instance.attendance_records.values_list('student_id', flat=True))
            all_students = form.instance.group.students.values_list('id', flat=True)

            for student_id in set(all_students) - existing_students:
                AttendanceRecord.objects.create(
                    repetition=form.instance,
                    student_id=student_id,
                    present=False,
                    status='absent'
                )


class AttendanceStatusFilter(admin.SimpleListFilter):
    title = 'Статус посещения'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('present', 'Присутствовал'),
            ('absent', 'Отсутствовал'),
            ('late', 'Опоздал'),
            ('excused', 'По уважительной причине'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())


class AttendanceRecordForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = '__all__'
        widgets = {
            'status': forms.RadioSelect
        }


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    form = AttendanceRecordForm
    list_display = ('student', 'repetition_link', 'status_icon', 'present', 'notes_short', 'updated_at')
    list_filter = (AttendanceStatusFilter, 'present', 'repetition__date', 'repetition__group')
    search_fields = ('student__last_name', 'student__first_name', 'notes')
    list_editable = ('present',)
    list_select_related = ('student', 'repetition', 'repetition__group')
    actions = ['mark_present', 'mark_absent']

    fieldsets = (
        (None, {
            'fields': ('repetition', 'student')
        }),
        ('Посещаемость', {
            'fields': ('present', 'status', 'notes')
        }),
    )

    def repetition_link(self, obj):
        link = reverse("admin:attendance_repetition_change", args=[obj.repetition.id])
        return mark_safe(f'<a href="{link}">{obj.repetition.date} {obj.repetition.group}</a>')

    repetition_link.short_description = 'Занятие'

    def status_icon(self, obj):
        icons = {
            'present': '✅',
            'absent': '❌',
            'late': '⏱️',
            'sick': '🤒',
        }
        return icons.get(obj.status, '')

    status_icon.short_description = ''

    def notes_short(self, obj):
        return obj.notes[:30] + '...' if obj.notes else ''

    notes_short.short_description = 'Комментарий'

    def mark_present(self, request, queryset):
        updated = queryset.update(present=True, status='present')
        self.message_user(request, f"{updated} записей отмечены как присутствовал")

    mark_present.short_description = "Отметить как присутствовал"

    def mark_absent(self, request, queryset):
        updated = queryset.update(present=False, status='absent')
        self.message_user(request, f"{updated} записей отмечены как отсутствовал")

    mark_absent.short_description = "Отметить как отсутствовал"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'student', 'repetition', 'repetition__group'
        ).order_by('-repetition__date', 'student__last_name')



