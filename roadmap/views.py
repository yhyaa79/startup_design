# roadmap/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotAllowed
from django.db.models import Q
from django.utils import timezone
from .models import Roadmap, Stage, StageActivity, Activity
from .forms import (
    RoadmapForm, StageForm,
    StageActivityFormSet
)
from accounts.models import (
    Profile,
    TrainingCourse,
    Article,
    Presentation,
    ExecutiveRecord,
    Education,
    SocialProfile,
)
from .services.ai_roadmap import generate_ai_roadmap
import logging
from accounts.models import TrainingCourse, Article, Presentation, ExecutiveRecord
from roadmap.services.profile_activity_sync import save_activity_to_profile

from .models import RoadmapActivity


logger = logging.getLogger(__name__)


@login_required
def roadmap_detail(request):
    try:
        roadmap = request.user.profile.roadmap
    except Roadmap.DoesNotExist:
        return redirect('roadmap:roadmap_create')

    stages = roadmap.stages.prefetch_related(
        'stage_activities__activity'
    ).all().order_by('order')

    total_progress = roadmap.get_total_progress()
    total_duration = roadmap.get_total_duration()

    active_stage_id = None
    now = timezone.now()
    should_reset_following_stages = False

    for s in stages:
        progress = s.get_progress()

        if progress == 100:
            should_reset_following_stages = True
            continue

        if active_stage_id is None:
            active_stage_id = s.id

        if should_reset_following_stages:
            s.updated_at = now
            s.save(update_fields=['updated_at'])


    context = {
        'roadmap': roadmap,
        'stages': stages,
        'total_progress': total_progress,
        'total_duration': total_duration,
        'active_stage_id': active_stage_id,
    }

    return render(request, 'roadmap/roadmap_detail.html', context)



@login_required
def roadmap_create(request):
    """ساخت رود مپ"""
    profile = request.user.profile

    if hasattr(profile, 'roadmap'):
        return redirect('roadmap:roadmap_detail')

    if request.method == 'POST':
        form = RoadmapForm(request.POST)
        if form.is_valid():
            roadmap = form.save(commit=False)
            roadmap.profile = profile
            roadmap.save()
            return redirect('roadmap:stage_create', roadmap_id=roadmap.id)
    else:
        form = RoadmapForm()

    context = {'form': form, 'action': 'ساخت'}
    return render(request, 'roadmap/roadmap_form.html', context)


@login_required
def roadmap_edit(request, roadmap_id):
    """ویرایش رود مپ"""
    roadmap = get_object_or_404(Roadmap, id=roadmap_id, profile=request.user.profile)

    if request.method == 'POST':
        form = RoadmapForm(request.POST, instance=roadmap)
        if form.is_valid():
            form.save()
            return redirect('roadmap:roadmap_detail')
    else:
        form = RoadmapForm(instance=roadmap)

    context = {
        'form': form,
        'action': 'ویرایش',
        'roadmap': roadmap,
        'stages': roadmap.stages.all().order_by('order'),
    }
    return render(request, 'roadmap/roadmap_form.html', context)


@login_required
def stage_create(request, roadmap_id):
    """ساخت مرحله جدید"""
    roadmap = get_object_or_404(Roadmap, id=roadmap_id, profile=request.user.profile)

    if request.method == 'POST':
        stage_form = StageForm(request.POST)
        if stage_form.is_valid():
            stage = stage_form.save(commit=False)
            stage.roadmap = roadmap
            stage.save()
            return redirect('roadmap:stage_edit', stage_id=stage.id)
    else:
        stage_form = StageForm()

    context = {
        'form': stage_form,
        'roadmap': roadmap,
        'action': 'ساخت',
    }
    return render(request, 'roadmap/stage_create.html', context)


@login_required
def stage_detail(request, stage_id):
    """نمایش جزئیات مرحله"""
    stage = get_object_or_404(
        Stage.objects.prefetch_related('stage_activities__activity'),
        id=stage_id,
        roadmap__profile=request.user.profile
    )

    roadmap = stage.roadmap

    active_stage = None
    stages = roadmap.stages.all().order_by('order')

    for s in stages:
        if s.get_progress() < 100:
            active_stage = s
            break

    context = {
        'stage': stage,
        'roadmap': roadmap,
        'active_stage': active_stage,
        'progress': stage.get_progress(),
        'duration': stage.get_total_duration(),
    }

    return render(request, 'roadmap/stage_detail.html', context)



@login_required
def stage_edit(request, stage_id):
    stage = get_object_or_404(Stage, id=stage_id, roadmap__profile=request.user.profile)

    if request.method == 'POST':
        stage_form = StageForm(request.POST, instance=stage)
        activity_formset = StageActivityFormSet(request.POST, instance=stage, prefix='activities')

        stage_valid = stage_form.is_valid()
        activity_valid = activity_formset.is_valid()

        if stage_valid and activity_valid :
            stage_form.save()

            activity_instances = activity_formset.save(commit=False)

            for obj in activity_formset.deleted_objects:
                obj.delete()

            for item in activity_instances:
                if item.activity_id:
                    item.stage = stage
                    item.save()


            return redirect('roadmap:stage_detail', stage_id=stage.id)

    else:
        stage_form = StageForm(instance=stage)
        activity_formset = StageActivityFormSet(instance=stage, prefix='activities')

    context = {
        'stage_form': stage_form,
        'activity_formset': activity_formset,
        'stage': stage,
        'roadmap': stage.roadmap,
        'action': 'ویرایش',
    }
    return render(request, 'roadmap/stage_form.html', context)


