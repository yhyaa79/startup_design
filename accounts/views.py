# accounts/views.py

import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from .models import (
    SocialProfile, Education, Article, Presentation,
    ExecutiveRecord, Profile, TrainingCourse
)
from .ai_utils import extract_profile_from_text
from .file_utils import extract_text_from_file, FileExtractionError
from .forms import (
    ProfileForm,
    SocialProfileFormSet,
    EducationFormSet,
    ArticleFormSet,
    PresentationFormSet,
    ExecutiveRecordFormSet,
    TrainingCourseFormSet,
)

logger = logging.getLogger(__name__)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')  # نام app خود را جایگزین کنید
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'core:home')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:edit_profile_ai')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


def profile(request, pk):
    profile = get_object_or_404(
        Profile.objects.prefetch_related(
            'social_profiles',
            'educations',
            'articles',
            'presentations',
            'executive_records',
            'training_courses',
        ),
        pk=pk,
    )
    return render(request, 'accounts/profile_details.html', {'profile': profile})


@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        social_formset = SocialProfileFormSet(request.POST, instance=profile)
        education_formset = EducationFormSet(request.POST, instance=profile)
        article_formset = ArticleFormSet(request.POST, instance=profile)
        presentation_formset = PresentationFormSet(request.POST, instance=profile)
        executive_formset = ExecutiveRecordFormSet(request.POST, instance=profile)
        training_course_formset = TrainingCourseFormSet(request.POST, instance=profile)

        if (
            form.is_valid()
            and social_formset.is_valid()
            and education_formset.is_valid()
            and article_formset.is_valid()
            and presentation_formset.is_valid()
            and executive_formset.is_valid()
            and training_course_formset.is_valid()
        ):
            form.save()
            social_formset.save()
            education_formset.save()
            article_formset.save()
            presentation_formset.save()
            executive_formset.save()
            training_course_formset.save()
            return redirect('accounts:profile', pk=profile.pk)
    else:
        form = ProfileForm(instance=profile)
        social_formset = SocialProfileFormSet(instance=profile)
        education_formset = EducationFormSet(instance=profile)
        article_formset = ArticleFormSet(instance=profile)
        presentation_formset = PresentationFormSet(instance=profile)
        executive_formset = ExecutiveRecordFormSet(instance=profile)
        training_course_formset = TrainingCourseFormSet(instance=profile)

    context = {
        'form': form,
        'social_formset': social_formset,
        'education_formset': education_formset,
        'article_formset': article_formset,
        'presentation_formset': presentation_formset,
        'executive_formset': executive_formset,
        'training_course_formset': training_course_formset,
    }
    return render(request, 'accounts/edit_profile_details.html', context)


@login_required
def edit_profile_ai(request):
    """
    ویرایش پروفایل با استفاده از هوش مصنوعی.
    کاربر متن یا فایل آپلود می‌کند و AI اطلاعات را استخراج می‌کند.
    بعد از استخراج، مستقیم به صفحه ادیت دستی می‌رود.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()

        # پردازش فایل آپلود شده
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            try:
                file_text = extract_text_from_file(uploaded_file)
                text = (text + '\n' + file_text).strip()
            except (ImportError, ValueError) as e:
                messages.error(request, str(e))
                return render(request, 'accounts/edit_profile_ai_details.html', {'raw_text': profile.raw_text})

        if not text:
            messages.error(request, 'لطفاً متن وارد کنید یا فایلی آپلود کنید.')
            return render(request, 'accounts/edit_profile_ai_details.html', {'raw_text': profile.raw_text})

        # ذخیره متن خام
        profile.raw_text = text
        profile.save(update_fields=['raw_text'])

        try:
            # استخراج اطلاعات با AI
            data = extract_profile_from_text(text)

            # ذخیره اطلاعات پروفایل در دیتابیس
            for field, value in data.get('profile', {}).items():
                if hasattr(profile, field):
                    setattr(profile, field, value)
            profile.save()

            # پاک کردن داده‌های قبلی و ذخیره داده‌های جدید
            _bulk_replace(profile.social_profiles, SocialProfile, data.get('social_profiles', []), profile)
            _bulk_replace(profile.educations, Education, data.get('educations', []), profile)
            _bulk_replace(profile.articles, Article, data.get('articles', []), profile)
            _bulk_replace(profile.presentations, Presentation, data.get('presentations', []), profile)
            _bulk_replace(profile.executive_records, ExecutiveRecord, data.get('executive_records', []), profile)
            _bulk_replace(profile.training_courses, TrainingCourse, data.get('training_courses', []), profile)

            messages.success(request, 'رزومه شما پردازش شد. اطلاعات استخراج شده را می‌توانید ادیت کنید.')
            return redirect('accounts:edit_profile')

        except ValueError as e:
            logger.exception("خطای AI (ValueError)")
            return render(request, 'accounts/edit_profile_ai_details.html', {
                'raw_text': profile.raw_text,
                'ai_error': True,
            })
        except ConnectionError as e:
            logger.exception("خطای اتصال به AI")
            return render(request, 'accounts/edit_profile_ai_details.html', {
                'raw_text': profile.raw_text,
                'ai_error': True,
            })
        except Exception as e:
            logger.exception("خطای غیرمنتظره در پردازش AI")
            return render(request, 'accounts/edit_profile_ai_details.html', {
                'raw_text': profile.raw_text,
                'ai_error': True,
            })

    return render(request, 'accounts/edit_profile_ai_details.html', {'raw_text': profile.raw_text})





def _bulk_replace(related_manager, model_class, items: list, profile):
    related_manager.all().delete()
    for item in items:
        model_class.objects.create(profile=profile, **item)


def _bulk_append(related_manager, model_class, items: list, profile):
    """
    آیتم‌های استخراج‌شده توسط AI را به رکوردهای مدل تبدیل می‌کند.
    فیلدهای ناشناخته را نادیده می‌گیرد و اگر یک آیتم به هر دلیلی خطای دیتابیس داد،
    کل درخواست را متوقف نمی‌کند بلکه فقط همان آیتم را رد می‌کند.
    """
    if not items:
        return

    valid_fields = {f.name for f in model_class._meta.get_fields() if hasattr(f, 'column')}

    for item in items:
        if not isinstance(item, dict):
            continue
        filtered = {k: v for k, v in item.items() if k in valid_fields}
        try:
            model_class.objects.create(profile=profile, **filtered)
        except Exception:
            logger.exception(
                "خطا هنگام ذخیره یک رکورد %s از داده‌های استخراج‌شده AI: %r",
                model_class.__name__, filtered
            )
            continue