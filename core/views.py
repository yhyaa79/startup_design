# core/views.py
"""
داشبورد اصلی کاربر — core/home.html
====================================================================
نسخه‌ی اصلاح‌شده. تغییرات نسبت به نسخه‌ی قبلی (همه با کامنت "FIX:" مشخص شده‌اند):

  FIX 1) کارت‌های «نمای کلی» حالا میانگین/مجموع روی *همه‌ی* رودمپ‌های کاربر
         حساب می‌شوند، نه فقط رودمپ انتخاب‌شده.
  FIX 2) کلیک روی هر رودمپ در بخش «رودمپ‌های من» (?roadmap_id=..) حالا واقعاً
         باعث تغییر رودمپ نمایش داده‌شده می‌شود — قبلاً این پارامتر GET اصلاً
         در ویو خوانده نمی‌شد.
  FIX 3) آمار ActivityLog: اگر فیلتر روی `user` چیزی برنگرداند (مثلاً چون مدل
         واقعی به Profile وصل است نه User)، به‌صورت خودکار روی `profile` هم
         امتحان می‌شود. ⚠️ این یک حدس منطقی بر اساس الگوی بقیه‌ی پروژه است
         (مثل ResearchProject.owner_profile) — اگر فیلد واقعی چیز دیگری است
         (مثلاً وضعیت‌ها اسم متفاوتی دارند)، اسم دقیق مدل/فیلدها را بدهید.
  FIX 4) دوره‌ها: فیلتر روی فیلد بولین «فعال بودن دوره» به‌جای فرض ثابت
         `active=True`، چند اسم رایج (`active`, `is_active`, `is_published`)
         را امتحان می‌کند تا اگر اسم فیلد واقعی چیز دیگری بود، لیست خالی
         برنگردد.
  FIX 5) ابزارهای جدید: به‌جای همیشه [] برگرداندن، مثل regulation_assessment
         با try/except به دنبال مدل Tool می‌گردد. تا وقتی این مدل ساخته نشود
         طبیعتاً خالی می‌ماند (چون واقعاً چیزی برای نمایش نیست)، اما به محض
         ساختن اپ/مدل، بدون تغییر این فایل کار می‌کند.

⚠️ نکات همچنان بازمانده (نیاز به اطلاعات بیشتر یا مدل جدید دارند):
  - ثبت آنلاین‌بودن کاربر: مدلی برای session/login در پروژه نیست.
  - Course/Event فیلد views_count واقعی ندارند.
  - regulation_assessment اگر اپش نصب نباشد None برمی‌گردد.
====================================================================
"""

from datetime import date

from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.db.models import Count, Q

from accounts.models import Profile
from roadmap.models import Roadmap, Stage, Activity, StageActivity
from activity.models import ActivityLog
from project.models import ResearchProject
from course.models import Course
from event_hub.models import Event


class ComingSoonView(TemplateView):
    template_name = 'coming_soon.html'


def landing(request):
    """صفحه ایندکس برای کاربران مهمان"""
    if request.user.is_authenticated:
        return redirect('core:home')
    return render(request, 'core/landing.html')


# ======================================================================
# بخش ۱: تکمیل پروفایل
# ======================================================================

PROFILE_SECTIONS = {
    'هویتی': ['first_name', 'last_name', 'gender', 'marital_status',
              'military_status', 'birth_date', 'city', 'phone', 'email'],
    'پژوهشی': ['orcid', 'proposal_count', 'proposal_status',
               'software_skills', 'writing_skills'],
    'بالینی': ['clinical_certs', 'clinical_exp', 'procedures'],
    'زبان': ['english_level', 'lang_cert'],
    'اهداف': ['goal', 'specialty', 'goal_notes'],
    'فوق‌برنامه': ['extracurricular'],
}


