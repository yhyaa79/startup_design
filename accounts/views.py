# accounts/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from .models import (
    SocialProfile, Education, Article, Presentation,
    ExecutiveRecord, Profile, TrainingCourse
)
from .ai_utils import extract_profile_from_text, _sanitize_profile_data
from .file_utils import extract_text_from_file
from .forms import (
    ProfileForm,
    SocialProfileFormSet,
    EducationFormSet,
    ArticleFormSet,
    PresentationFormSet,
    ExecutiveRecordFormSet,
    TrainingCourseFormSet,
)


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
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()

        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            try:
                file_text = extract_text_from_file(uploaded_file)
                text = (text + '\n' + file_text).strip()
            except (ImportError, ValueError) as e:
                messages.error(request, str(e))
                return render(
                    request,
                    'accounts/edit_profile_ai_details.html',
                    {'raw_text': profile.raw_text}
                )

        profile.raw_text = text
        profile.save(update_fields=['raw_text'])

        try:
            data = extract_profile_from_text(text)
        except Exception:
            messages.error(
                request,
                "در حال حاضر سرویس هوش مصنوعی در دسترس نیست. لطفاً بعداً دوباره تلاش کنید."
            )
            return render(
                request,
                'accounts/edit_profile_ai_details.html',
                {
                    'raw_text': text,
                    'ai_error': True
                }
            )

        for field, value in _sanitize_profile_data(data.get('profile', {})).items():
            setattr(profile, field, value)
        profile.save()

        _bulk_append(profile.social_profiles, SocialProfile, data.get('social_profiles', []), profile)
        _bulk_append(profile.educations, Education, data.get('educations', []), profile)
        _bulk_append(profile.articles, Article, data.get('articles', []), profile)
        _bulk_append(profile.presentations, Presentation, data.get('presentations', []), profile)
        _bulk_append(profile.executive_records, ExecutiveRecord, data.get('executive_records', []), profile)
        _bulk_append(profile.training_courses, TrainingCourse, data.get('training_courses', []), profile)

        return redirect('accounts:edit_profile')

    return render(request, 'accounts/edit_profile_ai_details.html', {'raw_text': profile.raw_text})


def _bulk_replace(related_manager, model_class, items: list, profile):
    related_manager.all().delete()
    for item in items:
        model_class.objects.create(profile=profile, **item)


def _bulk_append(related_manager, model_class, items: list, profile):
    # فیلدهای معتبر مدل رو بگیر
    valid_fields = {f.name for f in model_class._meta.get_fields() if hasattr(f, 'column')}
    for item in items:
        # فقط فیلدهای معتبر رو نگه دار
        filtered = {k: v for k, v in item.items() if k in valid_fields}
        model_class.objects.create(profile=profile, **filtered)