# event_hub/models.py


from django.db import models


class Event(models.Model):
    title = models.CharField('عنوان رویداد', max_length=300)
    slug = models.SlugField('اسلاگ', unique=True)
    section = models.CharField('بخش', max_length=100, blank=True)
    short_description = models.TextField('توضیح کوتاه', blank=True)
    compiler = models.CharField('تهیه‌کننده', max_length=200, blank=True)

    audience = models.JSONField('مخاطبان', default=list, blank=True)
    goal = models.TextField('هدف', blank=True)
    resume_impact = models.CharField('اثر در رزومه', max_length=50, blank=True)
    activity_type = models.CharField('نوع فعالیت', max_length=200, blank=True)

    activity_level = models.CharField('سطح فعالیت', max_length=200, blank=True)
    difficulty = models.CharField('سطح دشواری', max_length=50, blank=True)
    main_advantage = models.TextField('مزیت اصلی', blank=True)
    suitable_for = models.TextField('مناسب برای', blank=True)
    required_time = models.CharField('زمان موردنیاز', max_length=200, blank=True)

    intro = models.TextField('معرفی کامل', blank=True)
    research_audiences = models.JSONField('مخاطبان پژوهشی', default=list, blank=True)
    skills_learned = models.JSONField('مهارت‌های آموخته‌شده', default=list, blank=True)

    completion_steps = models.JSONField('مراحل تکمیل', default=list, blank=True)
    terms_and_conditions = models.JSONField('شرایط و ضوابط', default=list, blank=True)
    benefits = models.JSONField('مزایا', default=dict, blank=True)
    common_mistakes = models.JSONField('اشتباهات رایج', default=list, blank=True)
    practical_recommendations = models.JSONField('توصیه‌های کاربردی', default=list, blank=True)
    similar_opportunities = models.JSONField('فرصت‌های مشابه', default=list, blank=True)
    inline_cta_buttons = models.JSONField('دکمه‌های میان‌خطی', default=list, blank=True)
    page_cta_buttons = models.JSONField('دکمه‌های صفحه', default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'رویداد'
        verbose_name_plural = 'رویدادها'
        ordering = ['title']

    def __str__(self):
        return self.title