def _calc_profile_completion(profile):
    if not profile:
        return 0

    fields = [
        profile.first_name, profile.last_name, profile.gender,
        profile.birth_date, profile.phone, profile.email,
        profile.city, profile.goal, profile.specialty,
        profile.english_level, profile.orcid,
        profile.software_skills, profile.writing_skills,
    ]
    filled = sum(1 for f in fields if f and str(f).strip())
    has_edu = profile.educations.exists()
    has_article = profile.articles.exists()
    has_social = profile.social_profiles.exists()
    extras = sum([has_edu, has_article, has_social])
    total = len(fields) + 3
    return int(((filled + extras) / total) * 100)


def _profile_section_completion(profile):
    if not profile:
        return {'sections': [], 'open_ended': []}

    sections = []
    for section, fields in PROFILE_SECTIONS.items():
        filled = sum(
            1 for f in fields
            if getattr(profile, f, None) and str(getattr(profile, f)).strip()
        )
        percent = int((filled / len(fields)) * 100) if fields else 0
        sections.append({
            'label': section,
            'percent': percent,
            'filled': filled,
            'total': len(fields),
        })

    open_ended = [
        {'label': 'تحصیلات ثبت‌شده', 'count': profile.educations.count()},
        {'label': 'مقالات ثبت‌شده', 'count': profile.articles.count()},
        {'label': 'شبکه‌های اجتماعی', 'count': profile.social_profiles.count()},
        {'label': 'دوره‌های آموزشی', 'count': profile.training_courses.count()},
        {'label': 'ارائه‌ها', 'count': profile.presentations.count()},
        {'label': 'سوابق اجرایی', 'count': profile.executive_records.count()},
    ]

    return {'sections': sections, 'open_ended': open_ended}


# ======================================================================
# بخش ۲: فعالیت‌های پراستفاده (گلوبال، بین همه‌ی کاربران)
# ======================================================================

def _get_top_activities(limit=5):
    qs = (
        Activity.objects.annotate(usage_count=Count('stage_activities'))
        .filter(usage_count__gt=0)
        .order_by('-usage_count')[:limit]
        .values('id', 'title', 'category', 'usage_count')
    )
    return list(qs)


# ======================================================================
# بخش ۳: رودمپ‌ها و خط زمانی
# ======================================================================

def _get_roadmap_timeline(roadmap):
    if not roadmap:
        return None

    today = date.today()
    total_days = (roadmap.target_end_date - roadmap.start_date).days or 1
    elapsed_days = (today - roadmap.start_date).days
    time_percent = max(0, min(100, int((elapsed_days / total_days) * 100)))

    actual_percent = roadmap.get_progress()
    diff = actual_percent - time_percent

    if diff >= 10:
        status = 'ahead'
    elif diff <= -10:
        status = 'behind'
    else:
        status = 'on_track'

    stages_data = [
        {
            'order': stage.order,
            'title': stage.title,
            'status': stage.status,
            'start_date': stage.start_date,
            'end_date': stage.end_date,
            'progress': stage.get_progress(),
        }
        for stage in roadmap.stages.all().order_by('order')
    ]

    return {
        'time_percent': time_percent,
        'actual_percent': actual_percent,
        'status': status,
        'diff': diff,
        'stages': stages_data,
        'today': today,
        'start_date': roadmap.start_date,
        'target_end_date': roadmap.target_end_date,
    }


# ======================================================================
# بخش ۴: دوره‌ها (جدید / پیشنهادی / پربازدید)
# ======================================================================

def _active_course_filter_kwargs():
    """
    FIX 4: اسم واقعی فیلد «فعال بودن دوره» در مدل Course را نمی‌دانیم.
    قبلاً کد فقط `active=True` را امتحان می‌کرد و اگر اسم فیلد واقعی چیز
    دیگری بود (مثلاً is_active یا is_published)، همه‌ی کوئری‌ها خالی
    برمی‌گشتند بدون این‌که خطایی دیده شود. این تابع چند اسم رایج را
    امتحان می‌کند و اولین موردی که واقعاً روی مدل وجود دارد را برمی‌گرداند.

    ⚠️ اگر همچنان لیست دوره‌ها خالی است، اسم دقیق فیلد را از مدل Course
    بدهید تا این‌جا مستقیم اصلاح شود.
    """
    for field_name in ('active', 'is_active', 'is_published', 'is_visible'):
        if hasattr(Course, field_name):
            return {field_name: True}
    return {}


