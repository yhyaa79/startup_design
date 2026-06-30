# activity/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.paginator import Paginator
from roadmap.models import Roadmap, Activity, StageActivity
from datetime import date, timedelta


# -----------------------------------------------------
# Helper برای شبیه‌سازی ActivityLog
# -----------------------------------------------------

class ActivityLogProxy:
    """
    شبیه‌سازی ActivityLog بدون ذخیره در دیتابیس
    برای جلوگیری از خراب شدن template
    """

    STATUS_DISPLAY = {
        'pending': 'در انتظار',
        'completed': 'تکمیل‌شده',
    }

    def __init__(self, stage_activity):
        self._sa = stage_activity

        self.id = stage_activity.id
        self.activity = stage_activity.activity
        self.stage = stage_activity.stage
        self.roadmap = stage_activity.stage.roadmap
        self.user = stage_activity.stage.roadmap.user

        self.start_date = stage_activity.stage.start_date
        self.target_completion_date = stage_activity.stage.end_date
        self.progress_percentage = stage_activity.stage.get_progress()

        self.status = "completed" if stage_activity.is_completed else "pending"
        self.created_at = stage_activity.created_at

    def get_remaining_days(self):
        remaining = (self.target_completion_date - date.today()).days
        return max(0, remaining)

    def get_status_display(self):
        return self.STATUS_DISPLAY.get(self.status, self.status)


# -----------------------------------------------------
@login_required
def activity_list(request):
    """نمایش فعالیت‌ها بدون ذخیره مجدد در ActivityLog"""

    user = request.user
    view_mode = request.GET.get('view', 'my_activities')

    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    roadmap_filter = request.GET.get('roadmap', '')
    priority_filter = request.GET.get('priority', '')
    sort_by = request.GET.get('sort', '-created_at')

    activities = StageActivity.objects.select_related(
        'activity',
        'stage',
        'stage__roadmap',
        'stage__roadmap__user'
    )

    if view_mode == 'my_activities':
        activities = activities.filter(stage__roadmap__user=user)

    # ---------------- Filters ----------------

    if search_query:
        activities = activities.filter(
            Q(activity__title__icontains=search_query) |
            Q(stage__title__icontains=search_query) |
            Q(stage__roadmap__title__icontains=search_query) |
            Q(stage__roadmap__user__first_name__icontains=search_query) |
            Q(stage__roadmap__user__last_name__icontains=search_query)
        )

    if category_filter and category_filter in [c[0] for c in Activity.CATEGORY_CHOICES]:
        activities = activities.filter(activity__category=category_filter)

    if roadmap_filter:
        try:
            activities = activities.filter(stage__roadmap__id=int(roadmap_filter))
        except:
            pass

    if priority_filter in ['low', 'medium', 'high']:
        activities = activities.filter(stage__priority=priority_filter)

    if status_filter == 'completed':
        activities = activities.filter(is_completed=True)
    elif status_filter == 'pending':
        activities = activities.filter(is_completed=False)

    # ---------------- Sorting ----------------

    if sort_by == 'created_at':
        activities = activities.order_by('created_at')
    elif sort_by == '-created_at':
        activities = activities.order_by('-created_at')
    elif sort_by == 'target_completion_date':
        activities = activities.order_by('stage__end_date')
    elif sort_by == '-target_completion_date':
        activities = activities.order_by('-stage__end_date')
    else:
        activities = activities.order_by('-created_at')

    total_count = activities.count()

    paginator = Paginator(activities, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # ✅ تبدیل به Proxy تا template خراب نشود
    activity_logs = [ActivityLogProxy(sa) for sa in page_obj.object_list]

    # ---------------- Stats ----------------

    base_qs = StageActivity.objects.all()
    if view_mode == 'my_activities':
        base_qs = base_qs.filter(stage__roadmap__user=user)

    stats = {
        'total': base_qs.count(),
        'completed': base_qs.filter(is_completed=True).count(),
        'pending': base_qs.filter(is_completed=False).count(),
        'overdue': base_qs.filter(
            is_completed=False,
            stage__end_date__lt=date.today()
        ).count(),
    }

    roadmaps_for_filter = Roadmap.objects.filter(user=user) if view_mode == 'my_activities' else Roadmap.objects.all()

    context = {
        'page_obj': page_obj,
        'activities': activity_logs,  # ✅ همان چیزی که template انتظار دارد
        'total_count': total_count,
        'stats': stats,
        'roadmaps_for_filter': roadmaps_for_filter,
        'categories': Activity.CATEGORY_CHOICES,
        'statuses': [
            ('pending', 'در انتظار'),
            ('completed', 'تکمیل‌شده'),
        ],
        'priorities': [
            ('low', 'کم'),
            ('medium', 'متوسط'),
            ('high', 'زیاد'),
        ],
        'view_mode': view_mode,
    }

    return render(request, 'activity/activity_list.html', context)


# -----------------------------------------------------
@login_required
def activity_detail_modal(request, activity_log_id):
    """جزئیات فعالیت بدون ActivityLog"""

    stage_activity = get_object_or_404(
        StageActivity.objects.select_related(
            'activity',
            'stage',
            'stage__roadmap',
            'stage__roadmap__user'
        ),
        id=activity_log_id
    )

    activity_log = ActivityLogProxy(stage_activity)

    context = {
        'activity_log': activity_log,
    }

    return render(request, 'activity/activity_detail_modal.html', context)


# -----------------------------------------------------
@login_required
def activity_stats(request):

    user = request.user
    view_mode = request.GET.get('view', 'my_activities')

    activities_qs = StageActivity.objects.all()

    if view_mode == 'my_activities':
        activities_qs = activities_qs.filter(stage__roadmap__user=user)

    status_stats = [
        {'status': 'completed', 'count': activities_qs.filter(is_completed=True).count()},
        {'status': 'pending', 'count': activities_qs.filter(is_completed=False).count()},
    ]

    category_stats = activities_qs.values(
        'activity__category'
    ).annotate(
        count=Count('id')
    ).order_by('activity__category')

    upcoming = activities_qs.filter(
        is_completed=False,
        stage__end_date__gte=date.today(),
        stage__end_date__lte=date.today() + timedelta(days=7)
    ).count()

    context = {
        'status_stats': status_stats,
        'category_stats': list(category_stats),
        'upcoming_count': upcoming,
    }

    return render(request, 'activity/activity_stats.html', context)
