from django.contrib import admin
from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'purpose', 'template', 'use_ai', 'ai_enhanced', 'created_at']
    list_filter = ['purpose', 'template', 'use_ai', 'ai_enhanced']
    search_fields = ['title', 'user__username', 'user__first_name']
    readonly_fields = ['created_at', 'updated_at']