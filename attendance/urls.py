from django.urls import path
from attendance.views import HomeView, RepetitionListView, AttendanceFormView, RepetitionCreateView

app_name = 'attendance'  # Явное указание имени приложения

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('groups/<int:pk>/repetitions/', RepetitionListView.as_view(), name='repetition_list'),
    path('repetitions/<int:pk>/attendance/', AttendanceFormView.as_view(), name='attendance_form'),
    path('groups/<int:pk>/repetitions/create/', RepetitionCreateView.as_view(), name='repetition_create'),
]