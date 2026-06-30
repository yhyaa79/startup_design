# activity/models.py

from django.db import models
from django.contrib.auth.models import User
from roadmap.models import Roadmap, Stage, Activity, StageActivity
from django.utils.translation import gettext_lazy as _

class ActivityLog(models.Model):
    """at_ActivityLog - ثبت فعالیت‌های کاربر"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('in_progress', 'در حال انجام'),
        ('completed', 'تکمیل‌شده'),
        ('paused', 'متوقف'),
        ('cancelled', 'لغو شده'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='activity_logs')
    stage = models.ForeignKey(Stage, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE, related_name='activity_logs')
    stage_activity = models.ForeignKey(StageActivity, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='وضعیت'
    )
    
    # تاریخ‌ها
    start_date = models.DateField(auto_now_add=True, verbose_name='تاریخ شروع')
    target_completion_date = models.DateField(verbose_name='تاریخ هدف تکمیل')
    actual_completion_date = models.DateField(null=True, blank=True, verbose_name='تاریخ واقعی تکمیل')
    
    # پیشرفت
    progress_percentage = models.PositiveIntegerField(
        default=0,
        verbose_name='درصد پیشرفت'
    )
    
    # یادداشت‌ها
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    
    # نتایج
    result_summary = models.TextField(blank=True, null=True, verbose_name='خلاصه نتایج')
    outcome_data = models.JSONField(default=dict, blank=True, verbose_name='داده‌های نتیجه')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'ثبت فعالیت'
        verbose_name_plural = 'ثبت‌های فعالیت'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['roadmap', 'status']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.activity.title}"
    
    def get_remaining_days(self):
        """روزهای باقی‌مانده"""
        from datetime import date
        remaining = (self.target_completion_date - date.today()).days
        return max(0, remaining)
    
    def is_overdue(self):
        """آیا تاخیر دارد"""
        from datetime import date
        return self.status != 'completed' and date.today() > self.target_completion_date


class ActivityCheckpoint(models.Model):
    """at_ActivityCheckpoint - نقاط کنترل فعالیت"""
    
    activity_log = models.ForeignKey(
        ActivityLog,
        on_delete=models.CASCADE,
        related_name='checkpoints',
        verbose_name='ثبت فعالیت'
    )
    
    title = models.CharField(max_length=255, verbose_name='عنوان نقطه کنترل')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    
    is_completed = models.BooleanField(default=False, verbose_name='تکمیل‌شده')
    completion_date = models.DateField(null=True, blank=True, verbose_name='تاریخ تکمیل')
    
    order = models.PositiveIntegerField(verbose_name='ترتیب')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['activity_log', 'order']
        verbose_name = 'نقطه کنترل فعالیت'
        verbose_name_plural = 'نقاط کنترل فعالیت'
        unique_together = ('activity_log', 'order')
    
    def __str__(self):
        return f"{self.activity_log.activity.title} - {self.title}"


class ActivityResource(models.Model):
    """at_ActivityResource - منابع فعالیت"""
    
    activity_log = models.ForeignKey(
        ActivityLog,
        on_delete=models.CASCADE,
        related_name='resources',
        verbose_name='ثبت فعالیت'
    )
    
    title = models.CharField(max_length=255, verbose_name='عنوان منبع')
    resource_type = models.CharField(
        max_length=50,
        choices=[
            ('link', 'لینک'),
            ('file', 'فایل'),
            ('book', 'کتاب'),
            ('course', 'دوره'),
            ('other', 'سایر'),
        ],
        verbose_name='نوع منبع'
    )
    
    url = models.URLField(blank=True, null=True, verbose_name='آدرس')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'منبع فعالیت'
        verbose_name_plural = 'منابع فعالیت'
    
    def __str__(self):
        return f"{self.activity_log.activity.title} - {self.title}"
