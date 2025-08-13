from django.urls import path
from attendance.views import (HomeView, RepetitionListView, AttendanceFormView, RepetitionCreateView, CalendarView,
                              RepetitionEditView, RepetitionDeleteView)

app_name = 'attendance'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('groups/<int:pk>/repetitions/', RepetitionListView.as_view(), name='repetition_list'),
    path('repetitions/<int:pk>/attendance/', AttendanceFormView.as_view(), name='attendance_form'),
    path('groups/<int:pk>/repetitions/create/', RepetitionCreateView.as_view(), name='repetition_create'),
    path('repetitions/<int:pk>/edit/', RepetitionEditView.as_view(), name='repetition_edit'),
    path('groups/<int:pk>/calendar/<int:year>/<int:month>/', CalendarView.as_view(), name='calendar_view'),
    path('groups/<int:pk>/calendar/', CalendarView.as_view(), name='calendar_current'),
    path('repetitions/<int:pk>/delete/', RepetitionDeleteView.as_view(), name='repetition_delete'),
]