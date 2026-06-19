# roadmap/models.py

from django.db import models
from django.contrib.auth.models import User
from accounts.models import Profile
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Activity(models.Model):
    """فعالیت‌های قابل انجام برای مراحل رود مپ"""
    CATEGORY_CHOICES = [
        ('پژوهشی', 'پژوهشی'),
        ('بالینی', 'بالینی'),
        ('آموزشی', 'آموزشی'),
        ('نرم‌افزاری', 'نرم‌افزاری'),
        ('زبان', 'زبان'),
        ('شبکه‌سازی', 'شبکه‌سازی'),
        ('توسعه‌شخصی', 'توسعه‌شخصی'),
        ('سایر', 'سایر'),
    ]
    
    FIELD_CHOICES = [
        ('پزشکی', 'پزشکی'),
        ('دندان‌پزشکی', 'دندان‌پزشکی'),
        ('داروسازی', 'داروسازی'),
        ('پرستاری', 'پرستاری'),
        ('فیزیوتراپی', 'فیزیوتراپی'),
        ('سایر', 'سایر'),
        ('عمومی', 'عمومی'),
    ]

    RESUME_TARGET_CHOICES = [
        ('article', 'مقاله'),
        ('presentation', 'ارائه'),
        ('training_course', 'دوره آموزشی'),
        ('executive_record', 'سابقه اجرایی'),
        ('skill', 'مهارت'),
    ]

    GOAL_CHOICES = [
        ('استعداد درخشان', 'استعداد درخشان'),
        ('۴۰ امتیازی', '۴۰ امتیازی'),
        ('هیات علمی', 'هیات علمی'),
        ('ریسرچ پوزیشن / فلوشیپ خارج', 'ریسرچ پوزیشن / فلوشیپ خارج'),
        ('عمومی', 'عمومی'),  # مناسب همه اهداف
    ]



    title = models.CharField('عنوان فعالیت', max_length=300)
    description = models.TextField('توضیح فعالیت')
    category = models.CharField('دسته', max_length=30, choices=CATEGORY_CHOICES)
    field = models.CharField('حوزه تخصصی', max_length=30, choices=FIELD_CHOICES)
    resume_target = models.CharField(
        max_length=30,
        choices=RESUME_TARGET_CHOICES,
        blank=True
    )
    profile_template = models.JSONField(
        blank=True,
        null=True,
        help_text="JSON template for saving activity into profile"
    )
    duration_days = models.PositiveSmallIntegerField(
        'مدت زمان (روز)',
        validators=[MinValueValidator(1), MaxValueValidator(365)],
        default=7
    )
    difficulty_level = models.CharField(
        'سطح سختی',
        max_length=10,
        choices=[('آسان', 'آسان'), ('متوسط', 'متوسط'), ('سخت', 'سخت')],
        default='متوسط'
    )
    resume_output = models.TextField('خروجی رزومه‌ای')
    prerequisites = models.TextField('پیش‌نیازها', blank=True)
    resources = models.TextField('منابع و مراجع', blank=True)
    is_active = models.BooleanField('فعال', default=True)
    suitable_goals = models.JSONField(
        'اهداف مناسب',
        default=list,
        blank=True,
        help_text='لیست اهدافی که این فعالیت برای آن‌ها مناسب است. خالی = مناسب همه اهداف'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'فعالیت'
        verbose_name_plural = 'فعالیت‌ها'
        ordering = ['category', 'title']

    def __str__(self):
        return f'{self.title} ({self.category})'


class Roadmap(models.Model):
    """رود مپ شخصی کاربر"""
    STATUS_CHOICES = [
        ('پیش‌نویس', 'پیش‌نویس'),
        ('فعال', 'فعال'),
        ('تکمیل‌شده', 'تکمیل‌شده'),
        ('متوقف‌شده', 'متوقف‌شده'),
    ]

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='roadmap')
    title = models.CharField('عنوان رود مپ', max_length=300)
    description = models.TextField('توضیح رود مپ', blank=True)
    status = models.CharField('وضعیت', max_length=20, choices=STATUS_CHOICES, default='پیش‌نویس')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'رود مپ'
        verbose_name_plural = 'رود مپ‌ها'

    def __str__(self):
        return f'{self.title} - {self.profile.first_name} {self.profile.last_name}'

    def get_total_progress(self):
        """محاسبه درصد پیشرفت کل رود مپ"""
        stages = self.stages.all()
        if not stages:
            return 0
        total_progress = sum(stage.get_progress() for stage in stages)
        return int(total_progress / stages.count()) if stages else 0

    def get_total_duration(self):
        """محاسبه کل مدت زمان رود مپ"""
        return sum(stage.get_total_duration() for stage in self.stages.all())


