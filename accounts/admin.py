# accounts/admin.py

from django.contrib import admin
from .models import (
    Profile,
    SocialProfile,
    Education,
    Article,
    Presentation,
    ExecutiveRecord,
    TrainingCourse,
)


class SocialProfileInline(admin.TabularInline):
    model = SocialProfile
    extra = 0


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class ArticleInline(admin.TabularInline):
    model = Article
    extra = 0
    fields = ('title', 'journal', 'quartile', 'impact_factor', 'year', 'author_rank', 'total_authors', 'index')


class PresentationInline(admin.TabularInline):
    model = Presentation
    extra = 0


class ExecutiveRecordInline(admin.TabularInline):
    model = ExecutiveRecord
    extra = 0


class TrainingCourseInline(admin.TabularInline):
    model = TrainingCourse
    extra = 0
    fields = ('title', 'category', 'status', 'organizer', 'date', 'certificate', 'skills_gained')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'gender', 'goal', 'english_level', 'created_at', 'raw_text')
    list_filter = ('gender', 'marital_status', 'military_status', 'goal', 'english_level', 'service_plan')
    search_fields = ('first_name', 'last_name', 'user__username', 'phone', 'email', 'national_id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [
        SocialProfileInline,
        EducationInline,
        ArticleInline,
        PresentationInline,
        ExecutiveRecordInline,
        TrainingCourseInline,
    ]
    fieldsets = (
        ('هویتی', {
            'fields': (
                'user', 'first_name', 'last_name', 'gender', 'marital_status',
                'military_status', 'job_title', 'birth_date', 'country', 'city',
                'phone', 'email', 'website', 'national_id',
            )
        }),
        ('پژوهشی', {
            'fields': (
                'orcid', 'proposal_count', 'proposal_status',
                'software_skills', 'writing_skills',
            )
        }),
        ('بالینی', {
            'fields': ('clinical_certs', 'clinical_exp', 'procedures')
        }),
        ('زبان', {
            'fields': ('native_lang', 'english_level', 'lang_cert', 'other_langs')
        }),
        ('فوق برنامه', {
            'fields': ('extracurricular',)
        }),
        ('اهداف', {
            'fields': ('goal', 'specialty', 'goal_notes', 'service_plan')
        }),
        ('زمان‌بندی', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
        ('متن خام پروفایل', {
            'fields': ('raw_text',)
        }),
    )


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'degree', 'field', 'university', 'uni_type', 'gpa', 'start_date', 'end_date')
    list_filter = ('degree', 'field', 'uni_type', 'stage')
    search_fields = ('profile__first_name', 'profile__last_name', 'university')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'journal', 'quartile', 'impact_factor', 'year', 'author_rank', 'index')
    list_filter = ('quartile', 'index', 'year')
    search_fields = ('title', 'journal', 'profile__first_name', 'profile__last_name')


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'event', 'level', 'result')
    list_filter = ('level', 'result')
    search_fields = ('title', 'event', 'profile__first_name', 'profile__last_name')


@admin.register(ExecutiveRecord)
class ExecutiveRecordAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'start_date', 'end_date')
    search_fields = ('title', 'profile__first_name', 'profile__last_name')


@admin.register(SocialProfile)
class SocialProfileAdmin(admin.ModelAdmin):
    list_display = ('profile', 'social_type', 'url')
    list_filter = ('social_type',)
    search_fields = ('profile__first_name', 'profile__last_name', 'url')


@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'category', 'status', 'organizer', 'date', 'certificate')
    list_filter = ('category', 'status', 'certificate')
    search_fields = ('title', 'organizer', 'skills_gained', 'profile__first_name', 'profile__last_name')
