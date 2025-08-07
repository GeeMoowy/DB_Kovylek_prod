from django.urls import path

from attendance.apps import AttendanceConfig
from attendance.views import HomeView


app_name = AttendanceConfig.name

urlpatterns=[
    path('home/', HomeView.as_view(), name='home'),
]