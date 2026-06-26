# resume/urls.py

from django.urls import path
from . import views

app_name = 'resume'

urlpatterns = [
    path('', views.resume_list, name='resume_list'),
    path('create/', views.resume_create, name='resume_create'),
    path('<int:pk>/generate/', views.resume_generate, name='resume_generate'),
    path('<int:pk>/', views.resume_detail, name='resume_detail'),
    path('<int:pk>/edit/', views.resume_edit, name='resume_edit'),
    path('<int:pk>/delete/', views.resume_delete, name='resume_delete'),
    path('<int:pk>/regenerate/', views.resume_regenerate, name='resume_regenerate'),
    path('<int:pk>/download/pdf/', views.download_pdf, name='download_pdf'),
    path('<int:pk>/download/docx/', views.download_docx, name='download_docx'),
]