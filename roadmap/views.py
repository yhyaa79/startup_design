# roadmap/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from datetime import timedelta, date
import json

from .models import Roadmap, Stage, Activity, StageActivity
from .forms import RoadmapCreateForm, StageForm, ActivityForm
from .ai_roadmap import generate_roadmap
from .services.profile_data import collect_profile_data
from .services.scoring import calculate_roadmap_score
from .static_items import get_all_items_flat, get_item_by_id, CATEGORY_LABELS, LEVEL_LABELS, DIFFICULTY_LABELS

from course.models import Course, Category
from project.models import ResearchProject
from event_hub.models import Event

import logging

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
#  لیست رودمپ‌ها
# ═══════════════════════════════════════════════════════════════════

@login_required
def roadmap_list(request):
    """نمایش لیست رودمپ‌های کاربر"""
    
    roadmaps = Roadmap.objects.filter(user=request.user).prefetch_related('stages')
    
    context = {
        'roadmaps': roadmaps,
        'active_count': roadmaps.filter(status='active').count(),
        'completed_count': roadmaps.filter(status='completed').count(),
    }
    
    return render(request, 'roadmap/roadmap_list.html', context)


# ═══════════════════════════════════════════════════════════════════
#  ایجاد رودمپ
# ═══════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(["GET", "POST"])
def roadmap_create(request):
    """ایجاد رودمپ جدید"""

    if request.method == 'POST':
        form = RoadmapCreateForm(request.POST)

        if form.is_valid():
            goal = form.cleaned_data['goal']
            duration_days = form.cleaned_data['duration_days']
            goal_details = form.cleaned_data.get('goal_details', '')

            # جمع‌آوری داده‌های پروفایل
            try:
                profile = request.user.profile
                profile_data = collect_profile_data(profile)
            except Exception:
                logger.exception(f"خطا در جمع‌آوری پروفایل کاربر {request.user.id}")
                return render(request, 'roadmap/roadmap_create.html', {
                    'form': form,
                    'error': 'لطفاً ابتدا پروفایل خود را کامل کنید.',
                    'show_error_modal': True
                })

            # تولید رودمپ با AI
            try:
                roadmap_data = generate_roadmap(profile_data, goal, duration_days, goal_details)
            except (ConnectionError, TimeoutError) as e:
                logger.exception(
                    f"سرویس AI موقتاً در دسترس نبود | کاربر {request.user.id} | "
                    f"goal={goal} | duration_days={duration_days}"
                )
                return render(request, 'roadmap/roadmap_create.html', {
                    'form': form,
                    'error': 'سرویس هوش مصنوعی موقتاً پاسخگو نیست (Timeout). لطفاً چند دقیقه دیگر دوباره تلاش کنید.',
                    'show_error_modal': True
                })
            except Exception:
                logger.exception(
                    f"خطا در تولید رودمپ برای کاربر {request.user.id} | "
                    f"goal={goal} | duration_days={duration_days}"
                )
                return render(request, 'roadmap/roadmap_create.html', {
                    'form': form,
                    'error': 'خطا در تولید نقشه راه. لطفاً دوباره تلاش کنید.',
                    'show_error_modal': True
                })
            # ذخیره رودمپ
            try:
                with transaction.atomic():
                    quantitative_analysis = roadmap_data.get('quantitative_analysis', {}) or {}

                    roadmap = Roadmap.objects.create(
                        user=request.user,
                        title=roadmap_data.get('title', f'رودمپ {goal}'),
                        description=roadmap_data.get('description', ''),
                        goal=goal,
                        goal_details=goal_details,
                        duration_days=duration_days,
                        target_end_date=date.today() + timedelta(days=duration_days),
                        ai_generated=True,
                        ai_prompt=json.dumps({
                            'goal': goal,
                            'duration_days': duration_days,
                            'goal_details': goal_details,
                        }),
                        ai_analysis=profile_data,
                        total_score=quantitative_analysis.get('total_score', 0) or 0,
                        score_breakdown=quantitative_analysis,
                    )

                    # ایجاد مراحل
                    for stage_data in roadmap_data.get('stages', []):
                        stage = Stage.objects.create(
                            roadmap=roadmap,
                            order=stage_data.get('order', 1),
                            title=stage_data.get('title', ''),
                            description=stage_data.get('description', ''),
                            objectives=stage_data.get('objectives', ''),
                            phase_type=stage_data.get('phase_type', ''),
                            priority=stage_data.get('priority', 'medium'),
                            duration_days=stage_data.get('duration_days', 30),
                            start_date=date.today(),
                            end_date=date.today() + timedelta(days=stage_data.get('duration_days', 30)),
                            milestone=stage_data.get('milestone', ''),
                            success_criteria=stage_data.get('success_criteria', []),
                            risks=stage_data.get('risks', []),
                            recommended_resources=stage_data.get('recommended_resources', []),
                        )

                        # ایجاد فعالیت‌ها
                        for act_order, activity_data in enumerate(stage_data.get('activities', []), start=1):
                            raw_id = f"{roadmap.id}_{stage.id}_{activity_data.get('title', '')}"
                            external_id = raw_id[:50]

                            activity, _ = Activity.objects.get_or_create(
                                external_id=external_id,
                                defaults={
                                    'title': activity_data.get('title', ''),
                                    'description': activity_data.get('description', ''),
                                    'category': activity_data.get('category', 'course'),
                                    'duration_days': activity_data.get('duration_days', 7),
                                    'impact_score': activity_data.get('impact_score', 5),
                                    'difficulty_rating': activity_data.get('difficulty_rating', 'medium'),
                                    'resume_output': activity_data.get('resume_output', ''),
                                }
                            )

                            StageActivity.objects.create(
                                stage=stage,
                                activity=activity,
                                order=act_order,
                            )

                    # فعال کردن اولین مرحله
                    first_stage = roadmap.stages.first()
                    if first_stage:
                        first_stage.status = 'active'
                        first_stage.save()

                    roadmap.status = 'active'
                    roadmap.save()

            except Exception:
                logger.exception(
                    f"خطا در ذخیره رودمپ در دیتابیس برای کاربر {request.user.id}"
                )
                return render(request, 'roadmap/roadmap_create.html', {
                    'form': form,
                    'error': 'خطا در ذخیره‌سازی نقشه راه. لطفاً دوباره تلاش کنید.',
                    'show_error_modal': True
                })

            logger.info(f"رودمپ {roadmap.id} برای کاربر {request.user.id} با موفقیت ساخته شد.")
            return redirect('roadmap:roadmap_detail', pk=roadmap.id)

    else:
        form = RoadmapCreateForm()

    return render(request, 'roadmap/roadmap_create.html', {'form': form})


