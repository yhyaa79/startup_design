# roadmap/admin.py


from django.contrib import admin
from django.utils.html import format_html
import json
import nested_admin

from .models import (
    Activity,
    Roadmap,
    Stage,
    StageActivity,
    RoadmapActivity,
)


# =========================
# Helpers
# =========================
def pretty_json(data):
    if not data:
        return "-"
    try:
        return format_html("<pre style='white-space: pre-wrap; direction: ltr;'>{}</pre>", json.dumps(data, ensure_ascii=False, indent=2))
    except Exception:
        return str(data)


# =========================
# Activity Admin
# =========================
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'category',
        'field',
        'resume_target',
        'difficulty_level',
        'duration_days',
        'is_active',
        'display_suitable_goals',
        'created_at',
        'updated_at',
    ]
    list_filter = [
        'category',
        'field',
        'resume_target',
        'difficulty_level',
        'is_active',
        'created_at',
        'updated_at',
    ]
    search_fields = [
        'title',
        'description',
        'resume_output',
        'prerequisites',
        'resources',
    ]
    ordering = ['category', 'title']
    readonly_fields = [
        'created_at',
        'updated_at',
        'formatted_profile_template',
        'formatted_suitable_goals',
    ]
    list_per_page = 25

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': (
                'title',
                'description',
                'category',
                'field',
                'is_active',
            )
        }),
        ('اطلاعات کاربردی', {
            'fields': (
                'resume_target',
                'difficulty_level',
                'duration_days',
                'resume_output',
            )
        }),
        ('جزئیات تکمیلی', {
            'fields': (
                'prerequisites',
                'resources',
            )
        }),
        ('تنظیمات هوشمند / JSON', {
            'fields': (
                'profile_template',
                'formatted_profile_template',
                'suitable_goals',
                'formatted_suitable_goals',
            ),
            'classes': ('collapse',)
        }),
        ('زمان‌ها', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def display_suitable_goals(self, obj):
        if not obj.suitable_goals:
            return "همه اهداف"
        return "، ".join(obj.suitable_goals)
    display_suitable_goals.short_description = 'اهداف مناسب'

    def formatted_profile_template(self, obj):
        return pretty_json(obj.profile_template)
    formatted_profile_template.short_description = 'نمایش قالب پروفایل'

    def formatted_suitable_goals(self, obj):
        return pretty_json(obj.suitable_goals)
    formatted_suitable_goals.short_description = 'نمایش اهداف مناسب'


# =========================
# StageActivity Inline
# =========================
class StageActivityInline(nested_admin.NestedTabularInline):
    model = StageActivity
    extra = 0
    sortable_field_name = "order"
    autocomplete_fields = ['activity']
    fields = (
        'order',
        'activity',
        'is_completed',
        'notes',
        'created_at',
        'updated_at',
    )
    readonly_fields = ('created_at', 'updated_at')
    show_change_link = True


# =========================
# Stage Inline
# =========================
class StageInline(nested_admin.NestedStackedInline):
    model = Stage
    extra = 0
    sortable_field_name = "order"
    inlines = [StageActivityInline]
    fields = (
        'title',
        'description',
        'status',
        'objectives',
        'order',
        'phase_type',
        'priority',
        'milestone',
        'success_criteria',
        'risks',
        'recommended_resources',
        'created_at',
        'updated_at',
    )
    readonly_fields = ('created_at', 'updated_at')
    classes = ('collapse',)


# =========================
# Roadmap Admin
# =========================
@admin.register(Roadmap)
class RoadmapAdmin(nested_admin.NestedModelAdmin):
    list_display = [
        'title',
        'profile',
        'status',
        'total_stages',
        'get_total_progress_display',
        'get_total_duration_display',
        'created_at',
        'updated_at',
    ]
    list_filter = [
        'status',
        'created_at',
        'updated_at',
    ]
    search_fields = [
        'title',
        'description',
        'profile__first_name',
        'profile__last_name',
        'profile__user__username',
    ]
    readonly_fields = [
        'created_at',
        'updated_at',
        'total_stages',
        'get_total_progress_display',
        'get_total_duration_display',
    ]
    inlines = [StageInline]
    list_per_page = 20

    fieldsets = (
        ('اطلاعات اصلی رودمپ', {
            'fields': (
                'profile',
                'title',
                'description',
                'status',
            )
        }),
        ('اطلاعات محاسباتی', {
            'fields': (
                'total_stages',
                'get_total_progress_display',
                'get_total_duration_display',
            )
        }),
        ('زمان‌ها', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def total_stages(self, obj):
        return obj.stages.count()
    total_stages.short_description = 'تعداد مراحل'

    def get_total_progress_display(self, obj):
        return f"{obj.get_total_progress()}%"
    get_total_progress_display.short_description = 'پیشرفت کل'

    def get_total_duration_display(self, obj):
        return f"{obj.get_total_duration()} روز"
    get_total_duration_display.short_description = 'مدت کل'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile').prefetch_related('stages__stage_activities__activity')


# =========================
# Stage Admin
# =========================
@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'roadmap',
        'order',
        'status',
        'phase_type',
        'priority',
        'activities_count',
        'progress_display',
        'total_duration_display',
        'remaining_days_display',
        'created_at',
        'updated_at',
    ]
    list_filter = [
        'status',
        'phase_type',
        'priority',
        'created_at',
        'updated_at',
    ]
    search_fields = [
        'title',
        'description',
        'objectives',
        'milestone',
        'roadmap__title',
        'roadmap__profile__first_name',
        'roadmap__profile__last_name',
    ]
    ordering = ['roadmap', 'order']
    readonly_fields = [
        'created_at',
        'updated_at',
        'progress_display',
        'total_duration_display',
        'remaining_days_display',
        'formatted_success_criteria',
        'formatted_risks',
        'formatted_recommended_resources',
    ]
    list_per_page = 25

    fieldsets = (
        ('اطلاعات اصلی مرحله', {
            'fields': (
                'roadmap',
                'title',
                'description',
                'status',
                'objectives',
                'order',
            )
        }),
        ('اولویت و فاز', {
            'fields': (
                'phase_type',
                'priority',
                'milestone',
            )
        }),
        ('اطلاعات محاسباتی', {
            'fields': (
                'progress_display',
                'total_duration_display',
                'remaining_days_display',
            )
        }),
        ('داده‌های JSON', {
            'fields': (
                'success_criteria',
                'formatted_success_criteria',
                'risks',
                'formatted_risks',
                'recommended_resources',
                'formatted_recommended_resources',
            ),
            'classes': ('collapse',)
        }),
        ('زمان‌ها', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def activities_count(self, obj):
        return obj.stage_activities.count()
    activities_count.short_description = 'تعداد فعالیت‌ها'

    def progress_display(self, obj):
        return f"{obj.get_progress()}%"
    progress_display.short_description = 'پیشرفت مرحله'

    def total_duration_display(self, obj):
        return f"{obj.get_total_duration()} روز"
    total_duration_display.short_description = 'مدت کل مرحله'

    def remaining_days_display(self, obj):
        return f"{obj.get_remaining_days()} روز"
    remaining_days_display.short_description = 'روز باقی‌مانده'

    def formatted_success_criteria(self, obj):
        return pretty_json(obj.success_criteria)
    formatted_success_criteria.short_description = 'نمایش معیارهای موفقیت'

    def formatted_risks(self, obj):
        return pretty_json(obj.risks)
    formatted_risks.short_description = 'نمایش ریسک‌ها'

    def formatted_recommended_resources(self, obj):
        return pretty_json(obj.recommended_resources)
    formatted_recommended_resources.short_description = 'نمایش منابع پیشنهادی'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('roadmap').prefetch_related('stage_activities__activity')


# =========================
# StageActivity Admin
# =========================
@admin.register(StageActivity)
class StageActivityAdmin(admin.ModelAdmin):
    list_display = [
        'stage',
        'activity',
        'order',
        'is_completed',
        'activity_category',
        'activity_field',
        'activity_duration',
        'created_at',
        'updated_at',
    ]
    list_filter = [
        'is_completed',
        'activity__category',
        'activity__field',
        'activity__difficulty_level',
        'created_at',
        'updated_at',
    ]
    search_fields = [
        'stage__title',
        'activity__title',
        'notes',
        'stage__roadmap__title',
    ]
    autocomplete_fields = ['stage', 'activity']
    ordering = ['stage', 'order']
    readonly_fields = [
        'created_at',
        'updated_at',
    ]
    list_per_page = 30

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': (
                'stage',
                'activity',
                'is_completed',
                'order',
            )
        }),
        ('یادداشت‌ها', {
            'fields': (
                'notes',
            )
        }),
        ('زمان‌ها', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def activity_category(self, obj):
        return obj.activity.category
    activity_category.short_description = 'دسته فعالیت'

    def activity_field(self, obj):
        return obj.activity.field
    activity_field.short_description = 'حوزه'

    def activity_duration(self, obj):
        return f"{obj.activity.duration_days} روز"
    activity_duration.short_description = 'مدت فعالیت'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('stage', 'activity', 'stage__roadmap')


# =========================
# RoadmapActivity Admin
# =========================
@admin.register(RoadmapActivity)
class RoadmapActivityAdmin(admin.ModelAdmin):
    list_display = [
        'profile',
        'activity',
        'stage_activity',
        'stage_title',
        'roadmap_title',
        'created_at',
    ]
    list_filter = [
        'activity__category',
        'activity__field',
        'created_at',
    ]
    search_fields = [
        'profile__first_name',
        'profile__last_name',
        'profile__user__username',
        'activity__title',
        'stage_activity__stage__title',
        'stage_activity__stage__roadmap__title',
    ]
    autocomplete_fields = ['profile', 'activity', 'stage_activity']
    readonly_fields = ['created_at']
    list_per_page = 30

    fieldsets = (
        ('اطلاعات ثبت رزومه', {
            'fields': (
                'profile',
                'activity',
                'stage_activity',
            )
        }),
        ('زمان ثبت', {
            'fields': (
                'created_at',
            )
        }),
    )

    def stage_title(self, obj):
        return obj.stage_activity.stage.title if obj.stage_activity else "-"
    stage_title.short_description = 'مرحله'

    def roadmap_title(self, obj):
        if obj.stage_activity and obj.stage_activity.stage and obj.stage_activity.stage.roadmap:
            return obj.stage_activity.stage.roadmap.title
        return "-"
    roadmap_title.short_description = 'رودمپ'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'profile',
            'activity',
            'stage_activity',
            'stage_activity__stage',
            'stage_activity__stage__roadmap',
        )
