# course/urls.py

from django.urls import path
from . import views

app_name = 'course'

urlpatterns = [
    path('list/', views.course_list, name='list'),
    path('<str:course_id>/', views.course_detail, name='detail'),
]