# ═══════════════════════════════════════════════════════════════════
#  جزئیات رودمپ
# ═══════════════════════════════════════════════════════════════════

@login_required
def roadmap_detail(request, pk):
    """نمایش جزئیات رودمپ"""
    
    roadmap = get_object_or_404(Roadmap, pk=pk, user=request.user)
    stages = roadmap.stages.prefetch_related('stage_activities').order_by('order')
    
    # محاسبه امتیاز
    score_data = calculate_roadmap_score(roadmap, roadmap.ai_analysis)
    roadmap.total_score = score_data['total_score']
    roadmap.score_breakdown = score_data['breakdown']
    roadmap.save()
    
    context = {
        'roadmap': roadmap,
        'stages': stages,
        'total_progress': roadmap.get_progress(),
        'total_duration': roadmap.duration_days,
        'active_stage_id': roadmap.get_active_stage().id if roadmap.get_active_stage() else None,
        'remaining_days': roadmap.get_remaining_days(),
        'score_breakdown': score_data['breakdown'],
    }
    
    return render(request, 'roadmap/roadmap_detail.html', context)


# ═══════════════════════════════════════════════════════════════════
#  جزئیات مرحله
# ═══════════════════════════════════════════════════════════════════

@login_required
def stage_detail(request, stage_id):
    """نمایش جزئیات مرحله"""
    
    stage = get_object_or_404(Stage, id=stage_id)
    roadmap = stage.roadmap
    
    # بررسی دسترسی
    if roadmap.user != request.user:
        return redirect('roadmap:roadmap_list')
    
    activities = stage.stage_activities.select_related('activity').order_by('order')
    
    context = {
        'roadmap': roadmap,
        'stage': stage,
        'activities': activities,
        'progress': stage.get_progress(),
        'duration': stage.get_total_duration(),
        'active_stage': roadmap.get_active_stage(),
    }
    
    return render(request, 'roadmap/stage_detail.html', context)


