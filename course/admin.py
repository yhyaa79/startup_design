# course/admin.py

from django.contrib import admin
from .models import Category, Course


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'course_count')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order',)

    def course_count(self, obj):
        return obj.courses.count()
    course_count.short_description = 'تعداد دوره‌ها'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'course_id', 'category', 'instructor',
        'has_discount', 'active', 'view_count', 'created_at',
    )
    list_filter = ('category', 'active')
    search_fields = ('title', 'course_id', 'instructor', 'short_desc')
    list_editable = ('active',)
    readonly_fields = ('view_count', 'created_at', 'updated_at')
    ordering = ('category__order', '-created_at')

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('course_id', 'title', 'category', 'instructor', 'active')
        }),
        ('توضیحات', {
            'fields': ('short_desc', 'long_desc')
        }),
        ('قیمت و امتیاز', {
            'fields': ('stars', 'duration', 'main_price', 'discount_price', 'percentage')
        }),
        ('رسانه', {
            'fields': ('thumbnail', 'video_link')
        }),
        ('آمار', {
            'fields': ('view_count', 'created_at', 'updated_at')
        }),
    )

    def has_discount(self, obj):
        return obj.has_discount()
    has_discount.boolean = True
    has_discount.short_description = 'تخفیف دارد'
