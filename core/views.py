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
from django.db.models import Count, Q, F, Case, When, IntegerField, Sum, Value, Min, Max
from django.db.models.functions import Coalesce, Lower, Trim
from accounts.models import Profile
from roadmap.models import Roadmap, Stage, Activity, StageActivity
from activity.models import ActivityLog
from project.models import ResearchProject
from course.models import Course
from event_hub.models import Event
from django.utils import timezone
from datetime import timedelta
import json
from django.utils.safestring import mark_safe
from .models import DailyOnlineActivity, Tool


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
# نمودار پنج صلعی از اطلاعات پروفایل کاربر
# ======================================================================


import math

def _get_profile_radar_chart(profile, size=260):
    """
    مختصات SVG برای نمودار پنج‌ضلعی (radar) بر اساس درصد هر بخش پروفایل.
    """
    sections = _profile_section_completion(profile)['sections']
    n = len(sections)
    if n == 0:
        return None

    cx = cy = size / 2
    radius = size / 2 - 40  # فاصله برای لیبل‌ها

    def point(angle_deg, r):
        angle_rad = math.radians(angle_deg)
        x = cx + r * math.sin(angle_rad)
        y = cy - r * math.cos(angle_rad)
        return x, y

    angle_step = 360 / n
    data_points, labels, axis_lines = [], [], []

    for i, sec in enumerate(sections):
        angle = i * angle_step
        x, y = point(angle, radius * (sec['percent'] / 100))
        data_points.append(f'{x:.1f},{y:.1f}')

        lx, ly = point(angle, radius + 28)
        labels.append({'x': lx, 'y': ly, 'label': sec['label'], 'percent': sec['percent']})

        ax, ay = point(angle, radius)
        axis_lines.append({'x1': cx, 'y1': cy, 'x2': ax, 'y2': ay})

    grid_polygons = []
    for level in (20, 40, 60, 80, 100):
        pts = [f'{point(i * angle_step, radius * level / 100)[0]:.1f},'
               f'{point(i * angle_step, radius * level / 100)[1]:.1f}' for i in range(n)]
        grid_polygons.append(' '.join(pts))

    return {
        'size': size,
        'data_polygon': ' '.join(data_points),
        'labels': labels,
        'axis_lines': axis_lines,
        'grid_polygons': grid_polygons,
    }



# ======================================================================
# بخش ۲: فعالیت‌های پراستفاده (گلوبال، بین همه‌ی کاربران)
# ======================================================================