@login_required
def stage_delete(request, stage_id):
    """حذف مرحله"""
    stage = get_object_or_404(Stage, id=stage_id, roadmap__profile=request.user.profile)
    roadmap = stage.roadmap
    stage.delete()
    return redirect('roadmap:roadmap_detail')


@login_required
def activity_list(request):
    """لیست فعالیت‌های موجود"""
    activities = Activity.objects.filter(is_active=True)

    category = request.GET.get('category')
    field = request.GET.get('field')
    search = request.GET.get('search')

    if category:
        activities = activities.filter(category=category)
    if field:
        activities = activities.filter(field=field)
    if search:
        activities = activities.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    activities = activities.order_by('category', 'title')

    context = {
        'activities': activities,
        'categories': Activity.CATEGORY_CHOICES,
        'fields': Activity.FIELD_CHOICES,
    }
    return render(request, 'roadmap/activity_list.html', context)


@login_required
def activity_detail(request, activity_id):
    """جزئیات فعالیت"""
    activity = get_object_or_404(Activity, id=activity_id)
    context = {'activity': activity}
    return render(request, 'roadmap/activity_detail.html', context)


from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseNotAllowed

@login_required
def stage_activity_toggle(request, stage_activity_id):
    """تغییر وضعیت فعالیت - فقط یکبار قابل تکمیل"""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    stage_activity = get_object_or_404(
        StageActivity,
        id=stage_activity_id,
        stage__roadmap__profile=request.user.profile
    )

    # اگر قبلاً تکمیل شده، دیگر اجازه تغییر نده
    if stage_activity.is_completed:
        messages.warning(request, 'این فعالیت قبلاً تکمیل شده و دیگر قابل تغییر نیست.')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'این فعالیت قبلاً تکمیل شده و دیگر قابل تغییر نیست.'
            }, status=400)

        return redirect('roadmap:stage_detail', stage_id=stage_activity.stage.id)

    # فقط تکمیل کن، نه toggle
    stage_activity.is_completed = True
    stage_activity.save()

    profile = request.user.profile
    activity = stage_activity.activity

    RoadmapActivity.objects.get_or_create(
        profile=profile,
        stage_activity=stage_activity,
        activity=activity
    )

    save_activity_to_profile(profile, activity)

    messages.success(request, 'وضعیت فعالیت با موفقیت تغییر کرد.')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'is_completed': stage_activity.is_completed,
            'stage_progress': stage_activity.stage.get_progress()
        })

    return redirect('roadmap:stage_detail', stage_id=stage_activity.stage.id)



# roadmap/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.db import transaction

from .models import Roadmap, Stage, StageActivity, Activity
from .services.ai_roadmap import generate_ai_roadmap


@login_required
def roadmap_generate_ai(request):
    """
    ساخت رودمپ با استفاده از AI
    """

    profile = request.user.profile

    if hasattr(profile, "roadmap"):
        return redirect("roadmap:roadmap_detail")

    roadmap_json = generate_ai_roadmap(profile)

    with transaction.atomic():
        roadmap = Roadmap.objects.create(
            profile=profile,
            title=roadmap_json["title"],
            description=roadmap_json.get("description", ""),
            status=roadmap_json.get("status", "فعال"),
        )

        for stage_data in roadmap_json.get("stages", []):
            stage = Stage.objects.create(
                roadmap=roadmap,
                title=stage_data["title"],
                description=stage_data.get("description", ""),
                objectives=stage_data.get("objectives", ""),
                order=stage_data.get("order", 0),
            )

            for order, act in enumerate(stage_data.get("activities", []), start=1):
                activity = Activity.objects.filter(
                    title=act["title"],
                    is_active=True,
                ).first()

                if activity:
                    StageActivity.objects.create(
                        stage=stage,
                        activity=activity,
                        notes=act.get("notes", ""),
                        order=order,
                    )

    return redirect("roadmap:roadmap_detail")



@login_required
def activity_search_api(request):
    search = request.GET.get('q', '').strip()

    activities = Activity.objects.filter(is_active=True)

    if search:
        activities = activities.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(category__icontains=search) |
            Q(resume_output__icontains=search)
        )

    activities = activities.order_by('category', 'title')

    data = []
    for activity in activities:
        data.append({
            'id': activity.id,
            'title': activity.title,
            'description': activity.description,
            'category': activity.category,
            'resume_output': getattr(activity, 'resume_output', ''),
            'resume_target': getattr(activity, 'resume_target', ''),
            'duration_days': getattr(activity, 'duration_days', ''),
        })

    return JsonResponse({'results': data})
