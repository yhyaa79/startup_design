# roadmap/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.forms import inlineformset_factory
from django.db import transaction
from .models import Roadmap, Stage, StageActivity, Activity
from .forms import RoadmapForm, StageForm, StageActivityForm, StageActivityFormSet
from accounts.models import Profile


@login_required
def roadmap_view(request):
    """نمایش رود‌مپ"""
    try:
        profile = request.user.profile
        roadmap = profile.roadmap
    except:
        roadmap = None

    if not roadmap:
        return render(request, 'roadmap/roadmap_empty.html')

    stages = roadmap.stages.all().order_by('order')
    context = {
        'roadmap': roadmap,
        'stages': stages,
        'total_progress': roadmap.get_total_progress(),
        'total_duration': roadmap.get_total_duration(),
    }
    return render(request, 'roadmap/roadmap_view.html', context)


@login_required
def roadmap_create(request):
    """ساخت یا ویرایش رود‌مپ"""
    profile = request.user.profile
    roadmap, created = Roadmap.objects.get_or_create(profile=profile)

    if request.method == 'POST':
        form = RoadmapForm(request.POST, instance=roadmap)
        if form.is_valid():
            form.save()
            return redirect('roadmap:roadmap_view')
    else:
        form = RoadmapForm(instance=roadmap)

    context = {
        'form': form,
        'roadmap': roadmap,
        'is_edit': not created,
    }
    return render(request, 'roadmap/roadmap_form.html', context)


@login_required
def stage_create(request, roadmap_id):
    """ساخت مرحله جدید"""
    roadmap = get_object_or_404(Roadmap, id=roadmap_id, profile__user=request.user)

    if request.method == 'POST':
        form = StageForm(request.POST)
        if form.is_valid():
            stage = form.save(commit=False)
            stage.roadmap = roadmap
            stage.save()
            return redirect('roadmap:stage_edit', stage_id=stage.id)
    else:
        form = StageForm()

    context = {
        'form': form,
        'roadmap': roadmap,
        'is_edit': False,
    }
    return render(request, 'roadmap/stage_form.html', context)


@login_required
def stage_edit(request, stage_id):
    """ویرایش مرحله و فعالیت‌های آن"""
    stage = get_object_or_404(Stage, id=stage_id, roadmap__profile__user=request.user)
    StageActivityFormSet = inlineformset_factory(
        Stage, StageActivity,
        form=StageActivityForm,
        formset=StageActivityFormSet,
        extra=1,
        can_delete=True
    )

    if request.method == 'POST':
        form = StageForm(request.POST, instance=stage)
        formset = StageActivityFormSet(request.POST, instance=stage)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            return redirect('roadmap:roadmap_view')
    else:
        form = StageForm(instance=stage)
        formset = StageActivityFormSet(instance=stage)

    activities = Activity.objects.filter(is_active=True)
    context = {
        'form': form,
        'formset': formset,
        'stage': stage,
        'roadmap': stage.roadmap,
        'activities': activities,
        'total_duration': stage.get_total_duration(),
        'checklist_progress': stage.get_checklist_progress(),
    }
    return render(request, 'roadmap/stage_edit.html', context)


@login_required
def stage_delete(request, stage_id):
    """حذف مرحله"""
    stage = get_object_or_404(Stage, id=stage_id, roadmap__profile__user=request.user)
    roadmap = stage.roadmap

    if request.method == 'POST':
        stage.delete()
        return redirect('roadmap:roadmap_view')

    context = {
        'stage': stage,
        'roadmap': roadmap,
    }
    return render(request, 'roadmap/stage_confirm_delete.html', context)


@login_required
def stage_activity_delete(request, activity_id):
    """حذف فعالیت از مرحله"""
    stage_activity = get_object_or_404(StageActivity, id=activity_id, stage__roadmap__profile__user=request.user)
    stage = stage_activity.stage

    if request.method == 'POST':
        stage_activity.delete()
        return redirect('roadmap:stage_edit', stage_id=stage.id)

    context = {
        'stage_activity': stage_activity,
        'stage': stage,
    }
    return render(request, 'roadmap/stage_activity_confirm_delete.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_activity_completion(request, activity_id):
    """تغییر وضعیت تکمیل فعالیت"""
    stage_activity = get_object_or_404(StageActivity, id=activity_id, stage__roadmap__profile__user=request.user)
    stage_activity.is_completed = not stage_activity.is_completed
    stage_activity.save()

    return JsonResponse({
        'success': True,
        'is_completed': stage_activity.is_completed,
        'checklist_progress': stage_activity.stage.get_checklist_progress(),
    })


@login_required
def roadmap_detail_api(request):
    """API برای دریافت جزئیات رود‌مپ"""
    try:
        roadmap = request.user.profile.roadmap
    except:
        return JsonResponse({'error': 'رود‌مپ یافت نشد'}, status=404)

    stages_data = []
    for stage in roadmap.stages.all().order_by('order'):
        activities_data = []
        for sa in stage.stage_activities.all().order_by('order'):
            activities_data.append({
                'id': sa.id,
                'title': sa.activity.title,
                'duration': sa.get_duration(),
                'is_completed': sa.is_completed,
            })

        stages_data.append({
            'id': stage.id,
            'title': stage.title,
            'status': stage.status,
            'progress': stage.get_progress(),
            'checklist_progress': stage.get_checklist_progress(),
            'total_duration': stage.get_total_duration(),
            'activities': activities_data,
        })

    return JsonResponse({
        'roadmap': {
            'title': roadmap.title,
            'total_progress': roadmap.get_total_progress(),
            'total_duration': roadmap.get_total_duration(),
            'stages': stages_data,
        }
    })
