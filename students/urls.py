from django.urls import path

from students.apps import StudentsConfig
from students.views import MainView


app_name = StudentsConfig.name

urlpatterns=[
    path('', MainView.as_view(), name='main'),
]