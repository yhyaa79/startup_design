# event_hub/urls.py

from django.urls import path
from . import views

app_name = 'event_hub'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('<slug:slug>/', views.event_detail, name='event_detail'),
]