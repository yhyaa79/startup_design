from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from accounts.models import Profile
from roadmap.models import Roadmap


class ComingSoonView(TemplateView):
    template_name = 'coming_soon.html'


def _calc_profile_completion(profile):
    """درصد تکمیل پروفایل بر اساس فیلدهای مهم"""
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


def _get_stats(profile, roadmap, stages):
    """محاسبه آمارهای کلیدی برای داشبورد"""

    # ۱. درصد تکمیل پروفایل
    profile_completion = _calc_profile_completion(profile)

    # ۲. پیشرفت رودمپ
    roadmap_progress = roadmap.get_total_progress() if roadmap else 0
    stage_count = stages.count() if stages else 0
    completed_stages = sum(1 for s in stages if s.get_progress() == 100) if stages else 0

    # ۳. مراحل رودمپ
    stage_count = stages.count() if stages else 0
    completed_stages = sum(1 for s in stages if s.get_progress() == 100) if stages else 0
    stage_percent = int((completed_stages / stage_count) * 100) if stage_count else 0

    # ۴. فعالیت‌های رودمپ
    total_activities = 0
    completed_activities = 0
    if roadmap:
        from roadmap.models import StageActivity
        all_stage_acts = StageActivity.objects.filter(stage__roadmap=roadmap)
        total_activities = all_stage_acts.count()
        completed_activities = all_stage_acts.filter(is_completed=True).count()
    activity_percent = int((completed_activities / total_activities) * 100) if total_activities else 0


    stats = [
        {
            'sub': 'تکمیل پروفایل',
            'value': f'{profile_completion}٪',
            'percent': profile_completion,
            'sub': 'تکمیل پروفایل',
            'type': 'ring',
            'icon': 'user',
        },
        {
            'sub': 'پیشرفت رودمپ',
            'value': f'{roadmap_progress}٪',
            'percent': roadmap_progress,
            'type': 'ring',
            'icon': 'map',
        },
        {
            'sub': 'مراحل رودمپ',
            'value': f'{completed_stages} از {stage_count}',
            'percent': stage_percent,
            'type': 'ring',
            'icon': 'map',
        },
        {
            'sub': 'فعالیت‌های انجام‌شده',
            'value': f'{completed_activities} از {total_activities}',
            'percent': activity_percent,
            'type': 'ring',
            'icon': 'map',
        },

    ]

    return stats


def _get_weak_point(profile, roadmap, stages):
    """شناسایی نقطه ضعف اصلی کاربر"""
    weaknesses = []

    # بررسی مقالات
    article_count = profile.articles.count()
    if article_count == 0:
        weaknesses.append(('critical', 'هیچ مقاله‌ای ثبت نشده است', 'شرکت در یک پروژه تحقیقاتی یا ثبت مقاله موجود را در اولویت قرار دهید.'))
    elif article_count < 2:
        weaknesses.append(('high', 'تعداد مقالات کم است', 'تلاش برای ارسال حداقل ۲ مقاله به ژورنال‌های ایندکس‌شده توصیه می‌شود.'))

    # بررسی سطح زبان
    english_order = ['', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    level_index = english_order.index(profile.english_level) if profile.english_level in english_order else 0
    if level_index == 0:
        weaknesses.append(('critical', 'سطح زبان انگلیسی ثبت نشده است', 'اطلاعات مدرک زبان خود را تکمیل کنید یا برای آزمون IELTS/TOEFL برنامه‌ریزی کنید.'))
    elif level_index <= 2:
        weaknesses.append(('high', f'سطح زبان انگلیسی ({profile.english_level}) پایین است', 'بهبود سطح زبان به حداقل B2 برای اهداف حرفه‌ای ضروری است.'))

    # بررسی ارائه
    if profile.presentations.count() == 0:
        weaknesses.append(('medium', 'هیچ ارائه‌ای در کنگره‌ها ثبت نشده', 'شرکت در کنگره‌های دانشجویی و ارائه پوستر یا سخنرانی را در برنامه قرار دهید.'))

    # بررسی تکمیل پروفایل
    completion = _calc_profile_completion(profile)
    if completion < 50:
        weaknesses.append(('critical', f'پروفایل تنها {completion}٪ تکمیل شده', 'تکمیل اطلاعات پروفایل برای دریافت پیشنهادات دقیق‌تر ضروری است.'))

    # بررسی دوره‌های آموزشی
    if profile.training_courses.count() == 0:
        weaknesses.append(('medium', 'دوره آموزشی ثبت نشده', 'شرکت در دوره‌های تخصصی پژوهشی یا نرم‌افزاری را شروع کنید.'))

    # بررسی سوابق اجرایی
    if profile.executive_records.count() == 0:
        weaknesses.append(('low', 'سابقه اجرایی یا تشکل ثبت نشده', 'عضویت در تشکل‌های دانشجویی یا کمیته‌های علمی را در نظر بگیرید.'))

    # مرتب‌سازی بر اساس اولویت
    priority = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    weaknesses.sort(key=lambda x: priority.get(x[0], 99))

    return weaknesses[0] if weaknesses else None


@login_required
def home(request):
    profile = request.user.profile
    roadmap = getattr(profile, 'roadmap', None)
    active_stage = None
    stages = []

    if roadmap:
        stages = roadmap.stages.all().order_by('order')
        for stage in stages:
            if stage.get_progress() < 100:
                active_stage = stage
                break

    stats = _calc_profile_completion(profile)  # برای استفاده داخلی
    dashboard_stats = _get_stats(profile, roadmap, stages)
    weak_point = _get_weak_point(profile, roadmap, stages)

    context = {
        'roadmap': roadmap,
        'stages': stages,
        'active_stage': active_stage,
        'total_progress': roadmap.get_total_progress() if roadmap else 0,
        'goal_choices': Profile.GOAL_CHOICES,
        'dashboard_stats': dashboard_stats,
        'weak_point': weak_point,
    }
    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    return render(request, 'core/contact.html')