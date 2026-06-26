# project/urls.py

from django.urls import path
from .views import (
    ProjectListView,
    MyProjectListView,
    ProjectDetailView,
    ProjectCreateView,
    ProjectUpdateView,
    ProjectDeleteView,
    ProjectApplyView,
)

app_name = 'project'

urlpatterns = [
    path('', ProjectListView.as_view(), name='list'),
    path('my/', MyProjectListView.as_view(), name='my_projects'),
    path('create/', ProjectCreateView.as_view(), name='create'),
    path('<str:slug>/', ProjectDetailView.as_view(), name='detail'),
    path('<str:slug>/edit/', ProjectUpdateView.as_view(), name='edit'),
    path('<str:slug>/delete/', ProjectDeleteView.as_view(), name='delete'),
    path('<str:slug>/apply/', ProjectApplyView.as_view(), name='apply'),
]
