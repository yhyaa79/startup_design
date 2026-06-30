# regulation_assessment/urls.py

from django.urls import path
from . import views

app_name = 'regulation_assessment'

urlpatterns = [
    path('evaluation/', views.evaluation_form, name='evaluation_form'),
    path('save-video-interest/', views.save_user_video_interest, name='save_video_interest'),
    path('thank-you/', views.thank_you_page, name='thank_you'),
]
