# accounts/forms.py

from django import forms
from django.forms import inlineformset_factory

from .models import (
    Profile, SocialProfile, Education, Article,
    Presentation, ExecutiveRecord, TrainingCourse,
)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user', 'created_at', 'updated_at', 'raw_text']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': ''}),
            'last_name': forms.TextInput(attrs={'placeholder': ''}),
            'job_title': forms.TextInput(attrs={'placeholder': ''}),
            'birth_date': forms.TextInput(attrs={'placeholder': 'مثال: ۱۳۸۰/۰۵/۱۲'}),
            'country': forms.TextInput(attrs={'placeholder': 'مثال: ایران'}),
            'city': forms.TextInput(),
            'phone': forms.TextInput(attrs={'type': 'tel'}),
            'email': forms.EmailInput(),
            'website': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'national_id': forms.TextInput(),
            'orcid': forms.TextInput(attrs={'placeholder': '0000-0000-0000-0000'}),
            'proposal_count': forms.NumberInput(attrs={'min': 0, 'placeholder': 'مثال: ۲'}),
            'software_skills': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'مثال: SPSS - متوسط، Python - مقدماتی، EndNote - پیشرفته'
            }),
            'writing_skills': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'مثال: پروپوزال‌نویسی - متوسط، نگارش مقاله - مقدماتی'
            }),
            'clinical_certs': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'مثال: BLS - معتبر تا ۱۴۰۵، ACLS - ندارم'
            }),
            'clinical_exp': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'مثال: کار در داروخانه Y به مدت ۳ ماه'
            }),
            'procedures': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'مثال: بخیه، تزریق وریدی، گذاشتن IV Line'
            }),
            'native_lang': forms.TextInput(),
            'lang_cert': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'مثال: IELTS - نمره ۷ - معتبر تا ۱۴۰۶، یا ندارم'
            }),
            'other_langs': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'مثال: آلمانی B1 - گواهی گوته، فرانسه A2 - بدون مدرک'
            }),
            'extracurricular': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'مثال: عضو IFMSA، داوطلب هلال احمر'
            }),
            'specialty': forms.TextInput(attrs={
                'placeholder': 'مثال: قلب و عروق، انکولوژی، پزشکی اورژانس'
            }),
            'goal_notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'هر توضیح اضافه‌ای درباره مسیر شغلی مورد نظرتان'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['military_status'].required = False
        self.fields['marital_status'].required = False
        self.fields['service_plan'].required = False


class SocialProfileForm(forms.ModelForm):
    class Meta:
        model = SocialProfile
        exclude = ['profile']
        widgets = {
            'url': forms.URLInput(attrs={'placeholder': 'https://...'})
        }


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        exclude = ['profile']
        widgets = {
            'university': forms.TextInput(),
            'start_date': forms.TextInput(attrs={'placeholder': 'مثال: ۱۳۹۸/۰۷/۰۱'}),
            'end_date': forms.TextInput(attrs={'placeholder': 'مثال: ۱۴۰۴/۰۶/۳۱ یا در حال تحصیل'}),
            'current_term': forms.NumberInput(attrs={'min': 1, 'max': 20}),
            'remaining_terms': forms.NumberInput(attrs={'min': 0, 'max': 20}),
            'gpa': forms.NumberInput(attrs={
                'step': '0.01', 'min': 0, 'max': 20,
                'placeholder': 'مثال: ۱۷.۵۰'
            }),
        }


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        exclude = ['profile']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'عنوان کامل مقاله'}),
            'journal': forms.TextInput(),
            'impact_factor': forms.NumberInput(attrs={'step': '0.001', 'min': 0, 'placeholder': 'مثال: ۳.۵'}),
            'year': forms.NumberInput(attrs={'min': 1370, 'max': 1410, 'placeholder': 'مثال: ۱۴۰۲'}),
            'author_rank': forms.NumberInput(attrs={'min': 1, 'placeholder': 'مثال: ۱'}),
            'total_authors': forms.NumberInput(attrs={'min': 1, 'placeholder': 'مثال: ۵'}),
        }


class PresentationForm(forms.ModelForm):
    class Meta:
        model = Presentation
        exclude = ['profile']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'عنوان پوستر یا سخنرانی'}),
            'event': forms.TextInput(),
        }


class ExecutiveRecordForm(forms.ModelForm):
    class Meta:
        model = ExecutiveRecord
        exclude = ['profile']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'مثال: عضو کمیته تحقیقات دانشجویی، رئیس انجمن علمی پزشکی'
            }),
            'start_date': forms.TextInput(attrs={'placeholder': 'مثال: ۱۴۰۱/۰۷'}),
            'end_date': forms.TextInput(attrs={'placeholder': 'مثال: ۱۴۰۳/۰۳ یا تاکنون'}),
        }


class TrainingCourseForm(forms.ModelForm):
    class Meta:
        model = TrainingCourse
        exclude = ['profile']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'مثال: آموزش مقاله‌نویسی پزشکی'}),
            'organizer': forms.TextInput(attrs={'placeholder': 'مثال: آکادمی شما'}),
            'date': forms.TextInput(attrs={'placeholder': 'مثال: ۱۴۰۴/۰۸'}),
            'skills_gained': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'مثال: ساختار مقاله، کاورلتر، انتخاب ژورنال'
            }),
        }


# --- Inline Formsets ---
SocialProfileFormSet = inlineformset_factory(
    Profile, SocialProfile,
    form=SocialProfileForm,
    extra=1, can_delete=True,
)

EducationFormSet = inlineformset_factory(
    Profile, Education,
    form=EducationForm,
    extra=1, can_delete=True,
)

ArticleFormSet = inlineformset_factory(
    Profile, Article,
    form=ArticleForm,
    extra=1, can_delete=True,
)

PresentationFormSet = inlineformset_factory(
    Profile, Presentation,
    form=PresentationForm,
    extra=1, can_delete=True,
)

ExecutiveRecordFormSet = inlineformset_factory(
    Profile, ExecutiveRecord,
    form=ExecutiveRecordForm,
    extra=1, can_delete=True,
)

TrainingCourseFormSet = inlineformset_factory(
    Profile, TrainingCourse,
    form=TrainingCourseForm,
    extra=1, can_delete=True,
)
