# event_hub/admin.py

from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'section', 'resume_impact', 'created_at')
    search_fields = ('title', 'slug', 'section', 'activity_type', 'goal')
    prepopulated_fields = {'slug': ('title',)}
