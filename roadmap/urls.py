# roadmap/urls.py
from django.urls import path
from . import views

app_name = 'roadmap'

urlpatterns = [
    path('', views.roadmap_detail, name='roadmap_detail'),
    path('create/', views.roadmap_create, name='roadmap_create'),
    path('<int:roadmap_id>/edit/', views.roadmap_edit, name='roadmap_edit'),

    path('<int:roadmap_id>/stage/create/', views.stage_create, name='stage_create'),
    path('stage/<int:stage_id>/', views.stage_detail, name='stage_detail'),
    path('stage/<int:stage_id>/edit/', views.stage_edit, name='stage_edit'),
    path('stage/<int:stage_id>/delete/', views.stage_delete, name='stage_delete'),

    path('activities/', views.activity_list, name='activity_list'),
    path('activities/<int:activity_id>/', views.activity_detail, name='activity_detail'),

    path('stage-activity/<int:stage_activity_id>/toggle/', views.stage_activity_toggle, name='stage_activity_toggle'),

    path('generate-ai/', views.roadmap_generate_ai, name='roadmap_generate_ai'),

    path('activities/search/', views.activity_search_api, name='activity_search_api'),
]