class Stage(models.Model):
    """مراحل رود مپ"""
    STATUS_CHOICES = [
        ('پیش‌رو', 'پیش‌رو'),
        ('در حال انجام', 'در حال انجام'),
        ('تکمیل‌شده', 'تکمیل‌شده'),
    ]

    PHASE_TYPE_CHOICES = [
        ('foundation', 'پایه‌ریزی'),
        ('development', 'توسعه'),
        ('advancement', 'پیشرفت'),
        ('excellence', 'تعالی'),
    ]
    
    PRIORITY_CHOICES = [
        ('critical', 'بحرانی'),
        ('high', 'بالا'),
        ('medium', 'متوسط'),
        ('low', 'پایین'),
    ]

    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='stages')
    title = models.CharField('عنوان مرحله', max_length=300)
    description = models.TextField('توضیح مرحله', blank=True)
    status = models.CharField('وضعیت مرحله', max_length=20, choices=STATUS_CHOICES, default='پیش‌رو')
    objectives = models.TextField('اهداف مرحله')
    order = models.PositiveSmallIntegerField('ترتیب', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phase_type = models.CharField(
        'نوع فاز',
        max_length=20,
        choices=[('foundation','پایه‌ریزی'),('development','توسعه'),
                 ('advancement','پیشرفت'),('excellence','تعالی')],
        default='development',
        blank=True,
    )
    priority = models.CharField(
        'اولویت',
        max_length=10,
        choices=[('critical','بحرانی'),('high','بالا'),('medium','متوسط'),('low','پایین')],
        default='medium',
        blank=True,
    )
    milestone = models.TextField(
        'نقطه عطف (معیار تکمیل)',
        blank=True,
        help_text='خروجی ملموسی که نشان‌دهنده تکمیل این مرحله است',
    )
    success_criteria = models.JSONField(
        'معیارهای موفقیت',
        default=list,
        blank=True,
        help_text='لیست معیارهای قابل سنجش برای تکمیل مرحله',
    )
    risks = models.JSONField(
        'ریسک‌ها',
        default=list,
        blank=True,
        help_text='ریسک‌های احتمالی این مرحله',
    )
    recommended_resources = models.JSONField(
        'منابع پیشنهادی',
        default=list,
        blank=True,
        help_text='منابع پیشنهادی AI برای این مرحله',
    )

    class Meta:
        verbose_name = 'مرحله'
        verbose_name_plural = 'مراحل'
        ordering = ['order']

    def __str__(self):
        return f'{self.roadmap.title} - {self.title}'

    def get_total_duration(self):
        """محاسبه کل مدت زمان مرحله بر اساس فعالیت‌های انتخاب‌شده"""
        return sum(item.activity.duration_days for item in self.stage_activities.all())

    def get_progress(self):
        """محاسبه درصد پیشرفت مرحله"""
        items = self.stage_activities.all()
        if not items:
            return 0
        completed = items.filter(is_completed=True).count()
        return int((completed / items.count()) * 100) if items else 0

    def get_resume_outputs(self):
        """دریافت خروجی‌های رزومه‌ای مرحله"""
        return [item.activity.resume_output for item in self.stage_activities.all()]

    def get_remaining_days(self):
        """تعداد روزهای باقی‌مانده از آخرین ویرایش مرحله"""
        total_duration = self.get_total_duration()
        passed_days = (timezone.now() - self.updated_at).days
        remaining_days = total_duration - passed_days
        return max(remaining_days, 0)


class StageActivity(models.Model):
    """فعالیت‌های انتخاب‌شده برای هر مرحله"""
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name='stage_activities')
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    is_completed = models.BooleanField('تکمیل‌شده', default=False)
    notes = models.TextField('یادداشت‌ها', blank=True)
    order = models.PositiveSmallIntegerField('ترتیب', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'فعالیت مرحله'
        verbose_name_plural = 'فعالیت‌های مرحله'
        ordering = ['order']
        unique_together = ['stage', 'activity']

    def __str__(self):
        return f'{self.stage.title} - {self.activity.title}'



class RoadmapActivity(models.Model):
    """
    فعالیتی که از طریق رودمپ تکمیل شده
    و در رزومه کاربر ثبت می‌شود
    """

    profile = models.ForeignKey(
        'accounts.Profile',
        on_delete=models.CASCADE,
        related_name='roadmap_activities'
    )

    activity = models.ForeignKey(
        'Activity',
        on_delete=models.CASCADE
    )

    stage_activity = models.OneToOneField(
        'StageActivity',
        on_delete=models.CASCADE,
        related_name='resume_record'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "فعالیت تکمیل شده رودمپ"
        verbose_name_plural = "فعالیت‌های تکمیل شده رودمپ"

    def __str__(self):
        return f"{self.profile} - {self.activity.title}"
