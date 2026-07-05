# core/models.py

from django.db import models
from django.conf import settings
from django.urls import reverse, NoReverseMatch


class DailyOnlineActivity(models.Model):
    """هر رکورد = فعالیت آنلاین یک کاربر در یک روز مشخص."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='online_activities')
    date = models.DateField()
    duration_minutes = models.PositiveIntegerField(default=0)
    session_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user} - {self.date} - {self.duration_minutes}m"


class Tool(models.Model):
    """
    ابزارهای جدید داشبورد — هر ابزار متعلق به یک اپ دیگر است (مثل
    regulation_assessment) و فقط لینک/متادیتای نمایش آن اینجا ثبت می‌شود.
    """
    title = models.CharField('عنوان', max_length=150)
    description = models.CharField('توضیح کوتاه', max_length=300, blank=True)

    # اگر ابزار یک URL name نام‌گذاری‌شده در پروژه دارد (مثل
    # "regulation_assessment:evaluation_form") این را پر کنید.
    url_name = models.CharField(
        'نام URL (namespace:name)', max_length=150, blank=True,
        help_text='مثال: regulation_assessment:evaluation_form'
    )
    # اگر لینک بیرونی یا مسیر ثابت است (وقتی url_name خالی/نامعتبر باشد)
    external_url = models.CharField('لینک جایگزین / ثابت', max_length=300, blank=True)

    icon_svg = models.TextField(
        'کد SVG آیکون', blank=True,
        help_text='محتوای داخل تگ <svg>...</svg> را بدون تگ بیرونی paste کنید.'
    )

    is_active = models.BooleanField('فعال', default=True)
    is_new = models.BooleanField('برچسب «جدید»', default=True)
    order = models.PositiveIntegerField('ترتیب نمایش', default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'ابزار'
        verbose_name_plural = 'ابزارها'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    def get_url(self):
        if self.url_name:
            try:
                return reverse(self.url_name)
            except NoReverseMatch:
                pass
        return self.external_url or '#'
