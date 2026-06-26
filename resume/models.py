# resume/models.py

from django.db import models
from django.contrib.auth.models import User


TEMPLATE_CHOICES = [
    ('classic', 'کلاسیک حرفه‌ای'),
    ('modern', 'مدرن دو ستونه'),
    ('academic', 'آکادمیک پژوهشی'),
    ('minimal', 'مینیمال'),
]

PURPOSE_CHOICES = [
    ('residency', 'رزیدنتی / استعداد درخشان'),
    ('faculty', 'هیات علمی'),
    ('fellowship', 'فلوشیپ / ریسرچ پوزیشن خارج'),
    ('job', 'بازار کار بالینی'),
    ('general', 'عمومی'),
]


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField('عنوان رزومه', max_length=200, default='رزومه من')
    purpose = models.CharField('هدف رزومه', max_length=50, choices=PURPOSE_CHOICES, default='general')
    template = models.CharField('قالب رزومه', max_length=30, choices=TEMPLATE_CHOICES, default='classic')
    use_ai = models.BooleanField('استفاده از AI', default=False)
    ai_enhanced = models.BooleanField('بهبود یافته با AI', default=False)

    # Sections to include
    include_education = models.BooleanField('تحصیلات', default=True)
    include_articles = models.BooleanField('مقالات', default=True)
    include_presentations = models.BooleanField('ارائه‌ها', default=True)
    include_executive = models.BooleanField('سوابق اجرایی', default=True)
    include_training = models.BooleanField('دوره‌های آموزشی', default=True)
    include_clinical = models.BooleanField('سوابق بالینی', default=True)
    include_languages = models.BooleanField('زبان‌ها', default=True)
    include_skills = models.BooleanField('مهارت‌ها', default=True)
    include_extracurricular = models.BooleanField('فعالیت‌های فوق برنامه', default=True)

    # AI-generated content (stored if AI is used)
    ai_summary = models.TextField('خلاصه حرفه‌ای (AI)', blank=True)

    # Generated files
    pdf_file = models.FileField('فایل PDF', upload_to='resumes/pdf/', blank=True, null=True)
    docx_file = models.FileField('فایل Word', upload_to='resumes/docx/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'رزومه'
        verbose_name_plural = 'رزومه‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} - {self.user.get_full_name()}'