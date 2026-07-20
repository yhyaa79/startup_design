# accounts/models.py


from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Profile(models.Model):
    GENDER_CHOICES = [('مرد', 'مرد'), ('زن', 'زن')]
    MARITAL_CHOICES = [('مجرد', 'مجرد'), ('متأهل', 'متأهل')]
    MILITARY_CHOICES = [
        ('', 'مربوط نیست'),
        ('معاف', 'معاف'),
        ('طرح پزشکی', 'طرح پزشکی'),
        ('سرباز', 'سرباز'),
        ('پایان خدمت', 'پایان خدمت'),
    ]
    SERVICE_PLAN_CHOICES = [
        ('', 'انتخاب کنید'),
        ('مشمول نیستم', 'مشمول نیستم'),
        ('در حال گذراندن', 'در حال گذراندن'),
        ('پایان یافته', 'پایان یافته'),
    ]
    PROPOSAL_STATUS_CHOICES = [
        ('', 'انتخاب کنید'),
        ('همه در جریان', 'همه در جریان'),
        ('همه خاتمه‌یافته', 'همه خاتمه‌یافته'),
        ('ترکیبی', 'ترکیبی (برخی در جریان، برخی خاتمه‌یافته)'),
    ]
    ENGLISH_LEVEL_CHOICES = [
        ('', 'انتخاب کنید'),
        ('A1', 'A1'), ('A2', 'A2'),
        ('B1', 'B1'), ('B2', 'B2'),
        ('C1', 'C1'), ('C2', 'C2'),
    ]
    GOAL_CHOICES = [
        ('استعداد درخشان', 'استعداد درخشان'),
        ('۴۰ امتیازی', '۴۰ امتیازی'),
        ('هیات علمی', 'هیات علمی'),
        ('ریسرچ پوزیشن / فلوشیپ خارج', 'ریسرچ پوزیشن / فلوشیپ خارج'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # --- هویتی ---
    first_name = models.CharField('نام', max_length=100)
    last_name = models.CharField('نام خانوادگی', max_length=100)
    gender = models.CharField('جنسیت', max_length=10, choices=GENDER_CHOICES, blank=True)
    marital_status = models.CharField('وضعیت تأهل', max_length=10, choices=MARITAL_CHOICES, blank=True)
    military_status = models.CharField('وضعیت سربازی', max_length=20, choices=MILITARY_CHOICES, blank=True)
    job_title = models.CharField('عنوان شغلی', max_length=150, blank=True)
    birth_date = models.CharField('تاریخ تولد', max_length=20)
    country = models.CharField('کشور', max_length=100, blank=True)
    city = models.CharField('استان / شهر محل سکونت', max_length=100, blank=True)
    phone = models.CharField('شماره موبایل', max_length=20)
    email = models.EmailField('ایمیل', blank=True)
    website = models.URLField('وب‌سایت شخصی', blank=True)
    national_id = models.CharField('کد ملی / شماره پاسپورت', max_length=20, blank=True)

    # --- پژوهشی ---
    orcid = models.CharField('شناسه ORCID', max_length=20, blank=True)
    proposal_count = models.PositiveSmallIntegerField('تعداد پروپوزال‌ها', null=True, blank=True)
    proposal_status = models.CharField('وضعیت پروپوزال‌ها', max_length=50, choices=PROPOSAL_STATUS_CHOICES, blank=True)
    software_skills = models.TextField('مهارت‌های نرم‌افزاری', blank=True)
    writing_skills = models.TextField('مهارت‌های نگارشی', blank=True)

    # --- بالینی ---
    clinical_certs = models.TextField('گواهینامه‌های مهارتی', blank=True)
    clinical_exp = models.TextField('سوابق کار دانشجویی و بالینی', blank=True)
    procedures = models.TextField('مهارت‌های پروسیجرال', blank=True)

    # --- زبان ---
    native_lang = models.CharField('زبان مادری', max_length=50, blank=True)
    english_level = models.CharField('سطح زبان انگلیسی', max_length=5, choices=ENGLISH_LEVEL_CHOICES, blank=True)
    lang_cert = models.TextField('مدرک زبان انگلیسی', blank=True)
    other_langs = models.TextField('سایر زبان‌ها', blank=True)

    # --- فوق برنامه ---
    extracurricular = models.TextField('فعالیت‌های فوق برنامه', blank=True)

    # --- اهداف ---
    goal = models.CharField('هدف نهایی حرفه‌ای', max_length=50, choices=GOAL_CHOICES)
    specialty = models.CharField('حوزه تخصصی', max_length=200, blank=True)
    goal_notes = models.TextField('توضیحات اهداف', blank=True)

    # --- طرح نیروی انسانی ---
    service_plan = models.CharField('وضعیت طرح نیروی انسانی', max_length=30, choices=SERVICE_PLAN_CHOICES, blank=True)

    # --- متن خام پروفایل ---
    raw_text = models.TextField('متن خام پروفایل', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'پروفایل'
        verbose_name_plural = 'پروفایل‌ها'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class SocialProfile(models.Model):
    SOCIAL_TYPE_CHOICES = [
        ('LinkedIn', 'LinkedIn'),
        ('GitHub', 'GitHub'),
        ('Google Scholar', 'Google Scholar'),
        ('ResearchGate', 'ResearchGate'),
        ('Dribbble', 'Dribbble'),
        ('Twitter / X', 'Twitter / X'),
        ('Instagram', 'Instagram'),
        ('سایر', 'سایر'),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='social_profiles')
    social_type = models.CharField('نوع شبکه', max_length=30, choices=SOCIAL_TYPE_CHOICES, blank=True)
    url = models.URLField('لینک پروفایل', blank=True)

    class Meta:
        verbose_name = 'پروفایل اجتماعی'
        verbose_name_plural = 'پروفایل‌های اجتماعی'


class Education(models.Model):
    FIELD_CHOICES = [
        ('پزشکی', 'پزشکی'), ('دندان‌پزشکی', 'دندان‌پزشکی'),
        ('داروسازی', 'داروسازی'), ('پرستاری', 'پرستاری'),
        ('فیزیوتراپی', 'فیزیوتراپی'), ('سایر', 'سایر'),
    ]
    DEGREE_CHOICES = [
        ('کارشناسی', 'کارشناسی'), ('کارشناسی ارشد', 'کارشناسی ارشد'),
        ('دکتری عمومی', 'دکتری عمومی'), ('دکتری تخصصی', 'دکتری تخصصی'),
    ]
    UNI_TYPE_CHOICES = [('تیپ ۱', 'تیپ ۱'), ('تیپ ۲', 'تیپ ۲'), ('تیپ ۳', 'تیپ ۳')]
    STAGE_CHOICES = [
        ('علوم پایه', 'علوم پایه'), ('فیزیوپات', 'فیزیوپات'),
        ('استاژری', 'استاژری'), ('اینترنی', 'اینترنی'),
        ('فارغ‌التحصیل', 'فارغ‌التحصیل'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='educations')
    field = models.CharField('رشته تحصیلی', max_length=30, choices=FIELD_CHOICES)
    degree = models.CharField('مقطع تحصیلی', max_length=20, choices=DEGREE_CHOICES)
    university = models.CharField('دانشگاه', max_length=200, blank=True)
    uni_type = models.CharField('تیپ دانشگاه', max_length=10, choices=UNI_TYPE_CHOICES, blank=True)
    start_date = models.CharField('تاریخ شروع', max_length=20, blank=True)
    end_date = models.CharField('تاریخ پایان', max_length=50, blank=True)
    stage = models.CharField('مرحله تحصیلی', max_length=20, choices=STAGE_CHOICES, blank=True)
    current_term = models.PositiveSmallIntegerField(
        'ترم فعلی', null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    remaining_terms = models.PositiveSmallIntegerField(
        'ترم‌های باقیمانده', null=True, blank=True,
        validators=[MaxValueValidator(20)]
    )
    gpa = models.DecimalField(
        'معدل', max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)]
    )

    class Meta:
        verbose_name = 'تحصیلات'
        verbose_name_plural = 'تحصیلات'
        ordering = ['start_date']


class Article(models.Model):
    QUARTILE_CHOICES = [('Q1', 'Q1'), ('Q2', 'Q2'), ('Q3', 'Q3'), ('Q4', 'Q4')]
    INDEX_CHOICES = [
        ('ISI / Web of Science', 'ISI / Web of Science'),
        ('Scopus', 'Scopus'),
        ('PubMed', 'PubMed'),
        ('ISI + Scopus', 'ISI + Scopus'),
        ('سایر', 'سایر'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField('عنوان مقاله', max_length=500, blank=True)
    journal = models.CharField('نام ژورنال', max_length=200, blank=True)
    impact_factor = models.DecimalField('Impact Factor', max_digits=6, decimal_places=3, null=True, blank=True)
    quartile = models.CharField('چارک', max_length=2, choices=QUARTILE_CHOICES, blank=True)
    year = models.PositiveSmallIntegerField(
        'سال چاپ', null=True, blank=True,
        validators=[MinValueValidator(1370), MaxValueValidator(1410)]
    )
    author_rank = models.PositiveSmallIntegerField('نفر چندم', null=True, blank=True)
    total_authors = models.PositiveSmallIntegerField('تعداد نویسندگان', null=True, blank=True)
    index = models.CharField('ایندکس', max_length=30, choices=INDEX_CHOICES, blank=True)

    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'
        ordering = ['-year']


class Presentation(models.Model):
    LEVEL_CHOICES = [
        ('بین‌المللی', 'بین‌المللی'), ('ملی', 'ملی'),
        ('قطبی', 'قطبی'), ('دانشگاهی', 'دانشگاهی'),
    ]
    RESULT_CHOICES = [
        ('برگزیده / جایزه', 'برگزیده / جایزه'),
        ('ارائه عادی', 'ارائه عادی'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='presentations')
    title = models.CharField('عنوان ارائه', max_length=500, blank=True)
    event = models.CharField('نام کنگره / رویداد', max_length=200, blank=True)
    level = models.CharField('سطح رویداد', max_length=20, choices=LEVEL_CHOICES, blank=True)
    result = models.CharField('نتیجه', max_length=30, choices=RESULT_CHOICES, blank=True)

    class Meta:
        verbose_name = 'ارائه'
        verbose_name_plural = 'ارائه‌ها'


class ExecutiveRecord(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='executive_records')
    title = models.CharField('عنوان سمت / نام تشکل', max_length=300, blank=True)
    start_date = models.CharField('تاریخ شروع', max_length=20, blank=True)
    end_date = models.CharField('تاریخ پایان', max_length=50, blank=True)

    class Meta:
        verbose_name = 'سابقه اجرایی'
        verbose_name_plural = 'سوابق اجرایی'
        ordering = ['start_date']


class TrainingCourse(models.Model):
    CATEGORY_CHOICES = [
        ('پژوهشی', 'پژوهشی'),
        ('بالینی', 'بالینی'),
        ('آموزشی', 'آموزشی'),
        ('نرم‌افزاری', 'نرم‌افزاری'),
        ('زبان', 'زبان'),
        ('سایر', 'سایر'),
    ]
    STATUS_CHOICES = [
        ('تکمیل‌شده', 'تکمیل‌شده'),
        ('در حال گذراندن', 'در حال گذراندن'),
        ('ناتمام', 'ناتمام'),
    ]
    CERTIFICATE_CHOICES = [
        ('دارد', 'دارد'),
        ('ندارد', 'ندارد'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='training_courses')
    title = models.CharField('عنوان دوره', max_length=300, blank=True)
    category = models.CharField('دسته', max_length=30, choices=CATEGORY_CHOICES, blank=True)
    status = models.CharField('وضعیت', max_length=30, choices=STATUS_CHOICES, blank=True)
    organizer = models.CharField('برگزارکننده', max_length=200, blank=True)
    date = models.CharField('تاریخ', max_length=20, blank=True)
    certificate = models.CharField('گواهی', max_length=10, choices=CERTIFICATE_CHOICES, blank=True)
    skills_gained = models.TextField('مهارت کسب‌شده', blank=True)

    class Meta:
        verbose_name = 'دوره آموزشی'
        verbose_name_plural = 'دوره‌های آموزشی'
        ordering = ['date']

    def __str__(self):
        return self.title or 'دوره آموزشی'
