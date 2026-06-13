from django.contrib import admin
import nested_admin  # وارد کردن پکیج جدید
from .models import Activity, Roadmap, Stage, StageActivity

# 1. مدیریت مخزن فعالیت‌های اصلی (برای جستجو و تعریف اولیه)
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'field', 'duration_days', 'difficulty_level']
    search_fields = ['title']

# 2. اینلاین فعالیت‌های درونِ مرحله (سطح ۳)
class StageActivityInline(nested_admin.NestedTabularInline):
    model = StageActivity
    extra = 0
    sortable_field_name = "order"
    autocomplete_fields = ['activity'] # برای انتخاب سریع از فعالیت‌های تعریف شده


# 4. اینلاین مراحل درونِ رودمپ (سطح ۲)
class StageInline(nested_admin.NestedStackedInline):
    model = Stage
    extra = 0
    sortable_field_name = "order"
    # اینجا جادو اتفاق می‌افتد: اینلاین‌های سطح ۳ درون اینلاین سطح ۲ قرار می‌گیرند
    inlines = [StageActivityInline]

# 5. مدیریت اصلی رودمپ (سطح ۱)
@admin.register(Roadmap)
class RoadmapAdmin(nested_admin.NestedModelAdmin):
    list_display = ['title', 'profile', 'status', 'get_total_progress']
    list_filter = ['status']
    # اضافه کردن اینلاین مراحل که خودش شامل فعالیت‌هاست
    inlines = [StageInline]

    def get_total_progress(self, obj):
        return f"{obj.get_total_progress()}%"
    get_total_progress.short_description = 'پیشرفت کل'

# ثبت مدل‌های دیگر به صورت ساده (اختیاری)
admin.site.register(Stage) # اگر بخواهید جداگانه هم دسترسی داشته باشید
admin.site.register(StageActivity)
