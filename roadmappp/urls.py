# roadmap/urls.py

from django.urls import path
from . import views

app_name = 'roadmap'

urlpatterns = [
    path('', views.roadmap_view, name='roadmap_view'),
    path('create/', views.roadmap_create, name='roadmap_create'),
    path('stage/create/<int:roadmap_id>/', views.stage_create, name='stage_create'),
    path('stage/<int:stage_id>/edit/', views.stage_edit, name='stage_edit'),
    path('stage/<int:stage_id>/delete/', views.stage_delete, name='stage_delete'),
    path('activity/<int:activity_id>/delete/', views.stage_activity_delete, name='stage_activity_delete'),
    path('activity/<int:activity_id>/toggle/', views.toggle_activity_completion, name='toggle_activity_completion'),
    path('api/detail/', views.roadmap_detail_api, name='roadmap_detail_api'),
]
