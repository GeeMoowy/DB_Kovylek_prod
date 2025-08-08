from django.urls import path

from attendance.apps import AttendanceConfig
from attendance.views import HomeView, RepetitionListView, AttendanceFormView


app_name = AttendanceConfig.name

urlpatterns=[
    path('', HomeView.as_view(), name='home'),
    path('repetition_list/<int:pk>', RepetitionListView.as_view(), name='repetition_list'),
    path('repetition/<int:pk>/attendance/',
         AttendanceFormView.as_view(),
         name='attendance_form'),
]