# activity/admin.py

from django.contrib import admin
from .models import ActivityLog, ActivityCheckpoint, ActivityResource

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """at_ActivityLogAdmin"""
    
    list_display = [
        'user',
        'activity',
        'status',
        'progress_percentage',
        'target_completion_date',
        'is_overdue'
    ]
    
    list_filter = [
        'status',
        'created_at',
        'activity__category',
        'roadmap'
    ]
    
    search_fields = [
        'user__username',
        'activity__title',
        'notes'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'start_date'
    ]
    
    fieldsets = (
        ('اطلاعات اساسی', {
            'fields': (
                'user',
                'roadmap',
                'stage',
                'activity',
                'stage_activity',
            )
        }),
        ('وضعیت و پیشرفت', {
            'fields': (
                'status',
                'progress_percentage',
            )
        }),
        ('تاریخ‌ها', {
            'fields': (
                'start_date',
                'target_completion_date',
                'actual_completion_date',
            )
        }),
        ('یادداشت‌ها و نتایج', {
            'fields': (
                'notes',
                'result_summary',
                'outcome_data',
            )
        }),
        ('سیستم', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )


@admin.register(ActivityCheckpoint)
class ActivityCheckpointAdmin(admin.ModelAdmin):
    """at_ActivityCheckpointAdmin"""
    
    list_display = [
        'activity_log',
        'title',
        'is_completed',
        'order'
    ]
    
    list_filter = [
        'is_completed',
        'created_at'
    ]
    
    search_fields = [
        'title',
        'activity_log__activity__title'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at'
    ]


@admin.register(ActivityResource)
class ActivityResourceAdmin(admin.ModelAdmin):
    """at_ActivityResourceAdmin"""
    
    list_display = [
        'activity_log',
        'title',
        'resource_type',
        'created_at'
    ]
    
    list_filter = [
        'resource_type',
        'created_at'
    ]
    
    search_fields = [
        'title',
        'activity_log__activity__title'
    ]
