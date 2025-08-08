from django.urls import path

from attendance.apps import AttendanceConfig
from attendance.views import HomeView, RepetitionListView


app_name = AttendanceConfig.name

urlpatterns=[
    path('', HomeView.as_view(), name='home'),
    path('repetition_list/<int:pk>', RepetitionListView.as_view(), name='repetition_list')
]