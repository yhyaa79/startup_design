# networking/urls.py

from django.urls import path
from . import views

app_name = 'networking'

urlpatterns = [
    path('list/', views.networking_list, name='networking_list'),
    path('profile/<int:pk>/', views.profile_detail, name='profile_detail'),
    path('send-request/<int:pk>/', views.send_connection_request, name='send_connection'),
    path('accept/<int:connection_id>/', views.accept_connection_request, name='accept_connection'),
    path('reject/<int:connection_id>/', views.reject_connection_request, name='reject_connection'),
]
