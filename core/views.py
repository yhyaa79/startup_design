# core/views.py


from django.shortcuts import render
from django.views.generic import TemplateView
from accounts.models import Profile
from roadmap.models import Roadmap


class ComingSoonView(TemplateView):
    template_name = 'coming_soon.html'


def landing(request):
    """صفحه ایندکس برای کاربران مهمان"""
    if request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('core:home')
    return render(request, 'core/landing.html')
    

def _calc_profile_completion(profile):
    """درصد تکمیل پروفایل بر اساس فیلدهای مهم"""
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


def _get_stats(profile, roadmap, stages):
    """محاسبه آمارهای کلیدی برای داشبورد"""

    if not profile:
        return [
            {
                'sub': 'تکمیل پروفایل',
                'value': '0٪',
                'percent': 0,
                'type': 'ring',
                'icon': 'user',
            },
            {
                'sub': 'پیشرفت رودمپ',
                'value': '0٪',
                'percent': 0,
                'type': 'ring',
                'icon': 'map',
            },
            {
                'sub': 'مراحل رودمپ',
                'value': '0 از 0',
                'percent': 0,
                'type': 'ring',
                'icon': 'map',
            },
            {
                'sub': 'فعالیت‌های انجام‌شده',
                'value': '0 از 0',
                'percent': 0,
                'type': 'ring',
                'icon': 'map',
            },
        ]

    profile_completion = _calc_profile_completion(profile)

    roadmap_progress = roadmap.get_progress() if roadmap else 0

    # stages می‌تواند QuerySet یا لیست پایتون باشد؛ len() روی هر دو درست کار می‌کند،
    # برخلاف hasattr(stages, 'count') که چون لیست هم متد count(value) دارد
    # (با امضای متفاوت) باعث TypeError می‌شد.
    stage_count = len(stages)
    completed_stages = sum(1 for s in stages if s.get_progress() == 100) if stages else 0
    stage_percent = int((completed_stages / stage_count) * 100) if stage_count else 0

    total_activities = 0
    completed_activities = 0

    if roadmap:
        from roadmap.models import StageActivity

        all_stage_acts = StageActivity.objects.filter(stage__roadmap=roadmap)
        total_activities = all_stage_acts.count()
        completed_activities = all_stage_acts.filter(is_completed=True).count()

    activity_percent = int((completed_activities / total_activities) * 100) if total_activities else 0

    return [
        {
            'sub': 'تکمیل پروفایل',
            'value': f'{profile_completion}٪',
            'percent': profile_completion,
            'type': 'ring',
            'icon': 'user',
        },
        {
            'sub': 'پیشرفت رودمپ فعال',
            'value': f'{roadmap_progress}٪',
            'percent': roadmap_progress,
            'type': 'ring',
            'icon': 'map',
        },
        {
            'sub': 'مراحل رودمپ فعال',
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


def _get_weak_point(profile, roadmap, stages):
    """شناسایی نقطه ضعف اصلی کاربر"""
    if not profile:
        return None

    weaknesses = []

    # بررسی مقالات
    article_count = profile.articles.count()
    if article_count == 0:
        weaknesses.append((
            'critical',
            'هیچ مقاله‌ای ثبت نشده است',
            'شرکت در یک پروژه تحقیقاتی یا ثبت مقاله موجود را در اولویت قرار دهید.'
        ))
    elif article_count < 2:
        weaknesses.append((
            'high',
            'تعداد مقالات کم است',
            'تلاش برای ارسال حداقل ۲ مقاله به ژورنال‌های ایندکس‌شده توصیه می‌شود.'
        ))

    # بررسی سطح زبان
    english_order = ['', 'A1', 'A2', 'B1', 'B2', 'C1', 'C2']
    level_index = english_order.index(profile.english_level) if profile.english_level in english_order else 0
    if level_index == 0:
        weaknesses.append((
            'critical',
            'سطح زبان انگلیسی ثبت نشده است',
            'اطلاعات مدرک زبان خود را تکمیل کنید یا برای آزمون IELTS/TOEFL برنامه‌ریزی کنید.'
        ))
    elif level_index <= 2:
        weaknesses.append((
            'high',
            f'سطح زبان انگلیسی ({profile.english_level}) پایین است',
            'بهبود سطح زبان به حداقل B2 برای اهداف حرفه‌ای ضروری است.'
        ))

    # بررسی ارائه
    if profile.presentations.count() == 0:
        weaknesses.append((
            'medium',
            'هیچ ارائه‌ای در کنگره‌ها ثبت نشده',
            'شرکت در کنگره‌های دانشجویی و ارائه پوستر یا سخنرانی را در برنامه قرار دهید.'
        ))

    # بررسی تکمیل پروفایل
    completion = _calc_profile_completion(profile)
    if completion < 50:
        weaknesses.append((
            'critical',
            f'پروفایل تنها {completion}٪ تکمیل شده',
            'تکمیل اطلاعات پروفایل برای دریافت پیشنهادات دقیق‌تر ضروری است.'
        ))

    # بررسی دوره‌های آموزشی
    if profile.training_courses.count() == 0:
        weaknesses.append((
            'medium',
            'دوره آموزشی ثبت نشده',
            'شرکت در دوره‌های تخصصی پژوهشی یا نرم‌افزاری را شروع کنید.'
        ))

    # بررسی سوابق اجرایی
    if profile.executive_records.count() == 0:
        weaknesses.append((
            'low',
            'سابقه اجرایی یا تشکل ثبت نشده',
            'عضویت در تشکل‌های دانشجویی یا کمیته‌های علمی را در نظر بگیرید.'
        ))

    priority = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    weaknesses.sort(key=lambda x: priority.get(x[0], 99))

    return weaknesses[0] if weaknesses else None


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

        from roadmap.models import Stage

        active_stages_count = Stage.objects.filter(
            roadmap__user=request.user,
            status='active'
        ).count()

        total_stage_count = Stage.objects.filter(
            roadmap__user=request.user
        ).count()

        completed_stage_count = Stage.objects.filter(
            roadmap__user=request.user,
            status='completed'
        ).count()

        if total_roadmaps_count:
            progress_sum = sum(r.get_progress() for r in roadmaps)
            average_roadmap_progress = int(progress_sum / total_roadmaps_count)

        roadmap = active_roadmaps.first() or roadmaps.first()

        if roadmap:
            stages = roadmap.stages.all().order_by('order')
            active_stage = stages.filter(status='active').first()

            if not active_stage:
                for stage in stages:
                    if stage.get_progress() < 100:
                        active_stage = stage
                        break

    dashboard_stats = _get_stats(profile, roadmap, stages)
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
    }

    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html')


def contact(request):
    return render(request, 'core/contact.html')