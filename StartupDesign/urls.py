# StartupDesign/urls.py


from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('roadmap/', include('roadmap.urls', namespace='roadmap')),
    path('course/', include('course.urls', namespace='course')),
    path('networking/', include('networking.urls', namespace='networking')),
    path('resume/', include('resume.urls', namespace='resume')),
    path('project/', include('project.urls', namespace='project')),
    path('events/', include('event_hub.urls', namespace='event_hub')),
    path('activity/', include('activity.urls', namespace='activity')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