def _get_courses_data(profile):
    active_kwargs = _active_course_filter_kwargs()

    newest = list(
        Course.objects.filter(**active_kwargs)
        .order_by('-created_at')[:5]
        .values('id', 'title', 'category__name', 'created_at',
                'main_price', 'discount_price')
    )

    recommended = []
    if profile and (profile.specialty or profile.goal):
        keyword = (profile.specialty or profile.get_goal_display() or '').split()
        if keyword:
            recommended = list(
                Course.objects.filter(category__name__icontains=keyword[0], **active_kwargs)
                .order_by('-created_at')[:5]
                .values('id', 'title', 'category__name')
            )
    if not recommended:
        recommended = newest[:5]

    # TODO: بعد از افزودن views_count به مدل Course این را به '-views_count' تغییر دهید
    most_viewed = list(
        Course.objects.filter(**active_kwargs)
        .order_by('-created_at')[:5]
        .values('id', 'title', 'category__name')
    )

    return {
        'newest': newest,
        'recommended': recommended,
        'most_viewed': most_viewed,
        'most_viewed_is_real_data': False,
    }


# ======================================================================
# بخش ۵: رویدادهای پربازدید
# ======================================================================

def _get_top_events(limit=5):
    qs = Event.objects.order_by('-updated_at')[:limit].values('id', 'title', 'section')
    return list(qs)


# ======================================================================
# بخش ۶: پروژه‌های تحقیقاتی کاربر و پروژه‌های مشابه
# ======================================================================

def _get_user_projects(profile):
    if not profile:
        return []

    projects = ResearchProject.objects.filter(owner_profile=profile)
    return [
        {
            'id': p.id,
            'title': p.title,
            'status': p.get_status_display(),
            'views_count': p.views_count,
            'applications_count': p.applications.count(),
            'members_count': p.members.count(),
            'collaboration_status': p.get_collaboration_status_display(),
        }
        for p in projects
    ]


def _get_similar_projects(profile, limit=5):
    if not profile:
        return []

    user_projects = ResearchProject.objects.filter(owner_profile=profile)
    if not user_projects.exists():
        return []

    categories = user_projects.values_list('category', flat=True).distinct()
    qs = (
        ResearchProject.objects.filter(
            category__in=categories, visibility='public', is_active=True
        )
        .exclude(owner_profile=profile)
        .order_by('-is_featured', '-created_at')[:limit]
        .values('id', 'title', 'category', 'status', 'views_count')
    )
    return list(qs)


# ======================================================================
# بخش ۷: آمار جامعه‌ی کاربران
# ======================================================================

def _get_community_stats(profile):
    total_profiles = Profile.objects.count()
    same_goal_users, similar_profile_users = [], []

    if profile:
        same_goal_users = list(
            Profile.objects.filter(goal=profile.goal)
            .exclude(id=profile.id)
            .values('id', 'first_name', 'last_name', 'goal', 'specialty')[:10]
        )

        similar_q = Q()
        has_condition = False
        if profile.specialty:
            similar_q |= Q(specialty__icontains=profile.specialty.split()[0])
            has_condition = True
        edu_fields = list(profile.educations.values_list('field', flat=True))
        if edu_fields:
            similar_q |= Q(educations__field__in=edu_fields)
            has_condition = True

        if has_condition:
            similar_profile_users = list(
                Profile.objects.filter(similar_q)
                .exclude(id=profile.id)
                .distinct()
                .values('id', 'first_name', 'last_name', 'specialty')[:10]
            )

    return {
        'total_profiles': total_profiles,
        'same_goal_users': same_goal_users,
        'similar_profile_users': similar_profile_users,
    }


