# accounts/urls.py



from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/edit/ai/', views.edit_profile_ai, name='edit_profile_ai'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]
