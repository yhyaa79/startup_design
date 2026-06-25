# networking/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from accounts.models import Profile, Article, Presentation, Education, TrainingCourse, SocialProfile
from .models import NetworkingConnection
from .forms import ProfileSearchFilterForm


def networking_list(request):
    """لیست تمام پروفایل‌ها با امکان سرچ و فیلتر"""
    profiles = Profile.objects.all().select_related('user')
    form = ProfileSearchFilterForm(request.GET)
    
    # جستجو
    search_query = request.GET.get('search', '')
    if search_query:
        profiles = profiles.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(specialty__icontains=search_query) |
            Q(job_title__icontains=search_query)
        )
    
    # فیلتر بر اساس هدف
    goal = request.GET.get('goal', '')
    if goal:
        profiles = profiles.filter(goal=goal)
    
    # فیلتر بر اساس سطح انگلیسی
    english_level = request.GET.get('english_level', '')
    if english_level:
        profiles = profiles.filter(english_level=english_level)
    
    # فیلتر بر اساس جنسیت
    gender = request.GET.get('gender', '')
    if gender:
        profiles = profiles.filter(gender=gender)
    
    # فیلتر بر اساس کشور
    country = request.GET.get('country', '')
    if country:
        profiles = profiles.filter(country__icontains=country)
    
    # فیلتر بر اساس وضعیت سربازی
    military_status = request.GET.get('military_status', '')
    if military_status:
        profiles = profiles.filter(military_status=military_status)
    
    # pagination
    paginator = Paginator(profiles, 12)  # 12 پروفایل در هر صفحه
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'profiles': page_obj.object_list,
        'form': form,
        'search_query': search_query,
    }
    
    return render(request, 'networking/networking_list.html', context)


def profile_detail(request, pk):
    """صفحه جزئیات کامل پروفایل"""
    profile = get_object_or_404(Profile, pk=pk)
    
    # دریافت تمام اطلاعات مرتبط
    educations = profile.educations.all()
    articles = profile.articles.all()
    presentations = profile.presentations.all()
    training_courses = profile.training_courses.all()
    social_profiles = profile.social_profiles.all()
    executive_records = profile.executive_records.all()
    
    # بررسی وضعیت اتصال
    connection_status = None
    is_connected = False
    
    if request.user.is_authenticated:
        try:
            connection = NetworkingConnection.objects.get(
                from_user=request.user.profile,
                to_user=profile
            )
            connection_status = connection.status
            is_connected = connection.status == 'accepted'
        except NetworkingConnection.DoesNotExist:
            pass
    
    context = {
        'profile': profile,
        'educations': educations,
        'articles': articles,
        'presentations': presentations,
        'training_courses': training_courses,
        'social_profiles': social_profiles,
        'executive_records': executive_records,
        'connection_status': connection_status,
        'is_connected': is_connected,
    }
    
    return render(request, 'networking/profile_detail.html', context)


@login_required
def send_connection_request(request, pk):
    """ارسال درخواست اتصال"""
    to_profile = get_object_or_404(Profile, pk=pk)
    from_profile = request.user.profile
    
    if from_profile == to_profile:
        return redirect('networking:profile_detail', pk=pk)
    
    # بررسی اینکه درخواست قبلی وجود دارد یا نه
    connection, created = NetworkingConnection.objects.get_or_create(
        from_user=from_profile,
        to_user=to_profile,
        defaults={'status': 'pending'}
    )
    
    return redirect('networking:profile_detail', pk=pk)


@login_required
def accept_connection_request(request, connection_id):
    """پذیرش درخواست اتصال"""
    connection = get_object_or_404(NetworkingConnection, id=connection_id)
    
    if connection.to_user != request.user.profile:
        return redirect('networking:networking_list')
    
    connection.status = 'accepted'
    connection.save()
    
    return redirect('networking:profile_detail', pk=connection.from_user.pk)


@login_required
def reject_connection_request(request, connection_id):
    """رد درخواست اتصال"""
    connection = get_object_or_404(NetworkingConnection, id=connection_id)
    
    if connection.to_user != request.user.profile:
        return redirect('networking:networking_list')
    
    connection.status = 'rejected'
    connection.save()
    
    return redirect('networking:networking_list')