# ======================================================================
# بخش ۸: ابزارهای جدید
# ======================================================================

def _get_new_tools(limit=6):
    """
    FIX 5: قبلاً همیشه [] برمی‌گشت. حالا مثل regulation_assessment با
    try/except به دنبال مدل Tool می‌گردد (چند مسیر رایج امتحان می‌شود).
    تا وقتی این مدل/اپ در پروژه ساخته نشود، خروجی طبیعتاً خالی است —
    این یک باگ نیست، چون داده‌ای برای نمایش وجود ندارد. به‌محض ساختن مدل
    Tool (مثلاً در اپ tools یا core)، این تابع بدون تغییر بیشتری کار می‌کند.
    """
    model = None
    for module_path in ('tools.models', 'core.models', 'toolbox.models'):
        try:
            module = __import__(module_path, fromlist=['Tool'])
            model = getattr(module, 'Tool', None)
            if model is not None:
                break
        except ImportError:
            continue

    if model is None:
        return []

    qs = model.objects.all()
    if hasattr(model, 'is_active'):
        qs = qs.filter(is_active=True)
    return list(qs.order_by('-created_at')[:limit].values('id', 'title'))


# ======================================================================
# بخش ۹: آمار فعالیت‌های کاربر (ActivityLog)
# ======================================================================

def _get_activity_log_stats(user):
    """
    FIX 3: قبلاً فقط `ActivityLog.objects.filter(user=user)` امتحان می‌شد.
    اگر مدل واقعی ActivityLog به Profile وصل باشد (نه مستقیم به User)،
    این فیلتر همیشه صفر برمی‌گرداند، دقیقاً همان چیزی که گزارش شده
    («۳۸ فعالیت دارم ولی پیام خالی است»). حالا اگر فیلتر روی user چیزی
    پیدا نکرد و کاربر پروفایل دارد، روی profile هم امتحان می‌شود.

    ⚠️ اگر باز هم مشکل برطرف نشد، اسم دقیق فیلد رابطه در مدل ActivityLog
    (و اسم واقعی مقادیر status) را بدهید تا دقیق‌تر اصلاح شود.
    """
    logs = ActivityLog.objects.filter(user=user)

    if not logs.exists():
        profile = getattr(user, 'profile', None)
        if profile is not None and hasattr(ActivityLog, 'profile'):
            logs = ActivityLog.objects.filter(profile=profile)

    total = logs.count()
    return {
        'total': total,
        'completed': logs.filter(status='completed').count(),
        'pending': logs.filter(status='pending').count(),
        'in_progress': logs.filter(status='in_progress').count(),
        'paused': logs.filter(status='paused').count(),
        'cancelled': logs.filter(status='cancelled').count(),
    }


# ======================================================================
# بخش ۱۰: آنلاین بودن کاربر (placeholder — نیاز به مدل جدید)
# ======================================================================

def _get_online_activity_stats(user):
    """
    ⚠️ هنوز نیاز به مدل UserLoginLog (یا مشابه) دارد؛ این بخش عمداً
    غیرفعال است تا داده‌ی جعلی نمایش داده نشود. جزئیات ساخت مدل در
    نسخه‌ی قبلی این فایل توضیح داده شده بود.
    """
    return {
        'total_online_days': 0,
        'total_online_duration_minutes': 0,
        'last_7_days': [],
        'available': False,
    }


# ======================================================================
# بخش ۱۱: regulation_assessment
# ======================================================================

