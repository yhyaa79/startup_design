# roadmap/admin.py


from django.contrib import admin
from .models import Roadmap, Stage, Activity, StageActivity, RoadmapTemplate


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'goal', 'status', 'get_progress', 'created_at')
    list_filter = ('status', 'goal', 'created_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('ai_analysis', 'score_breakdown', 'created_at', 'updated_at')


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('title', 'roadmap', 'order', 'status', 'priority', 'duration_days')
    list_filter = ('status', 'priority', 'phase_type')
    search_fields = ('title', 'roadmap__title')


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'duration_days', 'impact_score', 'difficulty_rating')
    list_filter = ('category', 'difficulty_rating', 'impact_level')
    search_fields = ('title', 'external_id')


@admin.register(StageActivity)
class StageActivityAdmin(admin.ModelAdmin):
    list_display = ('activity', 'stage', 'is_completed', 'saved_to_profile')
    list_filter = ('is_completed', 'saved_to_profile')
    search_fields = ('activity__title', 'stage__title')


@admin.register(RoadmapTemplate)
class RoadmapTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'goal', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'goal')
