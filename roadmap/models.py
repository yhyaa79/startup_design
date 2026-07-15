# roadmap/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import json

class Roadmap(models.Model):
    """نقشه راه اصلی کاربر"""
    
    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('active', 'فعال'),
        ('completed', 'تکمیل‌شده'),
        ('paused', 'متوقف'),
    ]
    
    GOAL_CHOICES = [
        ('estedad_darakhshan', 'استعداد درخشان'),
        ('40_emtiaz', '۴۰ امتیازی'),
        ('heyat_elmi', 'هیات علمی'),
        ('research_position', 'ریسرچ پوزیشن / فلوشیپ خارج'),
        ('general', 'بهبود عمومی'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roadmaps')
    title = models.CharField(max_length=255, verbose_name='عنوان رودمپ')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    goal = models.CharField(max_length=50, choices=GOAL_CHOICES, verbose_name='هدف')
    goal_details = models.TextField(blank=True, null=True, verbose_name='جزئیات هدف')
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft',
        verbose_name='وضعیت'
    )
    
    # تایمینگ
    duration_days = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(1095)],
        verbose_name='مدت زمان (روز)'
    )
    start_date = models.DateField(auto_now_add=True, verbose_name='تاریخ شروع')
    target_end_date = models.DateField(verbose_name='تاریخ هدف')
    
    # AI
    ai_generated = models.BooleanField(default=False, verbose_name='تولید شده توسط AI')
    ai_prompt = models.TextField(blank=True, null=True, verbose_name='prompt AI')
    ai_analysis = models.JSONField(default=dict, blank=True, verbose_name='تحلیل AI')
    
    # امتیازدهی
    total_score = models.FloatField(default=0, verbose_name='امتیاز کل')
    score_breakdown = models.JSONField(default=dict, blank=True, verbose_name='تفکیک امتیاز')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'نقشه راه'
        verbose_name_plural = 'نقشه‌های راه'
    
    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"
    
    def get_progress(self):
        """درصد پیشرفت رودمپ"""
        stages = self.stages.all()
        if not stages:
            return 0
        total = sum(stage.get_progress() for stage in stages)
        return int(total / stages.count())
    
    def get_active_stage(self):
        """مرحله فعلی"""
        return self.stages.filter(status='active').first()
    
    def get_remaining_days(self):
        """روزهای باقی‌مانده"""
        from datetime import date
        remaining = (self.target_end_date - date.today()).days
        return max(0, remaining)


class Stage(models.Model):
    """مراحل رودمپ"""
    
    STATUS_CHOICES = [
        ('upcoming', 'در انتظار'),
        ('active', 'در حال انجام'),
        ('completed', 'تکمیل‌شده'),
    ]
    
    PHASE_TYPE_CHOICES = [
        ('foundation', 'بنیادی'),
        ('development', 'توسعه'),
        ('optimization', 'بهینه‌سازی'),
        ('execution', 'اجرا'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'زیاد'),
    ]
    
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='stages')
    order = models.PositiveIntegerField(verbose_name='ترتیب')
    
    title = models.CharField(max_length=255, verbose_name='عنوان مرحله')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    objectives = models.TextField(blank=True, null=True, verbose_name='اهداف')
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='upcoming',
        verbose_name='وضعیت'
    )
    
    phase_type = models.CharField(
        max_length=20,
        choices=PHASE_TYPE_CHOICES,
        blank=True,
        null=True,
        verbose_name='نوع فاز'
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name='اولویت'
    )
    
    # تایمینگ
    duration_days = models.PositiveIntegerField(verbose_name='مدت زمان (روز)')
    start_date = models.DateField(verbose_name='تاریخ شروع')
    end_date = models.DateField(verbose_name='تاریخ پایان')
    
    # معیارهای موفقیت
    milestone = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='نقطه عطف (معیار تکمیل)'
    )
    success_criteria = models.JSONField(default=list, blank=True, verbose_name='معیارهای موفقیت')
    risks = models.JSONField(default=list, blank=True, verbose_name='ریسک‌های احتمالی')
    recommended_resources = models.JSONField(default=list, blank=True, verbose_name='منابع پیشنهادی')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['roadmap', 'order']
        verbose_name = 'مرحله'
        verbose_name_plural = 'مراحل'
        unique_together = ('roadmap', 'order')
    
    def __str__(self):
        return f"مرحله {self.order}: {self.title}"
    
    def get_progress(self):
        """درصد پیشرفت مرحله"""
        activities = self.stage_activities.all()
        if not activities:
            return 0
        completed = activities.filter(is_completed=True).count()
        return int((completed / activities.count()) * 100)
    
    def get_remaining_days(self):
        """روزهای باقی‌مانده"""
        from datetime import date
        remaining = (self.end_date - date.today()).days
        return max(0, remaining)
    
    def get_total_duration(self):
        """مجموع مدت زمان فعالیت‌ها"""
        return sum(
            sa.activity.duration_days 
            for sa in self.stage_activities.all()
        )


