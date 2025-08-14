from django.urls import path

from students.apps import StudentsConfig
from students.views import MainView, StudentsListView


app_name = StudentsConfig.name

urlpatterns=[
    path('', MainView.as_view(), name='main'),
    path('students_list/', StudentsListView.as_view(), name='students_list')
]