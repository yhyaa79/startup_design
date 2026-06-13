# roadmap/models.py

from django.db import models
from django.contrib.auth.models import User
from accounts.models import Profile
from django.core.validators import MinValueValidator, MaxValueValidator


class Activity(models.Model):
    """فعالیت‌های پیش‌فرض که کاربران می‌توانند در مراحل رود‌مپ استفاده کنند"""
    CATEGORY_CHOICES = [
        ('پژوهشی', 'پژوهشی'),
        ('بالینی', 'بالینی'),
        ('آموزشی', 'آموزشی'),
        ('نرم‌افزاری', 'نرم‌افزاری'),
        ('زبان', 'زبان'),
        ('سایر', 'سایر'),
    ]

    title = models.CharField('عنوان فعالیت', max_length=300)
    description = models.TextField('توضیح فعالیت', blank=True)
    category = models.CharField('دسته', max_length=30, choices=CATEGORY_CHOICES)
    duration_hours = models.PositiveIntegerField('مدت زمان (ساعت)')
    difficulty_level = models.CharField(
        'سطح دشواری',
        max_length=20,
        choices=[('آسان', 'آسان'), ('متوسط', 'متوسط'), ('سخت', 'سخت')],
        default='متوسط'
    )
    is_active = models.BooleanField('فعال', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'فعالیت'
        verbose_name_plural = 'فعالیت‌ها'
        ordering = ['category', 'title']

    def __str__(self):
        return f'{self.title} ({self.duration_hours}h)'


class Roadmap(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='roadmap')
    title = models.CharField('عنوان رود‌مپ', max_length=300)
    description = models.TextField('توضیح رود‌مپ', blank=True)
    is_published = models.BooleanField('منتشر‌شده', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'رود‌مپ'
        verbose_name_plural = 'رود‌مپ‌ها'

    def __str__(self):
        return f'رود‌مپ {self.profile.first_name} {self.profile.last_name}'

    def get_total_progress(self):
        """محاسبه درصد پیشرفت کل رود‌مپ"""
        stages = self.stages.all()
        if not stages.exists():
            return 0
        total_progress = sum(stage.get_progress() for stage in stages)
        return int(total_progress / stages.count())

    def get_total_duration(self):
        """محاسبه کل زمان رود‌مپ"""
        return sum(stage.get_total_duration() for stage in self.stages.all())


class Stage(models.Model):
    STATUS_CHOICES = [
        ('پیش‌رو', 'پیش‌رو'),
        ('در حال انجام', 'در حال انجام'),
        ('تکمیل‌شده', 'تکمیل‌شده'),
    ]

    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='stages')
    title = models.CharField('عنوان مرحله', max_length=300)
    description = models.TextField('توضیح مرحله', blank=True)
    status = models.CharField('وضعیت مرحله', max_length=20, choices=STATUS_CHOICES, default='پیش‌رو')
    order = models.PositiveSmallIntegerField('ترتیب', default=0)
    objectives = models.TextField('اهداف مرحله')
    resume_output = models.TextField('خروجی رزومه‌ای', blank=True)
    start_date = models.DateField('تاریخ شروع', blank=True, null=True)
    end_date = models.DateField('تاریخ پایان', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'مرحله'
        verbose_name_plural = 'مراحل'
        ordering = ['roadmap', 'order']
        unique_together = ('roadmap', 'order')

    def __str__(self):
        return f'{self.roadmap.profile.first_name} - {self.title}'

    def get_total_duration(self):
        """محاسبه کل زمان این مرحله بر اساس فعالیت‌ها"""
        return sum(
            stage_activity.activity.duration_hours * stage_activity.repetition
            for stage_activity in self.stage_activities.all()
        )

    def get_progress(self):
        """محاسبه درصد پیشرفت این مرحله"""
        status_progress = {
            'پیش‌رو': 0,
            'در حال انجام': 50,
            'تکمیل‌شده': 100,
        }
        return status_progress.get(self.status, 0)

    def get_checklist_progress(self):
        """محاسبه درصد تکمیل چک‌لیست"""
        checklists = self.stage_activities.all()
        if not checklists.exists():
            return 0
        completed = checklists.filter(is_completed=True).count()
        return int((completed / checklists.count()) * 100)


class StageActivity(models.Model):
    """فعالیت‌های هر مرحله"""
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='stage_activities')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    repetition = models.PositiveSmallIntegerField('تعداد تکرار', default=1)
    is_completed = models.BooleanField('تکمیل‌شده', default=False)
    notes = models.TextField('یادداشت‌ها', blank=True)
    order = models.PositiveSmallIntegerField('ترتیب', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'فعالیت مرحله'
        verbose_name_plural = 'فعالیت‌های مرحله'
        ordering = ['stage', 'order']
        unique_together = ('stage', 'activity')

    def __str__(self):
        return f'{self.stage.title} - {self.activity.title}'

    def get_duration(self):
        """محاسبه زمان این فعالیت"""
        return self.activity.duration_hours * self.repetition