class Activity(models.Model):
    """فعالیت‌های موجود در سیستم"""
    
    CATEGORY_CHOICES = [
        ('course', 'دوره آموزشی'),
        ('event', 'رویداد / کنگره'),
        ('project', 'پروژه'),
        ('research', 'تحقیق / مقاله'),
    ]
    
    IMPACT_CHOICES = [
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'زیاد'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'آسان'),
        ('medium', 'متوسط'),
        ('hard', 'دشوار'),
    ]
    
    # شناسایی
    external_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='شناسه خارجی'
    )
    
    title = models.CharField(max_length=255, verbose_name='عنوان')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name='دسته'
    )
    
    # جزئیات
    duration_days = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        verbose_name='مدت زمان (روز)'
    )
    
    impact_score = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='امتیاز تاثیر'
    )
    
    difficulty_rating = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='medium',
        verbose_name='سطح دشواری'
    )
    
    impact_level = models.CharField(
        max_length=10,
        choices=IMPACT_CHOICES,
        default='medium',
        verbose_name='سطح تاثیر'
    )
    
    # خروجی
    resume_output = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='خروجی رزومه'
    )
    
    profile_template = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='الگو برای پروفایل',
        help_text='{"model": "articles", "fields": {...}}'
    )
    
    # اضافی
    organizer = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='برگزارکننده'
    )
    
    level = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='سطح (دانشگاهی/ملی/بین‌المللی)'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'title']
        verbose_name = 'فعالیت'
        verbose_name_plural = 'فعالیت‌ها'
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class StageActivity(models.Model):
    """ارتباط بین مراحل و فعالیت‌ها"""
    
    stage = models.ForeignKey(
        Stage,
        on_delete=models.CASCADE,
        related_name='stage_activities'
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='stage_activities'
    )
    
    order = models.PositiveIntegerField(verbose_name='ترتیب')
    is_completed = models.BooleanField(default=False, verbose_name='تکمیل‌شده')
    completion_date = models.DateField(blank=True, null=True, verbose_name='تاریخ تکمیل')
    
    # ثبت در پروفایل
    saved_to_profile = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('articles', 'مقالات'),
            ('presentations', 'ارائه‌ها'),
            ('executive_records', 'سوابق اجرایی'),
            ('training_courses', 'دوره‌های آموزشی'),
        ],
        verbose_name='ثبت شده در'
    )
    
    profile_data = models.JSONField(default=dict, blank=True, verbose_name='داده‌های پروفایل')
    
    # ✅ فیلدهای جدید برای جزئیات فعالیت
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name='درصد پیشرفت'
    )
    
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    
    actual_start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاریخ شروع واقعی'
    )
    
    actual_end_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='تاریخ پایان واقعی'
    )
    
    # ✅ فیلد برای ذخیره انتخاب از STATIC_ITEMS
    static_item_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='شناسه آیتم ثابت'
    )
    
    static_item_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='داده‌های آیتم ثابت'
    )
    
    # ✅ فیلد برای نوع فعالیت (ثابت یا دستی)
    activity_source = models.CharField(
        max_length=20,
        choices=[
            ('static', 'از لیست ثابت'),
            ('custom', 'دستی ایجاد شده'),
        ],
        default='custom',
        verbose_name='منبع فعالیت'
    )
    
    # ✅ فیلد برای checkpoints
    checkpoints = models.JSONField(
        default=list,
        blank=True,
        verbose_name='نقاط کنترل',
        help_text=(
            '[{"id": 1, "source_type": "manual|course|project", "title": "...", '
            '"description": "...", "priority": "low|medium|high", "due_date": null, '
            '"notes": "...", "source_id": null, "source_url": null, '
            '"is_completed": false, "date": null}]'
        )
    )
    
    # ✅ فیلد برای منابع
    resources = models.JSONField(
        default=list,
        blank=True,
        verbose_name='منابع',
        help_text='[{"title": "...", "url": "...", "type": "link"}]'
    )
    
    # ✅ فیلد برای نتایج
    result_summary = models.TextField(
        blank=True,
        null=True,
        verbose_name='خلاصه نتایج'
    )
    
    outcome_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='داده‌های نتیجه'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['stage', 'order']
        verbose_name = 'فعالیت مرحله'
        verbose_name_plural = 'فعالیت‌های مرحله'
        unique_together = ('stage', 'activity', 'order')
    
    def __str__(self):
        return f"{self.stage.title} - {self.activity.title}"
    
    def get_remaining_days(self):
        """روزهای باقی‌مانده"""
        from datetime import date
        end_date = self.actual_end_date or self.stage.end_date
        remaining = (end_date - date.today()).days
        return max(0, remaining)
    
    def is_overdue(self):
        """آیا تاخیر دارد"""
        from datetime import date
        if self.is_completed:
            return False
        end_date = self.actual_end_date or self.stage.end_date
        return date.today() > end_date


class RoadmapTemplate(models.Model):
    """الگوهای آماده رودمپ"""
    
    goal = models.CharField(max_length=50, unique=True, verbose_name='هدف')
    title = models.CharField(max_length=255, verbose_name='عنوان الگو')
    description = models.TextField(verbose_name='توضیحات')
    
    # ساختار
    template_data = models.JSONField(verbose_name='داده‌های الگو')
    
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'الگوی رودمپ'
        verbose_name_plural = 'الگوهای رودمپ'
    
    def __str__(self):
        return self.title
