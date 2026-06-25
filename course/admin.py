# course/admin.py

from django.contrib import admin
from .models import Course, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'instructor', 'duration', 'active')
    list_filter = ('active', 'category', 'stars')
    search_fields = ('title', 'instructor', 'short_desc')
    list_editable = ('active',)