# ═══════════════════════════════════════════════════════════════════
#  ✅ جزئیات فعالیت (صفحه کامل - جدید)
# ═══════════════════════════════════════════════════════════════════

@login_required
def stage_activity_detail(request, activity_id):
    """نمایش صفحه کامل جزئیات فعالیت"""

    stage_activity = get_object_or_404(
        StageActivity.objects.select_related('activity', 'stage', 'stage__roadmap'),
        id=activity_id
    )
    roadmap = stage_activity.stage.roadmap

    # بررسی دسترسی
    if roadmap.user != request.user:
        return redirect('roadmap:roadmap_list')

    activity = stage_activity.activity

    # لیست آیتم‌های ثابت برای انتخاب + برچسب فارسی دسته برای هر آیتم
    # (چون قبلاً کل دیکشنری category_labels توی تمپلیت پرینت می‌شد)
    static_items = get_all_items_flat()
    for item in static_items:
        item['category_label'] = CATEGORY_LABELS.get(item.get('category'), item.get('category'))

    context = {
        'roadmap': roadmap,
        'stage': stage_activity.stage,
        'stage_activity': stage_activity,
        'activity': activity,
        'static_items': static_items,

        # این‌ها برای ساخت select ها با for-loop استفاده می‌شن (به‌جای هاردکد)
        'category_labels': CATEGORY_LABELS,
        'level_labels': LEVEL_LABELS,
        'difficulty_labels': DIFFICULTY_LABELS,

        # مقدار نهاییِ برچسبِ خودِ همین فعالیت (نه کل دیکشنری)
        'activity_level_label': LEVEL_LABELS.get(activity.level, activity.level) if activity.level else '',
        'activity_difficulty_label': DIFFICULTY_LABELS.get(
            activity.difficulty_rating, activity.difficulty_rating
        ),
    }

    return render(request, 'roadmap/stage_activity_detail.html', context)

