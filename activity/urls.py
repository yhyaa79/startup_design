# activity/urls.py

from django.urls import path
from . import views

app_name = 'activity'

urlpatterns = [
    path('', views.activity_list, name='list'),
    path('detail/<int:activity_log_id>/', views.activity_detail_modal, name='detail'),
    path('stats/', views.activity_stats, name='stats'),
]
