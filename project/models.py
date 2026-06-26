# project/models.py

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import Profile


class ResearchProject(models.Model):
    CATEGORY_CHOICES = [
        ('clinical', 'بالینی'),
        ('basic_science', 'علوم پایه'),
        ('systematic_review', 'مرور سیستماتیک / متاآنالیز'),
        ('case_report', 'گزارش مورد'),
        ('epidemiology', 'اپیدمیولوژی'),
        ('public_health', 'سلامت عمومی'),
        ('medical_education', 'آموزش پزشکی'),
        ('ai_health', 'هوش مصنوعی در سلامت'),
        ('other', 'سایر'),
    ]

    STATUS_CHOICES = [
        ('idea', 'ایده اولیه'),
        ('proposal', 'در مرحله پروپوزال'),
        ('ethics', 'در انتظار کد اخلاق'),
        ('collecting_data', 'جمع‌آوری داده'),
        ('analysis', 'تحلیل داده'),
        ('writing', 'نگارش مقاله'),
        ('submitted', 'سابمیت شده'),
        ('published', 'منتشر شده'),
        ('paused', 'متوقف / غیرفعال'),
    ]

    COLLABORATION_CHOICES = [
        ('open', 'جذب همکار فعال'),
        ('limited', 'جذب محدود'),
        ('closed', 'عدم جذب همکار'),
    ]

    VISIBILITY_CHOICES = [
        ('public', 'عمومی'),
        ('private', 'خصوصی'),
    ]

    owner_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_research_projects',
        verbose_name='کاربر ثبت‌کننده'
    )
    owner_profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='research_projects',
        verbose_name='پروفایل ثبت‌کننده'
    )

    title = models.CharField('عنوان پروژه', max_length=300)
    slug = models.SlugField('اسلاگ', max_length=350, unique=True, allow_unicode=True)
    short_description = models.CharField('توضیح کوتاه', max_length=500)
    description = models.TextField('توضیحات کامل')

    category = models.CharField('دسته‌بندی', max_length=40, choices=CATEGORY_CHOICES)
    status = models.CharField('وضعیت پروژه', max_length=40, choices=STATUS_CHOICES)
    collaboration_status = models.CharField(
        'وضعیت جذب همکار',
        max_length=20,
        choices=COLLABORATION_CHOICES,
        default='open'
    )
    visibility = models.CharField(
        'نمایش',
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='public'
    )

    field = models.CharField('حوزه تخصصی', max_length=200, blank=True)
    keywords = models.CharField('کلیدواژه‌ها', max_length=300, blank=True)
    methodology = models.TextField('روش انجام / متدولوژی', blank=True)
    required_skills = models.TextField('مهارت‌های موردنیاز همکار', blank=True)
    expected_output = models.CharField(
        'خروجی مورد انتظار',
        max_length=250,
        blank=True,
        help_text='مثلاً مقاله، پوستر، ارائه، پروپوزال، گرانت'
    )

    supervisor = models.CharField('استاد راهنما / مسئول علمی', max_length=200, blank=True)
    institution = models.CharField('دانشگاه / مرکز تحقیقاتی', max_length=200, blank=True)
    ethics_code = models.CharField('کد اخلاق', max_length=100, blank=True)

    start_date = models.CharField('تاریخ شروع', max_length=20, blank=True)
    estimated_end_date = models.CharField('تاریخ پایان تقریبی', max_length=20, blank=True)

    capacity = models.PositiveSmallIntegerField('ظرفیت جذب همکار', null=True, blank=True)
    views_count = models.PositiveIntegerField('تعداد بازدید', default=0)

    is_featured = models.BooleanField('ویژه', default=False)
    is_active = models.BooleanField('فعال', default=True)

    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'پروژه / تحقیق'
        verbose_name_plural = 'پروژه‌ها و تحقیقات'
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['status', 'category']),
            models.Index(fields=['visibility', 'is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project:detail', kwargs={'slug': self.slug})

    @property
    def is_open_for_collaboration(self):
        return self.collaboration_status in ['open', 'limited']


class ProjectMember(models.Model):
    ROLE_CHOICES = [
        ('principal_investigator', 'مجری اصلی'),
        ('supervisor', 'استاد راهنما'),
        ('co_researcher', 'همکار پژوهشی'),
        ('data_collector', 'جمع‌آوری داده'),
        ('statistician', 'تحلیل‌گر آماری'),
        ('writer', 'نویسنده'),
        ('translator', 'مترجم'),
        ('other', 'سایر'),
    ]

    project = models.ForeignKey(
        ResearchProject,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='پروژه'
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='project_memberships',
        verbose_name='پروفایل'
    )
    role = models.CharField('نقش', max_length=40, choices=ROLE_CHOICES)
    contribution = models.TextField('شرح همکاری', blank=True)
    joined_at = models.DateTimeField('تاریخ عضویت', auto_now_add=True)

    class Meta:
        verbose_name = 'عضو پروژه'
        verbose_name_plural = 'اعضای پروژه'
        unique_together = ('project', 'profile')

    def __str__(self):
        return f'{self.profile} - {self.project}'


class ProjectApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار بررسی'),
        ('accepted', 'پذیرفته شده'),
        ('rejected', 'رد شده'),
    ]

    project = models.ForeignKey(
        ResearchProject,
        on_delete=models.CASCADE,
        related_name='applications',
        verbose_name='پروژه'
    )
    applicant_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_applications',
        verbose_name='کاربر متقاضی'
    )
    applicant_profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='project_applications',
        verbose_name='پروفایل متقاضی'
    )
    message = models.TextField('پیام درخواست همکاری')
    skills = models.TextField('مهارت‌ها و تجربه مرتبط', blank=True)
    status = models.CharField('وضعیت درخواست', max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField('تاریخ درخواست', auto_now_add=True)
    updated_at = models.DateTimeField('آخرین بروزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'درخواست همکاری'
        verbose_name_plural = 'درخواست‌های همکاری'
        ordering = ['-created_at']
        unique_together = ('project', 'applicant_profile')

    def __str__(self):
        return f'{self.applicant_profile} -> {self.project}'


class ProjectUpdate(models.Model):
    project = models.ForeignKey(
        ResearchProject,
        on_delete=models.CASCADE,
        related_name='updates',
        verbose_name='پروژه'
    )
    title = models.CharField('عنوان بروزرسانی', max_length=200)
    text = models.TextField('متن بروزرسانی')
    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)

    class Meta:
        verbose_name = 'بروزرسانی پروژه'
        verbose_name_plural = 'بروزرسانی‌های پروژه'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class ProjectFile(models.Model):
    project = models.ForeignKey(
        ResearchProject,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='پروژه'
    )
    title = models.CharField('عنوان فایل', max_length=200)
    file = models.FileField('فایل', upload_to='project_files/%Y/%m/')
    uploaded_at = models.DateTimeField('تاریخ آپلود', auto_now_add=True)

    class Meta:
        verbose_name = 'فایل پروژه'
        verbose_name_plural = 'فایل‌های پروژه'

    def __str__(self):
        return self.title
