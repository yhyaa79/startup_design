# project/admin.py

from django.contrib import admin
from .models import (
    ResearchProject,
    ProjectMember,
    ProjectApplication,
    ProjectUpdate,
    ProjectFile,
)


class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 0


class ProjectUpdateInline(admin.TabularInline):
    model = ProjectUpdate
    extra = 0


class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    extra = 0


@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'owner_profile',
        'category',
        'status',
        'collaboration_status',
        'visibility',
        'is_featured',
        'is_active',
        'created_at',
    ]
    list_filter = [
        'category',
        'status',
        'collaboration_status',
        'visibility',
        'is_featured',
        'is_active',
        'created_at',
    ]
    search_fields = [
        'title',
        'short_description',
        'description',
        'keywords',
        'owner_profile__first_name',
        'owner_profile__last_name',
    ]
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    inlines = [ProjectMemberInline, ProjectUpdateInline, ProjectFileInline]


@admin.register(ProjectApplication)
class ProjectApplicationAdmin(admin.ModelAdmin):
    list_display = ['project', 'applicant_profile', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = [
        'project__title',
        'applicant_profile__first_name',
        'applicant_profile__last_name',
        'message',
    ]


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ['project', 'profile', 'role', 'joined_at']
    list_filter = ['role', 'joined_at']
    search_fields = ['project__title', 'profile__first_name', 'profile__last_name']


@admin.register(ProjectUpdate)
class ProjectUpdateAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'created_at']
    search_fields = ['title', 'text', 'project__title']


@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'uploaded_at']
    search_fields = ['title', 'project__title']
