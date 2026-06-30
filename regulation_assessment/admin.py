# regulation_assessment/admin.py

from django.contrib import admin
from .models import UserVideoInterest

@admin.register(UserVideoInterest)
class UserVideoInterestAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone', 'email', 'total_score', 'course_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['first_name', 'last_name', 'phone', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('first_name', 'last_name', 'phone', 'email')
        }),
        ('اطلاعات امتیازات', {
            'fields': ('total_score', 'breakdown')
        }),
        ('دوره‌های درخواستی', {
            'fields': ('requested_courses',)
        }),
        ('تاریخ‌ها', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def course_count(self, obj):
        return len(obj.requested_courses)
    course_count.short_description = 'تعداد دوره‌ها'
