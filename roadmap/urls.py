# roadmap/urls.py


from django.urls import path
from . import views

app_name = 'roadmap'

urlpatterns = [
    # رودمپ
    path('', views.roadmap_list, name='roadmap_list'),
    path('create/', views.roadmap_create, name='roadmap_create'),
    path('<int:pk>/', views.roadmap_detail, name='roadmap_detail'),
    path('<int:pk>/edit/', views.roadmap_edit, name='roadmap_edit'),
    path('<int:pk>/delete/', views.roadmap_delete, name='roadmap_delete'),
    
    # مراحل
    path('<int:roadmap_id>/stage/create/', views.stage_create, name='stage_create'),
    path('stage/<int:stage_id>/', views.stage_detail, name='stage_detail'),
    path('stage/<int:stage_id>/edit/', views.stage_edit, name='stage_edit'),
    
    # ✅ فعالیت‌ها (جدید)
    path('activity/<int:activity_id>/', views.stage_activity_detail, name='stage_activity_detail'),
    path('activity/<int:activity_id>/update/', views.stage_activity_update, name='stage_activity_update'),
    path('activity/<int:activity_id>/toggle/', views.stage_activity_toggle, name='stage_activity_toggle'),
    path('activity/<int:activity_id>/select-static/', views.stage_activity_select_static_item, name='stage_activity_select_static'),
    path('activity/<int:activity_id>/create-custom/', views.stage_activity_create_custom, name='stage_activity_create_custom'),
    
    # ✅ Checkpoints (جدید)
    path('activity/<int:activity_id>/checkpoint/add/', views.stage_activity_add_checkpoint, name='stage_activity_add_checkpoint'),
    path('activity/<int:activity_id>/checkpoint/<int:checkpoint_id>/toggle/', views.stage_activity_toggle_checkpoint, name='stage_activity_toggle_checkpoint'),
    
    # ✅ Resources (جدید)
    path('activity/<int:activity_id>/resource/add/', views.stage_activity_add_resource, name='stage_activity_add_resource'),
    path('activity/<int:activity_id>/resource/<int:resource_id>/delete/', views.stage_activity_delete_resource, name='stage_activity_delete_resource'),
]