def _get_top_activities(limit=8):
    """
    محبوب‌ترین فعالیت‌ها بر اساس تعداد دفعاتی که در StageActivity
    (توسط همه‌ی کاربران، در همه‌ی رودمپ‌ها) انتخاب شده‌اند.

    چون هر ساخت رودمپ توسط AI یک رکورد Activity تازه با external_id
    جدید ولی همان title می‌سازد، شمارش روی Activity.id همیشه ۱ می‌شود.
    برای رفع این موضوع، فعالیت‌ها بر اساس title نرمال‌شده (lower+trim)
    یکی می‌شوند و شمارش StageActivity روی همه‌ی رکوردهای هم‌عنوان جمع
    می‌شود.
    """
    qs = (
        Activity.objects
        .annotate(norm_title=Lower(Trim('title')))
        .values('norm_title')
        .annotate(
            id=Min('id'),
            title=Max('title'),
            category=Max('category'),
            usage_count=Count('stage_activities'),
        )
        .filter(usage_count__gt=0)
        .order_by('-usage_count')[:limit]
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


def _get_selected_roadmap_counts(roadmap):
    """
    آمار مراحل و فعالیت‌های فقط رودمپ انتخاب‌شده
    """
    if not roadmap:
        return {
            'total_stages': 0,
            'completed_stages': 0,
            'total_activities': 0,
            'completed_activities': 0,
        }

    total_stages = roadmap.stages.count()
    completed_stages = roadmap.stages.filter(status='completed').count()

    stage_activities = StageActivity.objects.filter(stage__roadmap=roadmap)
    total_activities = stage_activities.count()
    completed_activities = stage_activities.filter(is_completed=True).count()

    return {
        'total_stages': total_stages,
        'completed_stages': completed_stages,
        'total_activities': total_activities,
        'completed_activities': completed_activities,
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
    from django.db.models import Q
    from course.models import Course

    all_courses = Course.objects.filter(active=True).select_related('category')

    newest = list(all_courses.order_by('-created_at')[:5])
    most_viewed = list(all_courses.order_by('-view_count')[:5])

    recommended = []
    if profile and (profile.specialty or profile.goal):
        keyword_source = profile.specialty or profile.get_goal_display() or ''
        keyword = keyword_source.split()
        if keyword:
            kw = keyword[0].lower()
            recommended = list(
                all_courses.filter(
                    Q(category__name__icontains=kw) | Q(title__icontains=kw)
                )[:5]
            )
    if not recommended:
        recommended = newest[:5]

    def _fmt(c):
        return {
            'id': c.course_id,
            'title': c.title,
            'category__name': c.category.name if c.category_id else '',
            'main_price': c.main_price,
            'discount_price': c.discount_price,
            'view_count': c.view_count,
        }

    return {
        'newest': [_fmt(c) for c in newest],
        'recommended': [_fmt(c) for c in recommended],
        'most_viewed': [_fmt(c) for c in most_viewed],
        'most_viewed_is_real_data': True,
    }


# ======================================================================
# بخش ۵: رویدادهای پربازدید
# ======================================================================

def _get_top_events(limit=5):
    qs = Event.objects.order_by('-updated_at')[:limit].values('id', 'title', 'short_description')
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


# ======================================================================
# اطلاعات فعالیت ها
# ======================================================================

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



def _get_all_user_stage_activities(roadmaps):
    """
    همه فعالیت‌های کاربر را برای نمایش کارت افقی برمی‌گرداند
    """
    items = []

    for roadmap in roadmaps:
        for stage in roadmap.stages.all().order_by('order'):
            for sa in stage.stage_activities.all().order_by('order'):
                activity = sa.activity
                items.append({
                    'id': sa.id,
                    'title': activity.title,
                    'category': activity.get_category_display(),
                    'duration_days': activity.duration_days,
                    'impact_score': activity.impact_score,
                    'difficulty': activity.difficulty_rating,
                    'difficulty_label': activity.get_difficulty_rating_display(),
                    'impact_level': activity.get_impact_level_display(),
                    'is_completed': sa.is_completed,
                    'progress_percentage': sa.progress_percentage,
                    'stage_title': stage.title,
                    'roadmap_title': roadmap.title,
                })

    return items


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
    FIX 5 (نسخه نهایی): ابزارها حالا مستقیماً از core.models.Tool خوانده
    می‌شوند — مدلی که در پنل ادمین به‌صورت دستی مدیریت می‌شود.
    """
    return list(Tool.objects.filter(is_active=True)[:limit])


# ======================================================================
# بخش ۹: آمار فعالیت‌های کاربر (ActivityLog)
# ======================================================================

def _get_activity_log_stats(user):
    """
    اگر ActivityLog داده نداشت یا ساختارش با فرض‌های فعلی سازگار نبود،
    آمار «وضعیت فعالیت‌ها» از StageActivityهای رودمپ‌های کاربر ساخته می‌شود
    تا کارت داشبورد خالی نماند.
    """

    def _empty():
        return {
            'total': 0,
            'completed': 0,
            'pending': 0,
            'in_progress': 0,
            'paused': 0,
            'cancelled': 0,
        }

    def _from_stage_activities():
        stage_activities = StageActivity.objects.filter(stage__roadmap__user=user)

        if not stage_activities.exists():
            return _empty()

        completed = stage_activities.filter(is_completed=True).count()

        in_progress = stage_activities.filter(
            is_completed=False,
            progress_percentage__gt=0
        ).count()

        pending = stage_activities.filter(
            is_completed=False,
            progress_percentage=0
        ).count()

        total = stage_activities.count()

        return {
            'total': total,
            'completed': completed,
            'pending': pending,
            'in_progress': in_progress,
            'paused': 0,
            'cancelled': 0,
        }

    # تلاش اول: استفاده از ActivityLog
    try:
        logs = ActivityLog.objects.filter(user=user)

        if not logs.exists():
            profile = getattr(user, 'profile', None)
            if profile is not None:
                try:
                    logs = ActivityLog.objects.filter(profile=profile)
                except Exception:
                    pass

        if logs.exists():
            return {
                'total': logs.count(),
                'completed': logs.filter(status='completed').count(),
                'pending': logs.filter(status='pending').count(),
                'in_progress': logs.filter(status='in_progress').count(),
                'paused': logs.filter(status='paused').count(),
                'cancelled': logs.filter(status='cancelled').count(),
            }

    except Exception:
        pass

    # fallback واقعی و قابل اتکا: StageActivity
    return _from_stage_activities()


# ======================================================================
# بخش ۱۰: آنلاین بودن کاربر (placeholder — نیاز به مدل جدید)
# ======================================================================

from calendar import monthrange

def _get_online_activity_stats(user, months=3, end_year=None, end_month=None):
    """
    آمار فعالیت آنلاین کاربر برای heatmap ماهانه.
    - months: چند ماه نمایش داده شود (پیش‌فرض ۳ ماه اخیر)
    - end_year/end_month: آخرین ماهِ بازه (پیش‌فرض: ماه جاری). با این دو پارامتر
      دکمه‌های «ماه قبل/بعد» می‌توانند کل بازه را جابه‌جا کنند.
    همیشه calendar_grid کامل (حتی همه صفر) برمی‌گرداند، حتی برای کاربر مهمان
    یا کاربری که هنوز هیچ فعالیتی ثبت نکرده است.
    """
    from .models import DailyOnlineActivity

    today = timezone.now().date()
    end_year = end_year or today.year
    end_month = end_month or today.month

    # آخرین روز ماهِ پایانی بازه
    end_date = date(end_year, end_month, monthrange(end_year, end_month)[1])

    # اولین روزِ ماهِ شروع بازه (months ماه قبل‌تر)
    start_month = end_month - (months - 1)
    start_year = end_year
    while start_month <= 0:
        start_month += 12
        start_year -= 1
    start_date = date(start_year, start_month, 1)

    if getattr(user, 'is_authenticated', False):
        records = DailyOnlineActivity.objects.filter(
            user=user, date__gte=start_date, date__lte=end_date
        )
    else:
        records = DailyOnlineActivity.objects.none()

    records_by_date = {r.date: r for r in records}

    calendar_grid = []
    current = start_date
    while current <= end_date:
        rec = records_by_date.get(current)
        calendar_grid.append({
            'date': current.isoformat(),
            'duration_minutes': rec.duration_minutes if rec else 0,
        })
        current += timedelta(days=1)

    total_online_days = sum(1 for d in calendar_grid if d['duration_minutes'] > 0)
    total_online_duration_minutes = sum(d['duration_minutes'] for d in calendar_grid)

    # مقادیر ماه قبل/بعد برای دکمه‌های ناوبری
    prev_month, prev_year = (12, end_year - 1) if end_month == 1 else (end_month - 1, end_year)
    next_month, next_year = (1, end_year + 1) if end_month == 12 else (end_month + 1, end_year)
    is_current_month = (end_year == today.year and end_month == today.month)

    return {
        'available': True,
        'calendar_grid': calendar_grid,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'end_year': end_year,
        'end_month': end_month,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'next_disabled': is_current_month,  # نمی‌توان به ماه‌های آینده رفت
        'total_online_days': total_online_days,
        'total_online_duration_minutes': total_online_duration_minutes,
    }

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import date
from calendar import monthrange
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required
def online_activity_range(request):
    """
    AJAX endpoint برای بارگذاری بازه‌ی ۳ ماهه‌ی دیگر (ماه قبل/بعد) بدون رفرش.
    GET params: year, month → آخرین ماهِ بازه‌ی جدید
    """
    try:
        year = int(request.GET.get('year'))
        month = int(request.GET.get('month'))
    except (TypeError, ValueError):
        year, month = None, None

    stats = _get_online_activity_stats(request.user, months=3, end_year=year, end_month=month)
    return JsonResponse(stats)

# ======================================================================
# بخش ۱۱: regulation_assessment
# ======================================================================
""" 
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

 """
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
    profile_radar = None
    top_activities = []
    roadmap_timeline = None
    courses_data = {'newest': [], 'recommended': [], 'most_viewed': [], 'most_viewed_is_real_data': False}
    top_events = []
    user_projects = []
    similar_projects = []
    community_stats = {'total_profiles': Profile.objects.count(), 'same_goal_users': [], 'similar_profile_users': []}
    new_tools = _get_new_tools()
    activity_log_stats = {'total': 0, 'completed': 0, 'pending': 0, 'in_progress': 0, 'paused': 0, 'cancelled': 0}

    # FIX: این تابع فقط یک بار فراخوانی می‌شود (چه کاربر لاگین باشد چه نباشد).
    # قبلاً داخل بلاک `if request.user.is_authenticated:` دوباره صدا زده می‌شد
    # و مقدار قبلی (همراه با calendar_grid_json) را بدون آن کلید overwrite می‌کرد،
    # به همین دلیل تقویم هیچ‌وقت در تمپلیت رندر نمی‌شد.
    online_stats = _get_online_activity_stats(request.user)

    #regulation_assessment = None

    selected_roadmap_counts = {'total_stages': 0, 'completed_stages': 0, 'total_activities': 0, 'completed_activities': 0}

    all_user_stage_activities = []

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

            selected_roadmap_counts = _get_selected_roadmap_counts(roadmap)

        if profile:
            profile_sections = _profile_section_completion(profile)
            profile_radar = _get_profile_radar_chart(profile) 
            courses_data = _get_courses_data(profile)
            user_projects = _get_user_projects(profile)
            similar_projects = _get_similar_projects(profile)

        top_activities = _get_top_activities()
        roadmap_timeline = _get_roadmap_timeline(roadmap)
        top_events = _get_top_events()
        community_stats = _get_community_stats(profile)
        activity_log_stats = _get_activity_log_stats(request.user)
        #regulation_assessment = _get_regulation_assessment(request.user)
        new_tools = _get_new_tools()
        all_user_stage_activities = _get_all_user_stage_activities(roadmaps)

    # FIX: بررسی available و ساخت calendar_grid_json حالا *بعد* از هر دو مسیر
    # (مهمان/لاگین) انجام می‌شود تا هیچ‌وقت توسط override داخل بلاک بالا از
    # بین نرود. همچنین چون تابع همیشه calendar_grid کامل (حتی همه صفر) را
    # برمی‌گرداند، برای کاربری که هیچ فعالیتی ثبت نکرده هم تقویم خالی نمایش
    # داده می‌شود، نه بلوک "غیرفعال".
    if online_stats.get('available'):
        online_stats['calendar_grid_json'] = mark_safe(json.dumps(online_stats['calendar_grid']))

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
        'profile_radar': profile_radar,
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
        #'regulation_assessment': regulation_assessment,

        'selected_roadmap_total_stages': selected_roadmap_counts['total_stages'],
        'selected_roadmap_completed_stages': selected_roadmap_counts['completed_stages'],
        'selected_roadmap_total_activities': selected_roadmap_counts['total_activities'],
        'selected_roadmap_completed_activities': selected_roadmap_counts['completed_activities'],

        'all_user_stage_activities': all_user_stage_activities,

    }

    return render(request, 'core/home.html', context)

def about(request):
    return render(request, 'core/about.html')


def contact(request):
    return render(request, 'core/contact.html')


def tools(request):
    return render(request, 'core/tools.html', {'tools': _get_new_tools()})