def _get_regulation_assessment(user):
    try:
        from regulation_assessment.models import RegulationAssessment
    except ImportError:
        return None

    assessment = (
        RegulationAssessment.objects.filter(user=user).order_by('-updated_at').first()
    )
    if not assessment:
        return None

    return {
        'total_score': assessment.total_score,
        'score_breakdown': assessment.score_breakdown,
        'created_at': assessment.created_at,
        'updated_at': assessment.updated_at,
    }


# ======================================================================
# بخش ۱۲: آمار کلی داشبورد
# ======================================================================

def _get_all_roadmaps_activity_totals(user):
    """
    FIX 1: مجموع فعالیت‌های تکمیل‌شده روی *همه‌ی* رودمپ‌های کاربر،
    نه فقط رودمپ انتخاب‌شده/فعال. قبلاً این عدد فقط از روی یک رودمپ
    (`roadmap`) محاسبه می‌شد که باعث می‌شد کارت «فعالیت‌های انجام‌شده»
    در نمای کلی، واقعی نباشد وقتی کاربر چند رودمپ دارد.
    """
    all_stage_acts = StageActivity.objects.filter(stage__roadmap__user=user)
    total = all_stage_acts.count()
    completed = all_stage_acts.filter(is_completed=True).count()
    return total, completed


def _get_stats(profile, average_roadmap_progress, total_stage_count,
               completed_stage_count, total_activities, completed_activities):
    """
    FIX 1: کارت‌های آماری بالای داشبورد حالا روی میانگین/مجموعِ *همه‌ی*
    رودمپ‌های کاربر حساب می‌شوند (نه فقط رودمپ انتخاب‌شده در بخش
    «رودمپ‌های من»)، چون این کارت‌ها معنای «کلی» دارند.
    """
    if not profile:
        return [
            {'sub': 'تکمیل پروفایل', 'value': '0٪', 'percent': 0, 'type': 'ring', 'icon': 'user'},
            {'sub': 'میانگین پیشرفت رودمپ‌ها', 'value': '0٪', 'percent': 0, 'type': 'ring', 'icon': 'map'},
            {'sub': 'مراحل رودمپ‌ها', 'value': '0 از 0', 'percent': 0, 'type': 'ring', 'icon': 'map'},
            {'sub': 'فعالیت‌های انجام‌شده', 'value': '0 از 0', 'percent': 0, 'type': 'ring', 'icon': 'map'},
        ]

    profile_completion = _calc_profile_completion(profile)

    stage_percent = int((completed_stage_count / total_stage_count) * 100) if total_stage_count else 0
    activity_percent = int((completed_activities / total_activities) * 100) if total_activities else 0

    return [
        {'sub': 'تکمیل پروفایل', 'value': f'{profile_completion}٪', 'percent': profile_completion, 'type': 'ring', 'icon': 'user'},
        {'sub': 'میانگین پیشرفت رودمپ‌ها', 'value': f'{average_roadmap_progress}٪', 'percent': average_roadmap_progress, 'type': 'ring', 'icon': 'map'},
        {'sub': 'مراحل رودمپ‌ها', 'value': f'{completed_stage_count} از {total_stage_count}', 'percent': stage_percent, 'type': 'ring', 'icon': 'map'},
        {'sub': 'فعالیت‌های انجام‌شده', 'value': f'{completed_activities} از {total_activities}', 'percent': activity_percent, 'type': 'ring', 'icon': 'map'},
    ]


