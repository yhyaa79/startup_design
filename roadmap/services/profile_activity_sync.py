# roadmap/services/profile_activity_sync.py

from accounts.models import TrainingCourse, Presentation, Article, ExecutiveRecord
from django.utils.timezone import now
from django.utils.timezone import now as tz_now
import jdatetime  


MODEL_MAP = {
    "training_courses": TrainingCourse,
    "presentations": Presentation,
    "articles": Article,
    "executive_records": ExecutiveRecord,
}


def _replace_dynamic_values(data: dict) -> dict:
    """جایگزینی مقادیر داینامیک مثل {today} در data"""
    today_str = now().strftime("%Y/%m/%d")
    result = {}
    for key, value in data.items():
        if isinstance(value, str) and "{today}" in value:
            result[key] = value.replace("{today}", today_str)
        else:
            result[key] = value
    return result




def save_activity_to_profile(profile, activity, override_model: str = None):
    """
    فعالیت تکمیل‌شده را در بخش درست پروفایل ذخیره می‌کند.
    override_model: اگر کاربر مکان دیگری انتخاب کرده، این پارامتر اولویت دارد.
    """
    template = activity.profile_template
    
    # تعیین مدل هدف — override کاربر اولویت دارد
    if override_model:
        target_model = override_model
    elif template and isinstance(template, dict):
        target_model = template.get('model')
    else:
        target_model = None

    if not target_model:
        return  # skill یا بدون template — چیزی ذخیره نمی‌شه

    # داده‌های پایه از profile_template (اگر موجود بود)
    data = {}
    if template and isinstance(template, dict):
        data = dict(template.get('data', {}))

    # جایگزینی {today} با تاریخ شمسی امروز
    try:
        today_jalali = jdatetime.date.today().strftime('%Y/%m/%d')
    except Exception:
        today_jalali = str(tz_now().date())

    def replace_today(val):
        if isinstance(val, str):
            return val.replace('{today}', today_jalali)
        return val

    data = {k: replace_today(v) for k, v in data.items()}

    # ذخیره در مدل هدف
    if target_model == 'training_courses':
        from accounts.models import TrainingCourse
        TrainingCourse.objects.create(
            profile=profile,
            title=data.get('title') or activity.title,
            category=data.get('category', ''),
            status=data.get('status', 'تکمیل‌شده'),
            organizer=data.get('organizer', 'Roadmap'),
            date=data.get('date', today_jalali),
            certificate=data.get('certificate', 'دارد'),
            skills_gained=data.get('skills_gained', activity.resume_output or ''),
        )

    elif target_model == 'articles':
        from accounts.models import Article
        Article.objects.create(
            profile=profile,
            title=data.get('title') or activity.title,
            journal=data.get('journal', ''),
            year=data.get('year') or None,
            author_rank=data.get('author_rank') or None,
            index=data.get('index', ''),
        )

    elif target_model == 'presentations':
        from accounts.models import Presentation
        Presentation.objects.create(
            profile=profile,
            title=data.get('title') or activity.title,
            event=data.get('event', ''),
            level=data.get('level', ''),
            result=data.get('result', 'ارائه عادی'),
        )

    elif target_model == 'executive_records':
        from accounts.models import ExecutiveRecord
        ExecutiveRecord.objects.create(
            profile=profile,
            title=data.get('title') or activity.title,
            start_date=data.get('start_date', today_jalali),
            end_date=data.get('end_date', ''),
        )
    # سایر مدل‌ها → نادیده گرفته می‌شه