# ═══════════════════════════════════════════════════════════════════
#  ✅ بروزرسانی فعالیت (جدید)
# ═══════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(["POST"])
def stage_activity_update(request, activity_id):
    """بروزرسانی جزئیات فعالیت"""
    
    stage_activity = get_object_or_404(StageActivity, id=activity_id)
    roadmap = stage_activity.stage.roadmap
    
    # بررسی دسترسی
    if roadmap.user != request.user:
        return JsonResponse({'error': 'دسترسی رد شد'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        # بروزرسانی فیلدهای اصلی
        
        if 'notes' in data:
            stage_activity.notes = data['notes']
        
        if 'actual_start_date' in data and data['actual_start_date']:
            stage_activity.actual_start_date = data['actual_start_date']
        
        if 'actual_end_date' in data and data['actual_end_date']:
            stage_activity.actual_end_date = data['actual_end_date']
        
        if 'result_summary' in data:
            stage_activity.result_summary = data['result_summary']
        
        # بروزرسانی checkpoints
        if 'checkpoints' in data:
            stage_activity.checkpoints = data['checkpoints']
        
        # بروزرسانی resources
        if 'resources' in data:
            stage_activity.resources = data['resources']
        
        stage_activity.save()
        
        return JsonResponse({
            'success': True,
            'message': 'فعالیت با موفقیت بروزرسانی شد'
        })
    
    except Exception as e:
        return JsonResponse({
            'error': f'خطا: {str(e)}'
        }, status=400)


# ═══════════════════════════════════════════════════════════════════
#  ✅ انتخاب آیتم از لیست ثابت (جدید)
# ═══════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(["POST"])
def stage_activity_select_static_item(request, activity_id):
    """انتخاب آیتم ثابت برای فعالیت"""
    
    stage_activity = get_object_or_404(StageActivity, id=activity_id)
    roadmap = stage_activity.stage.roadmap
    
    # بررسی دسترسی
    if roadmap.user != request.user:
        return JsonResponse({'error': 'دسترسی رد شد'}, status=403)
    
    try:
        data = json.loads(request.body)
        static_item_id = data.get('static_item_id')
        
        # دریافت آیتم
        static_item = get_item_by_id(static_item_id)
        if not static_item:
            return JsonResponse({'error': 'آیتم یافت نشد'}, status=404)
        
        with transaction.atomic():
            # بروزرسانی StageActivity
            stage_activity.activity_source = 'static'
            stage_activity.static_item_id = static_item_id
            stage_activity.static_item_data = static_item
            
            # بروزرسانی Activity اگر لازم باشد
            activity = stage_activity.activity
            activity.title = static_item['title']
            activity.description = static_item['description']
            activity.category = static_item['category']
            activity.duration_days = static_item['estimated_duration_days']
            activity.impact_score = static_item['impact_score']
            activity.difficulty_rating = static_item['difficulty']
            activity.organizer = static_item.get('organizer', '')
            activity.level = static_item.get('level', '')
            activity.save()
            
            stage_activity.save()
        
        return JsonResponse({
            'success': True,
            'message': 'آیتم با موفقیت انتخاب شد',
            'activity': {
                'title': activity.title,
                'description': activity.description,
                'category': activity.get_category_display(),
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'error': f'خطا: {str(e)}'
        }, status=400)


# ═══════════════════════════════════════════════════════════════════
#  ✅ ایجاد فعالیت دستی (جدید)
# ═══════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(["POST"])
def stage_activity_create_custom(request, activity_id):
    """ایجاد فعالیت دستی برای StageActivity"""
    
    stage_activity = get_object_or_404(StageActivity, id=activity_id)
    roadmap = stage_activity.stage.roadmap
    
    # بررسی دسترسی
    if roadmap.user != request.user:
        return JsonResponse({'error': 'دسترسی رد شد'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        with transaction.atomic():
            # بروزرسانی Activity
            activity = stage_activity.activity
            activity.title = data.get('title', 'فعالیت جدید')
            activity.description = data.get('description', '')
            activity.category = data.get('category', 'course')
            activity.duration_days = int(data.get('duration_days', 7))
            activity.impact_score = int(data.get('impact_score', 5))
            activity.difficulty_rating = data.get('difficulty_rating', 'medium')
            activity.organizer = data.get('organizer', '')
            activity.level = data.get('level', '')
            activity.save()
            
            # بروزرسانی StageActivity
            stage_activity.activity_source = 'custom'
            stage_activity.static_item_id = None
            stage_activity.static_item_data = {}
            stage_activity.save()
        
        return JsonResponse({
            'success': True,
            'message': 'فعالیت دستی با موفقیت ایجاد شد',
            'activity': {
                'id': activity.id,
                'title': activity.title,
                'category': activity.get_category_display(),
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'error': f'خطا: {str(e)}'
        }, status=400)


# ═══════════════════════════════════════════════════════════════════
#  تغییر وضعیت فعالیت (اصلاح شده)
# ═══════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(["POST"])
def stage_activity_toggle(request, activity_id):
    """تغییر وضعیت فعالیت"""
    
    stage_activity = get_object_or_404(StageActivity, id=activity_id)
    roadmap = stage_activity.stage.roadmap
    
    # بررسی دسترسی
    if roadmap.user != request.user:
        return JsonResponse({'error': 'دسترسی رد شد'}, status=403)
    
    save_target = request.POST.get('save_target', '__skip__')
    
    with transaction.atomic():
        stage_activity.is_completed = True
        stage_activity.completion_date = date.today()
        stage_activity.progress_percentage = 100
        stage_activity.saved_to_profile = save_target if save_target != '__skip__' else None
        stage_activity.save()
        
        # بررسی تکمیل مرحله
        stage = stage_activity.stage
        if stage.stage_activities.filter(is_completed=False).count() == 0:
            stage.status = 'completed'
            stage.save()
            
            # فعال کردن مرحله بعدی
            next_stage = stage.roadmap.stages.filter(order=stage.order + 1).first()
            if next_stage:
                next_stage.status = 'active'
                next_stage.save()
            else:
                # تمام مراحل تکمیل شده
                roadmap.status = 'completed'
                roadmap.save()
    
    return redirect('roadmap:stage_activity_detail', activity_id=activity_id)


# ═══════════════════════════════════════════════════════════════════
#  ✅ اضافه کردن checkpoint (جدید)
# ═══════════════════════════════════════════════════════════════════


@login_required
@require_http_methods(["POST"])
def stage_activity_add_checkpoint(request, activity_id):
    """اضافه کردن نقطه کنترل (دستی، یا از یک دوره/پروژه/رویداد)"""

    stage_activity = get_object_or_404(StageActivity, id=activity_id)
    roadmap = stage_activity.stage.roadmap

    if roadmap.user != request.user:
        return JsonResponse({'error': 'دسترسی رد شد'}, status=403)

    try:
        data = json.loads(request.body)
        source_type = data.get('source_type', 'manual')

        checkpoints = stage_activity.checkpoints or []
        new_id = (max(cp['id'] for cp in checkpoints) + 1) if checkpoints else 1

        checkpoint = {
            'id': new_id,
            'source_type': source_type,
            'is_completed': False,
            'date': None,
            'extra_details': {},
        }

        if source_type == 'manual':
            title = data.get('title', '').strip()
            if not title:
                return JsonResponse({'error': 'عنوان الزامی است'}, status=400)

            checkpoint.update({
                'title': title,
                'description': data.get('description', ''),
                'priority': data.get('priority', 'medium'),
                'due_date': data.get('due_date') or None,
                'notes': data.get('notes', ''),
                'source_id': None,
                'source_url': None,
            })

        elif source_type == 'course':
            course = get_object_or_404(Course, id=data.get('source_id'))
            checkpoint.update({
                'title': course.title,
                'description': course.short_desc,
                'priority': 'medium',
                'due_date': None,
                'notes': '',
                'source_id': course.id,
                'source_url': course.get_absolute_url(),
                'extra_details': {
                    'category': course.category.name,
                    'duration': course.duration,
                    'instructor': course.instructor,
                },
            })

        elif source_type == 'project':
            project = get_object_or_404(ResearchProject, id=data.get('source_id'))
            checkpoint.update({
                'title': project.title,
                'description': project.short_description,
                'priority': 'medium',
                'due_date': None,
                'notes': '',
                'source_id': project.id,
                'source_url': project.get_absolute_url(),
                'extra_details': {
                    'category': project.get_category_display(),
                    'status': project.get_status_display(),
                    'institution': project.institution,
                },
            })

        elif source_type == 'event':
            event = get_object_or_404(Event, id=data.get('source_id'))
            checkpoint.update({
                'title': event.title,
                'description': event.short_description,
                'priority': 'medium',
                'due_date': None,
                'notes': '',
                'source_id': event.id,
                'source_url': f'/event/{event.slug}/',
                'extra_details': {
                    'section': event.section,
                    'activity_type': event.activity_type,
                    'difficulty': event.difficulty,
                    'required_time': event.required_time,
                },
            })

        else:
            return JsonResponse({'error': 'نوع نامعتبر است'}, status=400)

        checkpoints.append(checkpoint)
        stage_activity.checkpoints = checkpoints
        stage_activity.save()

        return JsonResponse({'success': True, 'checkpoint': checkpoint})

    except Exception as e:
        return JsonResponse({'error': f'خطا: {str(e)}'}, status=400)
    

# ═══════════════════════════════════════════════════════
#  ✅ جستجوی دوره‌ها / پروژه‌ها برای افزودن به نقاط کنترل (جدید)
# ═══════════════════════════════════════════════════════

@login_required
@require_http_methods(["GET"])
def stage_activity_search_items(request):
    """جستجو و فیلتر دوره‌ها، پروژه‌ها یا رویدادها جهت انتخاب برای checklist"""

    item_type = request.GET.get('type', 'course')  # course | project | event
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    results = []

    if item_type == 'course':
        qs = Course.objects.filter(active=True).select_related('category')
        if query:
            qs = qs.filter(title__icontains=query)
        if category:
            qs = qs.filter(category__slug=category)

        for c in qs[:30]:
            results.append({
                'id': c.id,
                'title': c.title,
                'description': c.short_desc,
                'category': c.category.name,
                'meta': c.duration or '',
                'url': c.get_absolute_url(),
            })

        categories = list(Category.objects.values('slug', 'name'))

    elif item_type == 'project':
        qs = ResearchProject.objects.filter(is_active=True, visibility='public')
        if query:
            qs = qs.filter(title__icontains=query)
        if category:
            qs = qs.filter(category=category)

        for p in qs[:30]:
            results.append({
                'id': p.id,
                'title': p.title,
                'description': p.short_description,
                'category': p.get_category_display(),
                'meta': p.get_status_display(),
                'url': p.get_absolute_url(),
            })

        categories = [{'slug': k, 'name': v} for k, v in ResearchProject.CATEGORY_CHOICES]

    elif item_type == 'event':
        qs = Event.objects.all()
        if query:
            qs = qs.filter(title__icontains=query)
        if category:
            qs = qs.filter(section=category)

        for e in qs[:30]:
            results.append({
                'id': e.id,
                'title': e.title,
                'description': e.short_description,
                'category': e.section or 'عمومی',
                'meta': e.required_time or '',
                'url': f'/event/{e.slug}/',
            })

        sections = (
            Event.objects.exclude(section='')
            .values_list('section', flat=True)
            .distinct()
        )
        categories = [{'slug': s, 'name': s} for s in sections]

    else:
        return JsonResponse({'error': 'نوع نامعتبر است'}, status=400)

    return JsonResponse({'results': results, 'categories': categories})


# ═══════════════════════════════════════════════════════
#  ✅ بروزرسانی یادداشت یک نقطه کنترل خاص (جدید)
# ═══════════════════════════════════════════════════════

@login_required
@require_http_methods(["POST"])
def stage_activity_update_checkpoint_note(request, activity_id, checkpoint_id):
    """بروزرسانی یادداشت مربوط به یک آیتم checklist مشخص"""

    stage_activity = get_object_or_404(StageActivity, id=activity_id)
    roadmap = stage_activity.stage.roadmap

    if roadmap.user != request.user:
        return JsonResponse({'error': 'دسترسی رد شد'}, status=403)

    try:
        data = json.loads(request.body)
        note = data.get('notes', '')

        checkpoint_id = int(checkpoint_id)
        checkpoints = stage_activity.checkpoints or []
        found = False

        for checkpoint in checkpoints:
            if checkpoint['id'] == checkpoint_id:
                checkpoint['notes'] = note
                found = True
                break

        if not found:
            return JsonResponse({'error': 'نقطه کنترل یافت نشد'}, status=404)

        stage_activity.checkpoints = checkpoints
        stage_activity.save()

        return JsonResponse({'success': True, 'message': 'یادداشت ذخیره شد'})

    except Exception as e:
        return JsonResponse({'error': f'خطا: {str(e)}'}, status=400)
    

# ═══════════════════════════════════════════════════════════════════
#  ✅ تغییر وضعیت checkpoint 
# ═══════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(["POST"])
def stage_activity_toggle_checkpoint(request, activity_id, checkpoint_id):
    """تغییر وضعیت checkpoint"""
    
    stage_activity = get_object_or_404(StageActivity, id=activity_id)
    roadmap = stage_activity.stage.roadmap
    
    if roadmap.user != request.user:
        return JsonResponse({'error': 'دسترسی رد شد'}, status=403)
    
    try:
        checkpoint_id = int(checkpoint_id)
        checkpoints = stage_activity.checkpoints or []
        
        for checkpoint in checkpoints:
            if checkpoint['id'] == checkpoint_id:
                checkpoint['is_completed'] = not checkpoint['is_completed']
                if checkpoint['is_completed']:
                    checkpoint['date'] = str(date.today())
                else:
                    checkpoint['date'] = None
                break
        
        stage_activity.checkpoints = checkpoints
        stage_activity.save()
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ═══════════════════════════════════════════════════════════════════
#  ✅ اضافه کردن resource (جدید)
# ═══════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(["POST"])
def stage_activity_add_resource(request, activity_id):
    """اضافه کردن منبع"""
    
    stage_activity = get_object_or_404(StageActivity, id=activity_id)
    roadmap = stage_activity.stage.roadmap
    
    if roadmap.user != request.user:
        return JsonResponse({'error': 'دسترسی رد شد'}, status=403)
    
    try:
        data = json.loads(request.body)
        
        resource = {
            'id': len(stage_activity.resources) + 1,
            'title': data.get('title', ''),
            'type': data.get('type', 'link'),
            'url': data.get('url', ''),
            'description': data.get('description', ''),
        }
        
        resources = stage_activity.resources or []
        resources.append(resource)
        stage_activity.resources = resources
        stage_activity.save()
        
        return JsonResponse({
            'success': True,
            'resource': resource,
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ═══════════════════════════════════════════════════════════════════
#  ✅ حذف resource (جدید)
# ═══════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(["POST"])
def stage_activity_delete_resource(request, activity_id, resource_id):
    """حذف منبع"""
    
    stage_activity = get_object_or_404(StageActivity, id=activity_id)
    roadmap = stage_activity.stage.roadmap
    
    if roadmap.user != request.user:
        return JsonResponse({'error': 'دسترسی رد شد'}, status=403)
    
    try:
        resource_id = int(resource_id)
        resources = stage_activity.resources or []
        
        stage_activity.resources = [r for r in resources if r.get('id') != resource_id]
        stage_activity.save()
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)



# ═══════════════════════════════════════════════════════════════════
#  حذف ایتم های چک لیست
# ═══════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(["POST"])
def stage_activity_delete_checkpoint(request, activity_id, checkpoint_id):
    """حذف نقطه کنترل"""

    stage_activity = get_object_or_404(StageActivity, id=activity_id)
    roadmap = stage_activity.stage.roadmap

    if roadmap.user != request.user:
        return JsonResponse({'error': 'دسترسی رد شد'}, status=403)

    try:
        checkpoint_id = int(checkpoint_id)
        checkpoints = stage_activity.checkpoints or []

        new_checkpoints = [cp for cp in checkpoints if cp['id'] != checkpoint_id]

        if len(new_checkpoints) == len(checkpoints):
            return JsonResponse({'error': 'نقطه کنترل یافت نشد'}, status=404)

        stage_activity.checkpoints = new_checkpoints
        stage_activity.save()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ═══════════════════════════════════════════════════════════════════
#  ویرایش رودمپ
# ═══════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(["GET", "POST"])
def roadmap_edit(request, pk):
    """ویرایش رودمپ"""
    
    roadmap = get_object_or_404(Roadmap, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = RoadmapCreateForm(request.POST, instance=roadmap)
        
        if form.is_valid():
            form.save()
            return redirect('roadmap:roadmap_detail', pk=roadmap.id)
    
    else:
        form = RoadmapCreateForm(instance=roadmap)
    
    return render(request, 'roadmap/roadmap_edit.html', {
        'form': form,
        'roadmap': roadmap,
    })


# ═══════════════════════════════════════════════════════════════════
#  حذف رودمپ
# ═══════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(["POST"])
def roadmap_delete(request, pk):
    """حذف رودمپ"""
    
    roadmap = get_object_or_404(Roadmap, pk=pk, user=request.user)
    roadmap.delete()
    
    return redirect('roadmap:roadmap_list')


# ═══════════════════════════════════════════════════════════════════
#  ایجاد مرحله
# ═══════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(["GET", "POST"])
def stage_create(request, roadmap_id):
    """ایجاد مرحله جدید"""
    
    roadmap = get_object_or_404(Roadmap, id=roadmap_id, user=request.user)
    
    if request.method == 'POST':
        form = StageForm(request.POST)
        
        if form.is_valid():
            stage = form.save(commit=False)
            stage.roadmap = roadmap
            stage.order = roadmap.stages.count() + 1
            stage.save()
            
            return redirect('roadmap:stage_detail', stage_id=stage.id)
    
    else:
        form = StageForm()
    
    return render(request, 'roadmap/stage_create_edit.html', {
        'form': form,
        'roadmap': roadmap,
        'title': 'ایجاد مرحله جدید',
    })


# ═══════════════════════════════════════════════════════════════════
#  ویرایش مرحله
# ═══════════════════════════════════════════════════════════════════

@login_required
@require_http_methods(["GET", "POST"])
def stage_edit(request, stage_id):
    """ویرایش مرحله"""
    
    stage = get_object_or_404(Stage, id=stage_id)
    
    if stage.roadmap.user != request.user:
        return redirect('roadmap:roadmap_list')
    
    if request.method == 'POST':
        form = StageForm(request.POST, instance=stage)
        
        if form.is_valid():
            form.save()
            return redirect('roadmap:stage_detail', stage_id=stage.id)
    
    else:
        form = StageForm(instance=stage)
    
    return render(request, 'roadmap/stage_create_edit.html', {
        'form': form,
        'stage': stage,
        'title': 'ویرایش مرحله',
    })