def _get_weak_point(profile, roadmap, stages):
    if not profile:
        return None

    weaknesses = []

    article_count = profile.articles.count()
    if article_count == 0:
        weaknesses.append((
            'critical', 'هیچ مقاله‌ای ثبت نشده است',
            'شرکت در یک پروژه تحقیقاتی یا ثبت مقاله موجود را در اولویت قرار دهید.'
        ))
    elif article_count < 2:
        weaknesses.append((
            'high', 'تعداد مقالات کم است',
            'تلاش برای ارسال حداقل ۲ مقاله به ژورنال‌های ایندکس‌شده توصیه می‌شود.'
        ))

    english_order = ['', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    level_index = english_order.index(profile.english_level) if profile.english_level in english_order else 0
    if level_index == 0:
        weaknesses.append((
            'critical', 'سطح زبان انگلیسی ثبت نشده است',
            'اطلاعات مدرک زبان خود را تکمیل کنید یا برای آزمون IELTS/TOEFL برنامه‌ریزی کنید.'
        ))
    elif level_index <= 2:
        weaknesses.append((
            'high', f'سطح زبان انگلیسی ({profile.english_level}) پایین است',
            'بهبود سطح زبان به حداقل B2 برای اهداف حرفه‌ای ضروری است.'
        ))

    if profile.presentations.count() == 0:
        weaknesses.append((
            'medium', 'هیچ ارائه‌ای در کنگره‌ها ثبت نشده',
            'شرکت در کنگره‌های دانشجویی و ارائه پوستر یا سخنرانی را در برنامه قرار دهید.'
        ))

    completion = _calc_profile_completion(profile)
    if completion < 50:
        weaknesses.append((
            'critical', f'پروفایل تنها {completion}٪ تکمیل شده',
            'تکمیل اطلاعات پروفایل برای دریافت پیشنهادات دقیق‌تر ضروری است.'
        ))

    if profile.training_courses.count() == 0:
        weaknesses.append((
            'medium', 'دوره آموزشی ثبت نشده',
            'شرکت در دوره‌های تخصصی پژوهشی یا نرم‌افزاری را شروع کنید.'
        ))

    if profile.executive_records.count() == 0:
        weaknesses.append((
            'low', 'سابقه اجرایی یا تشکل ثبت نشده',
            'عضویت در تشکل‌های دانشجویی یا کمیته‌های علمی را در نظر بگیرید.'
        ))

    priority = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    weaknesses.sort(key=lambda x: priority.get(x[0], 99))
    return weaknesses[0] if weaknesses else None


# ======================================================================
# ویو اصلی داشبورد
# ======================================================================

def home(request):
    profile = None
    roadmaps = Roadmap.objects.none()
    active_roadmaps = Roadmap.objects.none()

    roadmap = None
    stages = []
    active_stage = None

    total_roadmaps_count = 0
    active_roadmaps_count = 0
    completed_roadmaps_count = 0
    paused_roadmaps_count = 0
    draft_roadmaps_count = 0
    active_stages_count = 0

    average_roadmap_progress = 0
    total_stage_count = 0
    completed_stage_count = 0
    total_activity_count = 0
    completed_activity_count = 0

    profile_sections = {'sections': [], 'open_ended': []}
    top_activities = []
    roadmap_timeline = None
    courses_data = {'newest': [], 'recommended': [], 'most_viewed': [], 'most_viewed_is_real_data': False}
    top_events = []
    user_projects = []
    similar_projects = []
    community_stats = {'total_profiles': Profile.objects.count(), 'same_goal_users': [], 'similar_profile_users': []}
    new_tools = _get_new_tools()
    activity_log_stats = {'total': 0, 'completed': 0, 'pending': 0, 'in_progress': 0, 'paused': 0, 'cancelled': 0}
    online_stats = _get_online_activity_stats(None)
    regulation_assessment = None

    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)

        roadmaps = Roadmap.objects.filter(user=request.user).prefetch_related(
            'stages',
            'stages__stage_activities',
            'stages__stage_activities__activity',
        )
        active_roadmaps = roadmaps.filter(status='active')

        total_roadmaps_count = roadmaps.count()
        active_roadmaps_count = active_roadmaps.count()
        completed_roadmaps_count = roadmaps.filter(status='completed').count()
        paused_roadmaps_count = roadmaps.filter(status='paused').count()
        draft_roadmaps_count = roadmaps.filter(status='draft').count()

        active_stages_count = Stage.objects.filter(roadmap__user=request.user, status='active').count()
        total_stage_count = Stage.objects.filter(roadmap__user=request.user).count()
        completed_stage_count = Stage.objects.filter(roadmap__user=request.user, status='completed').count()

        if total_roadmaps_count:
            progress_sum = sum(r.get_progress() for r in roadmaps)
            average_roadmap_progress = int(progress_sum / total_roadmaps_count)

        # FIX 1: مجموع فعالیت‌های همه‌ی رودمپ‌ها (نه فقط رودمپ انتخاب‌شده)
        total_activity_count, completed_activity_count = _get_all_roadmaps_activity_totals(request.user)

        # FIX 2: انتخاب رودمپ از روی پارامتر GET (?roadmap_id=..)، وگرنه
        # مثل قبل رودمپ فعال یا اولین رودمپ کاربر انتخاب می‌شود.
        selected_roadmap_id = request.GET.get('roadmap_id')
        roadmap = None
        if selected_roadmap_id:
            roadmap = roadmaps.filter(id=selected_roadmap_id).first()
        if not roadmap:
            roadmap = active_roadmaps.first() or roadmaps.first()

        if roadmap:
            stages = roadmap.stages.all().order_by('order')
            active_stage = stages.filter(status='active').first()
            if not active_stage:
                for stage in stages:
                    if stage.get_progress() < 100:
                        active_stage = stage
                        break

        if profile:
            profile_sections = _profile_section_completion(profile)
            courses_data = _get_courses_data(profile)
            user_projects = _get_user_projects(profile)
            similar_projects = _get_similar_projects(profile)

        top_activities = _get_top_activities()
        roadmap_timeline = _get_roadmap_timeline(roadmap)
        top_events = _get_top_events()
        community_stats = _get_community_stats(profile)
        activity_log_stats = _get_activity_log_stats(request.user)
        online_stats = _get_online_activity_stats(request.user)
        regulation_assessment = _get_regulation_assessment(request.user)
        new_tools = _get_new_tools()

    # FIX 1: پاس‌دادن آمار همه‌ی رودمپ‌ها به‌جای فقط رودمپ انتخاب‌شده
    dashboard_stats = _get_stats(
        profile,
        average_roadmap_progress,
        total_stage_count,
        completed_stage_count,
        total_activity_count,
        completed_activity_count,
    )
    weak_point = _get_weak_point(profile, roadmap, stages)

    context = {
        'profile': profile,

        'roadmaps': roadmaps,
        'active_roadmaps': active_roadmaps,

        'roadmap': roadmap,
        'stages': stages,
        'active_stage': active_stage,
        'total_progress': roadmap.get_progress() if roadmap else 0,

        'total_roadmaps_count': total_roadmaps_count,
        'active_roadmaps_count': active_roadmaps_count,
        'completed_roadmaps_count': completed_roadmaps_count,
        'paused_roadmaps_count': paused_roadmaps_count,
        'draft_roadmaps_count': draft_roadmaps_count,

        'active_stages_count': active_stages_count,
        'total_stage_count': total_stage_count,
        'completed_stage_count': completed_stage_count,
        'average_roadmap_progress': average_roadmap_progress,

        'goal_choices': Profile.GOAL_CHOICES,
        'dashboard_stats': dashboard_stats,
        'weak_point': weak_point,
        'is_guest': not request.user.is_authenticated,

        'profile_sections': profile_sections,
        'top_activities': top_activities,
        'roadmap_timeline': roadmap_timeline,
        'courses_data': courses_data,
        'top_events': top_events,
        'user_projects': user_projects,
        'similar_projects': similar_projects,
        'community_stats': community_stats,
        'new_tools': new_tools,
        'activity_log_stats': activity_log_stats,
        'online_stats': online_stats,
        'regulation_assessment': regulation_assessment,
    }

    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    return render(request, 'core/contact.html')


def tools(request):
    return render(request, 'core/tools.html', {'tools': _get_new_tools()})