# roadmap/admin.py

from django.contrib import admin
from .models import Activity, Roadmap, Stage, StageActivity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'duration_hours', 'difficulty_level', 'is_active')
    list_filter = ('category', 'difficulty_level', 'is_active')
    search_fields = ('title', 'description')
    ordering = ('category', 'title')


class StageActivityInline(admin.TabularInline):
    model = StageActivity
    extra = 1
    fields = ('activity', 'repetition', 'is_completed', 'notes', 'order')


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('title', 'roadmap', 'status', 'order', 'get_total_duration')
    list_filter = ('status', 'roadmap')
    search_fields = ('title', 'description')
    inlines = [StageActivityInline]
    ordering = ('roadmap', 'order')

    def get_total_duration(self, obj):
        return f'{obj.get_total_duration()} ساعت'
    get_total_duration.short_description = 'کل زمان'


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'is_published', 'get_total_duration', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'profile__first_name', 'profile__last_name')
    readonly_fields = ('created_at', 'updated_at')

    def get_total_duration(self, obj):
        return f'{obj.get_total_duration()} ساعت'
    get_total_duration.short_description = 'کل زمان'
